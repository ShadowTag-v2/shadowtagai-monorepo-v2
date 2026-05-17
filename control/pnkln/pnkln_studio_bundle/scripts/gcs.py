# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""GCS helpers for PNKLN: simple upload/download/list."""

from __future__ import annotations
from google.cloud import storage


def client(project: str | None = None) -> storage.Client:
  return storage.Client(project=project) if project else storage.Client()


def bucket(name: str, project: str | None = None) -> storage.Bucket:
  return client(project).bucket(name)


def upload_bytes(
  bkt: str, key: str, data: bytes, content_type: str = "application/octet-stream"
) -> str:
  b = bucket(bkt).blob(key)
  b.upload_from_string(data, content_type)
  return f"gs://{bkt}/{key}"


def upload_text(bkt: str, key: str, text: str, content_type: str = "text/plain") -> str:
  return upload_bytes(bkt, key, text.encode(), content_type)


def download_bytes(bkt: str, key: str) -> bytes:
  return bucket(bkt).blob(key).download_as_bytes()


def list_keys(bkt: str, prefix: str = "") -> list[str]:
  return [b.name for b in bucket(bkt).list_blobs(prefix=prefix)]
