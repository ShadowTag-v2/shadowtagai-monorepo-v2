# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import asyncio
from playwright.async_api import async_playwright


async def run():
  async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page(viewport={"width": 2560, "height": 1440})
    await page.goto("http://localhost:3000", wait_until="networkidle")
    await page.screenshot(
      path="/Users/pikeymickey/aiyou-stack/ShadowTag-v2/apps/shadowtag-web/public/final_replica_screenshot.jpeg",
      quality=90,
      type="jpeg",
    )
    await browser.close()
    print("Playwright screenshot captured!")


asyncio.run(run())
