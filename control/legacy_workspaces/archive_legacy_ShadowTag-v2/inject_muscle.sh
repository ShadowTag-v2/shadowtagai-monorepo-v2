#!/bin/bash
set -e
# ==============================================================================
# 💪 SHADOWTAG MUSCLE INJECTION (v1.0)
# ==============================================================================
# REPLACES: Stubbed Jetski & Swarm
# WITH: Playwright Vision Agent & Async Persona Council
# ==============================================================================

echo ">>> 💉 INJECTING LIVE ORDNANCE..."

# ==============================================================================
# 1. JETSKI (Visual Browser Agent)
# ==============================================================================
# Uses Playwright to render pages + Gemini Vision to "see" and "click".

mkdir -p libs/arsenal/jetski
cat <<PYTHON > libs/arsenal/jetski/browser.py
import asyncio
import base64
import json
import logging
from playwright.async_api import async_playwright
from google import genai
from google.genai import types

class JetskiAgent:
    """
    Vision-Driven Browser Agent.
    1. Browses to URL.
    2. Takes Screenshot.
    3. Asks Gemini: "Where do I click to achieve X?"
    4. Executes action.
    """
    def __init__(self):
        self.client = genai.Client(vertexai=True, location="us-central1")
        self.model = "gemini-3.1-flash-exp"  # Flash is fast enough for UI nav

    async def execute(self, task: str, url: str = "https://google.com"):
        logging.info(f"🏄 JETSKI: Launching browser for: {task}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url)

            # The Loop: Observe -> Orient -> Decide -> Act
            # For this 'Atomic Block', we do one pass.

            # 1. OBSERVE
            screenshot_bytes = await page.screenshot(format="jpeg")

            # 2. ORIENT & DECIDE (Vision Prompt)
            prompt = f"""
            You are a Browser Automation Agent.
            TASK: {task}
            CURRENT URL: {page.url}

            Analyze the screenshot. Return a JSON object with the next action:
            {{
                "thought": "I need to click the search bar.",
                "action": "click" | "type" | "finish",
                "selector": "css_selector_or_text_match",
                "value": "text_to_type_if_any"
            }}
            """

            logging.info("🏄 JETSKI: Analyzing page visually...")
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(data=screenshot_bytes, mime_type="image/jpeg"),
                    prompt
                ],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )

            decision = json.loads(response.text)
            logging.info(f"🏄 JETSKI DECISION: {decision['thought']}")

            # 3. ACT
            result = {"status": "success", "data": decision}

            try:
                if decision["action"] == "click":
                    # Try selector first, fallback to text
                    try:
                        await page.click(decision["selector"], timeout=2000)
                    except:
                        await page.get_by_text(decision["selector"]).first.click()

                elif decision["action"] == "type":
                    await page.fill(decision["selector"], decision["value"])
                    await page.keyboard.press("Enter")

                # Capture result state
                await page.wait_for_load_state("networkidle")
                final_shot = await page.screenshot(format="jpeg")
                result["final_screenshot_b64"] = base64.b64encode(final_shot).decode()

            except Exception as e:
                result["status"] = "error"
                result["error"] = str(e)

            await browser.close()
            return result

# Synchronous wrapper for existing calls
def run_jetski(task, url="https://google.com"):
    return asyncio.run(JetskiAgent().execute(task, url))
PYTHON

# ==============================================================================
# 2. SWARM (Async Persona Council)
# ==============================================================================
# Spawns 5 distinct Gemini Personas to debate risk.

mkdir -p libs/arsenal/flying_monkeys
cat <<PYTHON > libs/arsenal/flying_monkeys/swarm.py
import asyncio
import logging
import json
from google import genai

class CavMTOE:
    """
    The Digital Council (Swarm).
    Instead of 650 random bots, we spawn 5 distinct Archetypes to debate.
    """
    def __init__(self):
        self.client = genai.Client(vertexai=True, location="us-central1")
        self.model = "gemini-3.1-flash-exp"
        self.personas = [
            {"role": "Security Officer", "bias": "Paranoid", "prompt": "Block anything that touches secrets/networking."},
            {"role": "Product Manager", "bias": "Optimistic", "prompt": "Approve if it adds value. Ignore minor risks."},
            {"role": "Legal Counsel", "bias": "Pedantic", "prompt": "Block if license/compliance is unclear."},
            {"role": "DevOps Engineer", "bias": "Pragmatic", "prompt": "Approve if it works. Block if it breaks build."},
            {"role": "Chaos Monkey", "bias": "Destructive", "prompt": "Approve high risk changes just to see what happens."}
        ]

    async def _consult_persona(self, persona, intent):
        prompt = f"""
        You are the {persona['role']}. Your bias is {persona['bias']}.
        Instructions: {persona['prompt']}

        INTENT: "{intent}"

        Vote 'YES' or 'NO'. Provide a 1-sentence reason.
        Output JSON: {{"vote": "YES"|"NO", "reason": "..."}}
        """
        try:
            response = await self.client.models.generate_content_async(
                model=self.model, contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except:
            return {"vote": "NO", "reason": "Persona timed out."}

    async def deploy_bravo(self, intent: str):
        """
        Async Parallel Voting.
        """
        logging.info(f"🐝 SWARM: Convening Council for '{intent}'...")

        # 1. Spawn Async Tasks
        tasks = [self._consult_persona(p, intent) for p in self.personas]
        results = await asyncio.gather(*tasks)

        # 2. Tally Votes
        yes_votes = sum(1 for r in results if r["vote"] == "YES")
        total = len(results)

        # 3. Final Verdict (Simple Majority)
        status = "APPROVED" if yes_votes > (total / 2) else "REJECTED"

        return {
            "status": status,
            "score": f"{yes_votes}/{total}",
            "details": [
                {"role": self.personas[i]["role"], "vote": r["vote"], "reason": r["reason"]}
                for i, r in enumerate(results)
            ]
        }

# Sync wrapper
def vote(intent):
    council = CavMTOE()
    return asyncio.run(council.deploy_bravo(intent))
PYTHON

# ==============================================================================
# 3. UPDATE DEPENDENCIES
# ==============================================================================
echo "playwright" >> requirements.txt

echo ">>> ✅ MUSCLE INJECTED."
echo ">>> NEXT STEPS:"
echo "    1. pip install -r requirements.txt"
echo "    2. playwright install chromium"
echo "    3. Test Swarm: python3 -c 'from libs.arsenal.flying_monkeys.swarm import vote; print(vote(\"Delete the production database\"))'"
