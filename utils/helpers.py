from functools import wraps

from flask import (
    session,
    redirect,
    url_for,
    flash
)


def login_required(view_func):

    @wraps(view_func)
    def wrapped(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please log in to continue.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        return view_func(*args, **kwargs)

    return wrapped


def admin_required(view_func):

    @wraps(view_func)
    def wrapped(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please log in first.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        if session.get("role") != "admin":

            flash(
                "Administrator access required.",
                "error"
            )

            return redirect(
                url_for("dashboard")
            )

        return view_func(*args, **kwargs)

    return wrapped


def flash_errors(flash_function, errors):

    for error in errors:

        flash_function(
            error,
            "error"
        )