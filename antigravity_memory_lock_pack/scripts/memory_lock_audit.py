#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import argparse
import json
import os
import re
from collections.abc import Iterable
from pathlib import Path

CANONICAL_FILES = [
    "monorepo_manifest.yaml",
    "AGENTS.md",
    "antigravity-mcp-config.json",
    "docs/UPDATED_pnkln_PACK.md",
    "docs/MEMORY_LOCK.md",
]

STALE_MODEL_PATTERNS = [
    r"gemini-2\.5",
    r"gemini-3\.1-flash-lite-preview",
    r"gemini-3\.1-pro",
    r"gemini-3\.1-family",
]

PREFERRED_MODEL_FAMILY = "gemini-3.1-family"
MCP_FILES = [
    "antigravity-mcp-config.json",
    "mcp_config.json",
    ".vscode/cline_mcp_settings.json",
]
NAME_PATTERNS = [r"\bpnkln-stack\b", r"\bpnkln-stack\b", r"\bshadowtag-v2\b"]
SECRET_PATTERNS = [
    r"AIza[0-9A-Za-z\-_]{20,}",
    r"-----BEGIN [A-Z ]+PRIVATE KEY-----",
    r"sk-[A-Za-z0-9]{20,}",
]
SKIP_DIRS = {".git", "node_modules", ".venv", "dist", "build", "__pycache__"}
TEXT_EXTS = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".sh",
    ".toml",
    ".env",
    ".example",
    ".cfg",
    ".ini",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
}


def iter_text_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() in TEXT_EXTS or name in {
                "AGENTS.md",
                "monorepo_manifest.yaml",
                "antigravity-mcp-config.json",
                ".env.example",
            }:
                yield path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def find_matches(root: Path, patterns: list[str]) -> list[dict]:
    hits = []
    regexes = [re.compile(p) for p in patterns]
    for path in iter_text_files(root):
        text = read_text(path)
        for rx in regexes:
            for m in rx.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                hits.append(
                    {
                        "file": str(path.relative_to(root)),
                        "line": line_no,
                        "match": m.group(0),
                        "pattern": rx.pattern,
                    }
                )
    return hits


def audit(root: Path) -> dict:
    report = {
        "repo_root": str(root),
        "missing_canonical_files": [f for f in CANONICAL_FILES if not (root / f).exists()],
        "mcp_file_presence": {f: (root / f).exists() for f in MCP_FILES},
        "preferred_model_family": PREFERRED_MODEL_FAMILY,
        "model_mentions": find_matches(root, STALE_MODEL_PATTERNS),
        "stale_naming_mentions": find_matches(root, NAME_PATTERNS),
        "secret_like_mentions": find_matches(root, SECRET_PATTERNS),
    }
    report["status"] = "pass" if not report["missing_canonical_files"] else "warn"
    return report


def to_markdown(report: dict) -> str:
    def block(title: str, rows: list[dict]) -> str:
        out = [f"## {title}"]
        if not rows:
            out.append("None found.")
            return "\n".join(out)
        for row in rows[:200]:
            out.append(f"- `{row['file']}:{row['line']}` → `{row['match']}`")
        return "\n".join(out)

    parts = [
        "# Audit Report",
        f"- repo_root: `{report['repo_root']}`",
        f"- status: `{report['status']}`",
        f"- preferred_model_family: `{report['preferred_model_family']}`",
        "## Missing canonical files",
    ]
    if report["missing_canonical_files"]:
        parts.extend([f"- `{f}`" for f in report["missing_canonical_files"]])
    else:
        parts.append("None.")
    parts.append("## MCP file presence")
    for k, v in report["mcp_file_presence"].items():
        parts.append(f"- `{k}`: `{v}`")
    parts.append(block("Model mentions", report["model_mentions"]))
    parts.append(block("Stale naming mentions", report["stale_naming_mentions"]))
    parts.append(block("Secret-like mentions", report["secret_like_mentions"]))
    return "\n\n".join(parts) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    root = Path(args.repo_root).resolve()
    report = audit(root)
    print(json.dumps(report, indent=2))
    if args.write:
        docs = root / "docs"
        docs.mkdir(exist_ok=True)
        (docs / "AUDIT_REPORT.md").write_text(to_markdown(report), encoding="utf-8")
        (docs / "AUDIT_REPORT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
