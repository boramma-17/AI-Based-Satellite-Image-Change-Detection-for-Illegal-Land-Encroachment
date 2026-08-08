import os
import numpy as np
import cv2
import pytest

from model.change_detection import detect_changes


@pytest.fixture
def image_pair(tmp_path):
    """Create a 'before' image and an 'after' image with an obvious added
    rectangle (simulated new construction) to exercise the detector."""
    before = np.full((200, 200, 3), 60, dtype=np.uint8)
    after = before.copy()
    cv2.rectangle(after, (50, 50), (120, 120), (220, 220, 220), -1)

    before_path = tmp_path / "before.png"
    after_path = tmp_path / "after.png"
    cv2.imwrite(str(before_path), before)
    cv2.imwrite(str(after_path), after)
    return str(before_path), str(after_path)


def test_detect_changes_finds_region(image_pair):
    before_path, after_path = image_pair
    result = detect_changes(before_path, after_path, diff_threshold=30, min_area=100)

    assert result["num_regions"] >= 1
    assert result["change_percent"] > 0
    assert result["result_image"] is not None
    assert result["mask"].shape[:2] == (200, 200)


def test_detect_changes_no_change(tmp_path):
    img = np.full((100, 100, 3), 128, dtype=np.uint8)
    before_path = tmp_path / "b.png"
    after_path = tmp_path / "a.png"
    cv2.imwrite(str(before_path), img)
    cv2.imwrite(str(after_path), img)

    result = detect_changes(str(before_path), str(after_path))
    assert result["change_percent"] < 1.0
    assert result["num_regions"] == 0


def test_detect_changes_raises_on_missing_file(tmp_path):
    with pytest.raises(ValueError):
        detect_changes(str(tmp_path / "missing1.png"), str(tmp_path / "missing2.png"))