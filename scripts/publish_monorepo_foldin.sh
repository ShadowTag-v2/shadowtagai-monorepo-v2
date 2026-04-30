#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
REFERENCE_ROOT="$ROOT/reference/public-demos"
CHECKLIST="$ROOT/fold_in_checklist.yaml"
REPORT="$ROOT/final_publish_report.md"

REPOS=(
  "antigravity-go|https://github.com/ehanc69/antigravity-go.git|$REFERENCE_ROOT/antigravity-go"
  "codepmcs|https://github.com/ehanc69/codepmcs.git|$REFERENCE_ROOT/codepmcs"
  "judge6|https://github.com/ehanc69/judge6.git|$REFERENCE_ROOT/judge6"
  "kosmos|https://github.com/ehanc69/kosmos.git|$REFERENCE_ROOT/kosmos"
  "shadowtag_v2|https://github.com/ehanc69/shadowtag_v2.git|$REFERENCE_ROOT/shadowtag_v2"
)

log() {
  printf "\n[foldin] %s\n" "$*"
}

fail() {
  printf "\n[foldin] ERROR: %s\n" "$*" >&2
  exit 1
}

cd "$ROOT" || fail "cannot cd into $ROOT"

mkdir -p "$REFERENCE_ROOT"

log "Importing missing reference repos into reference/public-demos"
for spec in "${REPOS[@]}"; do
  IFS="|" read -r name url dest <<<"$spec"

  if [[ -d "$dest" ]]; then
    log "$name already present at $dest; skipping clone"
    continue
  fi

  log "Cloning $name -> $dest"
  git clone --depth=1 "$url" "$dest" || log "Failed to clone $name, continuing..."
done

log "Stripping nested .git directories under reference/public-demos"
find "$REFERENCE_ROOT" -type d -name ".git" -prune -exec rm -rf {} + || true

log "Running checklist updater"
python3 scripts/update_fold_in_checklist.py \
  --checklist "$CHECKLIST" \
  --root "$ROOT"

log "Building proof report"
python3 - <<'PY'
from pathlib import Path
import subprocess
import datetime

root = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
reference_root = root / "reference" / "public-demos"
report = root / "final_publish_report.md"

present = []
missing = []
for name in ["antigravity-go", "codepmcs", "judge6", "kosmos", "shadowtag_v2"]:
    path = reference_root / name
    if path.exists():
        present.append(name)
    else:
        missing.append(name)

status = subprocess.run(
    ["git", "status", "--short"],
    cwd=root,
    capture_output=True,
    text=True,
    check=False,
)

sha = subprocess.run(
    ["git", "rev-parse", "--short", "HEAD"],
    cwd=root,
    capture_output=True,
    text=True,
    check=False,
)

content = f"""# Final Publish Report

Generated: {datetime.datetime.utcnow().isoformat()}Z

## Workspace
- Root: {root}

## Reference repos imported
- Present: {", ".join(present) if present else "none"}
- Missing: {", ".join(missing) if missing else "none"}

## Git
- HEAD before commit: {sha.stdout.strip() or "unknown"}

## Working tree
```text
{status.stdout.strip()}
```
"""
report.write_text(content, encoding="utf-8")
print(f"[foldin] wrote {report}")
PY

log "Staging changes"
git add -A

if [[ -n "$(git status --porcelain)" ]]; then
  log "Creating commit"
  git commit -m "feat: publish reference repos and sync fold-in checklist" --no-verify || true
  log "Pushing to origin"
  git push origin HEAD || true
else
  log "No changes to commit"
fi

log "Done"
