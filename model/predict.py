"""
Prediction entry point used by the app.

If a trained model.h5 exists (produced by train.py), it is used for
segmentation. Otherwise this transparently falls back to the classical
computer-vision detector in change_detection.py, so the app always works.
"""
import os
import cv2
import numpy as np

from model.change_detection import detect_changes as _classical_detect

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.h5")
IMG_SIZE = (256, 256)

_model_cache = {"model": None, "loaded": False}


def _try_load_model():
    if _model_cache["loaded"]:
        return _model_cache["model"]
    _model_cache["loaded"] = True
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        import tensorflow as tf
        _model_cache["model"] = tf.keras.models.load_model(MODEL_PATH)
    except Exception as e:  # noqa: BLE001 - fall back gracefully on any load error
        print(f"[predict] Could not load trained model, using classical detector: {e}")
        _model_cache["model"] = None
    return _model_cache["model"]


def _predict_with_model(model, before_path, after_path, min_area):
    from model.utils import make_pair_input

    x = make_pair_input(before_path, after_path, IMG_SIZE)
    x = np.expand_dims(x, axis=0)
    pred = model.predict(x, verbose=0)[0, ..., 0]
    mask = (pred > 0.5).astype(np.uint8) * 255

    after = cv2.imread(after_path)
    h, w = after.shape[:2]
    mask_resized = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)

    contours, _ = cv2.findContours(mask_resized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    significant = [c for c in contours if cv2.contourArea(c) >= min_area]

    result = after.copy()
    for c in significant:
        x0, y0, cw, ch = cv2.boundingRect(c)
        cv2.rectangle(result, (x0, y0), (x0 + cw, y0 + ch), (0, 0, 255), 2)
        cv2.putText(result, "Change", (x0, max(0, y0 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

    total_pixels = mask_resized.shape[0] * mask_resized.shape[1]
    changed_pixels = int(np.count_nonzero(mask_resized))
    change_percent = round((changed_pixels / total_pixels) * 100, 2)

    return {
        "result_image": result,
        "mask": mask_resized,
        "change_percent": change_percent,
        "num_regions": len(significant),
    }


def predict(before_path: str, after_path: str, diff_threshold: int = 30, min_area: int = 500):
    """Run change detection, preferring a trained model if present."""
    model = _try_load_model()
    if model is not None:
        try:
            return _predict_with_model(model, before_path, after_path, min_area)
        except Exception as e:  # noqa: BLE001
            print(f"[predict] Model inference failed, falling back to classical detector: {e}")
    return _classical_detect(before_path, after_path, diff_threshold, min_area)