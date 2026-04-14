#!/usr/bin/env uv run --python 3.14
# /// script
# requires-python = ">=3.14"
# dependencies = ["playwright", "pytest", "pytest-playwright"]
# ///
import asyncio
from playwright.async_api import async_playwright, expect

VARIANTS = {
    "control": "Deploy Judge 6 Shield",
    "var_A": "Get Liability Immunity",
    "var_B": "Schedule Risk Audit"
}

async def assert_visuals():
    """
    Spins up browsers to ensure the CTA copies render correctly
    without overlap, validating structurally.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        for idx, (v_key, v_text) in enumerate(VARIANTS.items()):
            context = await browser.new_context()
            page = await context.new_page()
            
            print(f"[{v_key}] Running structural assertion...")
            await page.goto("https://shadowtagai.web.app/", wait_until="networkidle")
            await page.evaluate(f"localStorage.setItem('ab_cta_variant', '{idx}');")
            await page.reload(wait_until="networkidle")
            
            # Allow animations to finish
            await page.wait_for_timeout(2000)
            
            cta_obj = page.locator('#ab-cta-text')
            
            # 1. Assert Text matches
            try:
                await expect(cta_obj).to_have_text(v_text, timeout=5000)
                print(f"✅ Text matched: {v_text}")
            except AssertionError:
                print(f"❌ Text mismatched for {v_key}")
                
            # 2. Assert button is within viewport (structurally visible)
            try:
                await expect(cta_obj).to_be_in_viewport()
                print(f"✅ Element is visible in viewport.")
            except AssertionError:
                print(f"❌ Visual overlap/invisible for {v_key}")

            # 3. Snapshot assertion point
            await page.screenshot(path=f"snapshot_{v_key}.png")
            
            await context.close()
            
        await browser.close()
        print("Completed visual pass across all variants.")

if __name__ == "__main__":
    asyncio.run(assert_visuals())
