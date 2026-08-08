import os

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
    session,
    abort,
)

from utils.database import get_db
from utils.helpers import login_required
from services.ai_service import run_detection


# ONLY ONE detection blueprint
bp = Blueprint("detection", __name__)


def _get_owned_detection(db, detection_id):
    detection = db.execute(
        """
        SELECT *
        FROM detections
        WHERE id = ?
        AND user_id = ?
        """,
        (
            detection_id,
            session["user_id"],
        ),
    ).fetchone()

    if detection is None:
        abort(404)

    return detection


@bp.route("/detection/<int:detection_id>/run")
@login_required
def run_detection_view(detection_id):

    db = get_db()

    detection = _get_owned_detection(
        db,
        detection_id
    )

    before_path = os.path.join(
        current_app.config["UPLOAD_BEFORE"],
        detection["before_image"],
    )

    after_path = os.path.join(
        current_app.config["UPLOAD_AFTER"],
        detection["after_image"],
    )

    try:
        result = run_detection(
            before_path,
            after_path,
        )

    except Exception as e:
        flash(
            f"Detection failed: {e}",
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
            encroachment_flag = ?
        WHERE id = ?
        """,
        (
            result["result_filename"],
            result["change_percent"],
            int(result["encroachment_flag"]),
            detection_id,
        ),
    )

    db.commit()

    flash(
        "Detection completed successfully.",
        "success"
    )

    return redirect(
        url_for(
            "detection.result",
            detection_id=detection_id,
        )
    )


@bp.route("/detection/<int:detection_id>")
@login_required
def result(detection_id):

    db = get_db()

    detection = _get_owned_detection(
        db,
        detection_id
    )

    return render_template(
        "result.html",
        detection=detection,
    )