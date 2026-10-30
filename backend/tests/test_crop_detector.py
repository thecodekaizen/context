import cv2
import numpy as np
import pytest
from context_core.crop_detector import detect_crop_in_frames


@pytest.fixture
def test_scene():
    """Create a synthetic high-contrast benchmark scene."""
    img = np.zeros((720, 1280, 3), dtype=np.uint8)
    # Background gradient
    for y in range(720):
        img[y, :, 0] = y % 256
    # Title bar
    img[20:80, 100:1180] = [200, 200, 200]
    # Chart bars
    for i in range(10):
        x = 150 + i * 100
        h = 100 + i * 40
        img[600 - h : 600, x : x + 60] = [30, 220, 50]
    # Peripheral benchmark footer / disclaimer
    img[660:700, 100:1180] = [80, 80, 240]
    return img


def test_no_crop_identical(test_scene):
    res = detect_crop_in_frames(test_scene, test_scene.copy())
    assert not res.detected
    assert res.area_retained_fraction == 1.0
    assert res.area_omitted_fraction == 0.0
    assert len(res.omitted_margins) == 0


def test_unscaled_crop_reframe(test_scene):
    # Crop 840x460 at x=0, y=140
    crop = test_scene[140:600, 0:840].copy()
    res = detect_crop_in_frames(test_scene, crop)
    assert res.detected
    assert res.confidence > 0.95
    assert res.crop_box is not None
    assert abs(res.crop_box.x - 0) <= 2
    assert abs(res.crop_box.y - 140) <= 2
    assert abs(res.crop_box.width - 840) <= 2
    assert abs(res.crop_box.height - 460) <= 2
    assert res.area_omitted_fraction > 0.5
    # Bottom margin should include omitted footer
    assert any(m.name == "bottom" for m in res.omitted_margins)


def test_scaled_crop_zoom(test_scene):
    # Center crop 80% and scale to 960x640
    h, w = test_scene.shape[:2]
    cw, ch = int(w * 0.8), int(h * 0.8)
    cx, cy = (w - cw) // 2, (h - ch) // 2
    crop = test_scene[cy : cy + ch, cx : cx + cw]
    scaled = cv2.resize(crop, (960, 640), interpolation=cv2.INTER_LINEAR)

    res = detect_crop_in_frames(test_scene, scaled)
    assert res.detected
    assert res.confidence > 0.85
    assert res.area_omitted_fraction > 0.25
