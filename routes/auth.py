from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from utils.database import get_db
from utils.validation import (
    validate_registration,
    validate_login
)
from utils.helpers import flash_errors


bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        errors = validate_registration(
            username,
            email,
            password,
            confirm_password
        )

        db = get_db()

        if not errors:

            existing = db.execute(
                """
                SELECT id
                FROM users
                WHERE username = ?
                   OR email = ?
                """,
                (
                    username,
                    email
                )
            ).fetchone()

            if existing:

                errors.append(
                    "Username or email is already registered."
                )

        if errors:

            flash_errors(
                flash,
                errors
            )

            return render_template(
                "register.html",
                username=username,
                email=email
            )

        password_hash = generate_password_hash(
            password
        )

        db.execute(
            """
            INSERT INTO users
            (
                username,
                email,
                password_hash,
                role
            )
            VALUES (?, ?, ?, 'user')
            """,
            (
                username,
                email,
                password_hash
            )
        )

        db.commit()

        flash(
            "Registration successful. Please log in.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "register.html"
    )


@bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        errors = validate_login(
            email,
            password
        )

        if errors:

            flash_errors(
                flash,
                errors
            )

            return render_template(
                "login.html",
                email=email
            )

        db = get_db()

        user = db.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if user is None:

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template(
                "login.html",
                email=email
            )

        try:

            valid = check_password_hash(
                user["password_hash"],
                password
            )

        except Exception:

            valid = False

        if not valid:

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template(
                "login.html",
                email=email
            )

        session.clear()

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        flash(
            f"Welcome back, {user['username']}!",
            "success"
        )

        if user["role"] == "admin":

            return redirect(
                url_for("admin")
            )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "login.html"
    )


@bp.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("index")
    )