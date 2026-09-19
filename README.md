# OverflowTrace

Mobile viewport horizontal overflow and layout breakage tracer.

Part of the [WebAudits.pro](https://webaudits.pro) technical intelligence platform.

---

## What it does

OverflowTrace emulates mobile screen dimensions using headless Chromium via the Chrome DevTools Protocol (CDP) to detect and isolate horizontal layout spills. It detects:
- Elements whose bounding client rectangle exceeds the visual viewport width.
- The exact horizontal overflow spill in pixels (`scrollWidth - viewportWidth`).
- Root causes of layout breakages (such as `width: 100vw` accounting for scrollbar width, unconstrained flex children, fixed `px` widths, and table elements).
- Drop-in CSS engineering fixes tailored to each offending DOM node.

---

## Why it exists

Horizontal layout overflow is one of the most frustrating mobile user experience failures:
- It causes unintentional horizontal panning, breaks sticky navigation bars, and triggers mobile touch friction.
- Mobile crawlers evaluate responsive usability as a search experience factor.
- Standard responsive developer tools often obscure subtle 1px to 10px overflows caused by margins or viewport units (`100vw`).

OverflowTrace automates headless mobile inspection, locating the exact offending DOM node selector and generating drop-in CSS remedies.

---

## Key features

- **CDP Device Emulation:** Emulates mobile devices with accurate screen width, height, device scale factor, and touch event support.
- **Offending Node Isolation:** Evaluates in-browser geometry via `getBoundingClientRect()` to rank offending elements by spill severity.
- **Rogue Container Root Cause Diagnosis:** Identifies fixed-width containers, unconstrained `<pre>` or `<table>` tags, and improper viewport unit usage.
- **Drop-in CSS Remediation:** Generates tailored CSS recipes (such as `overflow-x: clip` and `min-width: 0`) for each identified culprit.
- **Multiple Output Formats:** High-contrast terminal reports, Markdown documents, and machine-readable JSON for automated CI/CD layout checks.

---

## Architecture

```text
[Target URL + Device Preset]
            |
            v
   [Chromium CDP Engine]
            |
            +---> Device Metrics Emulation (Width, Scale Factor, Touch)
            |
            +---> Network Idle Navigation & Layout Stabilization
            |
            v
[DOM Evaluation Script]
            |
            +---> Visual Viewport Bounds vs. ScrollWidth
            +---> Offending Node getBoundingClientRect() Scan
            +---> Root Cause Heuristics (100vw, flex, fixed px)
            |
            v
[Remediation Generator]
            |
            +---> Terminal CLI Report
            +---> Markdown Document / JSON Pipeline Output
```

OverflowTrace executes three core components:
1. `devices.py`: Manages mobile device specifications (iPhone SE, iPhone 14/15, compact 320px screen, custom dimensions).
2. `browser.py`: Coordinates headless Chromium via Pyppeteer/CDP, applying device metrics and running the inspection script after a stabilization buffer.
3. `inspector.py`: Runs a client-side JavaScript routine that queries every DOM node, compares its right edge against `window.innerWidth`, and identifies parent container constraints.

---

## Installation

### Prerequisites
- Python 3.10 or higher
- Chromium or Google Chrome installed and available in system PATH

### Install from Source
```bash
git clone https://github.com/xcalibur73/overflow-trace.git
cd overflow-trace
pip install -r requirements.txt
pip install -e .
```

---

## Usage

### Basic CLI Invocation
```bash
# Audit using default iPhone SE mobile viewport (375x667)
overflow-trace https://webaudits.pro

# Audit using iPhone 14/15 preset (390x844)
overflow-trace https://example.com --device iphone-14

# Audit using compact narrow viewport (320x568)
overflow-trace https://example.com --viewport 320x568

# Export JSON report for CI/CD layout regression tests
overflow-trace https://example.com --output json --save overflow.json

# Check installed version
overflow-trace --version
```

---

## Example output

```text
==============================================================================
  OVERFLOW-TRACE: Mobile Viewport Horizontal Overflow & Breakage Tracer
==============================================================================
  Target URL:       https://webaudits.pro
  Emulated Device:  iPhone SE (375x667 @ 2.0x)
  Viewport Width:   375 px
  Document Width:   375 px (ScrollWidth)
  Verdict:          [CLEAN PASS] 0px horizontal overflow (Mobile Responsive)
  Offending Nodes:  0 element(s) detected
  Inspection Time:  1,420 ms
------------------------------------------------------------------------------

  No elements violate mobile viewport bounds. Page layout is 100% contained.
==============================================================================
```

---

## Benchmark / methodology

### Mobile Viewport Benchmark Study
- **Dataset:** Evaluated against 10 production web applications and 5 synthetic layout breakage fixtures (fixed widths, negative margins, unconstrained tables).
- **Command Used:** `python run.py <url> --device iphone-se --output json`
- **Tool Version:** OverflowTrace v1.0.0
- **Environment:** Windows 11 / Ubuntu 22.04, Chromium 128.0, Python 3.12.
- **Calculation:**
  - Total overflow: `document.documentElement.scrollWidth - window.innerWidth`
  - Element spill: `Math.max(0, rect.right - window.innerWidth)`
- **Results:**
  - Isolated 100% of synthetic breakages down to the exact CSS selector.
  - Complete study documentation: [BENCHMARKS.md](BENCHMARKS.md).

---

## Limitations

- **Static State Evaluation:** Evaluates the page layout after navigation and rendering stabilization. Does not detect overflows that only appear during dynamic gestures (e.g. pinch-to-zoom) or after interactive element toggling.
- **Dynamic Mobile UI:** Headless Chromium emulates fixed viewport dimensions; it does not simulate dynamic address bar collapse or virtual keyboard appearances.
- **Print & Shadow DOM:** Inspects standard DOM nodes; deeply nested closed Shadow DOM trees may require custom penetration scripts.

---

## Accuracy / standards

OverflowTrace aligns its measurements with official browser layout APIs and project heuristics:

| Metric / Check | Classification | Authority / Standard |
|:---|:---|:---|
| Visual Viewport Width | Web Standard | W3C Visual Viewport API |
| Element Bounding Rectangles | Web Standard | W3C CSS Object Model (CSSOM) |
| Device Preset Metrics | Web Standard | Standardized Mobile Hardware Resolutions |
| Root Cause Diagnostic Classifier | Project-Derived Heuristic | Rule-based pattern matching (100vw, flex child) |
| Layout Containment Status | Web Standard | CSS Containment Module Level 2 |

---

## Testing

OverflowTrace includes unit tests covering device resolution, formatters, and remediation generators:

```bash
# Run unit test suite
python -m unittest discover -s tests

# Test execution output
# Ran 15 tests in 0.000s
# OK
```

Continuous integration runs automatically on every commit and pull request via GitHub Actions across Linux and Windows environments.

---

## Roadmap

- [x] Initial release with CDP device emulation and CSS remediation generator.
- [x] PEP 621 packaging, CLI `--version`, and Windows cp1252 encoding hardening.
- [ ] Automated visual highlight overlay rendering on captured screenshots.
- [ ] Multi-viewport concurrent sweep mode (320px, 375px, 390px, 412px, 768px in one run).
- [ ] WebAudits.pro continuous layout regression testing integration.

---

## License

MIT License. See [LICENSE](LICENSE) for full details.
