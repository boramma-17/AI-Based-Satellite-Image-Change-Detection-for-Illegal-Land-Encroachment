import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app
)

from utils.database import get_db
from utils.helpers import login_required

from services.image_processing import (
    detect_encroachment
)


bp = Blueprint(
    "upload",
    __name__
)


ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "tif",
    "tiff"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


@bp.route(
    "/upload",
    methods=["GET", "POST"]
)
@login_required
def upload():

    if request.method == "POST":

        before_file = request.files.get(
            "before_image"
        )

        after_file = request.files.get(
            "after_image"
        )

        latitude = request.form.get(
            "latitude",
            ""
        ).strip()

        longitude = request.form.get(
            "longitude",
            ""
        ).strip()

        title = request.form.get(
            "title",
            ""
        ).strip()

        if (
            not before_file
            or not after_file
            or not before_file.filename
            or not after_file.filename
        ):

            flash(
                "Both before and after images are required.",
                "error"
            )

            return redirect(
                request.url
            )

        if not allowed_file(
            before_file.filename
        ):

            flash(
                "Invalid before image format.",
                "error"
            )

            return redirect(
                request.url
            )

        if not allowed_file(
            after_file.filename
        ):

            flash(
                "Invalid after image format.",
                "error"
            )

            return redirect(
                request.url
            )

        ext1 = before_file.filename.rsplit(
            ".",
            1
        )[1].lower()

        ext2 = after_file.filename.rsplit(
            ".",
            1
        )[1].lower()

        before_filename = (
            f"before_{uuid.uuid4().hex}."
            f"{ext1}"
        )

        after_filename = (
            f"after_{uuid.uuid4().hex}."
            f"{ext2}"
        )

        result_filename = (
            f"result_{uuid.uuid4().hex}.png"
        )

        before_path = os.path.join(
            current_app.config["UPLOAD_BEFORE"],
            before_filename
        )

        after_path = os.path.join(
            current_app.config["UPLOAD_AFTER"],
            after_filename
        )

        result_path = os.path.join(
            current_app.config["UPLOAD_RESULTS"],
            result_filename
        )

        try:

            before_file.save(
                before_path
            )

            after_file.save(
                after_path
            )

            result = detect_encroachment(
                before_path,
                after_path,
                result_path
            )

        except Exception as e:

            flash(
                f"Detection failed: {e}",
                "error"
            )

            return redirect(
                request.url
            )

        try:

            latitude_value = (
                float(latitude)
                if latitude
                else None
            )

            longitude_value = (
                float(longitude)
                if longitude
                else None
            )

        except ValueError:

            flash(
                "Latitude and longitude must be numbers.",
                "error"
            )

            return redirect(
                request.url
            )

        db = get_db()

        user_id = session.get(
            "user_id"
        )

        # Make sure logged-in user actually exists
        user = db.execute(
            """
            SELECT id
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        if user is None:

            session.clear()

            flash(
                "Your session is invalid. Please log in again.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )

        cursor = db.execute(
            """
            INSERT INTO detections
            (
                user_id,
                title,
                before_image,
                after_image,
                result_image,
                change_percent,
                encroachment_flag,
                latitude,
                longitude
            )
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                title or "Satellite Change Detection",
                before_filename,
                after_filename,
                result_filename,
                result["change_percent"],
                int(result["encroachment_flag"]),
                latitude_value,
                longitude_value
            )
        )

        db.commit()

        detection_id = cursor.lastrowid

        flash(
            "Detection completed successfully.",
            "success"
        )

        return redirect(
            url_for(
                "detection.result",
                detection_id=detection_id
            )
        )

    return render_template(
        "upload.html"
    )