#!/usr/bin/env python3
"""PreToolUse hook for Bash - Validate bash commands for best practices and safety"""

import json
import re
import sys

# Define validation rules as a list of (regex pattern, message, severity) tuples
# severity: "error" (blocks), "warning" (suggests alternative)
VALIDATION_RULES = [
    (
        r"\bgrep\b(?!.*\|)",
        "Use 'rg' (ripgrep) instead of 'grep' for better performance and features",
        "error",
    ),
    (
        r"\bfind\s+\S+\s+-name\b",
        "Use 'rg --files | rg pattern' or 'rg --files -g pattern' instead of 'find -name' for better performance",
        "error",
    ),
    (r"\bcat\s+.*\.py\b", "Use Read tool instead of cat for reading Python files", "error"),
    (
        r"\bcat\s+.*\.(js|ts|json|md|txt)\b",
        "Use Read tool instead of cat for reading files",
        "error",
    ),
    (r"\brm\s+-rf\s+/", "Dangerous: Attempting to recursively delete from root directory", "error"),
    (
        r"\bchmod\s+777\b",
        "Security risk: Setting permissions to 777 makes files world-writable",
        "error",
    ),
    (r"\bcurl\s+.*\|\s*bash\b", "Security risk: Piping curl output to bash is dangerous", "error"),
]


def validate_command(command: str) -> tuple[list[str], list[str]]:
    """Validate a bash command against rules.
    Returns (errors, warnings) tuple.
    """
    errors = []
    warnings = []

    for pattern, message, severity in VALIDATION_RULES:
        if re.search(pattern, command):
            if severity == "error":
                errors.append(message)
            else:
                warnings.append(message)

    return errors, warnings


def main():
    try:
        # Load input from stdin
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        raise SystemExit(1)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Only process Bash tool calls
    if tool_name != "Bash" or not command:
        raise SystemExit(0)

    # Validate the command
    errors, warnings = validate_command(command)

    if errors:
        # Block the command and provide feedback to Claude
        for error in errors:
            print(f"❌ {error}", file=sys.stderr)
        # Exit code 2 blocks tool call and shows stderr to Claude
        raise SystemExit(2)

    if warnings:
        # Show warnings to user but allow command
        output = {
            "systemMessage": "⚠️  Command validation warnings:\n"
            + "\n".join(f"  • {w}" for w in warnings),
        }
        print(json.dumps(output))

    # Allow the command
    raise SystemExit(0)


if __name__ == "__main__":
    main()
