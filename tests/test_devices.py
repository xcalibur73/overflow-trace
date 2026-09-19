"""
Unit tests for device presets and viewport resolution.
"""

import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from overflow_trace.devices import resolve_device, DEVICE_PRESETS


class TestDevices(unittest.TestCase):

    def test_default_device(self):
        dev = resolve_device()
        self.assertEqual(dev["width"], 375)
        self.assertEqual(dev["height"], 667)
        self.assertTrue(dev["mobile"])
        self.assertTrue(dev["has_touch"])

    def test_all_presets_exist(self):
        for preset in ["iphone-se", "iphone-14", "pixel-7", "galaxy-s20", "small", "desktop"]:
            dev = resolve_device(preset)
            self.assertIn("width", dev)
            self.assertIn("height", dev)
            self.assertIn("user_agent", dev)
            self.assertGreater(dev["width"], 0)
            self.assertGreater(dev["height"], 0)

    def test_custom_viewport_parsing(self):
        dev = resolve_device("360x740")
        self.assertEqual(dev["width"], 360)
        self.assertEqual(dev["height"], 740)
        self.assertTrue(dev["mobile"])

    def test_desktop_preset(self):
        dev = resolve_device("desktop")
        self.assertEqual(dev["width"], 1280)
        self.assertEqual(dev["height"], 800)
        self.assertFalse(dev["mobile"])
        self.assertFalse(dev["has_touch"])


if __name__ == "__main__":
    unittest.main()
