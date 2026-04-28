# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import sys
import subprocess
import importlib.util


def install_if_needed():
    if importlib.util.find_spec("scrapling") is None:
        print("Scrapling not found. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scrapling", "lxml"])


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_scrapling.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    install_if_needed()

    from scrapling import Fetcher

    # We use StealthyFetcher for anti-bot resilience
    print(f"🕵️ Fetching {url} with Scrapling...")
    try:
        from scrapling import StealthyFetcher

        # Attempt stealth fetch
        fetcher = StealthyFetcher()
        page = fetcher.get(url)
    except Exception as e:
        print(f"Stealthy fetch failed ({e}). Falling back to regular Fetcher...")
        fetcher = Fetcher()
        page = fetcher.get(url)

    # Scrapling page objects often have markdown conversion, or we can just pull the text.
    # We will try to get the text of the main content or body.
    try:
        # A simple markdown approach if the feature exists, else clean text
        content = page.css("body").text
        print("\n=== EXTRACTION RESULTS ===")
        print(content)
        print("\n==========================")
    except Exception as e:
        print(f"Error during parsing: {e}")


if __name__ == "__main__":
    main()
