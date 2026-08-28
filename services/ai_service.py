import os
import uuid

from flask import current_app

from services.image_processing import (
    detect_encroachment
)


def run_detection(
    before_path,
    after_path
):

    result_filename = (
        f"result_{uuid.uuid4().hex[:10]}.png"
    )

    result_path = os.path.join(
        current_app.config["UPLOAD_RESULTS"],
        result_filename
    )

    detection_result = detect_encroachment(
        before_path,
        after_path,
        result_path
    )

    change_percent = detection_result.get(
        "change_percent",
        0.0
    )

    encroachment_flag = detection_result.get(
        "encroachment_flag",
        False
    )

    land_type = detection_result.get(
        "land_type",
        "Unknown"
    )

    threshold = current_app.config.get(
        "ENCROACHMENT_THRESHOLD",
        5.0
    )

    if encroachment_flag:

        decision = "Possible Encroachment"

    elif change_percent >= threshold:

        decision = "Requires Review"

    else:

        decision = "No Significant Change"

    return {
        "result_filename": result_filename,
        "change_percent": float(change_percent),
        "encroachment_flag": int(
            bool(encroachment_flag)
        ),
        "land_type": land_type,
        "decision": decision
    }