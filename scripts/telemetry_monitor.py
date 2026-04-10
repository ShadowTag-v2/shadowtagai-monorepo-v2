#!/usr/bin/env python3
import lancedb
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
LANCEDB_PATH = REPO_ROOT / "data" / "lancedb" / "workspace_knowledge"


def execute_hardware_telemetry():
    print("======================================================")
    print(" 📡 UPHILL SNOWBALL : LANCED B VECTOR TELEMETRY  ")
    print("======================================================")

    # Evaluate explicit PyArrow physical disk weight
    try:
        size_bytes = sum(f.stat().st_size for f in LANCEDB_PATH.rglob("*") if f.is_file())
        size_mb = size_bytes / (1024 * 1024)
        print(f"Physical macOS Memory Footprint: {size_mb:.2f} MB")
    except Exception as e:
        print(f"[!] Warning: Unable to parse physical bytes: {e}")

    try:
        db = lancedb.connect(str(LANCEDB_PATH))
        table = db.open_table("documents")
        row_count = table.count_rows()
        print(f"Total Structural Arrays Ingested: {row_count} Rows")

        print("\n=> Polling highly-active PM2 HackerNews Worker Egress:")
        try:
            # Polling top 3 trailing documents by ID
            results = table.to_pandas()
            # Because python dataframe doesn't guarantee insertion order natively without timestamps,
            # we simply pull the last 3 rows in the stack
            tail = results.tail(3)
            for idx, row in tail.iterrows():
                short_text = row["text"][:100].replace("\n", " ")
                print(f"   [ID: {row['document_id']}] -> {short_text}...")
        except Exception:
            pass

    except Exception as e:
        print(f"[!] Fatal Vector Sync Error: {e}")

    print("\n[TELEMETRY END]")


if __name__ == "__main__":
    execute_hardware_telemetry()
