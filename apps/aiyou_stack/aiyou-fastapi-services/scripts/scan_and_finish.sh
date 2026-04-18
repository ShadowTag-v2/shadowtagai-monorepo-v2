#!/bin/bash
# SCAN_AND_FINISH.SH
# CLASSIFICATION: TOOL // AUTOMATION
# PURPOSE: "Scan All, Complete Changes, Save, and Close"

set -e

# ROBUSTNESS: Resolve Repo Root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$REPO_ROOT" || exit 1


echo ">>> 🕵️ SCANNING FOR ENTROPY..."

# 1. SCAN: Find all modified files (Staged + Unstaged)
# We use 'git status --porcelain' to catch untracked (??) and modified (M) files
MODIFIED_FILES=$(git status --porcelain | awk '{print $2}')

if [ -z "$MODIFIED_FILES" ]; then
    echo "✅ Zero Entropy. No files to finish."
    exit 0
fi

echo ">>> 📋 FOUND TARGETS:"
echo "$MODIFIED_FILES"

# 2. COMPLETE: Polish the Code (Lint/Format)
for FILE in $MODIFIED_FILES; do
    if [ ! -f "$FILE" ]; then continue; fi

    echo ">>> ✨ POLISHING: $FILE"

    # Python Polish
    if [[ "$FILE" == *.py ]]; then
        python3 -m black "$FILE" --quiet || true
        python3 -m isort "$FILE" --quiet || true
    fi

    # TS/JS Polish (if prettier is available)
    if [[ "$FILE" == *.ts || "$FILE" == *.tsx ]]; then
        if command -v prettier &> /dev/null; then
             prettier --write "$FILE" --loglevel warn || true
        fi
    fi

    # 3. SAVE: Stage the polished file
    git add "$FILE"
done

# 4. CLOSE: Commit the Transaction
echo ">>> 💾 SAVING TO LEDGER..."
timestamp=$(date +"%Y-%m-%d %H:%M:%S")
git commit -m "chore(auto-finish): polished and saved at $timestamp" || echo "Nothing to commit (clean)."

echo ">>> 🏁 PROTOCOL COMPLETE. You may now close your editors."
