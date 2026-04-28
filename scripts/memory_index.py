# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Memory Index — memory_index.py.

Lightweight CLI entrypoint for the Three-Layer Context Memory system.
Delegates to tools/orchestrator/memory_indexer.py.

Usage:
  python scripts/memory_index.py add <file> <start> <end> "summary"
  python scripts/memory_index.py show
  python scripts/memory_index.py clear
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add repo root to path for orchestrator imports
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.orchestrator.memory_indexer import (  # noqa: E402
    clear_hot_context,
    get_hot_context,
    index_file_context,
)


def main() -> None:
    """CLI entrypoint."""
    if len(sys.argv) < 2:
        sys.exit(1)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) < 6:
            sys.exit(1)
        file_path = sys.argv[2]
        start_line = int(sys.argv[3])
        end_line = int(sys.argv[4])
        summary = sys.argv[5]
        tags = sys.argv[6:] if len(sys.argv) > 6 else None

        index_file_context(file_path, start_line, end_line, summary, tags)

    elif command == "show":
        content = get_hot_context()
        if content:
            pass
        else:
            pass

    elif command == "clear":
        clear_hot_context()

    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
