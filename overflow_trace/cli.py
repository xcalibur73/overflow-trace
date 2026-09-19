"""
Command-line interface for OverflowTrace.
"""

import argparse
import asyncio
import sys
from typing import List, Optional

from overflow_trace.browser import inspect_url_viewport
from overflow_trace.devices import resolve_device, DEVICE_PRESETS
from overflow_trace.inspector import OVERFLOW_EVALUATION_SCRIPT
from overflow_trace.formatters import format_cli, format_markdown, format_json


def create_parser() -> argparse.ArgumentParser:
    from overflow_trace import __version__
    parser = argparse.ArgumentParser(
        prog="overflow-trace",
        description="Headless Chromium Mobile Viewport Horizontal Overflow & Breakage Tracer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Audit using default iPhone SE mobile viewport (375x667):
  python run.py https://example.com

  # Audit using iPhone 14/15 preset (390x844):
  python run.py https://example.com --device iphone-14

  # Audit using custom narrow screen dimensions (320x568):
  python run.py https://example.com --viewport 320x568

  # Export JSON report for CI/CD integration:
  python run.py https://example.com --output json --save audit.json
        """
    )

    parser.add_argument("url", nargs="?", help="Target URL to inspect for mobile horizontal overflow")
    parser.add_argument(
        "--version",
        action="version",
        version=f"OverflowTrace v{__version__}"
    )
    parser.add_argument(
        "--device",
        choices=list(DEVICE_PRESETS.keys()),
        default="iphone-se",
        help="Target device preset to emulate (default: iphone-se [375x667])"
    )
    parser.add_argument(
        "--viewport",
        type=str,
        default=None,
        help="Custom viewport dimensions in WxH format (e.g. '360x740', overrides --device)"
    )
    parser.add_argument(
        "--output",
        choices=["cli", "markdown", "json"],
        default="cli",
        help="Output format (default: cli)"
    )
    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="Optional file path to save output to"
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=3000,
        help="Rendering wait buffer in milliseconds after navigation (default: 3000)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Maximum timeout in seconds for browser inspection (default: 30)"
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    parser = create_parser()
    parsed = parser.parse_args(args)

    if not parsed.url:
        parser.print_help()
        return 0

    # Resolve device configuration
    device_selector = parsed.viewport if parsed.viewport else parsed.device
    device_config = resolve_device(device_selector)

    # Normalize URL scheme if missing
    target_url = parsed.url
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    try:
        data = asyncio.run(
            inspect_url_viewport(
                url=target_url,
                device=device_config,
                eval_script=OVERFLOW_EVALUATION_SCRIPT,
                wait_ms=parsed.wait_ms,
                timeout_sec=parsed.timeout
            )
        )
    except Exception as e:
        print(f"Error during viewport inspection: {e}", file=sys.stderr)
        return 1

    # Format output
    if parsed.output == "json":
        output_str = format_json(data)
    elif parsed.output == "markdown":
        output_str = format_markdown(data)
    else:
        output_str = format_cli(data)

    print(output_str)

    # Save to file if requested
    if parsed.save:
        try:
            with open(parsed.save, "w", encoding="utf-8") as f:
                f.write(output_str)
            print(f"\n[Saved report to {parsed.save}]")
        except Exception as e:
            print(f"Error saving to {parsed.save}: {e}", file=sys.stderr)

    # Exit code: 1 if horizontal overflow detected, 0 if clean
    return 1 if data.get("has_horizontal_overflow") else 0


if __name__ == "__main__":
    sys.exit(main())
