"""
Unit tests for CSS root cause classification and drop-in remediation.
"""

import unittest
from overflow_trace.inspector import classify_css_fix


class TestRemediation(unittest.TestCase):

    def test_100vw_classification(self):
        res = classify_css_fix("div", {"width": "100vw"})
        self.assertTrue(any("100vw" in c for c in res["causes"]))
        self.assertIn("width: 100%", res["suggested_fix"])

    def test_min_width_classification(self):
        res = classify_css_fix("div", {"min-width": "420px"})
        self.assertTrue(any("min-width constraint" in c for c in res["causes"]))
        self.assertIn("min-width: 0", res["suggested_fix"])

    def test_preformatted_block_classification(self):
        res = classify_css_fix("pre", {})
        self.assertTrue(any("preformatted code block" in c for c in res["causes"]))
        self.assertIn("overflow-x: auto", res["suggested_fix"])

    def test_table_classification(self):
        res = classify_css_fix("table", {})
        self.assertTrue(any("Table markup" in c for c in res["causes"]))
        self.assertIn("display: block", res["suggested_fix"])

    def test_media_missing_max_width(self):
        res = classify_css_fix("img", {"max-width": "none"})
        self.assertTrue(any("Media asset lacking" in c for c in res["causes"]))
        self.assertIn("max-width: 100%", res["suggested_fix"])

    def test_nowrap_classification(self):
        res = classify_css_fix("span", {"white-space": "nowrap"})
        self.assertTrue(any("nowrap" in c for c in res["causes"]))
        self.assertIn("overflow-wrap: anywhere", res["suggested_fix"])

    def test_negative_margin_classification(self):
        res = classify_css_fix("aside", {}, spill_direction="LEFT")
        self.assertTrue(any("Negative margin" in c for c in res["causes"]))
        self.assertIn("margin-left: 0", res["suggested_fix"])


if __name__ == "__main__":
    unittest.main()
