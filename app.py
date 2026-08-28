import os
from flask import Flask, render_template, session, send_from_directory
from config import Config
from utils.database import ensure_db_exists, register_db_teardown, get_db
from utils.helpers import login_required, admin_required

from routes.auth import bp as auth_bp
from routes.upload import bp as upload_bp
from routes.detection import bp as detection_bp
from routes.history import bp as history_bp
from routes.report import bp as report_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required system storage directories exist
    for directory in [
        app.config["DATABASE_DIR"],
        app.config["UPLOAD_BEFORE"],
        app.config["UPLOAD_AFTER"],
        app.config["UPLOAD_RESULTS"],
        app.config["REPORTS_DIR"]
    ]:
        os.makedirs(directory, exist_ok=True)

    # Initialize Database and register teardown context
    ensure_db_exists(app)
    register_db_teardown(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(detection_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(report_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    # -------------------------------------------------------------
    # Defensive Dashboard Route with Schema Fallbacks & Safe COALESCE
    # -------------------------------------------------------------
    @app.route("/dashboard")
    @login_required
    def dashboard():
        db = get_db()

        # Dynamic runtime check: patch missing columns on the fly if needed
        cols = [r[1] for r in db.execute("PRAGMA table_info(detections)").fetchall()]
        schema_patches = {
            "title": "TEXT DEFAULT 'Untitled Detection'",
            "location_name": "TEXT DEFAULT 'Monitored Sector'",
            "latitude": "REAL DEFAULT 12.9716",
            "longitude": "REAL DEFAULT 77.5946",
            "land_type": "TEXT DEFAULT 'Unclassified'",
            "encroachment_flag": "INTEGER DEFAULT 0",
            "change_percent": "REAL DEFAULT 0.0",
            "area_sqm": "REAL DEFAULT 0.0"
        }
        for col_name, col_type in schema_patches.items():
            if col_name not in cols:
                db.execute(f"ALTER TABLE detections ADD COLUMN {col_name} {col_type}")
                db.commit()

        # Aggregate Statistics Query
        stats = db.execute("""
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(encroachment_flag), 0) AS flagged,
                COALESCE(AVG(change_percent), 0.0) AS average_change
            FROM detections
            WHERE user_id = ?
        """, (session["user_id"],)).fetchone()

        # Recent Detection Records with Explicit Column Fallbacks
        recent = db.execute("""
            SELECT 
                id,
                COALESCE(title, 'Untitled Scan') AS title,
                COALESCE(location_name, 'Monitored Sector') AS location_name,
                COALESCE(latitude, 12.9716) AS latitude,
                COALESCE(longitude, 77.5946) AS longitude,
                COALESCE(land_type, 'Unclassified') AS land_type,
                COALESCE(encroachment_flag, 0) AS encroachment_flag,
                COALESCE(change_percent, 0.0) AS change_percent,
                COALESCE(area_sqm, 0.0) AS area_sqm,
                created_at
            FROM detections 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 6
        """, (session["user_id"],)).fetchall()

        return render_template("dashboard.html", stats=stats, recent=recent)

    # -------------------------------------------------------------
    # Administrative Console
    # -------------------------------------------------------------
    @app.route("/admin")
    @admin_required
    def admin():
        db = get_db()
        users = db.execute(
            "SELECT id, username, email, role, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()

        detections = db.execute("""
            SELECT 
                d.id,
                u.username,
                COALESCE(d.title, 'Untitled Scan') AS title,
                COALESCE(d.location_name, 'Monitored Sector') AS location_name,
                COALESCE(d.land_type, 'Unclassified') AS land_type,
                COALESCE(d.encroachment_flag, 0) AS encroachment_flag,
                COALESCE(d.change_percent, 0.0) AS change_percent,
                COALESCE(d.area_sqm, 0.0) AS area_sqm,
                d.created_at
            FROM detections d
            JOIN users u ON u.id = d.user_id
            ORDER BY d.created_at DESC 
            LIMIT 50
        """).fetchall()

        return render_template("admin.html", users=users, detections=detections)

    # -------------------------------------------------------------
    # Static Image & Artifact Endpoints
    # -------------------------------------------------------------
    @app.route("/media/before/<path:filename>")
    @login_required
    def media_before(filename):
        return send_from_directory(app.config["UPLOAD_BEFORE"], filename)

    @app.route("/media/after/<path:filename>")
    @login_required
    def media_after(filename):
        return send_from_directory(app.config["UPLOAD_AFTER"], filename)

    @app.route("/media/results/<path:filename>")
    @login_required
    def media_results(filename):
        return send_from_directory(app.config["UPLOAD_RESULTS"], filename)

    # -------------------------------------------------------------
    # Error Handlers
    # -------------------------------------------------------------
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)