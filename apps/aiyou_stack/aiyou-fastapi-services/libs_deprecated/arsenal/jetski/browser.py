import asyncio
import base64
import json
import logging
import os
import shutil

from google import genai
from google.genai import types
from playwright.async_api import async_playwright


def find_brave_path():
    """Locates the Brave Browser executable on the host system."""
    # 1. Check Environment Override
    if os.environ.get("BRAVE_BIN"):
        return os.environ["BRAVE_BIN"]

    # 2. Common Paths
    paths = [
        "/usr/bin/brave-browser",  # Linux
        "/usr/bin/brave-browser-beta",  # Linux Beta
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",  # MacOS
        "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",  # Windows
    ]

    for p in paths:
        if os.path.exists(p):
            return p

    # 3. Path Search
    return shutil.which("brave-browser")


class JetskiAgent:
    """Brave-Driven Vision Agent."""

    def __init__(self):
        self.client = genai.Client(vertexai=True, location="us-central1")
        self.model = "gemini-3.1-flash-lite-preview"
        self.brave_path = find_brave_path()

    async def execute(self, task: str, url: str = "https://search.brave.com"):
        logging.info(f"🏄 JETSKI: Launching Browser for: {task}")

        launch_args = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        }

        # Force Brave if detected
        if self.brave_path:
            logging.info(f"🦁 JETSKI: Using Brave Browser at {self.brave_path}")
            launch_args["executable_path"] = self.brave_path
        else:
            logging.warning("⚠️ JETSKI: Brave not found. Falling back to bundled Chromium.")

        async with async_playwright() as p:
            # Launch the Browser
            browser = await p.chromium.launch(**launch_args)

            # Create context with anti-detect features often used in Sovereign setups
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )

            page = await context.new_page()
            await page.goto(url)

            # --- THE VISION LOOP ---

            # 1. OBSERVE
            screenshot_bytes = await page.screenshot(format="jpeg", quality=80)

            # 2. ORIENT & DECIDE
            prompt = f"""
            You are an Autonomous Browser Agent using Brave.
            TASK: {task}
            CURRENT URL: {page.url}

            Analyze the screenshot. Return a JSON object:
            {{
                "thought": "Reasoning here...",
                "action": "click" | "type" | "scroll" | "finish",
                "selector": "Visual description or CSS selector",
                "value": "text_to_type"
            }}
            """

            logging.info("🧠 JETSKI: Vision Reasoning...")
            response = await self.client.models.generate_content_async(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=screenshot_bytes, mime_type="image/jpeg"),
                    prompt,
                ],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )

            decision = json.loads(response.text)
            logging.info(f"👉 ACTION: {decision['thought']}")

            # 3. ACT
            result = {"status": "success", "data": decision}
            try:
                if decision["action"] == "click":
                    # Smart Click (Selector or Visual Text)
                    try:
                        await page.click(decision["selector"], timeout=2000)
                    except Exception:
                        await page.get_by_text(decision["selector"], exact=False).first.click()

                elif decision["action"] == "type":
                    await page.fill(decision["selector"], decision["value"])
                    await page.keyboard.press("Enter")

                elif decision["action"] == "scroll":
                    await page.evaluate("window.scrollBy(0, 500)")

                await page.wait_for_load_state("networkidle")

                # Evidence
                final_shot = await page.screenshot(format="jpeg")
                result["screenshot_b64"] = base64.b64encode(final_shot).decode()

            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)

            await browser.close()
            return result


# Sync Wrapper
def run_jetski(task, url="https://search.brave.com"):
    return asyncio.run(JetskiAgent().execute(task, url))
