#!/usr/bin/env python3
"""Quick end-to-end ingest validation:
  Reddit (free) → IngestedItem → SQLite → query back

Usage:
    cd apps/ShadowTag-v2_stack/shadowtag_v4-fastapi-services
    python scripts/test_ingest_pass.py
"""

import asyncio
import sys
from pathlib import Path

# Resolve project root so imports work from any cwd
ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

from ingestion.sources.reddit_adapter import RedditAdapter  # noqa: E402
from ingestion.storage.sqlite_store import IngestStore  # noqa: E402

TEST_DB = ROOT / "data/web_ingest/test_ingest.db"
TEST_SUBREDDITS = ["LocalLLaMA", "MachineLearning"]


async def main() -> None:
    print(f"\n{'=' * 60}")
    print("PNKLN Ingest Test Pass — Reddit → SQLite")
    print(f"{'=' * 60}\n")

    store = IngestStore(TEST_DB)
    adapter = RedditAdapter(subreddits=TEST_SUBREDDITS, limit=10)

    print(f"Target subreddits : {TEST_SUBREDDITS}")
    print(f"DB path           : {TEST_DB}\n")

    job_id = "test-pass-001"
    store.create_job(job_id)

    count = 0
    errors = []

    try:
        async for item in adapter.fetch_items():
            saved = store.save_item(item)
            status_ch = "NEW " if saved else "DUP "
            title_trunc = (item.title or "")[:60]
            print(f"  {status_ch}[{item.source}] {title_trunc}")
            count += 1
    except Exception as e:
        errors.append(str(e))
        print(f"\n  ERROR: {e}")

    store.complete_job(job_id, count, 1, errors)

    # Query back
    print(f"\n{'─' * 60}")
    print(f"Stored {count} items ({count - len(errors)} new)")

    rows = store.query_items(limit=5)
    print("\nTop 5 from DB:\n")
    for r in rows:
        print(f"  [{r['source']}] {r['title'][:60]}")
        print(f"    url: {r['url']}")
        print(f"    ingested: {r['ingested_at']}")
        print()

    counts = store.count_items()
    print(f"Total in DB : {counts.get('total', 0)}")
    print(f"By tier     : { {k: v for k, v in counts.items() if k != 'total'} }")

    job = store.get_job(job_id)
    print(f"\nJob status  : {job['status']}")
    print(f"Items       : {job['items_collected']}")
    if job["errors"]:
        print(f"Errors      : {job['errors']}")

    store.close()
    print(f"\n{'=' * 60}")
    print("Test pass complete.")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(main())
