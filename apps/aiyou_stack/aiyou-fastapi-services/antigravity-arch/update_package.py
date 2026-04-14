#!/usr/bin/env python3
"""Auto-update PKGBUILD when pyproject.toml version changes.
Runs in GitHub Actions daily.

Standard library only - no external dependencies.
"""

import os
import re
import ssl
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

# Support both main branch and current branch for testing
REPO_URL = "https://raw.githubusercontent.com/ShadowTag-v2/shadowtag_v4-fastapi-services"
DEFAULT_BRANCH = os.environ.get("UPDATE_BRANCH", "main")
PYPROJECT_URL = f"{REPO_URL}/{DEFAULT_BRANCH}/pyproject.toml"
PKGBUILD_PATH = Path(__file__).parent / "PKGBUILD"


def fetch_upstream_version() -> str:
    """Fetch version from pyproject.toml on main branch."""
    # Try local file first if --local flag or LOCAL_PYPROJECT env var
    local_path = PKGBUILD_PATH.parent.parent / "pyproject.toml"
    if "--local" in sys.argv or os.environ.get("LOCAL_PYPROJECT"):
        if local_path.exists():
            content = local_path.read_text()
            match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
        raise RuntimeError(f"Local pyproject.toml not found at {local_path}")

    try:
        # Handle SSL certificate issues on macOS
        ctx = ssl.create_default_context()
        if sys.platform == "darwin":
            # macOS often has SSL cert issues with Python
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        with urlopen(PYPROJECT_URL, timeout=30, context=ctx) as resp:
            content = resp.read().decode("utf-8")
    except URLError as e:
        # Fallback to local if remote fails
        if local_path.exists():
            print("Warning: Remote fetch failed, using local pyproject.toml")
            content = local_path.read_text()
        else:
            raise RuntimeError(f"Failed to fetch upstream pyproject.toml: {e}")

    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        raise RuntimeError("Could not parse version from pyproject.toml")
    return match.group(1)


def get_pkgbuild_version() -> str:
    """Get current version from PKGBUILD."""
    if not PKGBUILD_PATH.exists():
        raise RuntimeError(f"PKGBUILD not found at {PKGBUILD_PATH}")

    content = PKGBUILD_PATH.read_text()
    match = re.search(r"^pkgver=(.+)$", content, re.MULTILINE)
    return match.group(1) if match else "0.0.0"


def update_pkgbuild(new_version: str) -> bool:
    """Update pkgver in PKGBUILD. Returns True if changed."""
    content = PKGBUILD_PATH.read_text()

    # Update pkgver
    new_content = re.sub(
        r"^pkgver=.+$",
        f"pkgver={new_version}",
        content,
        flags=re.MULTILINE,
    )

    # Reset pkgrel to 1 on version bump
    new_content = re.sub(
        r"^pkgrel=.+$",
        "pkgrel=1",
        new_content,
        flags=re.MULTILINE,
    )

    if new_content == content:
        return False

    PKGBUILD_PATH.write_text(new_content)
    return True


def run_srcinfo() -> None:
    """Regenerate .SRCINFO using makepkg."""
    srcinfo_path = PKGBUILD_PATH.parent / ".SRCINFO"

    try:
        result = subprocess.run(
            ["makepkg", "--printsrcinfo"],
            cwd=PKGBUILD_PATH.parent,
            capture_output=True,
            text=True,
            check=True,
        )
        srcinfo_path.write_text(result.stdout)
    except FileNotFoundError:
        print("Warning: makepkg not available, skipping .SRCINFO generation")
    except subprocess.CalledProcessError as e:
        print(f"Warning: makepkg failed: {e.stderr}")


def git_commit(version: str) -> None:
    """Commit the changes."""
    try:
        subprocess.run(["git", "add", "PKGBUILD", ".SRCINFO"], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"chore(arch): bump shadowtagai to {version}"],
            check=True,
        )
        print(f"Committed version bump to {version}")
    except subprocess.CalledProcessError as e:
        print(f"Git commit failed: {e}")


def main() -> int:
    """Main entry point."""
    try:
        upstream = fetch_upstream_version()
        current = get_pkgbuild_version()

        print(f"Upstream version: {upstream}")
        print(f"Current version:  {current}")

        if upstream == current:
            print("Already up to date - no changes needed")
            return 0

        print(f"Updating PKGBUILD from {current} to {upstream}...")

        if update_pkgbuild(upstream):
            run_srcinfo()
            print(f"Successfully updated to {upstream}")

            # Check for --commit flag
            if "--commit" in sys.argv:
                git_commit(upstream)

            return 0
        print("No changes made to PKGBUILD")
        return 0

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
