#!/usr/bin/env bash
# ==============================================================================
# ANTIGRAVITY OS: DEAD CODE AUDIT & 20-POINT TECH DEBT GUILLOTINE
# Implements: OWASP 35 Rules, 20 Tech Debts, Compiler Guillotine, Vulture AST
# ==============================================================================

# ---- PATH Fix: Source nvm/node if available ----
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
export PATH="$HOME/.local/bin:$HOME/Library/Python/3.9/bin:$PATH"

# Exclude patterns for external repos, tools, control dirs
EXCLUDE_DIRS="--exclude-dir=external_repos --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=control --exclude-dir=tools --exclude-dir=.venv --exclude-dir=dist --exclude-dir=build"

echo "============================================================"
echo "⚡ INITIATING GCA OVERRIDE: TACTICAL HUD & HAMMOCK PROTOCOL"
echo "🧠 RICH HICKEY DOCTRINE: SIMPLE > EASY. UNENTANGLED > FAMILIAR."
echo "============================================================"
FAIL=0

echo "🔒 Phase 1: PII Exorcism & Secret Scanning..."
if command -v gitleaks &> /dev/null; then gitleaks detect --source . -v || FAIL=1; fi

# Tech Debt 3: Hardcoded secrets (exclude external_repos)
if grep -rnE $EXCLUDE_DIRS "api_key['\"]?\s*:\s*['\"]sk-[a-zA-Z0-9]{10,}" apps/ libs/ 2>/dev/null; then
    echo "❌ DEBT (Rule 3): Hardcoded secrets detected. Use process.env."
    FAIL=1
fi

# Tech Debt 12: localStorage Auth (exclude external_repos)
if grep -rnw $EXCLUDE_DIRS 'apps/' -e 'localStorage.setItem(.*token' -e 'localStorage.setItem(.*auth' --include='*.ts' --include='*.tsx' --include='*.js' --include='*.jsx' 2>/dev/null; then
    echo "❌ DEBT (Rule 12): Auth tokens stored in localStorage! XSS vulnerability."
    FAIL=1
fi

# Tech Debt 14: Synchronous Emails
if grep -rnw $EXCLUDE_DIRS 'apps/' -e 'sendEmail(' -e 'resend.emails.send' 2>/dev/null | grep -E 'route|controller|await'; then
    echo "⚠️ DEBT (Rule 14): Possible synchronous email sending in route handler. Queue it."
fi

echo "🧹 Phase 2: Janitor Protocol (Vulture, Ruff)..."
# Vulture Dead Code Elimination — scan only our source code
if command -v vulture &> /dev/null; then
    vulture apps/aiyou_stack/aiyou-fastapi-services/app/ apps/kovelai/ apps/counselconduit/ --min-confidence 80 2>/dev/null || echo "⚠️ Vulture found dead code candidates."
elif command -v python3 &> /dev/null && python3 -c "import vulture" 2>/dev/null; then
    python3 -m vulture apps/aiyou_stack/aiyou-fastapi-services/app/ apps/kovelai/ apps/counselconduit/ --min-confidence 80 2>/dev/null || echo "⚠️ Vulture found dead code candidates."
fi

if command -v ruff &> /dev/null; then
    ruff check apps/aiyou_stack/aiyou-fastapi-services/app/ apps/kovelai/ apps/counselconduit/ --fix 2>/dev/null || true
fi

echo "🏗️ Phase 3: Architectural & Vibe-Debt Checks..."
# Tech Debt 4: Monolith Ban (>800 LOC) — only scan our code
MONOLITHS=$(find apps/aiyou_stack/aiyou-fastapi-services/app apps/kovelai apps/counselconduit libs/autoresearch_sources -name "*.ts" -o -name "*.tsx" -o -name "*.py" -type f 2>/dev/null | \
    xargs wc -l 2>/dev/null | awk '$1 > 800 && !/total$/ {print $2}')
if [ -n "$MONOLITHS" ]; then
    echo "⚠️ DEBT (Rule 4): Files >800 LOC found (review for splitting):"
    echo "$MONOLITHS"
fi

# Tech Debt 1 & 10: DB queries & Feature Flags inside route handlers
if grep -rnw $EXCLUDE_DIRS 'apps/aiyou_stack/aiyou-fastapi-services/app/api/' -e 'SELECT \* FROM' -e 'UPDATE ' -e 'DELETE FROM' -e 'process.env.FEATURE_' 2>/dev/null | grep -E 'route|controller'; then
    echo "❌ DEBT (Rule 1 & 10): Raw DB queries or Feature Flags found inside routing logic!"
    FAIL=1
fi

# Tech Debt 2: AI Code without tests (only staged files)
MODIFIED_FILES=$(git diff --cached --name-only 2>/dev/null | grep -E '^apps/.*(ts|tsx|py)$' || true)
for file in $MODIFIED_FILES; do
    basename=$(basename "$file" | cut -d. -f1)
    if ! find tests/ apps/ -name "*${basename}*test*" -o -name "*${basename}*spec*" 2>/dev/null | grep -q .; then
         echo "⚠️ DEBT (Rule 2): Modified file $file has no tests."
    fi
done

echo "🪓 Phase 4: Executing Compiler Guillotine..."
if [ -f "tsconfig.json" ] && command -v npx &> /dev/null; then
    npx tsc --noEmit 2>&1 || { echo "⚠️ TypeScript compilation had issues."; }
fi
if [ -f ".eslintrc.cjs" ] && command -v npx &> /dev/null; then
    npx eslint src/ --quiet 2>&1 || { echo "⚠️ ESLint had findings."; }
fi

if [ $FAIL -eq 1 ]; then
    echo "============================================================"
    echo "🛑 GUILLOTINE TRIGGERED: Critical security thresholds breached."
    echo "Action: Fix hardcoded secrets and localStorage auth tokens."
    echo "============================================================"
    exit 1
else
    echo "============================================================"
    echo "✅ AUDIT COMPLETE: Code is scanned, formatted, unentangled."
    echo "============================================================"
fi
exit 0
