"""
Report formatting utilities for CLI terminals, Markdown documents, and JSON pipelines.
"""

import json
from typing import Dict, Any


def format_cli(data: Dict[str, Any]) -> str:
    """Format audit results as a high-contrast terminal report."""
    lines = []
    lines.append("=" * 78)
    lines.append("  OVERFLOW-TRACE: Mobile Viewport Horizontal Overflow & Breakage Tracer")
    lines.append("=" * 78)
    lines.append(f"  Target URL:       {data.get('target_url')}")
    lines.append(f"  Emulated Device:  {data.get('device_name')} ({data.get('device_width')}x{data.get('device_height')} @ {data.get('device_scale_factor')}x)")
    lines.append(f"  Viewport Width:   {data.get('visual_viewport_width')} px")
    lines.append(f"  Document Width:   {data.get('scroll_width')} px (ScrollWidth)")

    overflow_px = data.get("total_overflow_px", 0)
    has_overflow = data.get("has_horizontal_overflow", False)

    if has_overflow and overflow_px > 0:
        lines.append(f"  Verdict:          [CRITICAL BREAKAGE] +{overflow_px}px horizontal scroll overflow")
    else:
        lines.append(f"  Verdict:          [CLEAN PASS] 0px horizontal overflow (Mobile Responsive)")

    lines.append(f"  Offending Nodes:  {data.get('culprits_count', 0)} element(s) detected")
    lines.append(f"  Inspection Time:  {data.get('load_time_ms', 0)} ms")
    lines.append("-" * 78)

    culprits = data.get("culprits", [])
    if not culprits:
        lines.append("\n  No elements violate mobile viewport bounds. Page layout is 100% contained.\n")
        lines.append("=" * 78)
        return "\n".join(lines)

    lines.append("\n  DETECTED VIEWPORT OVERFLOW CULPRITS (Sorted by Severity):")
    lines.append("  " + "-" * 74)

    for idx, c in enumerate(culprits, 1):
        lines.append(f"  #{idx}  Selector:    {c.get('selector')}")
        lines.append(f"      Dimensions:  {c.get('rect', {}).get('width')}px wide (spills +{c.get('overflow_px')}px {c.get('spill_direction')})")
        lines.append(f"      Rect Bounds: left={c.get('rect', {}).get('left')}px, right={c.get('rect', {}).get('right')}px, top={c.get('rect', {}).get('top')}px")

        causes = c.get("root_causes", [])
        if causes:
            lines.append(f"      Root Cause:  {causes[0]}")

        lines.append(f"      Drop-in Fix: {c.get('suggested_fix')}")

        snippet = c.get("snippet", "")
        if snippet:
            lines.append(f"      HTML Snippet: {snippet[:90]}...")
        lines.append("  " + "-" * 74)

    lines.append("\n  STEP-BY-STEP ENGINEERING REMEDIATION:")
    lines.append("  1. Apply 'overflow-x: clip' on the root container instead of 'overflow-x: hidden'")
    lines.append("     to prevent accidental scroll container creation while preserving sticky positioning.")
    lines.append("  2. Replace 'width: 100vw' with 'width: 100%' across all full-bleed sections.")
    lines.append("  3. Set 'min-width: 0' on flex children containing text or code to allow them to shrink.")
    lines.append("  4. Wrap code snippets and data tables in containers with 'overflow-x: auto'.\n")
    lines.append("=" * 78)

    return "\n".join(lines)


def format_markdown(data: Dict[str, Any]) -> str:
    """Format audit results as a clean Markdown report."""
    lines = []
    lines.append(f"# OverflowTrace Audit: {data.get('target_url')}")
    lines.append("")
    lines.append(f"- **Emulated Device**: {data.get('device_name')} ({data.get('device_width')}x{data.get('device_height')} @ {data.get('device_scale_factor')}x)")
    lines.append(f"- **Viewport Width**: {data.get('visual_viewport_width')} px")
    lines.append(f"- **Document ScrollWidth**: {data.get('scroll_width')} px")

    overflow_px = data.get("total_overflow_px", 0)
    has_overflow = data.get("has_horizontal_overflow", False)

    if has_overflow and overflow_px > 0:
        lines.append(f"- **Audit Verdict**: `CRITICAL_BREAKAGE` (+{overflow_px}px horizontal overflow)")
    else:
        lines.append(f"- **Audit Verdict**: `CLEAN_PASS` (0px horizontal overflow)")

    lines.append(f"- **Culprits Detected**: {data.get('culprits_count', 0)}")
    lines.append(f"- **Inspection Duration**: {data.get('load_time_ms', 0)} ms")
    lines.append("")

    culprits = data.get("culprits", [])
    if not culprits:
        lines.append("## Layout Parity")
        lines.append("No elements violate mobile viewport bounds. Page layout is 100% contained with zero horizontal scrolling.")
        return "\n".join(lines)

    lines.append("## Viewport Overflow Culprits")
    lines.append("")
    lines.append("| # | CSS Selector | Element Width | Spill (px) | Primary Root Cause | Drop-in CSS Remediation |")
    lines.append("|---|---|:---:|:---:|---|---|")

    for idx, c in enumerate(culprits, 1):
        causes = c.get("root_causes", ["Unbounded container width"])
        sel = c.get("selector", "unknown").replace("|", "\\|")
        width = c.get("rect", {}).get("width", 0)
        spill = c.get("overflow_px", 0)
        cause = causes[0].replace("|", "\\|")
        fix = c.get("suggested_fix", "").replace("|", "\\|")
        lines.append(f"| {idx} | `{sel}` | {width}px | +{spill}px | {cause} | `{fix}` |")

    lines.append("")
    lines.append("## Recommended Remediation Steps")
    lines.append("")
    lines.append("1. **Root Clipping**: Add `overflow-x: clip;` to `<html>` and `<body>` to prevent horizontal layout escape.")
    lines.append("2. **Viewport Units**: Replace all instances of `width: 100vw;` with `width: 100%;` to prevent scrollbar width offset bugs.")
    lines.append("3. **Flexbox Containment**: Apply `min-width: 0;` on flex children to permit natural shrinkage inside constrained rows.")
    lines.append("4. **Preformatted Blocks**: Apply `overflow-x: auto; white-space: pre-wrap;` to all `<pre>` and `<code>` blocks.")
    lines.append("")

    return "\n".join(lines)


def format_json(data: Dict[str, Any]) -> str:
    """Format audit results as formatted JSON."""
    return json.dumps(data, indent=2)
