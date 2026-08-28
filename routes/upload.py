import os
import uuid

import numpy as np
from PIL import Image, ImageChops, ImageOps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
)

from utils.database import get_db
from utils.helpers import login_required


bp = Blueprint("upload", __name__, url_prefix="/upload")

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "tif",
    "tiff",
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_coordinates():
    """
    Get coordinates submitted by the frontend.

    We DO NOT silently use the same location for every detection.
    """

    latitude_raw = request.form.get("latitude", "").strip()
    longitude_raw = request.form.get("longitude", "").strip()

    if not latitude_raw or not longitude_raw:
        return None, None

    try:
        latitude = float(latitude_raw)
        longitude = float(longitude_raw)
    except ValueError:
        return None, None

    # Validate geographic ranges
    if not -90 <= latitude <= 90:
        return None, None

    if not -180 <= longitude <= 180:
        return None, None

    return latitude, longitude


@bp.route("/", methods=["GET", "POST"])
@login_required
def upload():

    if request.method == "POST":

        title = (
            request.form.get("title", "").strip()
            or "Satellite Detection Run"
        )

        location_name = (
            request.form.get("location_name", "").strip()
            or "Unknown Location"
        )

        land_type = (
            request.form.get("land_type", "").strip()
            or "Unclassified"
        )

        # ---------------------------------------------------------
        # GET REAL COORDINATES
        # ---------------------------------------------------------

        latitude, longitude = get_coordinates()

        if latitude is None or longitude is None:

            flash(
                "Please select or enter a valid latitude and longitude "
                "for this detection.",
                "danger",
            )

            return render_template("upload.html")

        # ---------------------------------------------------------
        # GET IMAGES
        # ---------------------------------------------------------

        file_before = request.files.get("before_image")
        file_after = request.files.get("after_image")

        if (
            not file_before
            or not file_after
            or file_before.filename == ""
            or file_after.filename == ""
        ):

            flash(
                "Both Baseline (T1) and Present (T2) satellite images "
                "are required.",
                "danger",
            )

            return render_template("upload.html")

        if not allowed_file(file_before.filename):

            flash(
                "Invalid baseline image format.",
                "danger",
            )

            return render_template("upload.html")

        if not allowed_file(file_after.filename):

            flash(
                "Invalid present image format.",
                "danger",
            )

            return render_template("upload.html")

        # ---------------------------------------------------------
        # CREATE UNIQUE FILE NAMES
        # ---------------------------------------------------------

        uid = uuid.uuid4().hex

        ext_before = file_before.filename.rsplit(".", 1)[1].lower()
        ext_after = file_after.filename.rsplit(".", 1)[1].lower()

        before_filename = f"before_{uid}.{ext_before}"
        after_filename = f"after_{uid}.{ext_after}"
        result_filename = f"result_{uid}.png"

        path_before = os.path.join(
            current_app.config["UPLOAD_BEFORE"],
            before_filename,
        )

        path_after = os.path.join(
            current_app.config["UPLOAD_AFTER"],
            after_filename,
        )

        path_result = os.path.join(
            current_app.config["UPLOAD_RESULTS"],
            result_filename,
        )

        # ---------------------------------------------------------
        # SAVE UPLOADED FILES
        # ---------------------------------------------------------

        file_before.save(path_before)
        file_after.save(path_after)

        # ---------------------------------------------------------
        # OPEN IMAGES
        # ---------------------------------------------------------

        try:

            img1 = Image.open(path_before).convert("RGB")
            img2 = Image.open(path_after).convert("RGB")

        except Exception:

            flash(
                "Could not read one of the satellite images.",
                "danger",
            )

            return render_template("upload.html")

        # ---------------------------------------------------------
        # STANDARDIZE SIZE
        # ---------------------------------------------------------

        if img1.size != img2.size:

            img2 = img2.resize(
                img1.size,
                Image.Resampling.LANCZOS,
            )

            img2.save(path_after)

        # ---------------------------------------------------------
        # CHANGE DETECTION
        # ---------------------------------------------------------

        diff = ImageChops.difference(
            img1,
            img2,
        )

        diff_gray = ImageOps.grayscale(diff)

        diff_np = np.array(diff_gray)

        threshold = 35

        change_mask = diff_np > threshold

        total_pixels = diff_np.size

        changed_pixels = int(
            np.count_nonzero(change_mask)
        )

        if total_pixels > 0:

            change_percent = round(
                (changed_pixels / total_pixels) * 100,
                2,
            )

        else:

            change_percent = 0.0

        # ---------------------------------------------------------
        # ESTIMATED AREA
        # ---------------------------------------------------------

        # Example:
        # one pixel = 2.5m x 2.5m = 6.25m²

        pixel_area = 6.25

        area_sqm = round(
            changed_pixels * pixel_area,
            2,
        )

        # ---------------------------------------------------------
        # CREATE RESULT IMAGE
        # ---------------------------------------------------------

        h, w = diff_np.shape

        rgba_mask = np.zeros(
            (h, w, 4),
            dtype=np.uint8,
        )

        rgba_mask[change_mask] = [
            244,
            63,
            94,
            210,
        ]

        mask_img = Image.fromarray(
            rgba_mask,
            mode="RGBA",
        )

        # Put mask over present image

        base_img = img2.convert("RGBA")

        result_img = Image.alpha_composite(
            base_img,
            mask_img,
        )

        result_img.save(
            path_result,
            "PNG",
        )

        # ---------------------------------------------------------
        # DECISION ENGINE
        # ---------------------------------------------------------

        normalized_land_type = land_type.lower()

        if normalized_land_type in [
            "forest",
            "water",
            "water body",
            "wetland",
        ]:

            threshold_percent = 4.0

        else:

            threshold_percent = 12.0

        if change_percent > threshold_percent:

            encroachment_flag = 1

            decision_status = "Illegal"

            decision_reason = (
                f"Detected change of {change_percent}% "
                f"exceeds the allowed threshold of "
                f"{threshold_percent}% for {land_type}."
            )

        else:

            encroachment_flag = 0

            decision_status = "Permitted"

            decision_reason = (
                f"Detected change of {change_percent}% "
                f"is within the allowed threshold of "
                f"{threshold_percent}%."
            )

        # ---------------------------------------------------------
        # DATABASE
        # ---------------------------------------------------------

        db = get_db()

        cursor = db.execute(
            """
            INSERT INTO detections (
                user_id,
                title,
                location_name,
                latitude,
                longitude,
                land_type,
                change_percent,
                area_sqm,
                encroachment_flag,
                decision_status,
                decision_reason,
                before_image,
                after_image,
                result_image
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                title,
                location_name,
                latitude,
                longitude,
                land_type,
                change_percent,
                area_sqm,
                encroachment_flag,
                decision_status,
                decision_reason,
                before_filename,
                after_filename,
                result_filename,
            ),
        )

        db.commit()

        detection_id = cursor.lastrowid

        flash(
            "Satellite image analysis completed successfully.",
            "success",
        )

        return redirect(
            url_for(
                "detection.result",
                detection_id=detection_id,
            )
        )

    return render_template("upload.html")