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
    # Single canonical root model: read canonical-root key first
    if isinstance(data, dict) and data.get("canonical-root"):
        return {"canonical_roots": [data["canonical-root"]], "raw": data}
    # Legacy: scan repo_roots for status: canonical (folded-in components, not root truth)
    canonical_roots = []
    for item in data.get("repos", []) if isinstance(data, dict) else []:
        if item.get("status") == "canonical" or item.get("canonical") is True:
            root = item.get("path") or item.get("root") or item.get("live_root")
            if root:
                canonical_roots.append(root)
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
    # Single-root model: look for canonical-root declaration
    m = re.search(r"canonical[-_]root[:\s]+([^\s\n]+)", raw)
    canonical_root = m.group(1).strip() if m else None
    return {
        "canonical_root": canonical_root,
        "canonical_roots": [canonical_root] if canonical_root else [],
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
        "canonical_root": roots[0] if roots else None,
        "canonical_repo_roots": roots,
        "merge_status": merge_status,
        "control_plane": control_plane,
        "rule": "ShadowTag-v2/Monorepo-Uphillsnowball is the one canonical root. "
        "ShadowTag-v2_stack/* are folded-in components, not root peers.",
    }
