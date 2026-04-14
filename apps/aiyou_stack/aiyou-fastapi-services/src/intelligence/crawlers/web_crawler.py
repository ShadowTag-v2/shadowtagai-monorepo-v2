import os
import subprocess
import sys

# Bridge to root level imports
__INTERNAL_LIB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if __INTERNAL_LIB_DIR not in sys.path:
    sys.path.append(__INTERNAL_LIB_DIR)

try:
    from markitdown import MarkItDown  # type: ignore
except ImportError:
    pass

try:
    from scrapling import StealthyFetcher  # type: ignore
except ImportError:
    pass

try:
    from vector_db import ingest_document  # type: ignore
except ImportError:

    def ingest_document(workspace_id: int, markdown: str) -> None:
        print(
            f"[WARN] vector_db module unavailable. Ingestion skipped for Workspace {workspace_id}",
        )


def execute_crawl_and_ingest(target_urls: list[str] | None = None, workspace_id: int = 1) -> None:
    """Executes headless crawling and MarkItDown extraction, persisting to LanceDB."""
    print("\n[🚀] Booting Scrapling Triad + MarkItDown + LangExtract.")
    print(f"[📍] Target Workspace ID: {workspace_id}\n")

    if not target_urls:
        print("[!] No Target URLs provided. Exiting.")
        return

    try:
        md = MarkItDown()
        fetcher = StealthyFetcher()
    except NameError:
        print("[!] Scrapling or MarkItDown libraries missing from python environment.")
        return

    for url in target_urls:
        try:
            print(f"[🔍] Fetching raw DOM payload from: {url}")
            html_content: str = ""

            # Specialized Routing for complex SPAs
            if "tiktok.com" in url:
                print("     [!] TikTok Domain Detected. Utilizing NPM hook...")
                js_hook: str = os.path.join(os.path.dirname(__file__), "tiktok_scraper.js")
                try:
                    js_data: str = subprocess.check_output(
                        ["node", js_hook, url], stderr=subprocess.DEVNULL, timeout=15,
                    ).decode("utf-8")
                    html_content = f"<html><body><pre>{js_data}</pre></body></html>"
                except Exception as e:
                    html_content = f"<html><body><p>Error: {e!s}</p></body></html>"
            else:
                try:
                    page = fetcher.get(url)  # type: ignore
                    html_content = page.html
                except Exception as fetch_err:
                    print(f"     [!] StealthyFetcher exception: {fetch_err}")
                    continue

            # Write temporarily to disk for MarkItDown to process safely
            tmp_path: str = f"/tmp/scraped_buffer_{workspace_id}.html"
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            print("     [+] DOM extracted. Passing to MarkItDown engine...")

            result = md.convert(tmp_path)  # type: ignore
            clean_markdown: str = (
                str(result.text_content) if hasattr(result, "text_content") else ""
            )

            # Ingest into the localized RAG LanceDB schema
            ingest_document(workspace_id, clean_markdown)
            print(f"     [✅] Ingested [{len(clean_markdown)} bytes] into LanceDB Schema!")

            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        except Exception as e:
            print(f"     [❌] Crawler Triad Exception on {url}: {e!s}")


if __name__ == "__main__":
    _default_urls: list[str] = [os.getenv("STRIKE_DEFAULT_TARGET", "https://example.com/ai-agents")]

    _ws_id: int = int(os.getenv("WORKSPACE_ID", "1"))
    execute_crawl_and_ingest(target_urls=_default_urls, workspace_id=_ws_id)
