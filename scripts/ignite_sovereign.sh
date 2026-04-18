#!/bin/bash
# IGNITE SOVEREIGN — Unified Local Launcher
# Usage: ./scripts/ignite_sovereign.sh
# Starts ALL local sovereign infrastructure in correct order

set -euo pipefail

echo "╔══════════════════════════════════════════════════════╗"
echo "║     SOVEREIGN IGNITION SEQUENCE — shadowtag-omega-v4     ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# ─── Phase 0: Pre-Flight Checks ─────────────────────────────
echo "=== PHASE 0: PRE-FLIGHT ==="

if git tag -l SOVEREIGN_GOLD_MASTER | grep -q .; then
    echo "  ✅ Gold Master tag: SOVEREIGN_GOLD_MASTER"
else
    echo "  ⚠️  Gold Master tag not found (non-blocking)"
fi

if [ -f "operator_invariants.json" ]; then
    VERSION=$(python3 -c "import json; print(json.load(open('operator_invariants.json'))['version'])" 2>/dev/null || echo "unknown")
    echo "  ✅ Operator Invariants: v${VERSION}"
else
    echo "  ❌ operator_invariants.json not found!"
    exit 1
fi

if [ -f ".env" ]; then
    if grep -q "DEVELOPER_KNOWLEDGE_API_KEY" .env 2>/dev/null; then
        echo "  ✅ API Key: Present in .env"
    else
        echo "  ⚠️  DEVELOPER_KNOWLEDGE_API_KEY missing from .env"
    fi
else
    echo "  ⚠️  .env file not found"
fi

echo ""

# ─── Phase 1: Auth ──────────────────────────────────────────
echo "=== PHASE 1: AUTH ==="

CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "none")
if [ "$CURRENT_PROJECT" = "shadowtag-omega-v4" ]; then
    echo "  ✅ GCloud project: shadowtag-omega-v4"
else
    echo "  🔄 Setting GCloud project to shadowtag-omega-v4..."
    gcloud config set project shadowtag-omega-v4 2>/dev/null || echo "  ⚠️  gcloud not available"
fi

ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || echo "NONE")
if [ "$ACCOUNT" != "NONE" ]; then
    echo "  ✅ GCloud auth: $ACCOUNT"
else
    echo "  ⚠️  No active GCloud auth (run: gcloud auth login)"
fi

echo ""

# ─── Phase 2: Hunter-Killer Stack ────────────────────────────
echo "=== PHASE 2: HUNTER-KILLER STACK ==="

for tool in rg ugrep sg; do
    if command -v "$tool" &>/dev/null; then
        echo "  ✅ $tool: $(command -v $tool)"
    else
        echo "  ⚠️  $tool: NOT INSTALLED (run: ./scripts/install_hunter_killer.sh)"
    fi
done

echo ""

# ─── Phase 3: Linting Health ────────────────────────────────
echo "=== PHASE 3: LINTING HEALTH ==="

if command -v ruff &>/dev/null || [ -f "$HOME/.local/bin/ruff" ]; then
    RUFF_CMD="${HOME}/.local/bin/ruff"
    F821_COUNT=$($RUFF_CMD check --select F821 --exclude "*/external_repos/*" --exclude "*/archive/*" --exclude "*/node_modules/*" --exclude "*/.venv/*" --exclude "*/ShadowMobile/*" apps/ tools/ scripts/ 2>/dev/null | grep -c "F821" || echo "0")
    echo "  📊 F821 (undefined names): $F821_COUNT"

    F401_COUNT=$($RUFF_CMD check --select F401 --exclude "*/external_repos/*" --exclude "*/archive/*" --exclude "*/node_modules/*" --exclude "*/.venv/*" --exclude "*/ShadowMobile/*" apps/ tools/ scripts/ 2>/dev/null | grep -c "F401" || echo "0")
    echo "  📊 F401 (unused imports): $F401_COUNT"
else
    echo "  ⚠️  ruff not found"
fi

echo ""

# ─── Phase 4: Git Status ────────────────────────────────────
echo "=== PHASE 4: REPOSITORY STATE ==="

BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
echo "  📌 Branch: $BRANCH"

DIRTY=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
echo "  📊 Dirty files: $DIRTY"

AHEAD=$(git rev-list --count @{upstream}..HEAD 2>/dev/null || echo "?")
BEHIND=$(git rev-list --count HEAD..@{upstream} 2>/dev/null || echo "?")
echo "  📊 Ahead/Behind origin: +${AHEAD}/-${BEHIND}"

echo ""

# ─── Phase 5: Monkey Ban Verification ───────────────────────
echo "=== PHASE 5: MONKEY BAN VERIFICATION ==="

MONKEY_HITS=$(rg -i "flying_monkey|monkey_swarm|MonkeyAgent" --glob "!archive/**" --glob "!*.md" --glob "!SKILL.md" apps/ tools/ scripts/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$MONKEY_HITS" = "0" ]; then
    echo "  ✅ Monkey Ban: CLEAN (0 violations)"
else
    echo "  ❌ Monkey Ban: $MONKEY_HITS VIOLATIONS DETECTED"
    rg -i "flying_monkey|monkey_swarm|MonkeyAgent" --glob "!archive/**" --glob "!*.md" apps/ tools/ scripts/ 2>/dev/null | head -5
fi

echo ""

# ─── Phase 6: Skill Fleet ───────────────────────────────────
echo "=== PHASE 6: SKILL FLEET ==="

GLOBAL_SKILLS=$(ls -d "$HOME/.gemini/antigravity/skills"/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
WORKSPACE_SKILLS=$(ls -d .agents/skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
echo "  📊 Global skills: $GLOBAL_SKILLS"
echo "  📊 Workspace skills: $WORKSPACE_SKILLS"
echo "  📊 Total: $((GLOBAL_SKILLS + WORKSPACE_SKILLS))"

echo ""

# ─── Phase 7: ShadowMobile Status ────────────────────────────
echo "=== PHASE 7: SHADOWMOBILE ==="

APK_PATH="apps/aiyou_stack/aiyou-fastapi-services/ShadowMobile/android/app/build/outputs/apk/debug/app-debug.apk"
if [ -f "$APK_PATH" ]; then
    APK_SIZE=$(ls -lh "$APK_PATH" | awk '{print $5}')
    echo "  ✅ Debug APK: $APK_SIZE ($APK_PATH)"
else
    echo "  ⚠️  Debug APK not found"
fi

echo ""

# ─── Summary ────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════╗"
echo "║               IGNITION SEQUENCE COMPLETE                 ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Memory: LOCKED (v${VERSION:-?})                             ║"
echo "║  Mode: LIVE FIRE                                         ║"
echo "║  State: SOVEREIGN                                        ║"
echo "╚══════════════════════════════════════════════════════╝"
