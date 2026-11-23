"""Creates synthetic leaf images in sample_images/ so you can test the severity grader
before you have any real photos.   Run: python make_sample_images.py
"""
import os

import cv2
import numpy as np

os.makedirs("sample_images", exist_ok=True)


def make_leaf(spots: int, seed: int):
    rng = np.random.default_rng(seed)
    img = np.full((256, 256, 3), 200, np.uint8)               # grey background
    cv2.ellipse(img, (128, 128), (95, 65), 30, 0, 360, (40, 150, 50), -1)  # green leaf (RGB)
    for _ in range(spots):
        x = int(rng.integers(70, 190)); y = int(rng.integers(90, 170))
        cv2.circle(img, (x, y), int(rng.integers(5, 14)), (120, 70, 20), -1)  # brown spot
    return img


for name, n in [("leaf_healthy", 0), ("leaf_mild", 6), ("leaf_severe", 160)]:
    rgb = make_leaf(n, seed=n)
    cv2.imwrite(f"sample_images/{name}.jpg", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
print("Wrote sample_images/")
