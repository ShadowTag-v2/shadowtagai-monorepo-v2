#!/bin/bash

# 0. Hook Protocol: Read Input (Sync)
# We must consume stdin to respect the hook contract, even if we don't use the payload.
input=$(cat)

# 1. Log to Stderr (Visible in logs, doesn't break JSON contract)
exec 3>&1 # Save original stdout to FD 3
exec 1>&2 # Redirect stdout to stderr
echo ">>> 🪝 HOOK: Auto-Finish Triggered"

# 2. Identify Modified Files (Git Tracked)
FILES=$(git diff --name-only HEAD)

if [ -n "$FILES" ]; then
    echo "Found active files: $FILES"

    for FILE in $FILES; do
        if [ ! -f "$FILE" ]; then
            continue
        fi

        # Python Polish
        if [[ "$FILE" == *.py ]]; then
            echo "✨ Polishing Python: $FILE"
            python3 -m black "$FILE" --quiet || true
            python3 -m isort "$FILE" --quiet || true
        fi

        # 3. Stage (Save State)
        echo "💾 Staging: $FILE"
        git add "$FILE"
    done
else
    echo "No files to stage."
fi

# 4. Protocol Output: Strict JSON to original Stdout
# Restore stdout
exec 1>&3
echo '{"decision": "allow"}'
exit 0
