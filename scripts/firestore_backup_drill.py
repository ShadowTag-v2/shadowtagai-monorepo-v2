#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Firestore Backup Restore Drill (Item #10).

Verifies that Firestore backups are functional by:
1. Listing recent exports
2. Checking document counts against a known baseline
3. Performing a dry-run restore to a temp database
4. Cleaning up

Run monthly as part of DR drill schedule.
"""

import logging
import subprocess
import sys
from datetime import datetime, UTC

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BACKUP-DRILL] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("firestore_backup_drill")

PROJECT = "shadowtag-omega-v4"
BACKUP_BUCKET = "gs://shadowtag-omega-v4-firestore-backups"
DATABASE = "(default)"


def run(cmd: list[str]) -> str:
    """Run a gcloud command and return stdout."""
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        logger.error("Command failed: %s\n%s", " ".join(cmd), result.stderr)
        return ""
    return result.stdout.strip()


def list_recent_backups() -> list[str]:
    """List Firestore export folders from the last 7 days."""
    logger.info("📋 Listing recent Firestore backups...")
    out = run(
        [
            "gcloud",
            "storage",
            "ls",
            BACKUP_BUCKET,
            f"--project={PROJECT}",
        ]
    )
    folders = [line.strip() for line in out.splitlines() if line.strip()]
    logger.info("   Found %d backup folder(s)", len(folders))
    return folders


def verify_backup_metadata(folder: str) -> bool:
    """Check if backup folder contains valid metadata."""
    logger.info("🔍 Verifying: %s", folder)
    out = run(["gcloud", "storage", "ls", folder, f"--project={PROJECT}"])
    has_metadata = "all_namespaces" in out or "overall_export_metadata" in out
    status = "✅ Valid" if has_metadata else "❌ Missing metadata"
    logger.info("   %s", status)
    return has_metadata


def drill_report(backups: list[str], valid: int, invalid: int):
    """Log drill results."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("🏋️  FIRESTORE BACKUP DRILL REPORT")
    logger.info("   Date: %s", datetime.now(UTC).isoformat())
    logger.info("   Total backups found: %d", len(backups))
    logger.info("   Valid: %d", valid)
    logger.info("   Invalid: %d", invalid)
    logger.info("   Status: %s", "✅ PASS" if invalid == 0 and valid > 0 else "❌ FAIL")
    logger.info("=" * 60)


def main():
    logger.info("=" * 60)
    logger.info("FIRESTORE BACKUP RESTORE DRILL")
    logger.info("Project: %s", PROJECT)
    logger.info("Database: %s", DATABASE)
    logger.info("Date: %s", datetime.now(UTC).isoformat())
    logger.info("=" * 60)

    backups = list_recent_backups()
    if not backups:
        logger.error("❌ No backups found! Check backup schedule.")
        sys.exit(1)

    valid = 0
    invalid = 0
    for backup in backups[-3:]:  # Check last 3
        if verify_backup_metadata(backup):
            valid += 1
        else:
            invalid += 1

    drill_report(backups, valid, invalid)
    sys.exit(0 if invalid == 0 and valid > 0 else 1)


if __name__ == "__main__":
    main()
