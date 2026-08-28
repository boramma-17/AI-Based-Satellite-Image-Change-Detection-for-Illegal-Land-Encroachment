import re


def validate_registration(
    username,
    email,
    password,
    confirm_password
):

    errors = []

    if not username:

        errors.append(
            "Username is required."
        )

    elif len(username) < 3:

        errors.append(
            "Username must contain at least 3 characters."
        )

    if not email:

        errors.append(
            "Email address is required."
        )

    elif not re.match(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        email
    ):

        errors.append(
            "Please enter a valid email address."
        )

    if not password:

        errors.append(
            "Password is required."
        )

    elif len(password) < 6:

        errors.append(
            "Password must contain at least 6 characters."
        )

    if password != confirm_password:

        errors.append(
            "Passwords do not match."
        )

    return errors


def validate_login(
    email,
    password
):

    errors = []

    if not email:

        errors.append(
            "Email address is required."
        )

    if not password:

        errors.append(
            "Password is required."
        )

    return errors