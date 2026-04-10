#!/bin/bash

# ==========================================
# CONFIGURATION
# ==========================================
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

REPO_DIR="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball"
LOG_FILE="$REPO_DIR/sync-daemon.log"

GIT_BIN="/usr/bin/git"
PYTHON_BIN="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv/bin/python3"
NPX_BIN="/opt/homebrew/bin/npx"
PYRIGHT_BIN="/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.venv/bin/basedpyright" 

# Log size limit in bytes (5MB = 5242880 bytes)
MAX_LOG_SIZE=5242880 
# ==========================================

# ---------------------------------------------------------
# AUTONOMOUS LOG ROTATION
# ---------------------------------------------------------
if [ -f "$LOG_FILE" ]; then
    # stat -f%z gets the exact file size in bytes natively on macOS
    FILE_SIZE=$(stat -f%z "$LOG_FILE")
    if [ "$FILE_SIZE" -gt "$MAX_LOG_SIZE" ]; then
        mv "$LOG_FILE" "${LOG_FILE}.old"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Log rotated. Previous logs saved to sync-daemon.log.old" > "$LOG_FILE"
    fi
fi
# ---------------------------------------------------------

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

notify_error() {
    osascript -e "display notification \"$1\" with title \"Antigravity Halted\" subtitle \"Human Intervention Required\""
}

log_message "========================================"
log_message "🚀 Antigravity Auto-Rebase Cycle Triggered"

cd "$REPO_DIR" || exit

# ---------------------------------------------------------
# 1. AUTHENTICATION
# ---------------------------------------------------------
GITHUB_TOKEN=$($PYTHON_BIN "$REPO_DIR/generate_token.py")

if [ -z "$GITHUB_TOKEN" ]; then
    notify_error "Auth token generation failed. Check script."
    exit 1
fi
REMOTE_URL="https://x-access-token:${GITHUB_TOKEN}@github.com/ShadowTag-v2/Monorepo-Uphillsnowball.git"
log_message "✅ Auth token secured."

# ---------------------------------------------------------
# 2. BIOME & PYRIGHT GATES
# ---------------------------------------------------------
log_message "Running Biome auto-fix..."
$NPX_BIN @biomejs/biome check --write apps/ pnkln-platform/ scripts/ src/ shadowtag-os/src/ shadowtag-os/frontend/ shadowtag-os/infra/ tools/ >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log_message "❌ ABORT: Biome syntax errors."
    notify_error "Biome halted pipeline. Fix JS/TS errors."
    exit 1
fi

log_message "Running BasedPyright..."
$PYRIGHT_BIN apps/ --level error >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log_message "❌ ABORT: BasedPyright type errors."
    notify_error "BasedPyright halted pipeline. Fix Python type errors."
    exit 1
fi
log_message "✅ Code validation passed."

# ---------------------------------------------------------
# 2.5. GITLEAKS SECURITY GATE
# ---------------------------------------------------------
log_message "Running Gitleaks security scan..."
/opt/homebrew/bin/gitleaks detect --source "$REPO_DIR" --redact -v >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log_message "❌ CRITICAL ABORT: Gitleaks detected hardcoded secrets in the workspace!"
    notify_error "Secrets Detected! Gitleaks halted the pipeline to protect your repo."
    exit 1
fi
log_message "✅ Security scan passed. No secrets detected."

# ---------------------------------------------------------
# 3. AUTO-COMMIT LOCAL CHANGES
# ---------------------------------------------------------
$GIT_BIN add -A

if ! $GIT_BIN diff-index --quiet HEAD; then
    COMMIT_MSG="antigravity(auto): local state $(date '+%Y-%m-%d %H:%M:%S')"
    $GIT_BIN commit --no-verify -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        log_message "❌ ERROR: Commit failed. Check git state."
        notify_error "Git commit failed in daemon."
        exit 1
    fi
    log_message "✅ Local changes committed."
else
    log_message "⏭️ Working tree clean."
fi

# ---------------------------------------------------------
# 4. AUTONOMOUS FETCH & REBASE
# ---------------------------------------------------------
log_message "Absorbing remote drift..."

$GIT_BIN pull --rebase "$REMOTE_URL" HEAD >> "$LOG_FILE" 2>&1

if [ $? -ne 0 ]; then
    log_message "❌ CONFLICT DETECTED: Aborting rebase to protect working tree."
    $GIT_BIN rebase --abort >> "$LOG_FILE" 2>&1
    notify_error "Merge conflict! Rebase aborted. Manual resolution required."
    exit 1
fi
log_message "✅ Remote changes integrated smoothly."

# ---------------------------------------------------------
# 5. SYNC: Push to GitHub Remote
# ---------------------------------------------------------
$GIT_BIN push "$REMOTE_URL" HEAD >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log_message "✅ SUCCESS: Antigravity payload shipped to orbit."
else
    log_message "❌ ERROR: Push rejected."
    notify_error "Push failed post-rebase. Check daemon logs."
    exit 1
fi
