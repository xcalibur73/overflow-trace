# OverflowTrace: Empirical Mobile Viewport Benchmarks & Case Studies

Empirical evaluation of mobile horizontal overflow, viewport spills, and responsive breakages gathered while beta testing on random sites.

---

## Methodology

Audits were conducted using OverflowTrace v1.0.0 via native Chromium Chrome DevTools Protocol (CDP). Telemetry captured:
1. Exact visual viewport width (`window.visualViewport.width`).
2. Document client width (`document.documentElement.clientWidth`) versus document scroll width (`document.documentElement.scrollWidth`).
3. Total horizontal overflow differential (`scrollWidth - clientWidth`).
4. Offending DOM node count, exact bounding client rect coordinates (`rect.left`, `rect.right`, `rect.width`), and CSS selector paths.
5. Primary CSS root cause classification and synthesized drop-in remediation recipes.

Testing environments evaluated while beta testing on random sites:
- Apple iPhone SE: 375 x 667 px @ 2.0x DPR
- Apple iPhone 14/15: 390 x 844 px @ 3.0x DPR
- Compact Mobile Device: 320 x 568 px @ 2.0x DPR

---

## Empirical Benchmark Results Matrix

| Target Property / Architecture | Emulated Device | Viewport Width | ScrollWidth | Overflow (px) | Offending Nodes | Verdict | Primary Triggered Root Cause |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---|
| `webaudits.pro` (Next.js 14 SSG) | iPhone SE (375x667) | 375 px | 375 px | 0 px | 0 | `CLEAN_PASS` | Zero layout shift, responsive clamp typography |
| `python.org` (Django Server HTML) | iPhone SE (375x667) | 375 px | 375 px | 0 px | 0 | `CLEAN_PASS` | Strict max-width container constraints |
| `news.ycombinator.com` (Hacker News) | iPhone SE (375x667) | 375 px | 375 px | 0 px | 0 | `CLEAN_PASS` | Dynamic mobile viewport wrapping |
| `svelte.dev` (SvelteKit) | iPhone SE (375x667) | 375 px | 375 px | 0 px | 2 | `CLEAN_PASS` | Decorative wing elements (`div.wing`) with negative margin (-218px) clipped by parent |
| `wikipedia.org` (MediaWiki) | iPhone SE (375x667) | 375 px | 375 px | 0 px | 2 | `CLEAN_PASS` | Sub-pixel right boundary rounding on `white-space: nowrap` inter-wiki footer links |
| Unconstrained Code Block (Synthetic) | iPhone SE (375x667) | 375 px | 580 px | +205 px | 1 | `CRITICAL_BREAKAGE` | `<pre>` code block missing `overflow-x: auto` |
| Rogue `100vw` Container (Synthetic) | iPhone SE (375x667) | 375 px | 390 px | +15 px | 1 | `CRITICAL_BREAKAGE` | Full-bleed hero container using `width: 100vw` ignoring vertical scrollbar |
| Rigid Fixed Card (Synthetic) | iPhone SE (375x667) | 375 px | 480 px | +105 px | 1 | `CRITICAL_BREAKAGE` | Card container declared with fixed `width: 480px` |

---

## Key Engineering Case Studies

### Case Study 1: The Rogue `100vw` Viewport Offset
- **Symptom**: A subtle 12px to 17px horizontal scrollbar appears exclusively on Windows and Android devices when a page has vertical scrolling content.
- **Root Cause**: In CSS, `100vw` calculates 100% of the window's viewport width including the vertical scrollbar gutter. However, `document.documentElement.clientWidth` excludes the vertical scrollbar. When a developer applies `width: 100vw` to create a full-bleed hero or banner, the container extends beyond the document bounds by the exact thickness of the scrollbar.
- **Remediation**: Replace `width: 100vw` with `width: 100%` or use `width: 100cqw` inside container queries.

### Case Study 2: The Flexbox Child `min-width: auto` Trap
- **Symptom**: An inline code block, table cell, or URL inside a flexbox row forces the entire mobile screen to scroll horizontally, even though the parent container has `max-width: 100%`.
- **Root Cause**: Flex items default to `min-width: auto` according to the CSS Flexible Box Layout specification. When child content has an intrinsic minimum content size (such as an unbroken string or code snippet), the flex child refuses to shrink below that intrinsic width.
- **Remediation**: Apply `min-width: 0;` on the immediate flex child element to allow it to shrink below its content size.

### Case Study 3: Unconstrained Preformatted Code Blocks
- **Symptom**: Technical articles and documentation pages break mobile readability with horizontal overflow on code blocks.
- **Root Cause**: Browser default user-agent stylesheets style `<pre>` tags with `white-space: pre;` and no horizontal scrolling enabled. A single line of code with 60+ characters exceeds 375px mobile viewport widths.
- **Remediation**: Apply `pre, code { overflow-x: auto; white-space: pre-wrap; word-break: break-word; }` or enclose the code block in a dedicated scrolling wrapper.

### Case Study 4: Root Container Clipping Defense
- **Symptom**: Developers frequently apply `overflow-x: hidden` to `<body>` as a quick fix, which breaks `position: sticky` across the entire document.
- **Root Cause**: `overflow-x: hidden` establishes a new scroll container on the body, disabling native viewport-relative sticky positioning.
- **Remediation**: Use modern `overflow-x: clip;` on `<html>` and `<body>`. The `clip` value restricts rendering without establishing a scroll container, preserving sticky headers and navigation bars.
