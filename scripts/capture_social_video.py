import asyncio
from playwright.async_api import async_playwright

async def capture_hero_video():
    """
    Captures a 10-second video of the ShadowTag AI hero section,
    specifically showcasing the rotating typography and urgency bar
    for social media distribution (LinkedIn/X).
    """
    async with async_playwright() as p:
        # We use Chromium for robust webm/mp4 capture
        browser = await p.chromium.launch()
        
        # 16:9 aspect ratio standard for social media videos
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            record_video_dir=".",
            record_video_size={'width': 1280, 'height': 720}
        )
        
        page = await context.new_page()
        
        print("Navigating to production site...")
        await page.goto("https://shadowtagai.web.app/", wait_until="networkidle")
        
        # Wait for the hero section and JS animations to initialize
        await page.wait_for_timeout(2000)
        
        print("Recording 12 seconds of rotating typography...")
        # 12 seconds allows for ~3 full tagline rotations (3.5s per cycle)
        await page.wait_for_timeout(12000)
        
        # Close to flush the video file
        await context.close()
        await browser.close()
        
        print("✅ Capture complete. Video saved in current directory.")

if __name__ == "__main__":
    asyncio.run(capture_hero_video())
