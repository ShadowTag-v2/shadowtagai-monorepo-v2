import os
import subprocess
import tempfile

from markitdown import MarkItDown
from scrapling import StealthyFetcher

from vector_db import ingest_document

WORKSPACE_ID = 1

TARGET_URLS = [
    "https://cloud.google.com/blog/products/"
    "ai-machine-learning/a-devs-guide-to-production-ready-ai-agents",
    "https://firebase.blog/posts/2026/02/ai-agent-skills-for-firebase",
    "https://firebase.google.com/docs/ai-assistance/mcp-server",
    "https://developers.googleblog.com/introducing-the-developer-knowledge-api-and-mcp-server/",
]


def execute_crawl_and_ingest():
    print("\n[boot] Booting Scrapling Triad + MarkItDown + LangExtract.")
    print(f"[workspace] Target Workspace ID: {WORKSPACE_ID}\n")

    md = MarkItDown()
    fetcher = StealthyFetcher()

    for url in TARGET_URLS:
        tmp_path = None
        try:
            print(f"[fetch] Fetching raw DOM payload from: {url}")

            if "tiktok.com" in url:
                print("     [!] TikTok Domain Detected. Utilizing NPM hook...")
                js_hook = os.path.join(os.path.dirname(__file__), "tiktok_scraper.js")
                try:
                    js_data = subprocess.check_output(
                        ["node", js_hook, url],
                        stderr=subprocess.DEVNULL,
                        timeout=15,
                    ).decode("utf-8")
                    html_content = f"<html><body><pre>{js_data}</pre></body></html>"
                except Exception as e:
                    html_content = f"<html><body><p>Error: {e!s}</p></body></html>"
            else:
                page = fetcher.get(url)
                html_content = page.html

            with tempfile.NamedTemporaryFile(
                "w", suffix=".html", delete=False, encoding="utf-8",
            ) as f:
                tmp_path = f.name
                f.write(html_content)

            print("     [+] DOM extracted. Passing to MarkItDown engine...")

            result = md.convert(tmp_path)
            clean_markdown = result.text_content

            ingest_document(WORKSPACE_ID, clean_markdown)
            print(f"     [ok] Ingested [{len(clean_markdown)} bytes] into LanceDB Schema!")
        except Exception as e:
            print(f"     [error] Crawler Triad Exception on {url}: {e!s}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == "__main__":
    execute_crawl_and_ingest()
