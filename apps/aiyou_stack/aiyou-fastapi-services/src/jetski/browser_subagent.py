# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging
import os
import uuid
from typing import Any

import uvicorn
from fastapi import FastAPI, Request

try:  # noqa: SIM105
    from playwright.sync_api import sync_playwright  # type: ignore
except ImportError:
    pass

try:
    from playwright_stealth import stealth_sync  # type: ignore
except ImportError:
    # Fallback if module is missing to prevent crash during staging
    def stealth_sync(context: Any) -> None:
        pass


app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger("jetski-subagent")

# Persistent state using robust environment fallback instead of unprivileged root /profile
PROFILE_DIR: str = os.getenv("JETSKI_PROFILE_DIR", "/tmp/jetski_profile")
PAGES: dict[str, dict[str, Any]] = {}


@app.get("/.identity")
def identity() -> dict[str, str]:
    """MCP Discovery Endpoint"""
    return {"identity": "jetski-browser-subagent", "version": "v3-antigravity"}


@app.post("/tool/{tool_name}")
async def execute_tool(tool_name: str, request: Request) -> dict[str, Any]:
    payload: dict[str, Any] = await request.json()
    page_id: str = payload.get("PageId", "default")

    # 1. Lazy Initialization of Browser
    if not PAGES:
        logger.info("🚀 Booting Headless Chromium...")
        playwright_context = sync_playwright().start()
        browser = playwright_context.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )
        # Persistent Context
        context = browser.new_context(
            user_data_dir=PROFILE_DIR,
            viewport={"width": 1920, "height": 1080},
        )
        stealth_sync(context)
        page = context.new_page()
        PAGES["default"] = {"page": page, "browser": browser, "context": context}

    # 2. Page Selection
    if page_id not in PAGES:
        PAGES[page_id] = PAGES["default"]

    page = PAGES[page_id]["page"]
    result: dict[str, Any] = {"status": "done", "page_id": page_id}

    try:
        # --- TOOL: OPEN URL ---
        if tool_name == "open_url":
            target_url: str = str(payload.get("Url", ""))
            logger.info(f"🌐 Navigating to: {target_url}")
            page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            result["title"] = page.title()

        # --- TOOL: READ DOM (Viewport Aware) ---
        elif tool_name in ["get_dom_tree", "read_browser_page"]:
            # Only fetch visible, interactive elements to reduce context noise
            elements: list[dict[str, Any]] = page.eval_on_selector_all(
                "a,button,input,textarea,[onclick]",
                """els => els.map((el, idx) => ({
                    idx,
                    tag: el.tagName,
                    text: el.innerText ? el.innerText.substring(0,100).replace(/\\n/g, ' ') : '',
                    visible: window.getComputedStyle(el).display !== 'none'
                }))""",
            )
            visible_elements: list[dict[str, Any]] = [e for e in elements if e.get("visible")]
            result["dom"] = visible_elements[:50]  # Cap to prevent overflow

            # Auto-Screenshot for Verification
            shot_path: str = f"/tmp/jetski_snap_{uuid.uuid4().hex[:8]}.png"
            page.screenshot(path=shot_path)
            result["screenshot"] = shot_path

        # --- TOOL: CLICK ELEMENT ---
        elif tool_name == "click_element":
            idx: int = int(payload.get("ElementIndex", 0))
            logger.info(f"🖱️ Clicking element index {idx}")
            page.click(f":nth-match(a,button,input,{idx + 1})")

        # --- TOOL: SCROLL ---
        elif tool_name == "scroll_down":
            page.evaluate("window.scrollBy(0, window.innerHeight)")

        # --- TOOL: SCREENSHOT ---
        elif tool_name == "capture_screenshot":
            filename = payload.get("Filename", f"snap_{uuid.uuid4().hex[:8]}")
            path: str = f"/tmp/{filename}.png"
            page.screenshot(path=path, full_page=True)
            result["path"] = path

        else:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}

    except Exception as e:
        logger.error(f"❌ Jetski Failure: {e}")
        return {"status": "failed", "error": str(e)}

    return result


if __name__ == "__main__":
    _port_str = os.getenv("JETSKI_PORT", "3000")
    try:
        port: int = int(_port_str)
    except ValueError:
        port = 3000
    uvicorn.run(app, host="0.0.0.0", port=port)
