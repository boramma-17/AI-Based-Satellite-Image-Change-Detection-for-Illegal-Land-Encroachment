import cv2
import numpy as np


def detect_encroachment(
    before_path,
    after_path,
    result_path
):
    """
    Compare two satellite images.

    Returns:
        dict containing:
        - change_percent
        - encroachment_flag
        - land_type
    """

    before = cv2.imread(
        before_path
    )

    after = cv2.imread(
        after_path
    )

    if before is None:

        raise ValueError(
            "Unable to load the before image."
        )

    if after is None:

        raise ValueError(
            "Unable to load the after image."
        )

    # Resize after image
    after = cv2.resize(
        after,
        (
            before.shape[1],
            before.shape[0]
        )
    )

    gray_before = cv2.cvtColor(
        before,
        cv2.COLOR_BGR2GRAY
    )

    gray_after = cv2.cvtColor(
        after,
        cv2.COLOR_BGR2GRAY
    )

    # Calculate difference
    difference = cv2.absdiff(
        gray_before,
        gray_after
    )

    # Threshold
    _, threshold = cv2.threshold(
        difference,
        30,
        255,
        cv2.THRESH_BINARY
    )

    # Remove small noise
    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    threshold = cv2.morphologyEx(
        threshold,
        cv2.MORPH_OPEN,
        kernel
    )

    threshold = cv2.morphologyEx(
        threshold,
        cv2.MORPH_CLOSE,
        kernel
    )

    # Calculate changed area
    changed_pixels = np.count_nonzero(
        threshold
    )

    total_pixels = threshold.shape[0] * threshold.shape[1]

    change_percent = (
        changed_pixels /
        total_pixels
    ) * 100

    # Find changed areas
    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    result_image = after.copy()

    significant_change = False

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area < 100:
            continue

        significant_change = True

        x, y, w, h = cv2.boundingRect(
            contour
        )

        cv2.rectangle(
            result_image,
            (x, y),
            (x + w, y + h),
            (0, 0, 255),
            3
        )

    cv2.imwrite(
        result_path,
        result_image
    )

    # Land classification is a placeholder
    # until the trained classification model
    # is connected.
    land_type = "Unknown"

    return {
        "change_percent": round(
            float(change_percent),
            2
        ),
        "encroachment_flag": significant_change,
        "land_type": land_type
    }