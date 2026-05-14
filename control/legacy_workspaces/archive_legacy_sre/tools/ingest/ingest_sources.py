#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import hashlib
import json
import pathlib
from datetime import datetime, timezone, UTC

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "raw"
PROV_DIR = ROOT / "data" / "provenance"
ALLOWED_SOURCES = {"upload", "github", "web", "video_transcript", "doc_portal", "other"}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def ensure_dirs():
    (OUT_DIR).mkdir(parents=True, exist_ok=True)
    (PROV_DIR).mkdir(parents=True, exist_ok=True)


def write_blob(name: str, content: bytes, meta: dict):
    h = sha256_bytes(content)
    blob = OUT_DIR / f"{h[:16]}_{name}"
    if not blob.exists():
        blob.write_bytes(content)
    prov = {
        "source": meta.get("source", "other"),
        "uri": meta.get("uri", ""),
        "collected_at": now_iso(),
        "hash_sha256": h,
        "license": meta.get("license", "unknown"),
        "license_notes": meta.get("license_notes", ""),
        "pii_flag": bool(meta.get("pii_flag", False)),
        "pii_notes": meta.get("pii_notes", ""),
        "confidence": float(meta.get("confidence", 0.9)),
        "tags": meta.get("tags", []),
        "owner": meta.get("owner", ""),
        "doc_type": meta.get("doc_type", ""),
        "lang": meta.get("lang", ""),
    }
    (PROV_DIR / f"{h}.json").write_text(json.dumps(prov, indent=2), encoding="utf-8")
    return h


def ingest_sample():
    content = b"example: replace with real fetchers (github, yt transcripts, docs, etc.)"
    meta = {"source": "other", "uri": "inline://example", "license": "permissive", "tags": ["sample"]}
    h = write_blob("sample.txt", content, meta)
    print(f"[INGEST] wrote {h}")


def main():
    ensure_dirs()
    ingest_sample()


if __name__ == "__main__":
    main()
