import json
import os
import random
import time

from firecrawl import Firecrawl
from scrapling import Core, DynamicFetcher, ProxyRotator


class AntigravityHybridScraper:
    def __init__(self):
        self.fc = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

        self.rotator = ProxyRotator(
            cycle=[
                "http://user:pass@brd.superproxy.io:22225",
                "http://user:pass@proxy.oxylabs.io:60000",
            ],
            strategy="sticky_session",
            failover=True,
            max_retries=3,
            backoff=2.0,
        )

        self.dynamic = DynamicFetcher(
            headless=True,
            network_idle=True,
            user_data_dir="./tmp/.persistent-browser-profile",
        )

    def safe_write(self, filename, data):
        allowed_dirs = ["./data", "./output", "./tmp"]
        filepath = os.path.abspath(filename)
        if not any(filepath.startswith(os.path.abspath(d)) for d in allowed_dirs):
            raise PermissionError("Antigravity Sandbox Violation: Write blocked outside allowed directories.")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def scrape_spa(self, url, selectors):
        print(f" [Scraper] Routing {url} via FireCrawl for DOM Hydration...")
        try:
            data = self.fc.scrape(
                url=url,
                formats=["html"],
                wait_for="domcontentloaded",
                js_code="window.scrollTo(0, document.body.scrollHeight);",
                timeout=60,
            )
            raw_html = data["html"]
        except Exception as e:
            print(f" [Scraper] FireCrawl failed ({e}). Arbitraging to Scrapling DynamicFetcher...")
            time.sleep(random.uniform(1, 3))
            page = self.dynamic.fetch(url, proxy=self.rotator.get(), wait_for="networkidle")
            page.wait_for_selector(selectors["container"], timeout=15000)
            raw_html = page.html

        print(" [Scraper] Scrapling: Parsing rendered HTML AST...")
        core = Core(html=raw_html)
        items = []
        for item in core.select(selectors["container"]):
            extracted = {k: item.select(v).text for k, v in selectors["fields"].items()}
            item_id = item.get(selectors.get("id_field", "data-id"))
            if item_id:
                extracted["id"] = item_id
            items.append(extracted)

        deduped = {item.get("id", i): item for i, item in enumerate(items)}
        return list(deduped.values())
