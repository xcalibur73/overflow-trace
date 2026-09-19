"""
Unit tests for report formatters.
"""

import json
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from overflow_trace.formatters import format_cli, format_markdown, format_json


class TestFormatters(unittest.TestCase):

    def setUp(self):
        self.sample_clean = {
            "target_url": "https://example.com",
            "device_name": "Apple iPhone SE",
            "device_width": 375,
            "device_height": 667,
            "device_scale_factor": 2.0,
            "visual_viewport_width": 375,
            "scroll_width": 375,
            "has_horizontal_overflow": False,
            "total_overflow_px": 0,
            "culprits_count": 0,
            "culprits": [],
            "load_time_ms": 1200.5
        }

        self.sample_broken = {
            "target_url": "https://broken-site.com",
            "device_name": "Apple iPhone SE",
            "device_width": 375,
            "device_height": 667,
            "device_scale_factor": 2.0,
            "visual_viewport_width": 375,
            "scroll_width": 500,
            "has_horizontal_overflow": True,
            "total_overflow_px": 125,
            "culprits_count": 1,
            "culprits": [
                {
                    "selector": "div#banner",
                    "rect": {"width": 500, "left": 0, "right": 500, "top": 10},
                    "overflow_px": 125,
                    "spill_direction": "RIGHT",
                    "root_causes": ["100vw viewport width offset (causes scrollbar overflow)"],
                    "suggested_fix": "width: 100%; (replace 100vw to respect document scrollbar)",
                    "snippet": '<div id="banner" style="width: 100vw">...</div>'
                }
            ],
            "load_time_ms": 1450.0
        }

    def test_format_cli_clean(self):
        out = format_cli(self.sample_clean)
        self.assertIn("CLEAN PASS", out)
        self.assertIn("0px horizontal overflow", out)

    def test_format_cli_broken(self):
        out = format_cli(self.sample_broken)
        self.assertIn("CRITICAL BREAKAGE", out)
        self.assertIn("+125px horizontal scroll overflow", out)
        self.assertIn("div#banner", out)

    def test_format_markdown(self):
        md = format_markdown(self.sample_broken)
        self.assertIn("# OverflowTrace Audit", md)
        self.assertIn("`div#banner`", md)
        self.assertIn("100vw", md)

    def test_format_json(self):
        js = format_json(self.sample_broken)
        data = json.loads(js)
        self.assertEqual(data["total_overflow_px"], 125)
        self.assertTrue(data["has_horizontal_overflow"])


if __name__ == "__main__":
    unittest.main()
