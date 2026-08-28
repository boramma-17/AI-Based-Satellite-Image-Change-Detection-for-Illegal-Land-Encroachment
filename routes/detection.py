import os

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
    session,
    abort
)

from utils.helpers import login_required
from utils.database import get_db

from services.ai_service import run_detection


bp = Blueprint(
    "detection",
    __name__,
    url_prefix="/detection"
)


def get_owned_detection(
    db,
    detection_id
):

    detection = db.execute(
        """
        SELECT *
        FROM detections
        WHERE id = ?
          AND user_id = ?
        """,
        (
            detection_id,
            session["user_id"]
        )
    ).fetchone()

    if detection is None:

        abort(404)

    return detection


@bp.route(
    "/<int:detection_id>/run"
)
@login_required
def run_detection_view(
    detection_id
):

    db = get_db()

    detection = get_owned_detection(
        db,
        detection_id
    )

    config = current_app.config

    before_path = os.path.join(
        config["UPLOAD_BEFORE"],
        detection["before_image"]
    )

    after_path = os.path.join(
        config["UPLOAD_AFTER"],
        detection["after_image"]
    )

    try:

        result = run_detection(
            before_path,
            after_path
        )

    except Exception as error:

        flash(
            f"Detection failed: {error}",
            "error"
        )

        return redirect(
            url_for("upload.upload")
        )

    db.execute(
        """
        UPDATE detections
        SET
            result_image = ?,
            change_percent = ?,
            encroachment_flag = ?,
            land_type = ?,
            decision = ?
        WHERE id = ?
          AND user_id = ?
        """,
        (
            result["result_filename"],
            result["change_percent"],
            result["encroachment_flag"],
            result["land_type"],
            result["decision"],
            detection_id,
            session["user_id"]
        )
    )

    db.commit()

    flash(
        "Satellite image detection completed.",
        "success"
    )

    return redirect(
        url_for(
            "detection.result",
            detection_id=detection_id
        )
    )


@bp.route(
    "/<int:detection_id>"
)
@login_required
def result(
    detection_id
):

    db = get_db()

    detection = get_owned_detection(
        db,
        detection_id
    )

    return render_template(
        "result.html",
        detection=detection
    )
    