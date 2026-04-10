import asyncio
import sys

from pyppeteer import launch


async def verify_deployment(url):
    print(f">>> 🦁 Brave Bot visiting: {url}")
    # Connect to the Brave instance we masquraded as Chrome
    # Note: Adjust executablePath if necessary for the environment
    executable_path = "/usr/bin/google-chrome"
    if not os.path.exists(executable_path):
        # Fallback for standard chrome if the symlink doesn't exist
        executable_path = None

    browser = await launch(
        executablePath=executable_path,
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox"],
    )
    page = await browser.newPage()
    await page.goto(url)

    # Take Proof of Life
    title = await page.title()
    print(f">>> Page Title: {title}")
    await page.screenshot({"path": "proof_of_life.png"})

    await browser.close()
    print(">>> ✅ Verification Complete. Screenshot saved.")


if __name__ == "__main__":
    import os

    if len(sys.argv) > 1:
        asyncio.get_event_loop().run_until_complete(verify_deployment(sys.argv[1]))
    else:
        print("Usage: python3 scripts/headless_tester.py <url>")
