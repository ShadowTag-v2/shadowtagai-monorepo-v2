#!/usr/bin/env python3
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
        raise RuntimeError("pyyaml is required. Install with: python3 -m pip install pyyaml")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def flatten(obj: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            out.update(flatten(v, key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            key = f"{prefix}[{i}]"
            out.update(flatten(v, key))
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
    ap = argparse.ArgumentParser(
        description="Compare two manifest files and emit a reconcile report"
    )
    ap.add_argument("primary_manifest")
    ap.add_argument("secondary_manifest")
    ap.add_argument("--markdown-out", default=None)
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    p1 = Path(args.primary_manifest).expanduser().resolve()
    p2 = Path(args.secondary_manifest).expanduser().resolve()
    d1 = load_yaml(p1)
    d2 = load_yaml(p2)
    f1 = flatten(d1)
    f2 = flatten(d2)

    only_primary = sorted(set(f1) - set(f2))
    only_secondary = sorted(set(f2) - set(f1))
    differing = sorted(k for k in set(f1).intersection(f2) if f1[k] != f2[k])

    classified = []
    for key in differing:
        classified.append(
            {
                "path": key,
                "section": classify_path(key),
                "primary": f1[key],
                "secondary": f2[key],
                "severity": "critical"
                if classify_path(key) in {"repo_roots", "control_plane"}
                else "medium",
            }
        )

    report = {
        "primary_manifest": str(p1),
        "secondary_manifest": str(p2),
        "summary": {
            "only_primary": len(only_primary),
            "only_secondary": len(only_secondary),
            "differing": len(differing),
            "critical_drift": sum(1 for x in classified if x["severity"] == "critical"),
        },
        "only_primary": only_primary,
        "only_secondary": only_secondary,
        "differing": classified,
        "recommendation": "Root manifest should remain canonical. Reconcile or retire the second manifest before any large migration or fold-in.",
    }

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# Manifest Reconcile Report",
        "",
        f"- Primary: `{p1}`",
        f"- Secondary: `{p2}`",
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
