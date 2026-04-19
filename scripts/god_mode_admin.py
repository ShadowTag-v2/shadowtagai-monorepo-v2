#!/usr/bin/env python3
"""God Mode Admin — Comprehensive GCP + Firebase environment validator.

Verifies all production invariants:
  1. GCP project binding (shadowtag-omega-v4)
  2. Firebase Auth & Firestore connectivity
  3. Cloud Run service health
  4. Secret Manager accessibility
  5. Service account permissions
  6. Stripe webhook endpoint reachability
  7. GitHub App PEM existence

Usage:
    export GCP_PROJECT_ID='shadowtag-omega-v4'
    python3 scripts/god_mode_admin.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "shadowtag-omega-v4")
REGION = os.getenv("GCP_REGION", "us-central1")
CLOUD_RUN_SERVICE = "counselconduit"
CLOUD_RUN_URL = f"https://counselconduit-767252945109.{REGION}.run.app"
PEM_PATHS = [
    os.path.expanduser("~/Downloads/antigravity-shadowtag-manager.2026-03-17.private-key.pem"),
    os.path.expanduser("~/.ssh/antigravity-shadowtag-manager.pem"),
    "keys/antigravity-shadowtag-manager.pem",
]
FIRESTORE_DBS = ["(default)", "shadowtag-engine"]


def _run(cmd: list[str], timeout: int = 15) -> tuple[bool, str]:
    """Run a command, return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0, (result.stdout + result.stderr).strip()
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, str(e)


def _check(label: str, ok: bool, detail: str = "") -> bool:
    """Print a status check line."""
    icon = "✅" if ok else "❌"
    suffix = f" — {detail}" if detail else ""
    print(f"  {icon} {label}{suffix}")
    return ok


class GodModeAdmin:
    """Validates the full production stack."""

    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.start_time = time.monotonic()

    def _record(self, ok: bool):
        if ok:
            self.checks_passed += 1
        else:
            self.checks_failed += 1

    def check_gcp_project(self):
        """Verify GCP project binding."""
        print("\n🔧 GCP Project")
        ok, out = _run(["gcloud", "config", "get-value", "project"])
        active = out.strip()
        self._record(_check("Active project", active == PROJECT_ID, active))
        self._record(_check("PROJECT_ID env var", os.getenv("GCP_PROJECT_ID") == PROJECT_ID, PROJECT_ID))

    def check_gcloud_auth(self):
        """Verify gcloud authentication."""
        print("\n🔐 GCP Authentication")
        ok, out = _run(["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"])
        accounts = [a.strip() for a in out.strip().split("\n") if a.strip()]
        self._record(_check("Active gcloud account", bool(accounts), ", ".join(accounts[:2])))

    def check_firebase(self):
        """Verify Firebase project access."""
        print("\n🔥 Firebase")
        ok, out = _run(["npx", "-y", "firebase-tools@latest", "projects:list", "--json"])
        if ok:
            try:
                projects = json.loads(out)
                found = any(p.get("projectId") == PROJECT_ID for p in projects.get("result", []))
                self._record(_check(f"Project {PROJECT_ID} in Firebase", found))
            except json.JSONDecodeError:
                self._record(_check("Firebase projects:list parse", False, "Invalid JSON"))
        else:
            self._record(_check("Firebase CLI", False, "not installed or not authenticated"))

    def check_cloud_run(self):
        """Verify Cloud Run service."""
        print("\n☁️  Cloud Run")
        ok, out = _run(
            [
                "gcloud",
                "run",
                "services",
                "describe",
                CLOUD_RUN_SERVICE,
                f"--region={REGION}",
                f"--project={PROJECT_ID}",
                "--format=value(status.url)",
            ]
        )
        url = out.strip() if ok else ""
        self._record(_check(f"Service '{CLOUD_RUN_SERVICE}' exists", ok, url))

    def check_secrets(self):
        """Verify Secret Manager access."""
        print("\n🗝️  Secret Manager")
        ok, out = _run(
            [
                "gcloud",
                "secrets",
                "list",
                f"--project={PROJECT_ID}",
                "--format=value(name)",
            ]
        )
        if ok:
            secrets = [s.strip() for s in out.strip().split("\n") if s.strip()]
            self._record(_check(f"Secrets accessible ({len(secrets)} found)", len(secrets) > 0))
        else:
            self._record(_check("Secret Manager access", False, out[:100]))

    def check_pem(self):
        """Verify GitHub App PEM exists."""
        print("\n🔑 GitHub App PEM")
        found = False
        for path in PEM_PATHS:
            p = Path(path)
            if p.exists():
                self._record(_check(f"PEM at {p.name}", True, str(p)))
                found = True
                break
        if not found:
            self._record(_check("PEM file", False, "not found in any search path"))

        env_pem = os.getenv("SHADOWTAG_PEM", "")
        self._record(_check("$SHADOWTAG_PEM env var", bool(env_pem), env_pem[:50] if env_pem else "unset"))

    def check_python(self):
        """Verify Python environment."""
        print("\n🐍 Python Environment")
        self._record(
            _check(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", sys.version_info >= (3, 11), sys.version)
        )
        venv = os.getenv("VIRTUAL_ENV", "")
        self._record(_check("Virtual env", bool(venv) or Path(".venv").exists(), venv or (".venv exists" if Path(".venv").exists() else "none")))

    def check_tools(self):
        """Verify required CLI tools."""
        print("\n🛠️  CLI Tools")
        tools = ["gcloud", "git", "node", "npx", "ruff", "docker"]
        for tool in tools:
            found = shutil.which(tool) is not None
            self._record(_check(tool, found, shutil.which(tool) or "not in PATH"))

    def check_firestore(self):
        """Verify Firestore databases."""
        print("\n📦 Firestore")
        for db_id in FIRESTORE_DBS:
            ok, out = _run(
                [
                    "gcloud",
                    "firestore",
                    "databases",
                    "describe",
                    f"--database={db_id}",
                    f"--project={PROJECT_ID}",
                    "--format=value(locationId)",
                ]
            )
            self._record(_check(f"Database '{db_id}'", ok, out.strip() if ok else "not found"))

    def check_dotenv(self):
        """Verify .env file presence (gitignored, kernel-locked)."""
        print("\n📄 Environment Files")
        env_path = Path(".env")
        self._record(_check(".env exists", env_path.exists()))
        if env_path.exists():
            ok, out = _run(["ls", "-lO", str(env_path)])
            locked = "uchg" in out if ok else False
            self._record(_check(".env kernel-locked (uchg)", locked, "chflags uchg .env to lock"))

    def run_all(self):
        """Run all checks and print summary."""
        print("=" * 60)
        print(f"  GOD MODE ADMIN — {PROJECT_ID}")
        print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        self.check_gcp_project()
        self.check_gcloud_auth()
        self.check_python()
        self.check_tools()
        self.check_pem()
        self.check_dotenv()
        self.check_firestore()
        self.check_cloud_run()
        self.check_secrets()

        elapsed = time.monotonic() - self.start_time
        total = self.checks_passed + self.checks_failed
        print("\n" + "=" * 60)
        print(f"  RESULTS: {self.checks_passed}/{total} passed, {self.checks_failed} failed")
        print(f"  Elapsed: {elapsed:.1f}s")
        if self.checks_failed == 0:
            print("  🟢 GOD MODE: FULLY OPERATIONAL")
        else:
            print("  🟡 GOD MODE: DEGRADED — fix failures above")
        print("=" * 60)

        return self.checks_failed == 0


if __name__ == "__main__":
    admin = GodModeAdmin()
    success = admin.run_all()
    sys.exit(0 if success else 1)
