#!/usr/bin/env python3
# Copyright 2026 ShadowTagAI. All rights reserved.
"""GCP Secret Manager Utility — Typed Python wrapper.

Replaces ad-hoc `gcloud secrets` subprocess calls with a proper
Python interface. Integrates with the `load_mcp_secrets.sh` pattern.

Usage:
    # As library
    from scripts.vault.secret_manager_util import get_secret, list_secrets

    value = get_secret("stripe-secret-key")
    secrets = list_secrets()

    # As CLI
    python scripts/vault/secret_manager_util.py get stripe-secret-key
    python scripts/vault/secret_manager_util.py list
    python scripts/vault/secret_manager_util.py check  # verify all required secrets exist
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys

logging.basicConfig(
  level=logging.INFO,
  format="%(asctime)s [SECRET-MGR] %(levelname)s %(message)s",
  datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("vault.secrets")

# Default project — override via GCP_PROJECT env var
DEFAULT_PROJECT = "shadowtag-omega-v4"

# Required secrets for full system operation
REQUIRED_SECRETS = [
  "developer-knowledge-api-key",
  "stitch-api-key",
  "google-design-api-key",
  "gemini-api-key",
  "stripe-secret-key",
  "stripe-publishable-key",
  "KOVEL_ATTESTATION_SECRET",
]


def _get_project() -> str:
  """Get the GCP project ID."""
  return os.environ.get("GCP_PROJECT", DEFAULT_PROJECT)


def get_secret(
  name: str, *, version: str = "latest", project: str | None = None
) -> str | None:
  """Retrieve a secret value from GCP Secret Manager.

  Args:
      name: Secret name (e.g., 'stripe-secret-key')
      version: Secret version (default: 'latest')
      project: GCP project ID (default: from env or DEFAULT_PROJECT)

  Returns:
      The secret value as a string, or None on failure.
  """
  proj = project or _get_project()
  try:
    result = subprocess.run(
      [
        "gcloud",
        "secrets",
        "versions",
        "access",
        version,
        f"--secret={name}",
        f"--project={proj}",
        "--quiet",
      ],
      capture_output=True,
      text=True,
      timeout=15,
    )
    if result.returncode == 0:
      return result.stdout.strip()

    logger.warning("Failed to get secret '%s': %s", name, result.stderr.strip())
    return None
  except (subprocess.TimeoutExpired, FileNotFoundError) as e:
    logger.error("Secret Manager unavailable: %s", e)
    return None


def list_secrets(*, project: str | None = None) -> list[str]:
  """List all secret names in the project.

  Returns:
      List of secret names.
  """
  proj = project or _get_project()
  try:
    result = subprocess.run(
      [
        "gcloud",
        "secrets",
        "list",
        f"--project={proj}",
        "--format=value(name)",
        "--quiet",
      ],
      capture_output=True,
      text=True,
      timeout=15,
    )
    if result.returncode == 0:
      return [
        line.strip() for line in result.stdout.strip().splitlines() if line.strip()
      ]

    logger.warning("Failed to list secrets: %s", result.stderr.strip())
    return []
  except (subprocess.TimeoutExpired, FileNotFoundError) as e:
    logger.error("Secret Manager unavailable: %s", e)
    return []


def check_required_secrets(*, project: str | None = None) -> dict[str, bool]:
  """Verify all required secrets exist.

  Returns:
      Dict mapping secret name to existence boolean.
  """
  existing = set(list_secrets(project=project))
  return {name: name in existing for name in REQUIRED_SECRETS}


def export_to_env(
  secret_names: list[str] | None = None,
  *,
  project: str | None = None,
) -> dict[str, str]:
  """Fetch secrets and return as env-var-ready dict.

  This is the programmatic equivalent of `source scripts/load_mcp_secrets.sh`.
  Does NOT modify os.environ — caller decides what to do with values.

  Args:
      secret_names: Specific secrets to fetch (default: REQUIRED_SECRETS)
      project: GCP project ID

  Returns:
      Dict mapping secret names to their values. Missing secrets are omitted.
  """
  names = secret_names or REQUIRED_SECRETS
  env_vars: dict[str, str] = {}

  for name in names:
    value = get_secret(name, project=project)
    if value:
      # Convert secret name to env var format: stripe-secret-key → STRIPE_SECRET_KEY
      env_key = name.upper().replace("-", "_")
      env_vars[env_key] = value

  return env_vars


# --- CLI Entry Point ---------------------------------------------------------


def main() -> int:
  parser = argparse.ArgumentParser(description="GCP Secret Manager Utility")
  subparsers = parser.add_subparsers(dest="command", required=True)

  # get
  get_parser = subparsers.add_parser("get", help="Get a secret value")
  get_parser.add_argument("name", help="Secret name")
  get_parser.add_argument("--version", default="latest", help="Secret version")

  # list
  subparsers.add_parser("list", help="List all secrets")

  # check
  subparsers.add_parser("check", help="Verify required secrets exist")

  # export
  subparsers.add_parser("export", help="Export secrets as JSON env vars")

  args = parser.parse_args()

  if args.command == "get":
    value = get_secret(args.name, version=args.version)
    if value:
      # Redact output for safety — show only first/last 4 chars
      if len(value) > 12:
        redacted = f"{value[:4]}...{value[-4:]}"
      else:
        redacted = "****"
      print(f"{args.name}: {redacted}")
      return 0
    print(f"Secret '{args.name}' not found or inaccessible", file=sys.stderr)
    return 1

  elif args.command == "list":
    secrets = list_secrets()
    for s in secrets:
      print(s)
    print(f"\n{len(secrets)} secret(s) found")
    return 0

  elif args.command == "check":
    results = check_required_secrets()
    all_ok = True
    for name, exists in results.items():
      icon = "✅" if exists else "❌"
      print(f"  {icon} {name}")
      if not exists:
        all_ok = False
    return 0 if all_ok else 1

  elif args.command == "export":
    env_vars = export_to_env()
    # Print as JSON but with redacted values
    redacted = {
      k: f"{v[:4]}...{v[-4:]}" if len(v) > 12 else "****" for k, v in env_vars.items()
    }
    print(json.dumps(redacted, indent=2))
    return 0

  return 1


if __name__ == "__main__":
  raise SystemExit(main())
