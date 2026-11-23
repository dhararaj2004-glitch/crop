"""OpenCV-based leaf severity grader.

Idea: estimate what fraction of the leaf area is NOT healthy green.
    severity % = diseased_pixels / leaf_pixels * 100

It is a classical (non-learned) heuristic based on HSV colour thresholds, so it
works best on a single leaf photographed against a plain background (like
PlantVillage). Tune the HSV ranges below for your own photos.
"""
from dataclasses import dataclass

import cv2
import numpy as np

# OpenCV HSV ranges: H 0-179, S 0-255, V 0-255
HEALTHY_H = (35, 90)      # green
LEAF_MIN_SAT = 35         # below this = grey/white/black background
DARK_V = 70               # very dark pixels inside leaf = necrotic spots

GRADES = [
    (0.0, 2.0, "Healthy / negligible"),
    (2.0, 10.0, "Mild"),
    (10.0, 30.0, "Moderate"),
    (30.0, 101.0, "Severe"),
]


@dataclass
class SeverityResult:
    percent: float
    grade: str
    leaf_mask: np.ndarray       # uint8 0/255
    disease_mask: np.ndarray    # uint8 0/255
    overlay: np.ndarray         # RGB image with diseased area highlighted


def grade_from_percent(p: float) -> str:
    for lo, hi, name in GRADES:
        if lo <= p < hi:
            return name
    return GRADES[-1][2]


def _largest_filled_contour(mask: np.ndarray) -> np.ndarray:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = np.zeros_like(mask)
    if not contours:
        return out
    biggest = max(contours, key=cv2.contourArea)
    cv2.drawContours(out, [biggest], -1, 255, thickness=cv2.FILLED)
    return out


def estimate_severity(rgb: np.ndarray) -> SeverityResult:
    """rgb: HxWx3 uint8 RGB image."""
    img = cv2.resize(rgb, (256, 256), interpolation=cv2.INTER_AREA)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    # 1) Leaf mask: coloured (non-grey) pixels, keep the biggest blob and fill holes
    coloured = ((s >= LEAF_MIN_SAT) & (v > 25)).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    coloured = cv2.morphologyEx(coloured, cv2.MORPH_CLOSE, kernel, iterations=2)
    leaf = _largest_filled_contour(coloured)

    # 2) Healthy green pixels
    healthy = (h >= HEALTHY_H[0]) & (h <= HEALTHY_H[1]) & (s >= LEAF_MIN_SAT) & (v > DARK_V)

    # 3) Diseased = inside leaf and not healthy green
    inside = leaf > 0
    diseased = inside & ~healthy
    disease_mask = diseased.astype(np.uint8) * 255
    disease_mask = cv2.morphologyEx(
        disease_mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    )

    leaf_px = int(inside.sum())
    percent = 0.0 if leaf_px < 500 else float((disease_mask > 0).sum()) / leaf_px * 100.0
    percent = round(min(percent, 100.0), 2)

    overlay = img.copy()
    sel = disease_mask > 0
    overlay[sel] = (0.4 * overlay[sel] + 0.6 * np.array([255, 0, 0])).astype(np.uint8)
    contours, _ = cv2.findContours(leaf, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay, contours, -1, (255, 255, 0), 1)

    return SeverityResult(percent, grade_from_percent(percent), leaf, disease_mask, overlay)
