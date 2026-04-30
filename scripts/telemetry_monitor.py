#!/usr/bin/env python3
from pathlib import Path

import lancedb

REPO_ROOT = Path(__file__).parent.parent
LANCEDB_PATH = REPO_ROOT / "data" / "lancedb" / "workspace_knowledge"


def execute_hardware_telemetry() -> None:
    # Evaluate explicit PyArrow physical disk weight
    try:
        size_bytes = sum(f.stat().st_size for f in LANCEDB_PATH.rglob("*") if f.is_file())
        size_bytes / (1024 * 1024)
    except Exception:
        pass

    try:
        db = lancedb.connect(str(LANCEDB_PATH))
        table = db.open_table("documents")
        table.count_rows()

        try:
            # Polling top 3 trailing documents by ID
            results = table.to_pandas()
            # Because python dataframe doesn't guarantee insertion order natively without timestamps,
            # we simply pull the last 3 rows in the stack
            tail = results.tail(3)
            for _idx, row in tail.iterrows():
                row["text"][:100].replace("\n", " ")
        except Exception:
            pass

    except Exception:
        pass


if __name__ == "__main__":
    execute_hardware_telemetry()
