#!/usr/bin/env python3
"""Scope Lint: Enforces single-domain PRs
Detects mega-merges that touch too many unrelated areas

Part of Dual-Model CI Pipeline
Cost: $0 (local)

Rationale:
- Single-domain PRs are easier to review (-25% review fatigue)
- Smaller PRs merge faster (-18% rework)
- Better git bisect capability
"""

import subprocess
import sys
from collections import defaultdict

# Domain classification patterns
DOMAIN_PATTERNS = {
    "shadowtag": ["shadowtag", "watermark", "stego", "attestation"],
    "api": ["api/", "routes/", "endpoints/", "routers/"],
    "auth": ["auth", "jwt", "session", "oauth", "login"],
    "database": ["models/", "database", "migration", "alembic"],
    "infra": ["docker", "k8s", "terraform", ".github/", "cloudbuild"],
    "tests": ["test_", "_test.py", "tests/", "conftest"],
    "docs": [".md", "docs/", "readme"],
    "config": ["config", "settings", ".env", ".yaml", ".yml", ".toml"],
    "frontend": ["static/", "templates/", ".html", ".css", ".js"],
    "monitoring": ["monitor", "metrics", "logging", "telemetry"],
}

# Domains that can coexist with any other domain
UNIVERSAL_DOMAINS = {"tests", "docs", "config"}

# Maximum non-universal domains allowed
MAX_DOMAINS = 1


def get_changed_files(diff_range: str) -> list:
    """Get list of changed files from git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", diff_range, "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        return files
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git diff failed: {e}", file=sys.stderr)
        return []


def classify_file(filepath: str) -> str:
    """Classify a file into a domain."""
    filepath_lower = filepath.lower()

    for domain, patterns in DOMAIN_PATTERNS.items():
        if any(p in filepath_lower for p in patterns):
            return domain

    return "other"


def main(diff_range: str = "origin/main...HEAD"):
    """Check PR scope."""
    files = get_changed_files(diff_range)

    if not files:
        print("✅ No files changed")
        return

    # Classify all files
    domains = defaultdict(list)
    for f in files:
        domain = classify_file(f)
        domains[domain].append(f)

    # Separate universal from non-universal domains
    non_universal = {d: files for d, files in domains.items() if d not in UNIVERSAL_DOMAINS}

    print(f"Files changed: {len(files)}")
    print(f"Domains touched: {list(domains.keys())}")
    print(f"Non-universal domains: {list(non_universal.keys())}")
    print()

    # Check if too many domains
    if len(non_universal) > MAX_DOMAINS:
        print("🔴 PR touches multiple domains:")
        print()

        for domain in sorted(domains.keys()):
            file_list = domains[domain]
            is_universal = domain in UNIVERSAL_DOMAINS
            marker = "📁" if is_universal else "⚠️ "
            print(f"{marker} [{domain}]: {len(file_list)} file(s)")
            for f in file_list[:5]:  # Show first 5
                print(f"      • {f}")
            if len(file_list) > 5:
                print(f"      ... and {len(file_list) - 5} more")
            print()

        print("─" * 60)
        print("💡 Recommendation: Split into separate PRs by domain")
        print()
        print("Benefits of single-domain PRs:")
        print("  • Faster review (−25% review time)")
        print("  • Less rework (−18% iterations)")
        print("  • Better git bisect for debugging")
        print("  • Smaller blast radius if issues arise")
        print()
        print("Suggested split:")
        for domain in sorted(non_universal.keys()):
            print(f"  • PR for [{domain}]: {len(non_universal[domain])} files")

        sys.exit(1)

    # Passed
    primary_domain = list(non_universal.keys())[0] if non_universal else "none"
    universal_count = sum(len(f) for d, f in domains.items() if d in UNIVERSAL_DOMAINS)

    print("─" * 60)
    print(f"✅ Single-domain PR: {primary_domain}")
    if universal_count > 0:
        print(f"   + {universal_count} supporting file(s) (tests/docs/config)")


if __name__ == "__main__":
    diff_range = sys.argv[1] if len(sys.argv) > 1 else "origin/main...HEAD"
    main(diff_range)
