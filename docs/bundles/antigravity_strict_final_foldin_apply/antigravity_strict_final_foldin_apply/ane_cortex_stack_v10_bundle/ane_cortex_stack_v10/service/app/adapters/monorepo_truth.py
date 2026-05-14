# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


def _safe_read(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")


def read_manifest(path: str) -> dict[str, Any]:
    raw = _safe_read(path)
    if not raw.strip():
        return {"canonical_roots": [], "raw": None}
    try:
        data = yaml.safe_load(raw) or {}
    except Exception:
        data = {}
    canonical_roots = []
    for item in data.get("repos", []) if isinstance(data, dict) else []:
        if item.get("status") == "canonical" or item.get("canonical") is True:
            root = item.get("path") or item.get("root") or item.get("live_root")
            if root:
                canonical_roots.append(root)
    # fallback heuristic: look for apps/pnkln-stack_stack/... paths in raw yaml
    if not canonical_roots:
        canonical_roots = re.findall(r"apps/pnkln-stack_stack/[A-Za-z0-9_\-]+", raw)
    return {"canonical_roots": canonical_roots, "raw": data or raw}


def summarize_merge_status(path: str) -> dict[str, Any]:
    raw = _safe_read(path)
    summary = {
        "canonical_count": None,
        "unresolved_count": None,
        "status_line": None,
        "raw_excerpt": raw[:4000],
    }
    m = re.search(r"(\d+)\s+canonical", raw, re.IGNORECASE)
    if m:
        summary["canonical_count"] = int(m.group(1))
    m = re.search(r"(\d+)\s+unresolved", raw, re.IGNORECASE)
    if m:
        summary["unresolved_count"] = int(m.group(1))
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if lines:
        summary["status_line"] = lines[0]
    return summary


def summarize_control_plane(path: str) -> dict[str, Any]:
    raw = _safe_read(path)
    roots = re.findall(r"apps/pnkln-stack_stack/[A-Za-z0-9_\-]+", raw)
    return {
        "canonical_roots": sorted(list(dict.fromkeys(roots))),
        "raw_excerpt": raw[:4000],
    }


def load_monorepo_truth(
    manifest_path: str, merge_status_path: str, control_plane_path: str
) -> dict[str, Any]:
    manifest = read_manifest(manifest_path)
    merge_status = summarize_merge_status(merge_status_path)
    control_plane = summarize_control_plane(control_plane_path)

    roots = []
    for r in manifest.get("canonical_roots", []):
        if r not in roots:
            roots.append(r)
    for r in control_plane.get("canonical_roots", []):
        if r not in roots:
            roots.append(r)

    return {
        "canonical_repo_roots": roots,
        "merge_status": merge_status,
        "control_plane": control_plane,
        "rule": "Canonical repo-root truth comes from manifest/control-plane docs, not stale local assumptions.",
    }
