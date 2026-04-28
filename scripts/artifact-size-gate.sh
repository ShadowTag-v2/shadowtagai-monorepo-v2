#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# ANTIGRAVITY OS: ARTIFACT SIZE GATEKEEPER (Invariant #114)
# Blocks staged files >1MB from entering git history without a manifest.
# Called from pre-commit hook chain.
# ------------------------------------------------------------------------------
set -euo pipefail

MAX_SIZE_KB=1024  # 1MB threshold

echo "📦 [Antigravity] Scanning staged files for oversized payloads..."

VIOLATIONS=""
while IFS= read -r file; do
    [ -z "$file" ] && continue
    [ ! -f "$file" ] && continue

    FILE_SIZE_KB=$(du -k "$file" 2>/dev/null | cut -f1)
    if [ "$FILE_SIZE_KB" -gt "$MAX_SIZE_KB" ]; then
        # Check for corresponding manifest
        MANIFEST="${file}.manifest.json"
        MANIFEST_ALT="${file%.*}.manifest.json"
        if [ ! -f "$MANIFEST" ] && [ ! -f "$MANIFEST_ALT" ]; then
            VIOLATIONS="${VIOLATIONS}\n  ⚠️  ${file} (${FILE_SIZE_KB}KB) — no manifest found"
        fi
    fi
done < <(git diff --cached --name-only --diff-filter=A 2>/dev/null)

if [ -n "$VIOLATIONS" ]; then
    echo -e "\n🛑 KERNEL BLOCK: Oversized payloads detected in Git index."
    echo -e "$VIOLATIONS"
    echo ""
    echo "Rule #114: Non-source payloads (>1MB) require an artifact manifest."
    echo "Options:"
    echo "  1. git rm --cached <file> && create <file>.manifest.json"
    echo "  2. Add the file to .gitignore"
    echo "  3. Use git-lfs for legitimate large assets"
    exit 1
fi

echo "✅ [Antigravity] Artifact size gate passed."
