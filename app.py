import os

from flask import (
    Flask,
    render_template,
    session,
    send_from_directory,
    redirect,
)

from config import Config

from utils.database import (
    ensure_db_exists,
    register_db_teardown,
    get_db,
)

from utils.helpers import (
    login_required,
    admin_required,
)

from routes.auth import bp as auth_bp
from routes.upload import bp as upload_bp
from routes.detection import bp as detection_bp
from routes.history import bp as history_bp
from routes.report import bp as report_bp


def create_app(config_class=Config):

    # --------------------------------------------------
    # Create Flask application
    # --------------------------------------------------

    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_class)

    # --------------------------------------------------
    # Create required directories
    # --------------------------------------------------

    required_directories = [
        app.config["UPLOAD_BEFORE"],
        app.config["UPLOAD_AFTER"],
        app.config["UPLOAD_RESULTS"],
        app.config["REPORTS_DIR"],
    ]

    for directory in required_directories:
        os.makedirs(directory, exist_ok=True)

    # --------------------------------------------------
    # Database setup
    # --------------------------------------------------

    register_db_teardown(app)
    ensure_db_exists(app)

    # --------------------------------------------------
    # Register blueprints
    #
    # IMPORTANT:
    # detection_bp is registered ONLY ONCE.
    # --------------------------------------------------

    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(report_bp)

    # --------------------------------------------------
    # HOME PAGE
    # --------------------------------------------------

    @app.route("/")
    def index():

        if session.get("user_id"):

            return redirect("/dashboard")

        return render_template("index.html")

    # --------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------

    @app.route("/dashboard")
    @login_required
    def dashboard():

        db = get_db()

        # Statistics
        stats = db.execute(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(
                    SUM(encroachment_flag),
                    0
                ) AS flagged
            FROM detections
            WHERE user_id = ?
            """,
            (
                session["user_id"],
            ),
        ).fetchone()

        # Recent detections
        recent = db.execute(
            """
            SELECT *
            FROM detections
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (
                session["user_id"],
            ),
        ).fetchall()

        return render_template(
            "dashboard.html",
            stats=stats,
            recent=recent,
        )

    # --------------------------------------------------
    # ADMIN PAGE
    # --------------------------------------------------

    @app.route("/admin")
    @admin_required
    def admin():

        db = get_db()

        # Users
        users = db.execute(
            """
            SELECT
                id,
                username,
                email,
                role,
                created_at
            FROM users
            ORDER BY created_at DESC
            """
        ).fetchall()

        # Detections
        detections = db.execute(
            """
            SELECT
                d.*,
                u.username
            FROM detections AS d
            JOIN users AS u
                ON u.id = d.user_id
            ORDER BY d.created_at DESC
            LIMIT 50
            """
        ).fetchall()

        return render_template(
            "admin.html",
            users=users,
            detections=detections,
        )

    # --------------------------------------------------
    # SERVE BEFORE IMAGES
    # --------------------------------------------------

    @app.route("/media/before/<path:filename>")
    def media_before(filename):

        return send_from_directory(
            app.config["UPLOAD_BEFORE"],
            filename,
        )

    # --------------------------------------------------
    # SERVE AFTER IMAGES
    # --------------------------------------------------

    @app.route("/media/after/<path:filename>")
    def media_after(filename):

        return send_from_directory(
            app.config["UPLOAD_AFTER"],
            filename,
        )

    # --------------------------------------------------
    # SERVE RESULT IMAGES
    # --------------------------------------------------

    @app.route("/media/results/<path:filename>")
    def media_results(filename):

        return send_from_directory(
            app.config["UPLOAD_RESULTS"],
            filename,
        )

    # --------------------------------------------------
    # 404 ERROR
    # --------------------------------------------------

    @app.errorhandler(404)
    def not_found(error):

        if template_exists(app, "404.html"):

            return render_template(
                "404.html"
            ), 404

        return (
            "Page not found",
            404,
        )

    # --------------------------------------------------
    # Return application
    # --------------------------------------------------

    return app


def template_exists(app, template_name):

    try:

        app.jinja_env.get_template(
            template_name
        )

        return True

    except Exception:

        return False


# ======================================================
# CREATE APPLICATION
# ======================================================

app = create_app()


# ======================================================
# RUN APPLICATION
# ======================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000,
    )