#!/usr/bin/env python3
"""
Scrub Secrets & PII — 10X Vibe Edition
Adapted for shadowtagai-monorepo-v2 structure (apps/, libs/, packages/, tools/, infra/)
"""

import re
from pathlib import Path
from typing import List, Tuple

# Common secret / credential patterns (expand as needed)
SECRET_PATTERNS: List[Tuple[str, str]] = [
    (r'(?i)(api[_-]?key|secret|token|password|auth[_-]?token)\s*[:=]\s*["\']?([a-z0-9_\-]{16,})["\']?', "Generic credential"),
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID"),
    (r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*["\']?[a-z0-9/+=]{40}["\']?', "AWS Secret Access Key"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token"),
    (r'gho_[a-zA-Z0-9]{36}', "GitHub OAuth Token"),
    (r'-----BEGIN (RSA|DSA|EC|OPENSSH|PRIVATE) PRIVATE KEY-----', "Private SSH/Key"),
    (r'sk-[a-zA-Z0-9]{48}', "OpenAI / Stripe Secret Key"),
    (r'xox[baprs]-[a-zA-Z0-9-]{10,}', "Slack Token"),
    (r'AIza[0-9A-Za-z\-_]{35}', "Google API Key"),
    (r'(?i)firebase.*(apiKey|authDomain|projectId).*["\'][^"\']+["\']', "Firebase Config"),
]

EXCLUDE_DIRS = {".git", "node_modules", "dist", "build", ".next", ".venv", "__pycache__", "coverage", ".pnpm-store"}

def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)

def scrub_file(file_path: Path) -> bool:
    """Scan and redact obvious secrets. Returns True if file was modified."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        original = content
        findings = []

        for pattern, label in SECRET_PATTERNS:
            matches = list(re.finditer(pattern, content))
            if matches:
                findings.append(f"  ⚠️  {label} ({len(matches)} occurrence(s))")
                # Redact — replace with placeholder (safe for most CI scenarios)
                content = re.sub(pattern, lambda m: m.group(0)[:10] + "...REDACTED..." + m.group(0)[-5:], content)

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            print(f"✅ Scrubbed: {file_path}")
            for f in findings:
                print(f)
            return True
        return False
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    root = Path(".")
    modified_count = 0
    scanned_count = 0

    print("🔐 10X Vibe Secret Exorcism starting...")

    for file_path in root.rglob("*"):
        if file_path.is_file() and not is_excluded(file_path):
            # Only scan likely source/config files
            if file_path.suffix.lower() in {".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".env", ".sh", ".md", ".toml"}:
                scanned_count += 1
                if scrub_file(file_path):
                    modified_count += 1

    print(f"\n🔐 Scan complete. {scanned_count} files scanned, {modified_count} files scrubbed.")
    if modified_count > 0:
        print("⚠️  Review git diff before committing — false positives possible.")
    else:
        print("✅ No secrets detected. Monorepo is clean.")

if __name__ == "__main__":
    main()
