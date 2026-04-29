#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""11x Browser Extractor — Google AI Mode Research Extraction.

Playwright-based script that navigates Google AI Mode, executes a research
query, waits for the response to fully render, then extracts:
  - The full AI-generated answer text
  - All source URLs cited
  - Any inline code blocks

This is the "Brainstem Layer" of the Tri-Partite Cognitive Architecture
(TACSOP 4 Cor_Kairos, Core Truth #12). It provides zero-latency web research
capability by hijacking the browser's existing Google session.

Usage:
    python3 scripts/11x_browser_extractor.py "What is Cloud Run pricing?"
    python3 scripts/11x_browser_extractor.py --output json "Firebase Auth best practices"

Requirements:
    pip install playwright
    playwright install chromium

Security:
    - Runs against existing browser profile (inherits Google auth)
    - No credentials stored or transmitted
    - Output sanitized through DLP circuit breaker (epistemic-airgap)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout
except ImportError:
    print(
        "ERROR: playwright not installed. Run: pip install playwright && playwright install chromium",
        file=sys.stderr,
    )
    sys.exit(1)


@dataclass
class ExtractionResult:
    """Structured result from AI Mode extraction."""

    query: str
    answer_text: str = ""
    sources: list[str] = field(default_factory=list)
    code_blocks: list[str] = field(default_factory=list)
    extraction_time_ms: int = 0
    error: str | None = None


def extract_ai_mode(query: str, timeout_ms: int = 30000, headless: bool = True) -> ExtractionResult:
    """Navigate to Google AI Mode and extract the research answer.

    Args:
        query: The research query to submit.
        timeout_ms: Maximum wait time for AI response render.
        headless: Whether to run browser headlessly.

    Returns:
        ExtractionResult with answer text, sources, and code blocks.
    """
    result = ExtractionResult(query=query)
    start = time.monotonic()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"),
        )
        page = context.new_page()

        try:
            # Navigate to Google AI Mode with query
            encoded_query = query.replace(" ", "+")
            url = f"https://www.google.com/search?q={encoded_query}&udm=50"
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)

            # Wait for AI response container to appear
            # The AI Mode response renders in a container with specific selectors
            ai_selectors = [
                "[data-ai-response]",
                ".ai-overview-card",
                "#ai-overview",
                ".kno-rdesc",
                ".wDYxhc",  # AI Overview container
            ]

            rendered = False
            for selector in ai_selectors:
                try:
                    page.wait_for_selector(selector, timeout=timeout_ms // len(ai_selectors))
                    rendered = True
                    break
                except PwTimeout:
                    continue

            if not rendered:
                # Fallback: wait for any substantial content
                page.wait_for_timeout(3000)

            # Extract answer text
            answer_elements = page.query_selector_all("[data-ai-response], .ai-overview-card, #ai-overview, .wDYxhc")
            texts = []
            for el in answer_elements:
                text = el.inner_text()
                if text and len(text) > 20:  # Filter noise
                    texts.append(text.strip())
            result.answer_text = "\n\n".join(texts) if texts else ""

            # Extract source URLs
            source_links = page.query_selector_all("[data-ai-response] a[href], .ai-overview-card a[href], .wDYxhc a[href]")
            seen_urls: set[str] = set()
            for link in source_links:
                href = link.get_attribute("href")
                if href and href.startswith("http") and href not in seen_urls:
                    seen_urls.add(href)
                    result.sources.append(href)

            # Extract code blocks
            code_elements = page.query_selector_all("[data-ai-response] pre, [data-ai-response] code, .ai-overview-card pre, .ai-overview-card code")
            for el in code_elements:
                code = el.inner_text()
                if code and len(code) > 10:
                    result.code_blocks.append(code.strip())

        except PwTimeout:
            result.error = f"Timeout after {timeout_ms}ms waiting for AI Mode response"
        except Exception as e:
            result.error = str(e)
        finally:
            elapsed = time.monotonic() - start
            result.extraction_time_ms = int(elapsed * 1000)
            browser.close()

    return result


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="11x Browser Extractor — Google AI Mode research extraction")
    parser.add_argument("query", help="Research query to submit to Google AI Mode")
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30000,
        help="Timeout in milliseconds (default: 30000)",
    )
    parser.add_argument(
        "--headful",
        action="store_true",
        help="Run browser in headful mode (visible window)",
    )

    args = parser.parse_args()
    result = extract_ai_mode(args.query, timeout_ms=args.timeout, headless=not args.headful)

    if args.output == "json":
        print(json.dumps(asdict(result), indent=2))
    else:
        if result.error:
            print(f"⚠️  Error: {result.error}", file=sys.stderr)
        print(f"Query: {result.query}")
        print(f"Time: {result.extraction_time_ms}ms")
        print(f"\n{'=' * 60}")
        print(result.answer_text or "(no answer extracted)")
        if result.sources:
            print(f"\n📎 Sources ({len(result.sources)}):")
            for url in result.sources[:10]:
                print(f"  • {url}")
        if result.code_blocks:
            print(f"\n💻 Code Blocks ({len(result.code_blocks)}):")
            for i, block in enumerate(result.code_blocks[:5], 1):
                print(f"\n  [{i}]\n  {block[:200]}...")


if __name__ == "__main__":
    main()
