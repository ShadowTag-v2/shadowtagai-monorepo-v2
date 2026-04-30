import os
import pathlib

ROOT = pathlib.Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")

files = {}

files["scripts/green_loop.py"] = """\
#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
OUT = ROOT / "data" / "green_loop"
OUT.mkdir(parents=True, exist_ok=True)

payload = {
    "status": "ok",
    "system": "green-loop",
    "goal": "patch, verify, summarize, preserve only passing artifacts"
}

(OUT / "latest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps(payload))
"""

files["scripts/drive_ingest_daemon.py"] = """\
#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
OUT = ROOT / "data" / "drive_ingest"
OUT.mkdir(parents=True, exist_ok=True)

state = {
    "status": "ok",
    "system": "drive-ingest-daemon",
    "mode": "placeholder-for-gdrive-langextract-ingest",
    "next": [
        "pull latest docs",
        "extract structured summaries",
        "append to active resources"
    ]
}

(OUT / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
print(json.dumps(state))
"""

files["scripts/retriever_eval.py"] = """\
#!/usr/bin/env python3
from __future__ import annotations

import json

report = {
    "status": "ok",
    "system": "retriever-eval",
    "metrics": {
        "precision_at_5": None,
        "recall_at_10": None,
        "grounding_pass_rate": None
    },
    "note": "wire this to Drive-ingest corpus and CounselConduit retrieval scenarios"
}

print(json.dumps(report, indent=2))
"""

files["scripts/ocr_summary_ingest.py"] = """\
#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
OUT = ROOT / "data" / "ocr"
OUT.mkdir(parents=True, exist_ok=True)

summary = {
    "status": "ok",
    "system": "ocr-summary-ingest",
    "sources": [],
    "note": "attach OCR/image summaries here and feed them through SOP-A triage"
}

(OUT / "latest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary))
"""

files["scripts/subtree_merge_57.py"] = """\
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Iterable

DEFAULT_SRC_ROOT = Path("/Users/pikeymickey/aiyou-stack")
DEFAULT_DST_ROOT = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/aiyou_stack")
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", ".DS_Store"}


def iter_sources(root: Path) -> Iterable[Path]:
    for child in sorted(root.iterdir()):
        if child.name in EXCLUDE_DIRS:
            continue
        yield child


def copy_tree(src: Path, dst: Path) -> dict:
    copied = 0
    skipped = 0
    dst.mkdir(parents=True, exist_ok=True)

    for current_root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        rel_root = Path(current_root).relative_to(src)
        target_root = dst / rel_root
        target_root.mkdir(parents=True, exist_ok=True)

        for name in files:
            if name in EXCLUDE_DIRS:
                skipped += 1
                continue
            s = Path(current_root) / name
            t = target_root / name
            shutil.copy2(s, t)
            copied += 1

    return {
        "source": str(src),
        "destination": str(dst),
        "copied_files": copied,
        "skipped_files": skipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge external trees into monorepo subtree")
    parser.add_argument("--src-root", default=str(DEFAULT_SRC_ROOT))
    parser.add_argument("--dst-root", default=str(DEFAULT_DST_ROOT))
    parser.add_argument("--one", help="Merge only one named child repo/folder from src-root")
    args = parser.parse_args()

    src_root = Path(args.src_root).expanduser().resolve()
    dst_root = Path(args.dst_root).expanduser().resolve()

    if not src_root.exists():
        raise SystemExit(f"missing src root: {src_root}")

    results = []

    if args.one:
        src = src_root / args.one
        if not src.exists():
            raise SystemExit(f"missing requested source: {src}")
        dst = dst_root / args.one
        results.append(copy_tree(src, dst))
    else:
        for src in iter_sources(src_root):
            dst = dst_root / src.name
            if src.is_dir():
                results.append(copy_tree(src, dst))

    print(json.dumps({
        "status": "ok",
        "src_root": str(src_root),
        "dst_root": str(dst_root),
        "merged_count": len(results),
        "results": results
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""

files["scripts/vertex_bootstrap.sh"] = """\
#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-shadowtag-omega-v4}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
MODEL="${GEMINI_MODEL:-gemini-3.1-flash-lite-preview}"

echo "[vertex_bootstrap] project=${PROJECT_ID} region=${REGION} model=${MODEL}"

gcloud services enable aiplatform.googleapis.com compute.googleapis.com >/dev/null 2>&1 || true

echo "[vertex_bootstrap] done"
"""

files["scripts/gemini_stream_test.sh"] = """\
#!/usr/bin/env bash
set -euo pipefail

: "${API_KEY:?API_KEY is required}"

curl "https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-3.1-flash-lite-preview:streamGenerateContent?key=${API_KEY}" \\
  -X POST \\
  -H "Content-Type: application/json" \\
  -d '{
    "contents": [
      {
        "role": "user",
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'
"""

files["scripts/write_updated_pnkln_pack.sh"] = """\
#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
mkdir -p "${ROOT}"

echo "[write_updated_pnkln_pack] write the reconciled pack files here"
echo "[write_updated_pnkln_pack] this script is a placeholder wrapper for the atomic file blocks printed in chat"
"""

for fname, content in files.items():
    if fname.startswith("/"):
        path = pathlib.Path(fname)
    else:
        path = ROOT / fname
    path.write_text(content, encoding="utf-8")
    if fname.endswith(".sh") or fname.endswith(".py"):
        os.chmod(path, 0o755)
    print(f"Wrote {path}")
