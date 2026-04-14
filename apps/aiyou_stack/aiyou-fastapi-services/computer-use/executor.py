"""Computer-Use Agent Action Executor

Translates Gemini Computer-Use API function calls to Playwright actions.
"""

from __future__ import annotations

from playwright.sync_api import Page

# Recommended viewport size per Gemini Computer-Use docs
VW, VH = 1440, 900


def _px(x_norm: float, y_norm: float) -> tuple[int, int]:
    """Convert normalized coordinates (0-999) to pixel coordinates.

    Args:
        x_norm: Normalized X coordinate (0-999)
        y_norm: Normalized Y coordinate (0-999)

    Returns:
        Tuple of (x_pixels, y_pixels)

    """
    x = int(max(0, min(VW - 1, x_norm * VW / 999)))
    y = int(max(0, min(VH - 1, y_norm * VH / 999)))
    return x, y


def run_action(page: Page, name: str, args: dict) -> str:
    """Execute a single Computer-Use action on the page.

    Args:
        page: Playwright Page instance
        name: Function name (e.g., "click_at", "type_text_at")
        args: Function arguments from Gemini API

    Returns:
        Result string describing what was executed

    """
    if name == "open_web_browser":
        # No-op (browser managed externally)
        return "ok"

    if name == "navigate":
        url = args.get("url") or "about:blank"
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return f"nav:{url}"

    if name == "click_at":
        x, y = _px(args.get("x", 0), args.get("y", 0))
        page.mouse.click(x, y)
        return f"click:{x},{y}"

    if name == "type_text_at":
        x, y = _px(args.get("x", 0), args.get("y", 0))
        page.mouse.click(x, y)
        text = args.get("text", "")
        page.keyboard.type(text, delay=10)
        if args.get("press_enter"):
            page.keyboard.press("Enter")
        return f"type:{len(text)}"

    if name == "wait":
        ms = int(args.get("ms", 500))
        page.wait_for_timeout(ms)
        return f"wait:{ms}"

    if name == "back":
        page.go_back()
        return "back"

    if name == "forward":
        page.go_forward()
        return "forward"

    # Unknown action
    return f"unknown:{name}"
