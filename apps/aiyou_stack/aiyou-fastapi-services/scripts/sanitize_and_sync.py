#!/usr/bin/env python3
"""Sanitize and sync Claude CLI sessions + iCloud notes to monorepo.
Strips PII, secrets, and sensitive data before committing.
"""

import re
import shutil
from pathlib import Path

# Source and destination paths
SOURCES = {
    "claude_cli": {
        "src": "/Users/pikeymickey/shadowtag_v4-stack/workspace_archive/claude_cli",
        "dst": "/Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2/docs/claude_cli_sessions",
    },
    "icloud_notes": {
        "src": "/Users/pikeymickey/shadowtag_v4-stack/workspace_archive/icloud_notes",
        "dst": "/Users/pikeymickey/shadowtag_v4-stack/ShadowTag-v2/docs/icloud_notes_imported",
    },
}

# Patterns to redact
REDACT_PATTERNS = [
    # API Keys & Tokens
    (r"ghp_[a-zA-Z0-9]{36}", "[GITHUB_PAT_REDACTED]"),
    (r"gho_[a-zA-Z0-9]{36}", "[GITHUB_OAUTH_REDACTED]"),
    (r"sk-[a-zA-Z0-9]{48,}", "[OPENAI_KEY_REDACTED]"),
    (r"sk-ant-[a-zA-Z0-9-]{40,}", "[ANTHROPIC_KEY_REDACTED]"),
    (r"AKIA[A-Z0-9]{16}", "[AWS_ACCESS_KEY_REDACTED]"),
    (r"AIza[a-zA-Z0-9_-]{35}", "[GOOGLE_API_KEY_REDACTED]"),
    (r"xox[baprs]-[a-zA-Z0-9-]+", "[SLACK_TOKEN_REDACTED]"),
    (r"ya29\.[a-zA-Z0-9_-]+", "[GOOGLE_OAUTH_REDACTED]"),
    # Private Keys
    (
        r"-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----[\s\S]*?-----END (RSA |EC |OPENSSH |)PRIVATE KEY-----",
        "[PRIVATE_KEY_REDACTED]",
    ),
    (r"-----BEGIN CERTIFICATE-----[\s\S]*?-----END CERTIFICATE-----", "[CERTIFICATE_REDACTED]"),
    # Personal Info (be conservative)
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL_REDACTED]"),
    (r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b", "[PHONE_REDACTED]"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_REDACTED]"),
    (r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b", "[CARD_REDACTED]"),
    # IP Addresses (internal)
    (
        r"\b(?:192\.168|10\.|172\.(?:1[6-9]|2[0-9]|3[01]))\.\d{1,3}\.\d{1,3}\b",
        "[INTERNAL_IP_REDACTED]",
    ),
    # Passwords in common formats
    (
        r'(?i)(password|passwd|pwd|secret|token|api_key|apikey|auth)[\s]*[=:]\s*["\']?[^\s"\']+["\']?',
        "[CREDENTIAL_REDACTED]",
    ),
    # Database connection strings
    (r"(?i)(mongodb|postgres|mysql|redis)://[^\s]+", "[DB_CONNECTION_REDACTED]"),
    # JWT tokens
    (r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*", "[JWT_REDACTED]"),
]

# Keep these emails (business/public)
ALLOWED_EMAILS = [
    "redacted@shadowtag-v4.local",
    "redacted@shadowtag-v4.local",
    "redacted@shadowtag-v4.local",
]


def sanitize_content(content: str) -> str:
    """Apply all redaction patterns to content."""
    for pattern, replacement in REDACT_PATTERNS:
        # Special handling for emails - keep allowed ones
        if "EMAIL" in replacement:

            def email_replacer(match):
                email = match.group(0)
                if any(allowed in email.lower() for allowed in ALLOWED_EMAILS):
                    return email
                return replacement

            content = re.sub(pattern, email_replacer, content, flags=re.IGNORECASE)
        else:
            content = re.sub(
                pattern,
                replacement,
                content,
                flags=re.IGNORECASE if "password" in pattern.lower() else 0,
            )
    return content


def process_file(src_path: Path, dst_path: Path) -> bool:
    """Process a single file, sanitizing if text-based."""
    try:
        # Create destination directory
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        # Skip binary files
        binary_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".ico",
            ".svg",
            ".pdf",
            ".zip",
            ".tar",
            ".gz",
        }
        if src_path.suffix.lower() in binary_extensions:
            shutil.copy2(src_path, dst_path)
            return True

        # Read and sanitize text files
        try:
            with open(src_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except:
            shutil.copy2(src_path, dst_path)
            return True

        sanitized = sanitize_content(content)

        with open(dst_path, "w", encoding="utf-8") as f:
            f.write(sanitized)

        return True
    except Exception as e:
        print(f"  Error processing {src_path}: {e}")
        return False


def sync_source(name: str, src: str, dst: str) -> tuple:
    """Sync a source directory with sanitization."""
    src_path = Path(src)
    dst_path = Path(dst)

    if not src_path.exists():
        print(f"  Source not found: {src}")
        return 0, 0

    # Clean destination
    if dst_path.exists():
        shutil.rmtree(dst_path)
    dst_path.mkdir(parents=True, exist_ok=True)

    success = 0
    failed = 0

    for src_file in src_path.rglob("*"):
        if src_file.is_file():
            rel_path = src_file.relative_to(src_path)
            dst_file = dst_path / rel_path

            if process_file(src_file, dst_file):
                success += 1
            else:
                failed += 1

    return success, failed


def main():
    print("=== Sanitize & Sync to Monorepo ===\n")

    total_success = 0
    total_failed = 0

    for name, paths in SOURCES.items():
        print(f"Processing {name}...")
        success, failed = sync_source(name, paths["src"], paths["dst"])
        print(f"  ✓ {success} files synced, {failed} failed\n")
        total_success += success
        total_failed += failed

    print(f"=== Complete: {total_success} files synced, {total_failed} failed ===")

    # Show sample redactions
    print("\n=== Redaction patterns active ===")
    for _pattern, replacement in REDACT_PATTERNS[:5]:
        print(f"  {replacement}")
    print(f"  ... and {len(REDACT_PATTERNS) - 5} more patterns")


if __name__ == "__main__":
    main()
