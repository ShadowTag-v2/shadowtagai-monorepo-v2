#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
  import yaml  # type: ignore
except Exception:
  yaml = None


def load_yaml(path: Path) -> Any:
  if yaml is None:
    raise RuntimeError(
      "pyyaml is required. Install with: python3 -m pip install pyyaml"
    )
  with path.open("r", encoding="utf-8") as file:
    return yaml.safe_load(file)


def flatten(obj: Any, prefix: str = "") -> dict[str, Any]:
  out: dict[str, Any] = {}
  if isinstance(obj, dict):
    for key, value in obj.items():
      next_key = f"{prefix}.{key}" if prefix else str(key)
      out.update(flatten(value, next_key))
  elif isinstance(obj, list):
    for i, value in enumerate(obj):
      next_key = f"{prefix}[{i}]"
      out.update(flatten(value, next_key))
  else:
    out[prefix] = obj
  return out


def classify_path(path: str) -> str:
  if path.startswith("repo_roots"):
    return "repo_roots"
  if path.startswith("control_plane"):
    return "control_plane"
  if path.startswith("products"):
    return "products"
  if path.startswith("workspace"):
    return "workspace"
  return "other"


def main() -> int:
  parser = argparse.ArgumentParser(
    description="Compare two manifest files and emit a reconcile report"
  )
  parser.add_argument("primary_manifest")
  parser.add_argument("secondary_manifest")
  parser.add_argument("--markdown-out", default=None)
  parser.add_argument("--json-out", default=None)
  args = parser.parse_args()

  primary = Path(args.primary_manifest).expanduser().resolve()
  secondary = Path(args.secondary_manifest).expanduser().resolve()
  data_primary = load_yaml(primary)
  data_secondary = load_yaml(secondary)
  flat_primary = flatten(data_primary)
  flat_secondary = flatten(data_secondary)

  only_primary = sorted(set(flat_primary) - set(flat_secondary))
  only_secondary = sorted(set(flat_secondary) - set(flat_primary))
  differing = sorted(
    key
    for key in set(flat_primary).intersection(flat_secondary)
    if flat_primary[key] != flat_secondary[key]
  )

  classified = []
  for key in differing:
    section = classify_path(key)
    classified.append(
      {
        "path": key,
        "section": section,
        "primary": flat_primary[key],
        "secondary": flat_secondary[key],
        "severity": "critical"
        if section in {"repo_roots", "control_plane"}
        else "medium",
      }
    )

  report = {
    "primary_manifest": str(primary),
    "secondary_manifest": str(secondary),
    "summary": {
      "only_primary": len(only_primary),
      "only_secondary": len(only_secondary),
      "differing": len(differing),
      "critical_drift": sum(1 for item in classified if item["severity"] == "critical"),
    },
    "only_primary": only_primary,
    "only_secondary": only_secondary,
    "differing": classified,
    "recommendation": "Root manifest should remain canonical. Reconcile or retire the second manifest before any large migration or fold-in.",
  }

  if args.json_out:
    Path(args.json_out).write_text(
      json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )

  md_lines = [
    "# Manifest Reconcile Report",
    "",
    f"- Primary: `{primary}`",
    f"- Secondary: `{secondary}`",
    "",
    "## Summary",
    "",
    f"- only in primary: {report['summary']['only_primary']}",
    f"- only in secondary: {report['summary']['only_secondary']}",
    f"- differing keys: {report['summary']['differing']}",
    f"- critical drift items: {report['summary']['critical_drift']}",
    "",
    "## Recommendation",
    "",
    report["recommendation"],
    "",
    "## Differing keys",
    "",
  ]
  if classified:
    for item in classified:
      md_lines.extend(
        [
          f"### `{item['path']}`",
          f"- section: `{item['section']}`",
          f"- severity: `{item['severity']}`",
          f"- primary: `{item['primary']}`",
          f"- secondary: `{item['secondary']}`",
          "",
        ]
      )
  else:
    md_lines.append("No differing keys found.\n")

  markdown = "\n".join(md_lines)
  print(markdown)
  if args.markdown_out:
    Path(args.markdown_out).write_text(markdown + "\n", encoding="utf-8")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
