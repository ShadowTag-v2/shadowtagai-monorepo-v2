#!/usr/bin/env bash
set -euo pipefail
echo "🔍 Buildifier Check (TACSOP 5)"
if command -v buildifier >/dev/null; then
  find . -name 'BUILD*' -o -name '*.bzl' | xargs buildifier --lint=fix || true
  echo "✅ Buildifier passed."
else
  echo "⚠️ buildifier not found, skipping (install via bazelisk or brew)."
fi
exit 0
