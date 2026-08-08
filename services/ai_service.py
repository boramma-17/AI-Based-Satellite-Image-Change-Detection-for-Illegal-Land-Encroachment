"""Service layer that the routes call into -- keeps model/ internals decoupled from Flask."""
import os
import cv2
from flask import current_app

from model.predict import predict as run_prediction


def run_detection(before_path: str, after_path: str) -> dict:
    """Run detection and persist the annotated result image.

    Returns a dict with change_percent, num_regions, encroachment_flag,
    and result_filename (saved under uploads/results/).
    """
    cfg = current_app.config
    output = run_prediction(
        before_path,
        after_path,
        diff_threshold=cfg["DIFF_THRESHOLD"],
        min_area=cfg["CHANGE_AREA_THRESHOLD"],
    )

    os.makedirs(cfg["UPLOAD_RESULTS"], exist_ok=True)
    result_filename = f"result_{os.path.basename(after_path)}"
    result_path = os.path.join(cfg["UPLOAD_RESULTS"], result_filename)
    cv2.imwrite(result_path, output["result_image"])

    encroachment_flag = output["change_percent"] >= cfg["CHANGE_PERCENT_ALERT"]

    return {
        "result_filename": result_filename,
        "change_percent": output["change_percent"],
        "num_regions": output["num_regions"],
        "encroachment_flag": encroachment_flag,
    }