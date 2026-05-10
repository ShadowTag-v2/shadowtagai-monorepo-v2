#!/bin/bash
# PostToolUse hook for Write/Edit - Format code after modifications

set -e

# Read the input JSON
INPUT=$(cat)

# Parse tool information
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_name', ''))")
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('file_path', ''))")

# Only process Write/Edit operations
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
    exit 0
fi

# Skip if no file path
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Skip if file doesn't exist
if [ ! -f "$FILE_PATH" ]; then
    exit 0
fi

# Get file extension
EXT="${FILE_PATH##*.}"

# Format based on file type
case "$EXT" in
    py)
        # Format Python files with black if available
        if command -v black &> /dev/null; then
            black --quiet "$FILE_PATH" 2>/dev/null || true
            echo "Formatted Python file with black: $FILE_PATH"
        fi
        ;;
    js|ts|jsx|tsx)
        # Format JavaScript/TypeScript with prettier if available
        if command -v prettier &> /dev/null; then
            prettier --write "$FILE_PATH" 2>/dev/null || true
            echo "Formatted JavaScript/TypeScript file with prettier: $FILE_PATH"
        fi
        ;;
    json)
        # Format JSON files with jq if available
        if command -v jq &> /dev/null; then
            TMP=$(mktemp)
            jq '.' "$FILE_PATH" > "$TMP" 2>/dev/null && mv "$TMP" "$FILE_PATH" || rm -f "$TMP"
            echo "Formatted JSON file with jq: $FILE_PATH"
        fi
        ;;
    sh)
        # Make shell scripts executable
        chmod +x "$FILE_PATH" 2>/dev/null || true
        echo "Made shell script executable: $FILE_PATH"
        ;;
esac

exit 0
