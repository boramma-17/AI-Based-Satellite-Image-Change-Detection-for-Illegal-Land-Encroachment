"""
land_classifier.py

Rule-based (no training required) land-type classifier for satellite
imagery. Buckets every pixel into one of: forest, water, open_land,
built_up, or unclassified, using HSV color thresholds.

This is a placeholder for objective 1.2.2 ("identify different land
types") until a trained model is available. Swap classify_land()'s body
for a real model call later -- callers only depend on the return shape,
not on how it's computed.

Usage:
    from land_classifier import classify_land

    result = classify_land("path/to/image.jpg", save_overlay_to="path/to/overlay.png")
    # result = {
    #     "percentages": {"forest": 42.1, "water": 12.4, "open_land": 30.0, "built_up": 12.0, "unclassified": 3.5},
    #     "dominant": "forest",
    #     "overlay_path": "path/to/overlay.png",  # only if save_overlay_to was given
    # }
"""

import cv2
import numpy as np


# Legend colors used both for the overlay image and the frontend swatches.
# Keep these in sync with the CSS in land-classifier.css.
CLASS_COLORS_BGR = {
    "forest":        (46, 125, 50),    # green
    "water":         (216, 132, 30),   # blue
    "open_land":     (60, 145, 210),   # tan / sandy
    "built_up":      (110, 110, 110),  # gray
    "unclassified":  (30, 30, 30),     # near-black, low-opacity in overlay
}

CLASS_LABELS = {
    "forest": "Forest / Vegetation",
    "water": "Water Body",
    "open_land": "Open Land / Soil",
    "built_up": "Built-up / Construction",
    "unclassified": "Unclassified",
}


def _hsv_masks(hsv):
    """Return a dict of boolean masks, one per land-type class."""

    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    # Vegetation: green hues, reasonably saturated.
    forest = (h >= 35) & (h <= 85) & (s >= 40)

    # Water: blue hues, or very dark low-saturation areas (shadowed water).
    water = ((h >= 90) & (h <= 130) & (s >= 30)) | ((v <= 60) & (s <= 60))

    # Built-up / construction: low saturation, mid-to-high brightness,
    # not already claimed by water's dark-pixel rule.
    built_up = (s <= 35) & (v >= 90) & ~water

    # Open land / bare soil: warm, low-saturation-to-moderate hues
    # (tan, brown, dry ground) not already classified above.
    open_land = (h >= 5) & (h <= 34) & (s >= 20) & ~forest & ~built_up

    claimed = forest | water | built_up | open_land
    unclassified = ~claimed

    return {
        "forest": forest,
        "water": water,
        "open_land": open_land,
        "built_up": built_up,
        "unclassified": unclassified,
    }


def classify_land(image_path, save_overlay_to=None, overlay_opacity=0.55):
    """
    Classify land types in a satellite image using HSV color thresholds.

    Args:
        image_path: path to the input image (jpg/png).
        save_overlay_to: optional path to write a color-coded overlay PNG.
        overlay_opacity: 0-1, how strongly the classification tint is
            blended over the original image in the overlay.

    Returns:
        dict with "percentages" (per class, sums to ~100), "dominant"
        (the largest class), and "overlay_path" (if save_overlay_to given).
    """

    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    masks = _hsv_masks(hsv)

    total_pixels = image.shape[0] * image.shape[1]
    percentages = {
        cls: round(float(mask.sum()) / total_pixels * 100, 1)
        for cls, mask in masks.items()
    }
    dominant = max(percentages, key=percentages.get)

    result = {"percentages": percentages, "dominant": dominant}

    if save_overlay_to:
        overlay = image.copy().astype(np.float32)
        tint_layer = np.zeros_like(image, dtype=np.float32)

        for cls, mask in masks.items():
            tint_layer[mask] = CLASS_COLORS_BGR[cls]

        blended = cv2.addWeighted(
            overlay, 1 - overlay_opacity,
            tint_layer, overlay_opacity,
            0,
        )
        cv2.imwrite(save_overlay_to, blended.astype(np.uint8))
        result["overlay_path"] = save_overlay_to

    return result


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: python land_classifier.py <image_path> [overlay_output_path]")
        sys.exit(1)

    img_path = sys.argv[1]
    overlay_path = sys.argv[2] if len(sys.argv) > 2 else None

    output = classify_land(img_path, save_overlay_to=overlay_path)
    print(json.dumps(output, indent=2))