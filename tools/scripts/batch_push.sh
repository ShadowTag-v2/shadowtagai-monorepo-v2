#!/usr/bin/env bash
set -euo pipefail

REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-main}"
BATCH_SIZE="${BATCH_SIZE:-5}"

echo "🚀 Batch Push Script — Two-Lane Upload Doctrine (TACSOP 5)"

git fetch "${REMOTE}" "${BRANCH}" --prune

mapfile -t commits < <(git rev-list --reverse "${REMOTE}/${BRANCH}..HEAD")

if [ "${#commits[@]}" -eq 0 ]; then
  echo "No unpushed commits."
  exit 0
fi

echo "Unpushed commits: ${#commits[@]}"

start=0
while [ "${start}" -lt "${#commits[@]}" ]; do
  end=$((start + BATCH_SIZE - 1))
  if [ "${end}" -ge "$((${#commits[@]} - 1))" ]; then
    end=$((${#commits[@]} - 1))
  fi

  target="${commits[$end]}"

  echo "== Preflight for batch commits ${start}-${end} target=${target} =="

  # Run preflight gates
  if [ -f tools/scripts/check-buildifier.sh ]; then
    tools/scripts/check-buildifier.sh || true
  fi
  if [ -f tools/scripts/prepush-bloat-gate.sh ]; then
    tools/scripts/prepush-bloat-gate.sh
  else
    echo "⚠️ prepush-bloat-gate.sh not found, skipping..."
  fi

  echo "== Pushing batch target ${target} =="

  # Push current branch only up to target SHA.
  python tools/scripts/auth_github_app.py --push-ref "${target}:refs/heads/${BRANCH}" || {
    echo "Push failed at ${target}"
    exit 1
  }

  git fetch "${REMOTE}" "${BRANCH}" --prune
  git rev-parse "${REMOTE}/${BRANCH}"

  start=$((end + 1))

  if [ "${start}" -lt "${#commits[@]}" ]; then
    echo "Batch complete. Renewing token before next batch."
    python tools/scripts/auth_github_app.py --renew-token >/dev/null || true
  fi
done

git fetch "${REMOTE}" "${BRANCH}" --prune
remaining="$(git log --oneline "${REMOTE}/${BRANCH}..HEAD")"

if [ -n "${remaining}" ]; then
  echo "ERROR: unpushed commits remain:"
  echo "${remaining}"
  exit 1
fi

echo "All batches pushed successfully."
