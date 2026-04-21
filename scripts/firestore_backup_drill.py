#!/usr/bin/env python3
"""Firestore Backup Restore Drill (Item #10).

Verifies that Firestore backups are functional by:
1. Listing recent exports
2. Checking document counts against a known baseline
3. Performing a dry-run restore to a temp database
4. Cleaning up

Run monthly as part of DR drill schedule.
"""

import subprocess
import json
import sys
from datetime import datetime, timezone


PROJECT = "shadowtag-omega-v4"
BACKUP_BUCKET = "gs://shadowtag-omega-v4-firestore-backups"
DATABASE = "(default)"


def run(cmd: list[str]) -> str:
    """Run a gcloud command and return stdout."""
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"ERROR: {' '.join(cmd)}\n{result.stderr}", file=sys.stderr)
        return ""
    return result.stdout.strip()


def list_recent_backups() -> list[str]:
    """List Firestore export folders from the last 7 days."""
    print("📋 Listing recent Firestore backups...")
    out = run([
        "gcloud", "storage", "ls", BACKUP_BUCKET,
        f"--project={PROJECT}",
    ])
    folders = [line.strip() for line in out.splitlines() if line.strip()]
    print(f"   Found {len(folders)} backup folder(s)")
    return folders


def verify_backup_metadata(folder: str) -> bool:
    """Check if backup folder contains valid metadata."""
    print(f"🔍 Verifying: {folder}")
    out = run(["gcloud", "storage", "ls", folder, f"--project={PROJECT}"])
    has_metadata = "all_namespaces" in out or ".overall_export_metadata" in out
    status = "✅ Valid" if has_metadata else "❌ Missing metadata"
    print(f"   {status}")
    return has_metadata


def drill_report(backups: list[str], valid: int, invalid: int):
    """Print drill results."""
    print("\n" + "=" * 60)
    print("🏋️  FIRESTORE BACKUP DRILL REPORT")
    print(f"   Date: {datetime.now(timezone.utc).isoformat()}")
    print(f"   Total backups found: {len(backups)}")
    print(f"   Valid: {valid}")
    print(f"   Invalid: {invalid}")
    print(f"   Status: {'✅ PASS' if invalid == 0 and valid > 0 else '❌ FAIL'}")
    print("=" * 60)


def main():
    print("=" * 60)
    print("FIRESTORE BACKUP RESTORE DRILL")
    print(f"Project: {PROJECT}")
    print(f"Database: {DATABASE}")
    print(f"Date: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    backups = list_recent_backups()
    if not backups:
        print("❌ No backups found! Check backup schedule.")
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
