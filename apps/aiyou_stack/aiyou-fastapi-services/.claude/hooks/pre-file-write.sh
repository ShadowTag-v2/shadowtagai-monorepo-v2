#!/bin/bash
# PreToolUse hook for Write/Edit - Validates file operations before they occur

set -e

# Read hook input from stdin
INPUT=$(cat)

# Extract file path from tool input
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tool_input = data.get('tool_input', {})
    print(tool_input.get('file_path', ''))
except:
    print('')
")

if [ -z "$FILE_PATH" ]; then
    # No file path, allow operation
    exit 0
fi

# Check for sensitive files that shouldn't be modified
SENSITIVE_PATTERNS=(
    ".env"
    "credentials"
    "secrets"
    ".pem"
    ".key"
    "id_rsa"
    ".git/config"
)

BASENAME=$(basename "$FILE_PATH")

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if [[ "$BASENAME" == *"$pattern"* ]]; then
        echo "⚠️  Warning: Attempting to modify potentially sensitive file: $FILE_PATH" >&2
        echo "   Please review this operation carefully" >&2
        # Exit 1 for warning (non-blocking)
        exit 1
    fi
done

# Check for path traversal attempts
if [[ "$FILE_PATH" == *".."* ]]; then
    echo "⛔ Blocked: File path contains '..' (path traversal): $FILE_PATH" >&2
    # Exit 2 to block
    exit 2
fi

# All checks passed
exit 0
