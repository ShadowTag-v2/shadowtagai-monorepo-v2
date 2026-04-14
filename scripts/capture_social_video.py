#!/usr/bin/env uv run --python 3.14
# /// script
# requires-python = ">=3.14"
# dependencies = ["playwright"]
# ///
import asyncio
import os
from playwright.async_api import async_playwright

VARIANTS = {
    0: "control",
    1: "var_A",
    2: "var_B"
}

async def record_variant(browser, variant_idx, variant_name):
    print(f"[{variant_name}] Preparing capture...")
    context = await browser.new_context(
        viewport={'width': 1280, 'height': 720},
        record_video_dir=".",
        record_video_size={'width': 1280, 'height': 720}
    )
    
    page = await context.new_page()
    await page.goto("https://shadowtagai.web.app/", wait_until="networkidle")
    
    await page.evaluate(f"localStorage.setItem('ab_cta_variant', '{variant_idx}');")
    await page.reload(wait_until="networkidle")
    
    print(f"[{variant_name}] Recording 12 seconds of rotating typography...")
    await page.wait_for_timeout(12000)
    
    video_path = await page.video.path()
    await context.close()
    
    final_name = f"hero_demo_{variant_name}.webm"
    if os.path.exists(final_name):
        os.remove(final_name)
    os.rename(video_path, final_name)
    print(f"✅ Saved {final_name}")

async def capture_hero_video():
    """
    Captures 12-second videos concurrently.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # Multi-thread through asyncio.gather
        tasks = []
        for variant_idx, variant_name in VARIANTS.items():
            tasks.append(record_variant(browser, variant_idx, variant_name))
            
        await asyncio.gather(*tasks)
            
        await browser.close()
        print("All variants captured concurrently.")

if __name__ == "__main__":
    asyncio.run(capture_hero_video())
