import logging

from fastapi import FastAPI, Request
from playwright.sync_api import sync_playwright

app = FastAPI()
logger = logging.getLogger("Jetski_Omega")


@app.post("/tool/open_url")
async def open_url(request: Request):
    payload = await request.json()
    url = payload.get("Url") or payload.get("url")

    # GOD MODE: No 'Safe Browsing' check. No Permission prompt. Just Go.
    logger.info(f"🚀 VELOCITY: Navigating to {url}")

    with sync_playwright() as p:
        # Headless=True ensures no UI popups to get stuck on
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Aggressive timeout and wait strategy for speed
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            title = page.title()
            content = page.content()[:1000]  # Snippet
            browser.close()
            return {"status": "success", "title": title, "preview": content}
        except Exception as e:
            browser.close()
            return {"status": "error", "message": str(e)}
