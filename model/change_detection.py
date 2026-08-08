"""
Core change-detection algorithm.

This module implements a classical computer-vision change detector
(image alignment -> grayscale diff -> thresholding -> contour extraction)
that works out of the box with no training data. `model/predict.py`
will prefer a trained CNN (model.h5) when one is present, and fall
back to this module otherwise -- so the app is functional immediately
and can be upgraded later by running model/train.py on your own
labeled before/after dataset.
"""
import cv2
import numpy as np


def _align_images(img1: np.ndarray, img2: np.ndarray):
    """Resize the second image to match the first (simple alignment)."""
    h, w = img1.shape[:2]
    img2_resized = cv2.resize(img2, (w, h), interpolation=cv2.INTER_AREA)
    return img1, img2_resized


def detect_changes(before_path: str, after_path: str, diff_threshold: int = 30,
                    min_area: int = 500):
    """
    Compare two images and return:
      - result_image: BGR image (the 'after' image with changed regions outlined)
      - change_percent: float, % of pixels flagged as changed
      - num_regions: number of distinct changed regions detected
      - mask: binary mask (numpy array) of the changed pixels
    """
    before = cv2.imread(before_path)
    after = cv2.imread(after_path)

    if before is None or after is None:
        raise ValueError("Could not read one or both images. Please check the file format.")

    before, after = _align_images(before, after)

    before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    # Smooth slightly to reduce sensor-noise false positives
    before_blur = cv2.GaussianBlur(before_gray, (5, 5), 0)
    after_blur = cv2.GaussianBlur(after_gray, (5, 5), 0)

    diff = cv2.absdiff(before_blur, after_blur)
    _, mask = cv2.threshold(diff, diff_threshold, 255, cv2.THRESH_BINARY)

    # Clean up small noise / fill small holes
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    significant = [c for c in contours if cv2.contourArea(c) >= min_area]

    result = after.copy()
    for c in significant:
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(result, "Change", (x, max(0, y - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

    total_pixels = mask.shape[0] * mask.shape[1]
    changed_pixels = int(np.count_nonzero(mask))
    change_percent = round((changed_pixels / total_pixels) * 100, 2)

    return {
        "result_image": result,
        "mask": mask,
        "change_percent": change_percent,
        "num_regions": len(significant),
    }