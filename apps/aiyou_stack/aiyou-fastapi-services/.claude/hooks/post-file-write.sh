#!/bin/bash
# PostToolUse hook for Write/Edit - Auto-formats files after writing

set -e

# Read hook input from stdin
INPUT=$(cat)

# Extract file path and tool response
EXTRACT_INFO=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tool_input = data.get('tool_input', {})
    tool_response = data.get('tool_response', {})
    file_path = tool_input.get('file_path', '')
    success = tool_response.get('success', False)
    print(f'{file_path}|{success}')
except Exception as e:
    print('|False')
")

FILE_PATH=$(echo "$EXTRACT_INFO" | cut -d'|' -f1)
SUCCESS=$(echo "$EXTRACT_INFO" | cut -d'|' -f2)

if [ "$SUCCESS" != "True" ] || [ -z "$FILE_PATH" ]; then
    # Tool didn't succeed or no file path, nothing to do
    exit 0
fi

if [ ! -f "$FILE_PATH" ]; then
    # File doesn't exist, nothing to format
    exit 0
fi

FORMATTED=false
FILE_EXT="${FILE_PATH##*.}"

# Format based on file extension
case "$FILE_EXT" in
    py)
        # Format Python files with black (if available)
        if command -v black &> /dev/null; then
            echo "Formatting Python file with black: $FILE_PATH"
            black --quiet "$FILE_PATH" 2>/dev/null || true
            FORMATTED=true
        fi
        # Also run isort if available
        if command -v isort &> /dev/null; then
            echo "Sorting imports with isort: $FILE_PATH"
            isort --quiet "$FILE_PATH" 2>/dev/null || true
            FORMATTED=true
        fi
        ;;

    js|jsx|ts|tsx)
        # Format JavaScript/TypeScript files with prettier (if available)
        if command -v prettier &> /dev/null; then
            echo "Formatting JS/TS file with prettier: $FILE_PATH"
            prettier --write "$FILE_PATH" 2>/dev/null || true
            FORMATTED=true
        fi
        ;;

    json)
        # Format JSON files with jq or python (if available)
        if command -v jq &> /dev/null; then
            echo "Formatting JSON file with jq: $FILE_PATH"
            TMP_FILE=$(mktemp)
            jq '.' "$FILE_PATH" > "$TMP_FILE" 2>/dev/null && mv "$TMP_FILE" "$FILE_PATH" || rm -f "$TMP_FILE"
            FORMATTED=true
        elif command -v python3 &> /dev/null; then
            echo "Formatting JSON file with python: $FILE_PATH"
            python3 -m json.tool "$FILE_PATH" > "${FILE_PATH}.tmp" 2>/dev/null && mv "${FILE_PATH}.tmp" "$FILE_PATH" || rm -f "${FILE_PATH}.tmp"
            FORMATTED=true
        fi
        ;;

    md|mdx)
        # Format Markdown files with prettier (if available)
        if command -v prettier &> /dev/null; then
            echo "Formatting Markdown file with prettier: $FILE_PATH"
            prettier --write "$FILE_PATH" 2>/dev/null || true
            FORMATTED=true
        fi
        ;;
esac

if [ "$FORMATTED" = true ]; then
    echo "✓ File formatted successfully: $FILE_PATH"
else
    # No formatter available for this file type
    exit 0
fi

exit 0
