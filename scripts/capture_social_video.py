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

async def capture_hero_video():
    """
    Captures 12-second videos of the ShadowTag AI hero section for each CTA variant.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        for variant_idx, variant_name in VARIANTS.items():
            print(f"[{variant_name}] Preparing capture...")
            # We record in 16:9 720p for socials
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                record_video_dir=".",
                record_video_size={'width': 1280, 'height': 720}
            )
            
            page = await context.new_page()
            
            # Go to site
            await page.goto("https://shadowtagai.web.app/", wait_until="networkidle")
            
            # Inject local storage variant to force the A/B test branch
            await page.evaluate(f"localStorage.setItem('ab_cta_variant', '{variant_idx}');")
            # Reload to apply
            await page.reload(wait_until="networkidle")
            
            print(f"[{variant_name}] Recording 12 seconds of rotating typography...")
            await page.wait_for_timeout(12000)
            
            # Grab path before closing
            video_path = await page.video.path()
            await context.close()
            
            # Rename video to variant name
            final_name = f"hero_demo_{variant_name}.webm"
            if os.path.exists(final_name):
                os.remove(final_name)
            os.rename(video_path, final_name)
            print(f"✅ Saved {final_name}")
            
        await browser.close()
        print("All variants captured successfully.")

if __name__ == "__main__":
    asyncio.run(capture_hero_video())
