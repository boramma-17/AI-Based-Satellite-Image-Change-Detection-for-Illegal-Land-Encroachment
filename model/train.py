"""
Training script for a real CNN-based change-detection model.

This is a skeleton: it expects paired images in dataset/before/<name>.jpg
and dataset/after/<name>.jpg with matching filenames, and a binary
change-mask in dataset/masks/<name>.png (0 = no change, 255 = change).
If you don't have masks yet, generate weak labels first using
model/change_detection.py's classical detector, then refine by hand.

Run:
    python model/train.py --epochs 20 --batch-size 8

Produces model/model.h5, which predict.py will automatically pick up.
"""
import os
import argparse
import numpy as np

try:
    import tensorflow as tf
    from tensorflow.keras import layers, models
except ImportError:
    tf = None


DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "dataset")
MODEL_OUT = os.path.join(os.path.dirname(__file__), "model.h5")
IMG_SIZE = (256, 256)


def build_model():
    """A small U-Net-style siamese-diff segmentation model.
    Input: 6-channel (before RGB + after RGB) stacked image.
    Output: 1-channel change probability mask."""
    inputs = layers.Input(shape=(*IMG_SIZE, 6))

    c1 = layers.Conv2D(32, 3, activation="relu", padding="same")(inputs)
    p1 = layers.MaxPooling2D()(c1)

    c2 = layers.Conv2D(64, 3, activation="relu", padding="same")(p1)
    p2 = layers.MaxPooling2D()(c2)

    c3 = layers.Conv2D(128, 3, activation="relu", padding="same")(p2)

    u1 = layers.UpSampling2D()(c3)
    u1 = layers.Concatenate()([u1, c2])
    c4 = layers.Conv2D(64, 3, activation="relu", padding="same")(u1)

    u2 = layers.UpSampling2D()(c4)
    u2 = layers.Concatenate()([u2, c1])
    c5 = layers.Conv2D(32, 3, activation="relu", padding="same")(u2)

    outputs = layers.Conv2D(1, 1, activation="sigmoid")(c5)

    model = models.Model(inputs, outputs)
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def load_dataset():
    import cv2
    before_dir = os.path.join(DATASET_DIR, "before")
    after_dir = os.path.join(DATASET_DIR, "after")
    mask_dir = os.path.join(DATASET_DIR, "masks")

    X, y = [], []
    for fname in sorted(os.listdir(before_dir)):
        before_path = os.path.join(before_dir, fname)
        after_path = os.path.join(after_dir, fname)
        mask_path = os.path.join(mask_dir, fname)
        if not (os.path.exists(after_path) and os.path.exists(mask_path)):
            continue

        b = cv2.resize(cv2.cvtColor(cv2.imread(before_path), cv2.COLOR_BGR2RGB), IMG_SIZE) / 255.0
        a = cv2.resize(cv2.cvtColor(cv2.imread(after_path), cv2.COLOR_BGR2RGB), IMG_SIZE) / 255.0
        m = cv2.resize(cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE), IMG_SIZE) / 255.0

        X.append(np.concatenate([b, a], axis=-1))
        y.append(m[..., np.newaxis])

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()

    if tf is None:
        raise SystemExit("TensorFlow is not installed. Run: pip install tensorflow")

    X, y = load_dataset()
    if len(X) == 0:
        raise SystemExit(
            "No training pairs found. Populate dataset/before, dataset/after, "
            "and dataset/masks with matching filenames first."
        )

    model = build_model()
    model.fit(X, y, epochs=args.epochs, batch_size=args.batch_size, validation_split=0.15)
    model.save(MODEL_OUT)
    print(f"Model saved to {MODEL_OUT}")


if __name__ == "__main__":
    main()