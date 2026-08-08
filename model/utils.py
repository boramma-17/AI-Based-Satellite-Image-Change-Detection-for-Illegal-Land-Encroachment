"""Image loading/preprocessing helpers shared by train.py and predict.py."""
import numpy as np
import cv2


def load_image(path: str, target_size=(256, 256)):
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Could not read image at {path}")
    img = cv2.resize(img, target_size)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img.astype(np.float32) / 255.0


def make_pair_input(before_path: str, after_path: str, target_size=(256, 256)):
    """Stack before/after images along the channel axis -> (H, W, 6) input for a CNN."""
    before = load_image(before_path, target_size)
    after = load_image(after_path, target_size)
    return np.concatenate([before, after], axis=-1)