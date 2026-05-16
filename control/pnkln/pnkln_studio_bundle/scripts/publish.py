# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Publish manifest with section list and optional extra data to GCS."""

from __future__ import annotations
import time
import json
from .gcs import upload_text

DEFAULT_SECTIONS = [
    "env",
    "pip",
    "vertex",
    "bucket",
    "paths",
    "util",
    "gcs",
    "gem",
    "emb",
    "ocr",
    "ocr_sum",
    "rag_build",
    "rag_query",
    "batch_sum",
    "prompts",
    "runners",
    "imgcap",
    "ocr_dir",
    "io_api",
    "manifest",
    "harvest",
    "publish",
    "mini_demo",
    "end",
]


def publish_manifest(bucket: str, extra: dict | None = None) -> str:
    m = {"sections": DEFAULT_SECTIONS, "ts": int(time.time())}
    if extra:
        m["extra"] = extra
    key = f"manifests/{m['ts']}.json"
    return upload_text(bucket, key, json.dumps(m, separators=(",", ":")), "application/json")
