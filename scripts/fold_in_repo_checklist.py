#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

STALE_MODEL_PATTERNS = [
    r"gemini-2\.5[\w.-]*",
    r"gemini-3\.1-flash-lite-preview",
]

CURRENT_MODEL_HINT = "gemini-3.1-family"

STALE_MCP_PATTERNS = [
    r"mcp_config\.json",
    r"cline_mcp_settings\.json",
    r"shadowtag-omega-v4",
    r"shadowtag-v2",
]

STALE_NAMING_PATTERNS = [
    r"\bShadowTag-v2\b",
    r"\bShadowTag\b",
    r"\bShadowTag-v2\b",
    r"\bshadowtag-v2\b",
    r"\bflash-lite-preview\b",
]

SECRET_PATTERNS = [
    r"AIza[0-9A-Za-z\-_]{20,}",
    r"sk-[A-Za-z0-9]{20,}",
    r"-----BEGIN (?:RSA|EC|OPENSSH|PRIVATE) KEY-----",
    r"X-Goog-Api-Key:\s*[A-Za-z0-9\-_]{20,}",
]

TEXT_EXTS = {
    ".py",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".sh",
    ".bash",
    ".zsh",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".env",
    ".cfg",
    ".ini",
    ".bazel",
    ".bzl",
    "",
}

IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".next",
    ".idea",
    ".vscode",
}


@dataclass
class Finding:
    kind: str
    severity: str
    path: str
    detail: str


def load_yaml(path: Path) -> Any:
    if yaml is None:
        raise RuntimeError("pyyaml is required for manifest-aware checks. Install with: python3 -m pip install pyyaml")
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def find_manifest_paths(monorepo_root: Path) -> list[Path]:
    candidates = []
    for rel in ["monorepo_manifest.yaml", "manifests/monorepo_manifest.yaml"]:
        path = monorepo_root / rel
        if path.exists():
            candidates.append(path)
    return candidates


def canonical_destinations(root_manifest: dict[str, Any]) -> set[str]:
    repo_roots = root_manifest.get("repo_roots", {}) or {}
    out: set[str] = set()
    for _, meta in repo_roots.items():
        if isinstance(meta, dict):
            canonical_path = meta.get("canonical_path")
            if isinstance(canonical_path, str) and canonical_path.strip():
                out.add(canonical_path.strip().strip("/"))
    return out


def file_text(path: Path) -> str | None:
    try:
        if path.suffix.lower() not in TEXT_EXTS and path.name not in {
            ".env",
            ".gitignore",
            "BUILD",
            "WORKSPACE",
        }:
            return None
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


def iter_text_files(root: Path):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for name in files:
            path = Path(base) / name
            if path.suffix.lower() in TEXT_EXTS or name in {
                ".env",
                ".gitignore",
                "BUILD",
                "WORKSPACE",
            }:
                yield path


def search_patterns(root: Path, patterns: list[str], kind: str, severity: str, detail_prefix: str) -> list[Finding]:
    findings: list[Finding] = []
    compiled = [re.compile(p) for p in patterns]
    for path in iter_text_files(root):
        text = file_text(path)
        if not text:
            continue
        for rx in compiled:
            match = rx.search(text)
            if match:
                rel = str(path.relative_to(root))
                findings.append(Finding(kind, severity, rel, f"{detail_prefix}: {match.group(0)[:160]}"))
                break
    return findings


def find_nested_git_dirs(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in root.rglob(".git"):
        if path.parent == root:
            continue
        findings.append(
            Finding(
                "nested_git",
                "high",
                str(path.parent.relative_to(root)),
                "Nested .git directory detected; subtree may be a repo, not a fold-in.",
            )
        )
    return findings


def compare_manifests(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    if len(paths) <= 1:
        return findings
    loaded = []
    for path in paths:
        try:
            loaded.append((path, load_yaml(path)))
        except Exception as exc:
            findings.append(Finding("manifest_parse", "high", str(path), f"Failed to parse manifest: {exc}"))
            return findings
    first_path, first_doc = loaded[0]
    for path, doc in loaded[1:]:
        if doc != first_doc:
            findings.append(
                Finding(
                    "manifest_split_brain",
                    "critical",
                    f"{first_path.name} <> {path.relative_to(path.parent.parent if path.parent.name == 'manifests' else path.parent)}",
                    "Multiple manifest surfaces disagree. Reconcile before any fold-in or path migration.",
                )
            )
    return findings


def check_destination_conflict(dest_rel: str, manifest_paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    if not manifest_paths:
        findings.append(
            Finding(
                "manifest_missing",
                "high",
                "monorepo_manifest.yaml",
                "No manifest found at monorepo root; destination conflict checks are incomplete.",
            )
        )
        return findings
    try:
        root_manifest = load_yaml(manifest_paths[0])
    except Exception as exc:
        findings.append(Finding("manifest_parse", "high", str(manifest_paths[0]), f"Failed to parse manifest: {exc}"))
        return findings
    destinations = canonical_destinations(root_manifest)
    norm = dest_rel.strip().strip("/")
    if norm in destinations:
        findings.append(
            Finding(
                "destination_conflict",
                "critical",
                norm,
                "Destination already declared canonical in manifest. Fold-in must be merge-aware, not a blind copy.",
            )
        )
    return findings


def summarize(findings: list[Finding]) -> dict[str, int]:
    out = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for finding in findings:
        out[finding.severity] = out.get(finding.severity, 0) + 1
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Manifest-aware repo fold-in preflight checker")
    parser.add_argument("repo_name")
    parser.add_argument("incoming_repo")
    parser.add_argument("dest_rel")
    parser.add_argument("--monorepo-root", required=True)
    parser.add_argument("--out", default=None, help="Write JSON report to this path")
    args = parser.parse_args()

    incoming = Path(args.incoming_repo).expanduser().resolve()
    monorepo_root = Path(args.monorepo_root).expanduser().resolve()

    if not incoming.exists():
        print(f"ERROR: incoming repo missing: {incoming}", file=sys.stderr)
        return 2
    if not monorepo_root.exists():
        print(f"ERROR: monorepo root missing: {monorepo_root}", file=sys.stderr)
        return 2

    manifest_paths = find_manifest_paths(monorepo_root)
    findings: list[Finding] = []
    findings.extend(compare_manifests(manifest_paths))
    findings.extend(check_destination_conflict(args.dest_rel, manifest_paths))
    findings.extend(find_nested_git_dirs(incoming))
    findings.extend(
        search_patterns(
            incoming,
            STALE_MODEL_PATTERNS,
            "stale_model",
            "high",
            f"Stale model reference; migrate to {CURRENT_MODEL_HINT}",
        )
    )
    findings.extend(search_patterns(incoming, STALE_MCP_PATTERNS, "stale_mcp", "medium", "Stale MCP/control-plane reference"))
    findings.extend(
        search_patterns(
            incoming,
            STALE_NAMING_PATTERNS,
            "stale_naming",
            "medium",
            "Stale naming/control-plane drift",
        )
    )
    findings.extend(
        search_patterns(
            incoming,
            SECRET_PATTERNS,
            "secret_like",
            "critical",
            "Potential secret material detected",
        )
    )

    report = {
        "repo_name": args.repo_name,
        "incoming_repo": str(incoming),
        "monorepo_root": str(monorepo_root),
        "destination": args.dest_rel,
        "manifest_paths": [str(p) for p in manifest_paths],
        "summary": summarize(findings),
        "blocked": any(f.severity in {"critical", "high"} for f in findings),
        "findings": [asdict(f) for f in findings],
    }

    payload = json.dumps(report, indent=2)
    print(payload)
    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
