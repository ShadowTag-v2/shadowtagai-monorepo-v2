#!/usr/bin/env bash
# ------------------------------------------------------------------------------
# ANTIGRAVITY OS: ZERO-TRUST SECRET SCANNER (Invariant #115)
# Adapted to betterleaks (primary) per TACSOP 5 doctrine.
# Gitleaks as fallback. Regex as last-resort.
# ------------------------------------------------------------------------------
set -euo pipefail

echo "🔍 [Antigravity] Scanning payload for exposed secrets..."

if command -v betterleaks &> /dev/null; then
    echo "   Using: betterleaks (primary)"
    betterleaks protect -v --staged || {
        echo "🛑 KERNEL BLOCK: BETTERLEAKS detected secret in staging! Sync aborted."
        exit 1
    }
    betterleaks detect -v --no-git || {
        echo "🛑 KERNEL BLOCK: BETTERLEAKS detected secret in working directory! Sync aborted."
        exit 1
    }
elif command -v gitleaks &> /dev/null; then
    echo "   Using: gitleaks (fallback)"
    gitleaks protect -v --staged || {
        echo "🛑 KERNEL BLOCK: GITLEAKS detected secret in staging! Sync aborted."
        exit 1
    }
    gitleaks detect -v --no-git || {
        echo "🛑 KERNEL BLOCK: GITLEAKS detected secret in working directory! Sync aborted."
        exit 1
    }
else
    echo "   Using: Fallback Regex Egress Scanner (no binary found)"
    if git diff --cached --name-only | xargs grep -E -i \
        "(sk-ant-api|AIza[0-9A-Za-z_-]{35}|sk_live_[0-9a-zA-Z]{24}|sk_test_[0-9a-zA-Z]{24}|ghp_[0-9a-zA-Z]{36}|AKIA[0-9A-Z]{16})" \
        2>/dev/null; then
        echo -e "\n🛑 KERNEL BLOCK: Raw API Key detected via fallback regex! Sync aborted."
        exit 1
    fi
fi

echo "✅ [Antigravity] Egress scan clear. Payload authorized for deployment."
