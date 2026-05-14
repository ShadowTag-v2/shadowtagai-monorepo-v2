import os
import time
import json
import random
from firecrawl import Firecrawl
from scrapling import DynamicFetcher, ProxyRotator, Core

# ==============================================================================
#  SINGULARITY HYBRID SCRAPER: FireCrawl + Scrapling + Proxy Arbitrage
# ==============================================================================


class AntigravityHybridScraper:
    def __init__(self):
        self.fc = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY", ""))

        # 2026 Residential Proxy Rotation
        self.rotator = ProxyRotator(
            cycle=[
                "http://user:pass@brd.superproxy.io:22225",
                "http://user:pass@proxy.oxylabs.io:60000",
            ],
            strategy="sticky_session",  # Keep IP for 5-15 mins to avoid trigger heuristics
            failover=True,
            max_retries=3,
            backoff=2.0,
        )

        self.dynamic = DynamicFetcher(
            headless=True,
            network_idle=True,
            user_data_dir="./tmp/.persistent-browser-profile",  # Prevents tmp drive deletion
        )

    def safe_write(self, filename, data):
        """Antigravity Safe-Mode: Prevents drive deletion, only writes to allowed dirs."""
        allowed_dirs = ["./data", "./output", "./tmp"]
        filepath = os.path.abspath(filename)

        # Security Sandbox Gate
        if not any(filepath.startswith(os.path.abspath(d)) for d in allowed_dirs):
            raise PermissionError("Antigravity Sandbox Violation: Write blocked outside allowed directories.")

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def scrape_spa(self, url, selectors):
        """Solves the 'SPA Spacing' issue: Render with FireCrawl, Parse with Scrapling."""
        print(f" [Scraper] Routing {url} via FireCrawl for DOM Hydration...")
        try:
            # Phase 1: Firecrawl handles infinite scroll and JS hydration
            data = self.fc.scrape(url=url, formats=["html"], params={"waitFor": 3000}, timeout=60)
            raw_html = data["html"]
        except Exception as e:
            print(f" [Scraper] FireCrawl failed ({e}). Arbitraging to Scrapling DynamicFetcher...")
            # Phase 1 Fallback: Scrapling DynamicFetcher with Proxy Rotator
            time.sleep(random.uniform(1, 3))
            page = self.dynamic.fetch(url, proxy=self.rotator.get(), wait_for="networkidle")
            page.wait_for_selector(selectors["container"], timeout=15000)
            raw_html = page.html

        # Phase 2: Scrapling parses the ALREADY RENDERED html. No duplicate network fetch.
        print(" [Scraper] Scrapling: Parsing rendered HTML AST...")
        core = Core(html=raw_html)

        items = []
        for item in core.select(selectors["container"]):
            extracted = {k: item.select(v).text for k, v in selectors["fields"].items()}
            # Extract ID for deduplication
            item_id = item.get(selectors.get("id_field", "data-id"))
            if item_id:
                extracted["id"] = item_id
            items.append(extracted)

        # Phase 3: Deduplicate to handle virtual-list rendering overlap
        deduped = {item.get("id", i): item for i, item in enumerate(items)}
        return list(deduped.values())


if __name__ == "__main__":
    scraper = AntigravityHybridScraper()
    # Agent autonomously orchestrates extraction
    results = scraper.scrape_spa(
        url="https://example-spa.com/products",
        selectors={"container": "div.vue-list-item", "id_field": "data-key", "fields": {"title": "h3.title", "price": "span.price"}},
    )
    scraper.safe_write("./output/spa_results.json", results)
