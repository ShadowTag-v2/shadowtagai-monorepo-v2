# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Utility helpers for PNKLN: IO, hashing, compression, cosine similarity."""

from __future__ import annotations
import json
import gzip
import hashlib
from typing import Any
from collections.abc import Iterable
import numpy as np


def json_dumps(x: Any) -> str:
    """Compact JSON serialization."""
    return json.dumps(x, separators=(",", ":"))


def write(path: str, x: Any) -> str:
    """Write bytes/str/obj as bytes to path and return path."""
    if isinstance(x, (bytes, bytearray)):
        data = x
    elif isinstance(x, str):
        data = x.encode()
    else:
        data = json_dumps(x).encode()
    with open(path, "wb") as f:
        f.write(data)
    return path


def read(path: str) -> bytes:
    """Read file as bytes."""
    with open(path, "rb") as f:
        return f.read()


def gz_compress(x: Any) -> bytes:
    """Gzip compress any serializable input."""
    if isinstance(x, (bytes, bytearray)):
        data = x
    elif isinstance(x, str):
        data = x.encode()
    else:
        data = json_dumps(x).encode()
    return gzip.compress(data)


def sha256_short(x: Any) -> str:
    """First 16 hex chars of sha256 for content addressing."""
    if not isinstance(x, (bytes, bytearray)):
        x = x.encode() if isinstance(x, str) else json_dumps(x).encode()
    return hashlib.sha256(x).hexdigest()[:16]


def cosine(a: Iterable[float], b: Iterable[float]) -> float:
    """Cosine similarity between 1-D vectors."""
    a = np.asarray(list(a))
    b = np.asarray(list(b))
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-9
    return float(a.dot(b) / denom)
