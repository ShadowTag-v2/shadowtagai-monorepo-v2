#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import collections
import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
METRICS_FILE = REPO_ROOT / ".ci" / "metrics.jsonl"
SUMMARY_FILE = REPO_ROOT / ".ci" / "metrics_summary.md"


def main() -> int:
  by_model = collections.Counter()
  total_tokens = 0
  notes = collections.Counter()
  if METRICS_FILE.exists():
    with METRICS_FILE.open(encoding="utf-8") as f:
      for line in f:
        try:
          row = json.loads(line)
        except Exception:
          continue
        by_model[row.get("model", "?")] += 1
        total_tokens += int(row.get("prompt_tokens", 0)) + int(row.get("resp_max", 0))
        n = row.get("note")
        if n:
          notes[n] += 1
  md = [
    "## AI Autofix Token Metrics",
    "",
    f"Total calls: {sum(by_model.values())}",
    f"Total token budget used (approx): {total_tokens}",
    "",
    "### Calls by model:",
  ]
  for m, c in by_model.most_common():
    md.append(f"- {m}: {c}")
  if notes:
    md.extend(["", "### Notes:"])
    for n, c in notes.most_common():
      md.append(f"- {n}: {c}")
  SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
  SUMMARY_FILE.write_text("\n".join(md) + "\n", encoding="utf-8")
  print(SUMMARY_FILE.read_text(encoding="utf-8"))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
