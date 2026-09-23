"""
DOM inspector script and CSS root cause classification engine.
"""

from typing import Dict, Any, List

OVERFLOW_EVALUATION_SCRIPT = """
(() => {
    const vw = window.visualViewport ? window.visualViewport.width : window.innerWidth;
    const vh = window.visualViewport ? window.visualViewport.height : window.innerHeight;
    const docEl = document.documentElement;
    const scrollWidth = docEl.scrollWidth;
    const clientWidth = docEl.clientWidth;
    const hasHorizontalOverflow = scrollWidth > clientWidth + 1;
    const totalOverflowPx = Math.max(0, scrollWidth - clientWidth);

    const ignoredTags = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'DEFS', 'CLIPPATH']);
    const elements = document.querySelectorAll('*');
    const culprits = [];

    for (const el of elements) {
        if (ignoredTags.has(el.tagName)) continue;

        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden') continue;
        if (parseFloat(style.opacity || '1') === 0) continue;

        const rect = el.getBoundingClientRect();
        if (rect.width === 0 && rect.height === 0) continue;

        // Check if element spills beyond right viewport edge or before left edge
        const rightSpill = rect.right - vw;
        const leftSpill = -rect.left;

        if (rightSpill > 1.0 || leftSpill > 1.0) {
            const overflowPx = Math.max(rightSpill, leftSpill);
            const tag = el.tagName.toLowerCase();

            // Build unique descriptive CSS selector
            let selector = tag;
            if (el.id) {
                selector += '#' + el.id;
            } else if (el.className && typeof el.className === 'string') {
                const classes = el.className
                    .trim()
                    .split(/\\s+/)
                    .filter(c => c && !c.includes(':') && !c.includes('/'))
                    .slice(0, 3);
                if (classes.length) selector += '.' + classes.join('.');
            }

            // Identify root cause rules
            const rootCauses = [];
            const inlineStyle = el.getAttribute('style') || '';

            if (inlineStyle.includes('100vw') || style.width.includes('vw')) {
                rootCauses.push('100vw viewport width offset (causes scrollbar overflow)');
            }
            if (style.minWidth && style.minWidth !== '0px' && style.minWidth !== 'auto') {
                rootCauses.push(`min-width constraint: ${style.minWidth}`);
            }
            if (style.whiteSpace === 'nowrap') {
                rootCauses.push('white-space: nowrap prevents text wrapping');
            }
            if (tag === 'pre' || tag === 'code') {
                rootCauses.push('Unconstrained preformatted code block');
            }
            if (tag === 'table') {
                rootCauses.push('Table markup exceeding mobile column width');
            }
            if (tag === 'img' || tag === 'svg' || tag === 'video' || tag === 'iframe') {
                if ((!style.maxWidth || style.maxWidth === 'none') && style.width !== '100%') {
                    rootCauses.push('Media asset lacking max-width: 100%');
                }
            }
            if (leftSpill > 1.0) {
                rootCauses.push(`Negative position or margin: left ${Math.round(rect.left)}px`);
            }
            if (rootCauses.length === 0) {
                rootCauses.push(`Unbounded container width: ${Math.round(rect.width)}px > ${Math.round(vw)}px`);
            }

            // Synthesize tailored drop-in CSS remediation
            let fix = 'max-width: 100%; box-sizing: border-box;';
            if (inlineStyle.includes('100vw') || style.width.includes('vw')) {
                fix = 'width: 100%; (replace 100vw to respect document scrollbar)';
            } else if (style.minWidth && style.minWidth !== '0px') {
                fix = 'min-width: 0; max-width: 100%; (allow flex child to shrink)';
            } else if (tag === 'pre' || tag === 'code') {
                fix = 'overflow-x: auto; white-space: pre-wrap; word-break: break-word;';
            } else if (tag === 'table') {
                fix = 'display: block; overflow-x: auto; max-width: 100%;';
            } else if (tag === 'img' || tag === 'video' || tag === 'iframe') {
                fix = 'max-width: 100%; height: auto;';
            } else if (style.whiteSpace === 'nowrap') {
                fix = 'white-space: normal; overflow-wrap: anywhere;';
            } else {
                fix = 'max-width: 100%; overflow-x: clip;';
            }

            // Grab snippet of outerHTML
            const snippet = el.outerHTML ? el.outerHTML.slice(0, 160).replace(/\\s+/g, ' ').trim() : '';

            culprits.push({
                tag: tag,
                selector: selector,
                id: el.id || '',
                class_names: typeof el.className === 'string' ? el.className.split(/\\s+/).filter(Boolean) : [],
                rect: {
                    left: Math.round(rect.left),
                    right: Math.round(rect.right),
                    top: Math.round(rect.top),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height)
                },
                overflow_px: Math.round(overflowPx),
                spill_direction: rightSpill > 1.0 ? 'RIGHT' : 'LEFT',
                root_causes: rootCauses,
                suggested_fix: fix,
                snippet: snippet
            });
        }
    }

    // Sort culprits by overflow severity descending
    culprits.sort((a, b) => b.overflow_px - a.overflow_px);

    return JSON.stringify({
        visual_viewport_width: Math.round(vw),
        visual_viewport_height: Math.round(vh),
        client_width: Math.round(clientWidth),
        scroll_width: Math.round(scrollWidth),
        has_horizontal_overflow: hasHorizontalOverflow,
        total_overflow_px: Math.round(totalOverflowPx),
        culprits_count: culprits.length,
        culprits: culprits
    });
})()
"""


def classify_css_fix(tag: str, styles: Dict[str, str], spill_direction: str = "RIGHT") -> Dict[str, Any]:
    """
    Python-side classifier for determining CSS root causes and drop-in fixes.
    Useful for offline testing and synthetic DOM diagnostics.
    """
    causes = []
    width = styles.get("width", "")
    min_width = styles.get("min-width", "")
    white_space = styles.get("white-space", "")
    max_width = styles.get("max-width", "")

    if "100vw" in width:
        causes.append("100vw viewport width offset (causes scrollbar overflow)")
        fix = "width: 100%; (replace 100vw to respect document scrollbar)"
    elif min_width and min_width not in ("0px", "auto", "0"):
        causes.append(f"min-width constraint: {min_width}")
        fix = "min-width: 0; max-width: 100%; (allow flex child to shrink)"
    elif tag in ("pre", "code"):
        causes.append("Unconstrained preformatted code block")
        fix = "overflow-x: auto; white-space: pre-wrap; word-break: break-word;"
    elif tag == "table":
        causes.append("Table markup exceeding mobile column width")
        fix = "display: block; overflow-x: auto; max-width: 100%;"
    elif tag in ("img", "video", "iframe") and (not max_width or max_width == "none") and width != "100%":
        causes.append("Media asset lacking max-width: 100%")
        fix = "max-width: 100%; height: auto;"
    elif white_space == "nowrap":
        causes.append("white-space: nowrap prevents text wrapping")
        fix = "white-space: normal; overflow-wrap: anywhere;"
    elif spill_direction == "LEFT":
        causes.append("Negative margin or absolute positioning offset")
        fix = "margin-left: 0; left: 0; max-width: 100%;"
    else:
        causes.append("Unbounded container width exceeding mobile viewport")
        fix = "max-width: 100%; box-sizing: border-box; overflow-x: clip;"

    return {
        "causes": causes,
        "suggested_fix": fix
    }
