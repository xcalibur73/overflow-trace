"""
Mobile device emulation profiles and viewport definitions.
"""

from typing import Dict, Any, Optional

DEFAULT_USER_AGENT_IOS = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
)

DEFAULT_USER_AGENT_ANDROID = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
)

DEFAULT_USER_AGENT_DESKTOP = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

DEVICE_PRESETS: Dict[str, Dict[str, Any]] = {
    "iphone-se": {
        "name": "Apple iPhone SE (2nd/3rd Gen)",
        "width": 375,
        "height": 667,
        "device_scale_factor": 2.0,
        "mobile": True,
        "has_touch": True,
        "user_agent": DEFAULT_USER_AGENT_IOS,
    },
    "iphone-14": {
        "name": "Apple iPhone 14 / 15",
        "width": 390,
        "height": 844,
        "device_scale_factor": 3.0,
        "mobile": True,
        "has_touch": True,
        "user_agent": DEFAULT_USER_AGENT_IOS,
    },
    "pixel-7": {
        "name": "Google Pixel 7",
        "width": 412,
        "height": 915,
        "device_scale_factor": 2.625,
        "mobile": True,
        "has_touch": True,
        "user_agent": DEFAULT_USER_AGENT_ANDROID,
    },
    "galaxy-s20": {
        "name": "Samsung Galaxy S20",
        "width": 360,
        "height": 800,
        "device_scale_factor": 3.0,
        "mobile": True,
        "has_touch": True,
        "user_agent": DEFAULT_USER_AGENT_ANDROID,
    },
    "small": {
        "name": "Compact Mobile Device (Legacy / Budget)",
        "width": 320,
        "height": 568,
        "device_scale_factor": 2.0,
        "mobile": True,
        "has_touch": True,
        "user_agent": DEFAULT_USER_AGENT_IOS,
    },
    "desktop": {
        "name": "Standard Desktop Display",
        "width": 1280,
        "height": 800,
        "device_scale_factor": 1.0,
        "mobile": False,
        "has_touch": False,
        "user_agent": DEFAULT_USER_AGENT_DESKTOP,
    },
}


def resolve_device(preset_or_dimensions: Optional[str] = None) -> Dict[str, Any]:
    """
    Resolve device preset by name or custom WxH dimensions (e.g. '375x667').
    Defaults to 'iphone-se'.
    """
    if not preset_or_dimensions:
        return DEVICE_PRESETS["iphone-se"]

    key = preset_or_dimensions.strip().lower()

    if key in DEVICE_PRESETS:
        return DEVICE_PRESETS[key]

    # Check custom dimensions e.g. 375x667
    if "x" in key:
        parts = key.split("x")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            w = int(parts[0])
            h = int(parts[1])
            is_mobile = w < 768
            return {
                "name": f"Custom Viewport ({w}x{h})",
                "width": w,
                "height": h,
                "device_scale_factor": 2.0 if is_mobile else 1.0,
                "mobile": is_mobile,
                "has_touch": is_mobile,
                "user_agent": DEFAULT_USER_AGENT_IOS if is_mobile else DEFAULT_USER_AGENT_DESKTOP,
            }

    # Fallback to iphone-se if unrecognized
    return DEVICE_PRESETS["iphone-se"]
