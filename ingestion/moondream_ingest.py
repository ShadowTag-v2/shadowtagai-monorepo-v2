# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Moondream Vision Ingestion Pipeline

Processes images/documents with Moondream vision model and outputs structured JSON.
Integrates with safety controls and audit logging.
"""

from __future__ import annotations
import json
import hashlib
import time
from pathlib import Path
from typing import Any
import os

# Placeholder for Moondream integration
# from moondream import Moondream  # Install when package available


def sha256(data: bytes) -> str:
  """Compute SHA-256 hash of data."""
  return hashlib.sha256(data).hexdigest()


def parse_with_moondream(file_path: Path) -> dict[str, Any]:
  """
  Parse a file with Moondream vision model.

  Args:
      file_path: Path to image/PDF file

  Returns:
      Parsed data structure with text, JSON, and metadata
  """
  # PLACEHOLDER: In production, call Moondream model here
  # md = Moondream(model="moondream2")
  # result = md.extract(str(file_path))

  # For now, return placeholder structure
  ext = file_path.suffix.lower()

  if ext in {".txt", ".md", ".csv", ".json"}:
    # Plain text files
    try:
      text = file_path.read_text(encoding="utf-8")
      return {
        "text": text,
        "json": None,
        "meta": {"mode": "plain_text", "encoding": "utf-8"},
      }
    except:
      return {
        "text": "",
        "json": None,
        "meta": {"mode": "error", "error": "Could not read text file"},
      }

  elif ext in {".png", ".jpg", ".jpeg", ".pdf", ".tiff", ".bmp", ".webp"}:
    # Vision processing (placeholder)
    return {
      "text": f"[Placeholder: Moondream would extract text/layout from {file_path.name}]",
      "json": {
        "file_type": ext.lstrip("."),
        "size_bytes": file_path.stat().st_size,
        "placeholder": True,
      },
      "meta": {"mode": "vision_placeholder"},
    }

  else:
    return {"text": "", "json": None, "meta": {"mode": "unsupported", "ext": ext}}


def ingest_directory(root: Path, output: Path, seen_path: Path | None = None) -> int:
  """
  Ingest all supported files from a directory.

  Args:
      root: Root directory to scan
      output: Output JSONL file path
      seen_path: Optional path to seen-hashes file (for deduplication)

  Returns:
      Number of files processed
  """
  # Supported extensions
  exts = {
    ".png",
    ".jpg",
    ".jpeg",
    ".pdf",
    ".tiff",
    ".bmp",
    ".webp",
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".html",
  }

  # Load seen hashes
  seen = set()
  if seen_path and seen_path.exists():
    seen = set(seen_path.read_text(encoding="utf-8").strip().split("\n"))

  # Ensure output directory exists
  output.parent.mkdir(parents=True, exist_ok=True)

  # Process files
  count = 0
  with output.open("a", encoding="utf-8") as out_f:
    for file_path in root.rglob("*"):
      if not file_path.is_file():
        continue
      if file_path.suffix.lower() not in exts:
        continue

      try:
        # Read file and compute hash
        data = file_path.read_bytes()
        h = sha256(data)

        # Skip if already processed
        if h in seen:
          continue

        # Parse with Moondream
        parsed = parse_with_moondream(file_path)

        # Create JSONL record
        rec = {
          "sha256": h,
          "path": str(file_path),
          "ext": file_path.suffix.lower(),
          "size": len(data),
          "mtime": int(file_path.stat().st_mtime),
          "text": parsed.get("text") or "",
          "data": parsed.get("json"),
          "meta": parsed.get("meta") or {},
          "timestamp": int(time.time()),
          "source": "moondream-ingest",
        }

        # Write to output
        out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        out_f.flush()

        # Mark as seen
        seen.add(h)
        count += 1

      except Exception as e:
        print(f"Error processing {file_path}: {e}")
        continue

  # Update seen file
  if seen_path:
    seen_path.write_text("\n".join(sorted(seen)) + "\n", encoding="utf-8")

  return count


def main():
  """CLI entry point for Moondream ingestion."""
  # Configuration from environment
  roots_str = os.environ.get("INGEST_ROOTS", "samples/")
  output_path = Path(os.environ.get("INGEST_OUT", "ingest/out/downloads.jsonl"))
  seen_path = Path(os.environ.get("INGEST_SEEN", "ingest/out/.seen.txt"))

  roots = [Path(r.strip()) for r in roots_str.split(";") if r.strip()]

  total_count = 0
  for root in roots:
    if not root.exists():
      print(f"Warning: {root} does not exist, skipping")
      continue

    print(f"Ingesting from: {root}")
    count = ingest_directory(root, output_path, seen_path)
    total_count += count
    print(f"  → Processed {count} files")

  print(f"\nTotal: {total_count} files ingested")
  print(f"Output: {output_path}")
  print(f"Seen hashes: {seen_path}")


if __name__ == "__main__":
  main()
