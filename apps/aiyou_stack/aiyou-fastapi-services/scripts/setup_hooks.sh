#!/bin/bash
# Setup Antigravity Git Hooks
# Automates: Spell Checking (Judge 6) on Commit

set -e

HOOK_PATH=".git/hooks/pre-commit"

echo "🛡️ Installing Judge 6 Hook..."

cat > "$HOOK_PATH" << 'EOF'
#!/bin/bash
# Antigravity Pre-Commit Hook (Judge 6 Linter)

echo "🛡️ Judge 6: Scanning Staged Files..."

# 1. Spell Check
if command -v npx >/dev/null 2>&1; then
    echo "   Running CSpell..."
    # Only scan staged files
    git diff --cached --name-only | xargs npx cspell --config cspell.yaml --no-summary
    if [ $? -ne 0 ]; then
        echo "❌ Judge 6 Verdict: REJECTED (Spelling Errors)."
        echo "   Run 'npx cspell \"**\"' to see all errors or fix the typos above."
        exit 1
    fi
else
    echo "⚠️  npx not found. Skipping Spell Check."
fi

# 2. Syntax Check (Ruff)
if command -v ruff >/dev/null 2>&1; then
    echo "   Running Ruff (Syntax)..."
    # Only check staged python files
    git diff --cached --name-only | grep ".py$" | xargs ruff check
    if [ $? -ne 0 ]; then
        echo "❌ Judge 6 Verdict: REJECTED (Syntax Errors)."
        echo "   Run 'ruff check .' to see details."
        exit 1
    fi
else
    echo "⚠️  ruff not found. Skipping Syntax Check."
fi

echo "✅ Judge 6 Verdict: APPROVED."
EOF

chmod +x "$HOOK_PATH"
echo "✅ Hook Installed. Judge 6 will now audit every commit."

# 2. Post-Commit Hook (MemoryRAG)
POST_HOOK_PATH=".git/hooks/post-commit"
echo "🧠 Installing Antigravity Memory Hook..."

cat > "$POST_HOOK_PATH" << 'EOF'
#!/bin/bash
# Antigravity Post-Commit Hook (Memory Indexing)
# Triggers Vertex AI Indexing after a successful commit

echo "🧠 [Antigravity] Indexing commit to Permanent Memory..."
COMMIT_HASH=$(git rev-parse HEAD)

# Run in background to not block the user, or foreground if critical
# "gcloud gemini-cli-hooks" pattern
if command -v python3 >/dev/null 2>&1; then
    python3 src/antigravity/memory_client.py --commit "$COMMIT_HASH" &
fi
EOF

chmod +x "$POST_HOOK_PATH"
echo "✅ Memory Hook Installed. Changes will be remembered forever."
