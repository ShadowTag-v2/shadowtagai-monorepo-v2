# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Gemini Computer-Use Agent

Safety-controlled browser automation agent using Gemini 2.5 Computer-Use API.
"""

from __future__ import annotations
import os
import sys
from pathlib import Path
from urllib.parse import urlparse
from google import genai
from google.genai import types
from playwright.sync_api import sync_playwright
import yaml

# Import our local modules
from .executor import run_action, VW, VH
from .audit import log

# Configuration
MODEL = os.environ.get("CU_MODEL", "gemini-2.5-computer-use-preview-10-2025")
GOAL = os.environ.get("CU_GOAL", "Navigate to example.com and verify the page loads.")
START = os.environ.get("CU_START_URL", "https://example.com")

# Load allowlist
ALLOWLIST_PATH = Path(__file__).parent / "allowlist.yaml"
ALLOW = yaml.safe_load(ALLOWLIST_PATH.read_text(encoding="utf-8"))

MAX_TURNS = int(ALLOW.get("limits", {}).get("max_turns", 10))
DOMAINS = set(ALLOW.get("domains", []))
BLOCK_URL_SUBSTR = set(ALLOW.get("block", {}).get("url_contains", []))
EXCLUDED_FUNCTIONS = set(ALLOW.get("excluded_functions", []))


def _allowed(url: str) -> bool:
    """Check if a URL is allowed per the allowlist."""
    try:
        host = (urlparse(url).hostname or "").lower()
    except:
        return False

    # Check domain allowlist
    if DOMAINS and not any(host.endswith(d) for d in DOMAINS):
        return False

    # Check blocked substrings
    return not any(s in url for s in BLOCK_URL_SUBSTR)


def _part_image(png_bytes: bytes) -> types.Part:
    """Create a Gemini Part from PNG screenshot bytes."""
    return types.Part.from_bytes(data=png_bytes, mime_type="image/png")


def main() -> int:
    """
    Run the Computer-Use agent.

    Returns:
        Exit code (0 = success, non-zero = failure)
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set", file=sys.stderr)
        return 2

    client = genai.Client(api_key=api_key)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": VW, "height": VH})
        page = ctx.new_page()

        # Navigate to starting URL
        page.goto(START, wait_until="domcontentloaded")
        log("start", goal=GOAL, start=START, model=MODEL)

        turns = 0
        while turns < MAX_TURNS:
            turns += 1

            # Capture screenshot
            png = page.screenshot(full_page=False)

            # Configure Computer-Use tool
            cfg = types.GenerateContentConfig(
                tools=[types.Tool(computer_use=types.ComputerUse())], excluded_predefined_functions=list(EXCLUDED_FUNCTIONS)
            )

            # Call Gemini with goal + screenshot
            try:
                resp = client.models.generate_content(
                    model=MODEL,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part(text=GOAL),
                                _part_image(png),
                            ],
                        )
                    ],
                    config=cfg,
                )
            except Exception as e:
                log("error", turn=turns, error=str(e))
                print(f"Error calling Gemini: {e}", file=sys.stderr)
                break

            # Extract function calls
            cand = resp.candidates[0]
            acts = []
            for part in cand.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    acts.append(part.function_call)

            # Log safety ratings
            if getattr(cand, "safety_ratings", None):
                log("safety", turn=turns, ratings=[{"category": sr.category, "probability": sr.probability} for sr in cand.safety_ratings])

            # If no actions, agent thinks it's done
            if not acts:
                log("done", reason="no-actions", turn=turns)
                break

            # Execute actions
            for fc in acts:
                name = fc.name
                args = dict(fc.args or {})

                # Enforce allowlist on navigate
                if name == "navigate":
                    url = args.get("url", "")
                    if not _allowed(url):
                        log("blocked", turn=turns, action=name, url=url, reason="not-in-allowlist")
                        continue

                # Execute action
                try:
                    res = run_action(page, name, args)
                    log("action", turn=turns, name=name, args=args, result=res)
                except Exception as e:
                    log("action_error", turn=turns, name=name, args=args, error=str(e))

        # Save final HTML snapshot
        out_html = Path(os.environ.get("CU_HTML_OUT", ".ci/computer_use_final.html"))
        out_html.parent.mkdir(parents=True, exist_ok=True)
        out_html.write_text(page.content(), encoding="utf-8")

        browser.close()
        print(f"Agent completed. Final HTML: {out_html}")
        log("completed", turns=turns, output_html=str(out_html))

    return 0


if __name__ == "__main__":
    sys.exit(main())
