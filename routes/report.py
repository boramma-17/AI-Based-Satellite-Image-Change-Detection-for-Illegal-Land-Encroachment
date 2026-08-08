import os

from flask import (
    Blueprint,
    send_file,
    current_app,
    session,
    abort,
    flash,
    redirect,
    url_for
)

from utils.helpers import login_required
from utils.database import get_db

from services.pdf_service import generate_report


bp = Blueprint(
    "report",
    __name__
)


@bp.route(
    "/detection/<int:detection_id>/report"
)
@login_required
def download_report(
    detection_id
):

    db = get_db()

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

    if not detection["result_image"]:

        flash(
            "Run detection before generating a report.",
            "error"
        )

        return redirect(
            url_for(
                "detection.result",
                detection_id=detection_id
            )
        )

    cfg = current_app.config

    before_path = os.path.join(
        cfg["UPLOAD_BEFORE"],
        detection["before_image"]
    )

    after_path = os.path.join(
        cfg["UPLOAD_AFTER"],
        detection["after_image"]
    )

    result_path = os.path.join(
        cfg["UPLOAD_RESULTS"],
        detection["result_image"]
    )

    output_path = os.path.join(
        cfg["REPORTS_DIR"],
        f"report_{detection_id}.pdf"
    )

    generate_report(
        dict(detection),
        before_path,
        after_path,
        result_path,
        output_path
    )

    db.execute(
        """
        UPDATE detections
        SET report_path = ?
        WHERE id = ?
          AND user_id = ?
        """,
        (
            os.path.basename(
                output_path
            ),
            detection_id,
            session["user_id"]
        )
    )

    db.commit()

    return send_file(
        output_path,
        as_attachment=True,
        download_name=(
            f"encroachment_report_"
            f"{detection_id}.pdf"
        )
    )