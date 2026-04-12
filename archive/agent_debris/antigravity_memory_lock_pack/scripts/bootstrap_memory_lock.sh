#!/usr/bin/env bash
set -euo pipefail
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd -P)"
REPO_ROOT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-root) REPO_ROOT="$2"; shift 2 ;;
    *) echo "unknown arg: $1"; exit 2 ;;
  esac
done
if [[ -z "$REPO_ROOT" ]]; then
  echo "usage: $0 --repo-root /path/to/repo"
  exit 2
fi
mkdir -p "$REPO_ROOT/scripts" "$REPO_ROOT/docs" "$REPO_ROOT/.cursor/rules" "$REPO_ROOT/.vscode"
cp "$SRC_DIR/docs/MEMORY_LOCK.md" "$REPO_ROOT/docs/MEMORY_LOCK.md"
cp "$SRC_DIR/scripts/root_guard.sh" "$REPO_ROOT/scripts/root_guard.sh"
cp "$SRC_DIR/scripts/omega_startup.sh" "$REPO_ROOT/scripts/omega_startup.sh"
cp "$SRC_DIR/scripts/memory_lock_audit.py" "$REPO_ROOT/scripts/memory_lock_audit.py"
cp "$SRC_DIR/scripts/rebuild_context_packet.py" "$REPO_ROOT/scripts/rebuild_context_packet.py"
cp "$SRC_DIR/templates/.cursor/rules/memory-lock.mdc" "$REPO_ROOT/.cursor/rules/memory-lock.mdc"
cp "$SRC_DIR/templates/.vscode/tasks.json" "$REPO_ROOT/.vscode/tasks.json"
if [[ -f "$REPO_ROOT/AGENTS.md" ]]; then
  printf '\n' >> "$REPO_ROOT/AGENTS.md"
  cat "$SRC_DIR/templates/AGENTS_APPEND.md" >> "$REPO_ROOT/AGENTS.md"
fi
chmod +x "$REPO_ROOT/scripts/root_guard.sh" "$REPO_ROOT/scripts/omega_startup.sh" "$REPO_ROOT/scripts/memory_lock_audit.py" "$REPO_ROOT/scripts/rebuild_context_packet.py"
echo "[bootstrap_memory_lock] installed into $REPO_ROOT"
