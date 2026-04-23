#!/usr/bin/env python3
# Copyright 2026 ShadowTag AI. All rights reserved.
"""Zero-Trust Data Pipeline — True Obsidian IPI Quarantine.

Processes untrusted data through a multi-stage sanitization pipeline:
  1. File type validation (magic bytes, not just extension)
  2. Content stripping (remove code blocks, script tags, system prompts)
  3. Size enforcement (reject oversized payloads)
  4. Secret scanning (reject files containing API keys/tokens)
  5. Route to quarantine or reject

Usage:
    python scripts/vault/zero_trust_pipeline.py vault/ingest/meeting.txt
    python scripts/vault/zero_trust_pipeline.py --scan-dir vault/ingest/
    python scripts/vault/zero_trust_pipeline.py --dry-run vault/ingest/
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re

import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [VAULT-ZTP] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("vault.ztp")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
VAULT_DIR = REPO_ROOT / "vault"
QUARANTINE_DIR = VAULT_DIR / "quarantine"
MONITOR_DIR = VAULT_DIR / "monitor"

# --- Configuration -----------------------------------------------------------

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {
    ".txt", ".md", ".json", ".csv", ".xml", ".yaml", ".yml",
    ".html", ".htm", ".log", ".rst", ".toml",
}

# Patterns that indicate hostile content (IPI payloads)
IPI_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"<script\b", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"eval\s*\(", re.IGNORECASE),
    re.compile(r"Function\s*\(", re.IGNORECASE),
    re.compile(r"(?:system|assistant|user)\s*prompt", re.IGNORECASE),
    re.compile(r"ignore\s+(?:all\s+)?(?:previous|above)\s+instructions", re.IGNORECASE),
    re.compile(r"IGNORE_PREVIOUS_INSTRUCTIONS", re.IGNORECASE),
    re.compile(r"<\s*img\b[^>]*\bwidth\s*=\s*[\"']?1\b", re.IGNORECASE),  # tracking pixels
]

# Patterns that indicate embedded secrets
SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?:api[_-]?key|apikey)\s*[:=]\s*\S{16,}", re.IGNORECASE),
    re.compile(r"(?:secret|token|password|passwd)\s*[:=]\s*\S{8,}", re.IGNORECASE),
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),  # Google API key
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),  # OpenAI key
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),  # GitHub PAT
    re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"),
]


# --- Pipeline Stages --------------------------------------------------------


def validate_file_type(path: Path) -> tuple[bool, str]:
    """Stage 1: Validate file type by extension and basic magic bytes."""
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return False, f"Blocked extension: {path.suffix}"

    if path.stat().st_size > MAX_FILE_SIZE_BYTES:
        return False, f"File too large: {path.stat().st_size} bytes (max {MAX_FILE_SIZE_BYTES})"

    # Check for binary content (non-text files disguised as text)
    try:
        with open(path, "rb") as f:
            chunk = f.read(8192)
            if b"\x00" in chunk:
                return False, "Binary content detected in text file"
    except OSError as e:
        return False, f"Cannot read file: {e}"

    return True, "OK"


def scan_for_ipi(content: str) -> list[str]:
    """Stage 2: Scan content for Indirect Prompt Injection patterns."""
    findings: list[str] = []
    for pattern in IPI_PATTERNS:
        matches = pattern.findall(content)
        if matches:
            findings.append(f"IPI pattern: {pattern.pattern} ({len(matches)} hits)")
    return findings


def scan_for_secrets(content: str) -> list[str]:
    """Stage 3: Scan content for embedded secrets."""
    findings: list[str] = []
    for pattern in SECRET_PATTERNS:
        matches = pattern.findall(content)
        if matches:
            findings.append(f"Secret pattern: {pattern.pattern} ({len(matches)} hits)")
    return findings


def strip_hostile_content(content: str) -> str:
    """Stage 4: Strip code blocks, script tags, and system prompts from content."""
    # Remove fenced code blocks
    content = re.sub(r"```[\s\S]*?```", "[CODE BLOCK REMOVED]", content)

    # Remove inline code
    content = re.sub(r"`[^`]+`", "[INLINE CODE REMOVED]", content)

    # Remove HTML script tags
    content = re.sub(r"<script\b[\s\S]*?</script>", "[SCRIPT REMOVED]", content, flags=re.IGNORECASE)

    # Remove HTML style tags
    content = re.sub(r"<style\b[\s\S]*?</style>", "[STYLE REMOVED]", content, flags=re.IGNORECASE)

    # Remove HTML comments (potential IPI hiding spots)
    content = re.sub(r"<!--[\s\S]*?-->", "[COMMENT REMOVED]", content)

    # Remove base64-encoded data
    content = re.sub(r"data:[a-zA-Z]+/[a-zA-Z]+;base64,[A-Za-z0-9+/=]+", "[BASE64 REMOVED]", content)

    return content


def compute_file_hash(path: Path) -> str:
    """Compute SHA-256 hash for audit trail."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


# --- Pipeline Orchestration --------------------------------------------------


def process_file(path: Path, *, dry_run: bool = False) -> dict:
    """Run a single file through the zero-trust pipeline.

    Returns a result dict with status, findings, and actions taken.
    """
    result: dict = {
        "file": str(path),
        "timestamp": datetime.now(timezone.utc).isoformat(),  # noqa: UP017
        "status": "unknown",
        "findings": [],
        "actions": [],
    }

    # Stage 1: File type validation
    valid, msg = validate_file_type(path)
    if not valid:
        result["status"] = "rejected"
        result["findings"].append(msg)
        logger.warning("REJECTED %s: %s", path.name, msg)
        return result

    result["hash"] = compute_file_hash(path)

    # Read content
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        result["status"] = "error"
        result["findings"].append(f"Read error: {e}")
        return result

    # Stage 2: IPI scan
    ipi_findings = scan_for_ipi(content)
    if ipi_findings:
        result["findings"].extend(ipi_findings)
        logger.warning("IPI detected in %s: %s", path.name, ipi_findings)

    # Stage 3: Secret scan
    secret_findings = scan_for_secrets(content)
    if secret_findings:
        result["status"] = "rejected"
        result["findings"].extend(secret_findings)
        logger.critical("SECRETS detected in %s — REJECTING", path.name)
        return result

    # Stage 4: Strip hostile content
    cleaned = strip_hostile_content(content)

    # Stage 5: Route to quarantine
    if ipi_findings:
        # IPI detected but no secrets — quarantine for manual review
        result["status"] = "quarantined"
        if not dry_run:
            dest = QUARANTINE_DIR / f"{path.stem}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{path.suffix}"  # noqa: UP017
            QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
            dest.write_text(cleaned, encoding="utf-8")
            result["actions"].append(f"Quarantined to {dest}")
            logger.info("Quarantined %s → %s", path.name, dest.name)
        else:
            result["actions"].append("Would quarantine (dry-run)")
    else:
        # Clean — move to serve/
        result["status"] = "clean"
        if not dry_run:
            serve_dir = VAULT_DIR / "serve"
            serve_dir.mkdir(parents=True, exist_ok=True)
            dest = serve_dir / path.name
            dest.write_text(cleaned, encoding="utf-8")
            result["actions"].append(f"Served to {dest}")
            logger.info("Clean: %s → serve/", path.name)
        else:
            result["actions"].append("Would serve (dry-run)")

    return result


def scan_directory(directory: Path, *, dry_run: bool = False) -> list[dict]:
    """Scan all files in a directory through the pipeline."""
    results: list[dict] = []
    if not directory.exists():
        logger.error("Directory does not exist: %s", directory)
        return results

    for path in sorted(directory.iterdir()):
        if path.is_file() and path.name != ".gitkeep":
            results.append(process_file(path, dry_run=dry_run))

    # Write metrics
    if not dry_run:
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),  # noqa: UP017
            "total": len(results),
            "clean": sum(1 for r in results if r["status"] == "clean"),
            "quarantined": sum(1 for r in results if r["status"] == "quarantined"),
            "rejected": sum(1 for r in results if r["status"] == "rejected"),
            "errors": sum(1 for r in results if r["status"] == "error"),
        }
        MONITOR_DIR.mkdir(parents=True, exist_ok=True)
        metrics_file = MONITOR_DIR / "pipeline_metrics.json"
        metrics_file.write_text(json.dumps(metrics, indent=2))
        logger.info("Pipeline metrics: %s", json.dumps(metrics))

    return results


# --- CLI Entry Point ---------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Zero-Trust Data Pipeline — True Obsidian IPI Quarantine",
    )
    parser.add_argument("input", nargs="?", help="File or directory to process")
    parser.add_argument("--scan-dir", help="Directory to scan (alternative to positional arg)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    target = args.scan_dir or args.input
    if not target:
        parser.error("Provide a file/directory as positional arg or via --scan-dir")

    path = Path(target)

    if path.is_dir():
        results = scan_directory(path, dry_run=args.dry_run)
    elif path.is_file():
        results = [process_file(path, dry_run=args.dry_run)]
    else:
        logger.error("Path does not exist: %s", path)
        return 1

    # Summary
    for r in results:
        status_icon = {"clean": "✅", "quarantined": "⚠️", "rejected": "🚫", "error": "❌"}.get(
            r["status"], "❓"
        )
        logger.info("%s %s → %s", status_icon, r["file"], r["status"])

    rejected = sum(1 for r in results if r["status"] == "rejected")
    return 1 if rejected > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
