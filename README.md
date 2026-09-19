# OverflowTrace

Mobile Viewport Horizontal Overflow & Responsive Breakage Tracer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Status: Production](https://img.shields.io/badge/status-production-success.svg)](#)
[![Cloud Engine: WebAudits.pro](https://img.shields.io/badge/cloud-webaudits.pro-orange.svg)](https://webaudits.pro)

OverflowTrace is a command-line utility and headless Chromium diagnostic engine that pinpoints the exact DOM elements causing horizontal scroll breakages on mobile screens (320px to 390px).

Key capabilities:
- Native mobile viewport emulation across iPhone SE, iPhone 14/15, Pixel 7, Galaxy S20, and custom dimensions.
- Bounding client rect inspection measuring sub-pixel edge spills (`rect.right > window.visualViewport.width`).
- Root cause CSS classification isolating rogue `100vw` container offsets, flex items missing `min-width: 0`, unconstrained `<pre>`/`<table>` blocks, and fixed pixel widths.
- Actionable drop-in CSS remediation recipes formatted for instant developer resolution.
- Multi-format output supporting high-contrast terminal tables, Markdown audit reports, and JSON pipelines.

---

## The Engineering Problem

Horizontal scroll breakages are among the most common mobile layout defects:
1. Viewport width confusion: using `width: 100vw` causes elements to expand beyond the document width by the width of the vertical scrollbar.
2. Flexbox child overflow: flex children default to `min-width: auto`, preventing long strings or preformatted code from shrinking inside constrained rows.
3. Rigid container widths: fixed pixel widths (e.g. `width: 480px`) or unconstrained data tables force the mobile document width to expand, breaking touch navigation.
4. Invisible culprits: inspecting overflow manually in mobile browser DevTools requires repeatedly deleting parent elements in the DOM tree to locate the specific child causing the layout spill.

OverflowTrace automates this forensic investigation in under 4 seconds.

---

## Architecture Overview

```
                         [ Target URL / Route ]
                                   │
                                   ▼
                   [ Headless Chromium CDP Controller ]
                    - Chrome / Edge binary auto-discovery
                    - Emulation.setUserAgentOverride
                    - Emulation.setDeviceMetricsOverride
                    - Emulation.setTouchEmulationEnabled
                                   │
                                   ▼
                     [ In-Page DOM Inspector AST ]
                    - Visual viewport & scrollWidth telemetry
                    - Bounding client rect evaluation
                    - Left/right spill differential calculation
                                   │
                                   ▼
                    [ CSS Root Cause Classifier ]
                    - 100vw viewport scrollbar offset check
                    - Flexbox min-width constraint detection
                    - Preformatted code & table container check
                    - Media element max-width audit
                                   │
                                   ▼
                  [ Report & Remediation Synthesizer ]
                    - High-contrast CLI terminal table
                    - Markdown audit teardown export
                    - Machine-readable JSON for CI/CD
```

---

## Installation

```bash
git clone https://github.com/xcalibur73/overflow-trace.git
cd overflow-trace
pip install -r requirements.txt
```

OverflowTrace uses native headless Chrome or Edge already installed on your operating system (Windows, macOS, or Linux). No heavy browser binaries or third-party automation drivers required.

---

## Quick Start

### Basic Mobile Audit (iPhone SE 375px)
```bash
python run.py https://example.com
```

### Audit Larger Mobile Screen (iPhone 14/15 390px)
```bash
python run.py https://example.com --device iphone-14
```

### Audit Compact Mobile Screen (Legacy 320px)
```bash
python run.py https://example.com --device small
```

### Audit Custom Dimensions (e.g. 360x740)
```bash
python run.py https://example.com --viewport 360x740
```

### Export Markdown Audit Report
```bash
python run.py https://example.com --output markdown --save audit_report.md
```

### Export JSON for CI/CD Deployment Gates
```bash
python run.py https://example.com --output json --save audit.json
```

---

## Sample Diagnostic Output

```
==============================================================================
  OVERFLOW-TRACE: Mobile Viewport Horizontal Overflow & Breakage Tracer
==============================================================================
  Target URL:       https://news.ycombinator.com
  Emulated Device:  Apple iPhone SE (2nd/3rd Gen) (375x667 @ 2.0x)
  Viewport Width:   375 px
  Document Width:   515 px (ScrollWidth)
  Verdict:          [CRITICAL BREAKAGE] +140px horizontal scroll overflow
  Offending Nodes:  14 element(s) detected
  Inspection Time:  3120.45 ms
------------------------------------------------------------------------------

  DETECTED VIEWPORT OVERFLOW CULPRITS (Sorted by Severity):
  --------------------------------------------------------------------------
  #1  Selector:    table#hnmain
      Dimensions:  500px wide (spills +140px RIGHT)
      Rect Bounds: left=8px, right=515px, top=10px
      Root Cause:  Table markup exceeding mobile column width
      Drop-in Fix: display: block; overflow-x: auto; max-width: 100%;
      HTML Snippet: <table id="hnmain" border="0" cellpadding="0" cellspacing="0" width="85%" bgcolor="#f6f6ef">...
  --------------------------------------------------------------------------

  STEP-BY-STEP ENGINEERING REMEDIATION:
  1. Apply 'overflow-x: clip' on the root container instead of 'overflow-x: hidden'
     to prevent accidental scroll container creation while preserving sticky positioning.
  2. Replace 'width: 100vw' with 'width: 100%' across all full-bleed sections.
  3. Set 'min-width: 0' on flex children containing text or code to allow them to shrink.
  4. Wrap code snippets and data tables in containers with 'overflow-x: auto'.
==============================================================================
```

---

## Empirical Benchmarks & Case Studies

OverflowTrace has been evaluated while beta testing on random sites across media publications, developer frameworks, legacy forums, and modern static architectures. Detailed findings and telemetry: [BENCHMARKS.md](BENCHMARKS.md).

Key empirical findings:
- Modern static layouts (`webaudits.pro`, `wikipedia.org`, `python.org`) maintain 0px horizontal overflow across all mobile viewports down to 320px.
- Legacy table-based layouts expand horizontal scroll width by +140px to +195px on iPhone SE and compact mobile screens.
- Preformatted code elements without `overflow-x: auto` are the primary culprit behind mobile layout breakages in technical blogs and documentation hubs.

---

## Test Suite

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Result:
```
...........
----------------------------------------------------------------------
Ran 11 tests in 0.000s

OK
```

---

## Author & Attribution

Maintained by [@xcalibur73](https://github.com/xcalibur73), creator of [WebAudits.pro](https://webaudits.pro).

Part of a technical web performance and crawl architecture engineering suite:
1. [dom-hydrate](https://github.com/xcalibur73/dom-hydrate): Headless Chromium SSR vs CSR DOM diff engine.
2. [citation-pulse](https://github.com/xcalibur73/citation-pulse): GEO and AI search citability benchmark engine.
3. [index-trace](https://github.com/xcalibur73/index-trace): Search Console emergency triage and crawler collision tracer.
4. [overflow-trace](https://github.com/xcalibur73/overflow-trace): Mobile viewport horizontal overflow and layout breakage tracer.

Licensed under the [MIT License](LICENSE).
