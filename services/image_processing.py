import cv2
import numpy as np


def detect_encroachment(
    before_path,
    after_path,
    result_path
):

    img1 = cv2.imread(
        before_path
    )

    img2 = cv2.imread(
        after_path
    )

    if img1 is None:

        raise ValueError(
            "Could not load the before image."
        )

    if img2 is None:

        raise ValueError(
            "Could not load the after image."
        )

    # Resize after image to match before image
    img2 = cv2.resize(
        img2,
        (
            img1.shape[1],
            img1.shape[0]
        )
    )

    gray1 = cv2.cvtColor(
        img1,
        cv2.COLOR_BGR2GRAY
    )

    gray2 = cv2.cvtColor(
        img2,
        cv2.COLOR_BGR2GRAY
    )

    diff = cv2.absdiff(
        gray1,
        gray2
    )

    _, threshold = cv2.threshold(
        diff,
        30,
        255,
        cv2.THRESH_BINARY
    )

    # Remove small noise
    kernel = np.ones(
        (3, 3),
        np.uint8
    )

    threshold = cv2.morphologyEx(
        threshold,
        cv2.MORPH_OPEN,
        kernel
    )

    threshold = cv2.dilate(
        threshold,
        kernel,
        iterations=1
    )

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    result_img = img2.copy()

    changed_pixels = cv2.countNonZero(
        threshold
    )

    total_pixels = threshold.shape[0] * threshold.shape[1]

    if total_pixels > 0:

        change_percent = (
            changed_pixels /
            total_pixels
        ) * 100

    else:

        change_percent = 0.0

    encroachment_detected = False

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area > 100:

            encroachment_detected = True

            x, y, w, h = cv2.boundingRect(
                contour
            )

            cv2.rectangle(
                result_img,
                (x, y),
                (x + w, y + h),
                (0, 0, 255),
                2
            )

    success = cv2.imwrite(
        result_path,
        result_img
    )

    if not success:

        raise ValueError(
            "Could not save result image."
        )

    return {
        "encroachment_flag": encroachment_detected,
        "change_percent": float(change_percent)
    }