#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# scripts/clone-yard-fetch.sh — Clone Yard Upstream Fetcher
# Reads external_repos/upstream_manifest.yaml and performs
# shallow clones into external_repos/upstream/<group>/<org>/<repo>
#
# Policy: depth=1, default branch only, gitignored, never indexed.
# All clones are read-only reference architectures.
#
# Usage: bash scripts/clone-yard-fetch.sh [--group <name>] [--dry-run]
# ═══════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

MANIFEST="external_repos/upstream_manifest.yaml"
TARGET_DIR="external_repos/upstream"
DRY_RUN=false
TARGET_GROUP=""

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --group)   shift; TARGET_GROUP="${1:-}" ;;
  esac
  shift 2>/dev/null || true
done

if [ ! -f "$MANIFEST" ]; then
  echo "::error::Manifest not found: $MANIFEST"
  exit 1
fi

echo "═══ Clone Yard — Upstream Fetch ═══"
echo "  Manifest: $MANIFEST"
echo "  Target:   $TARGET_DIR"
echo "  Dry Run:  $DRY_RUN"
echo ""

# Ensure the target directory exists and is gitignored
mkdir -p "$TARGET_DIR"
if ! grep -qxF "external_repos/upstream/" .gitignore 2>/dev/null; then
  echo "external_repos/upstream/" >> .gitignore
  echo "  ✓ Added external_repos/upstream/ to .gitignore"
fi

# Parse manifest with stdlib Python (no pyyaml dependency)
python3 -c "
import re, sys, subprocess, os

manifest_path = '$MANIFEST'
target_dir = '$TARGET_DIR'
dry_run = '$DRY_RUN' == 'true'
target_group = '$TARGET_GROUP'

with open(manifest_path) as f:
    content = f.read()

# Parse clone depth from policy section
depth_match = re.search(r'clone_depth:\s*(\d+)', content)
clone_depth = depth_match.group(1) if depth_match else '1'

# Parse groups and their repos
# Pattern: group name followed by indented repo entries
group_pattern = re.compile(r'^  (\w[\w_]*):\s*$', re.MULTILINE)
repo_pattern = re.compile(r'^\s+-\s+(\S+)', re.MULTILINE)

groups = {}
current_group = None
for line in content.split('\n'):
    group_match = re.match(r'^  (\w[\w_]*):\s*$', line)
    repo_match = re.match(r'^\s+-\s+(\S+)', line)
    if group_match:
        current_group = group_match.group(1)
        groups[current_group] = []
    elif repo_match and current_group:
        groups[current_group].append(repo_match.group(1))

total_repos = sum(len(repos) for repos in groups.values())
cloned = 0
skipped = 0
failed = 0

print(f'  Groups: {len(groups)} | Total repos: {total_repos}')
print()

for group_name, repos in sorted(groups.items()):
    if target_group and group_name != target_group:
        continue
    print(f'── {group_name} ({len(repos)} repos) ──')
    for repo_ref in repos:
        parts = repo_ref.split('/')
        if len(parts) != 2:
            print(f'  ✗ Invalid ref: {repo_ref}')
            failed += 1
            continue
        org, repo = parts
        clone_path = os.path.join(target_dir, group_name, org, repo)

        if os.path.exists(clone_path):
            print(f'  ⊘ {repo_ref} (exists)')
            skipped += 1
            continue

        url = f'https://github.com/{repo_ref}.git'

        if dry_run:
            print(f'  ◎ {repo_ref} → {clone_path} (dry-run)')
            cloned += 1
            continue

        os.makedirs(os.path.dirname(clone_path), exist_ok=True)
        cmd = ['git', 'clone', '--depth', clone_depth, '--single-branch', '--quiet', url, clone_path]
        print(f'  ↓ {repo_ref}...', end=' ', flush=True)
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
            print('✓')
            cloned += 1
        except subprocess.TimeoutExpired:
            print('⏱ timeout')
            failed += 1
        except subprocess.CalledProcessError as e:
            print(f'✗ {e.stderr.decode().strip()[:80]}')
            failed += 1

print()
print(f'═══ Clone Summary: {cloned} cloned | {skipped} existing | {failed} failed ═══')
if failed > 0:
    sys.exit(1)
"
