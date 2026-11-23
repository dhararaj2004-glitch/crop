import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.severity import estimate_severity, grade_from_percent  # noqa: E402
import cv2  # noqa: E402


def leaf(spots):
    rng = np.random.default_rng(spots)
    img = np.full((256, 256, 3), 200, np.uint8)
    cv2.ellipse(img, (128, 128), (95, 65), 30, 0, 360, (40, 150, 50), -1)
    for _ in range(spots):
        cv2.circle(img, (int(rng.integers(70, 190)), int(rng.integers(90, 170))),
                   int(rng.integers(5, 14)), (120, 70, 20), -1)
    return img


def test_healthy_is_low():
    assert estimate_severity(leaf(0)).percent < 5


def test_more_spots_more_severity():
    assert estimate_severity(leaf(40)).percent > estimate_severity(leaf(6)).percent


def test_grades():
    assert grade_from_percent(0) == "Healthy / negligible"
    assert grade_from_percent(15) == "Moderate"
    assert grade_from_percent(60) == "Severe"
