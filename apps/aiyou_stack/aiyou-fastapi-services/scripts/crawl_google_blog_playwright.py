import os
import time

from playwright.sync_api import sync_playwright

OUTPUT_FILE = "/Users/Deleted Users/pikeymickey/shadowtag_v4-fastapi-services/erik-hancock-llm-memory/extractions/google_blog_urls.txt"
BASE_URL = "https://developers.googleblog.com"


def crawl(query, page):
    search_url = f"{BASE_URL}/search?q={query}"
    print(f"🔍 crawling: {search_url}")
    page.goto(search_url)

    # Wait for initial load
    try:
        page.wait_for_selector("a", timeout=5000)
    except:
        print("   Warning: Timeout waiting for initial links")

    # Scroll loop
    last_height = 0
    unchanged_count = 0
    max_scrolls = 50  # Prevent infinite loops

    for i in range(max_scrolls):
        # Scroll to bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)  # Wait for lazy load

        # Check height
        new_height = page.evaluate("document.body.scrollHeight")
        print(f"   Scroll {i + 1}: height {last_height} -> {new_height}")

        if new_height == last_height:
            unchanged_count += 1
            if unchanged_count >= 3:  # Stop if height hasn't changed for 3 scrolls
                print("   Reached bottom (height unchanged).")
                break
        else:
            unchanged_count = 0

        last_height = new_height

    # Extract Links
    print("   Extracting links...")
    links = page.evaluate("""() => {
        const anchors = Array.from(document.querySelectorAll('a'));
        return anchors.map(a => a.href);
    }""")

    # Filter
    valid_urls = set()
    for link in links:
        # Modern URL structure: https://developers.googleblog.com/slug-name/
        # Legacy: https://developers.googleblog.com/2023/01/slug.html
        if (
            BASE_URL in link
            and "/search" not in link
            and "/label" not in link
            and "/feeds" not in link
            and link != BASE_URL
            and link != BASE_URL + "/"
        ):
            valid_urls.add(link)

    print(f"   found {len(valid_urls)} videos/articles.")
    return valid_urls


def main():
    print("🚀 Starting Google Blog Crawl...")
    if not os.path.exists(os.path.dirname(OUTPUT_FILE)):
        os.makedirs(os.path.dirname(OUTPUT_FILE))

    all_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Crawl Gemini
        gemini_urls = crawl("Gemini", page)
        all_urls.update(gemini_urls)

        # Crawl AI
        ai_urls = crawl("AI", page)
        all_urls.update(ai_urls)

        browser.close()

    print(f"\n✅ Total Unique URLs found: {len(all_urls)}")

    with open(OUTPUT_FILE, "w") as f:
        for url in sorted(all_urls):
            f.write(url + "\n")

    print(f"💾 Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
