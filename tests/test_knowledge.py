import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.help_finder import get_help  # noqa: E402
from utils.knowledge import action_plan, all_entries, find_entry  # noqa: E402
from utils.report import build_html_report  # noqa: E402


def test_lookup():
    assert find_entry("Tomato", "Late blight")["id"] == "late_blight"
    assert find_entry("Soybean", "healthy")["id"] == "healthy"
    assert find_entry("Grape", "Esca (Black Measles)")["id"] == "esca"
    assert find_entry("Cassava", "Mosaic Disease")["id"] == "cassava_mosaic"
    assert find_entry("Banana", "Sigatoka")["id"] == "unknown"


def test_entries_complete():
    for e in all_entries():
        assert e["title"] and e["symptoms"] and e["cultural"], e["id"]


def test_plan_scales_with_severity():
    e = find_entry("Tomato", "Early blight")
    assert "Urgent" in action_plan(e, 50, "Severe")["headline"]
    assert "Act early" in action_plan(e, 5, "Mild")["headline"]


def test_help_india_and_other():
    h = get_help("India", "West Bengal", "Nadia", "Tomato")
    assert any(c.get("phone") == "1800-180-1551" for c in h["contacts"])
    assert all(u.startswith("https://www.google.com/maps/search/") for _, u in h["searches"])
    assert "Nadia" in h["place"]
    assert get_help("Other country", "", "")["contacts"]


def test_report_builds():
    img = np.zeros((64, 64, 3), np.uint8)
    e = find_entry("Tomato", "Late blight")
    html = build_html_report(dict(plant="Tomato", condition="Late blight", confidence_text="91%",
                                  top=[("Tomato - Late blight", 0.91)], severity=12.0, grade="Moderate",
                                  place="Nadia, West Bengal", entry=e, plan=action_plan(e, 12, "Moderate"),
                                  contacts=get_help("India")["contacts"], rgb=img, overlay=img, safety="x"))
    assert "Late blight" in html and "1800-180-1551" in html
