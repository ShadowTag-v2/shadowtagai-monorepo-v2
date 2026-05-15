#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$PWD/external}"
mkdir -p "$ROOT"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

need_cmd git

ensure_uv_if_needed() {
  if command -v uv >/dev/null 2>&1; then
    return 0
  fi
  echo "uv is required but not installed." >&2
  echo "Install it explicitly; this script will not curl-pipe installers." >&2
  exit 1
}

repo_exists() {
  git ls-remote --exit-code "$1" >/dev/null 2>&1
}

clone_or_update() {
  local url="$1"
  local dir="$2"

  if ! repo_exists "$url"; then
    echo "Skipping unavailable repo: $url" >&2
    return 1
  fi

  if [ ! -d "$dir/.git" ]; then
    git clone --depth=1 "$url" "$dir"
  else
    git -C "$dir" fetch --depth=1 origin
    git -C "$dir" reset --hard FETCH_HEAD
  fi
}

prepare_python_repo_if_supported() {
  local dir="$1"

  if [ -f "$dir/pyproject.toml" ]; then
    ensure_uv_if_needed
    (
      cd "$dir"
      uv sync
    )
  fi

  if [ -f "$dir/prepare.py" ]; then
    ensure_uv_if_needed
    (
      cd "$dir"
      uv run prepare.py
    )
  fi
}

ROOT_KOSMOS="$ROOT/Kosmos"
ROOT_BIOAGENTS="$ROOT/BioAgents"
ROOT_AUTORESEARCH="$ROOT/autoresearch-macos"

clone_or_update "https://github.com/jimmc414/Kosmos.git" "$ROOT_KOSMOS" || true
clone_or_update "https://github.com/bio-xyz/BioAgents.git" "$ROOT_BIOAGENTS" || true
clone_or_update "https://github.com/miolini/autoresearch-macos.git" "$ROOT_AUTORESEARCH" || true

prepare_python_repo_if_supported "$ROOT_AUTORESEARCH"

echo "Setup complete."
echo "No automatic source rewriting was performed."
echo "Any BullMQ or repo-specific dependency removal must be done with a code-aware patch, not sed."
