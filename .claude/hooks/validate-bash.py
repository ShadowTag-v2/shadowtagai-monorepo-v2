#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
PreToolUse hook for Bash - Validates commands and suggests better alternatives
"""

import json
import re
import sys

# Define validation rules as a list of (regex pattern, message) tuples
VALIDATION_RULES = [
    (
        r"\bgrep\b(?!.*--)",
        "Consider using 'rg' (ripgrep) instead of 'grep' for better performance",
    ),
    (
        r"\bfind\s+\S+\s+-name\b",
        "Consider using Glob tool or 'rg --files -g pattern' instead of 'find -name'",
    ),
    (
        r"\bcat\s+[^|>]+$",
        "Consider using Read tool instead of 'cat' for reading files",
    ),
    (
        r"\bsed\s+-i",
        "Consider using Edit tool instead of 'sed -i' for file modifications",
    ),
    (
        r"\brm\s+-rf\s+/",
        "DANGER: Attempting to remove from root directory - BLOCKING",
    ),
    (
        r">[>]?\s*/dev/null\s+2>&1\s*$",
        "Suppressing all output - consider if this is necessary for debugging",
    ),
]

# Patterns that should block the command
BLOCKING_PATTERNS = [
    r"\brm\s+-rf\s+/",
    r"\bsudo\s+rm\s+-rf",
    r"\bchmod\s+-R\s+777",
]


def validate_command(command: str) -> tuple[list[str], bool]:
    """
    Validate a bash command.

    Returns:
        tuple: (list of issues, should_block)
    """
    issues = []
    should_block = False

    # Check blocking patterns first
    for pattern in BLOCKING_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            should_block = True
            issues.append(f"BLOCKED: Dangerous command pattern detected: {pattern}")

    # Check validation rules
    for pattern, message in VALIDATION_RULES:
        if re.search(pattern, command):
            if "DANGER" in message or "BLOCKING" in message:
                should_block = True
            issues.append(f"• {message}")

    return issues, should_block


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    if tool_name != "Bash" or not command:
        # Not a Bash command, allow it
        sys.exit(0)

    # Validate the command
    issues, should_block = validate_command(command)

    if issues:
        for message in issues:
            print(message, file=sys.stderr)

        if should_block:
            # Exit code 2 blocks tool call and shows stderr to Claude
            sys.exit(2)
        else:
            # Exit code 1 shows warning but doesn't block
            sys.exit(1)

    # No issues, allow the command
    sys.exit(0)


if __name__ == "__main__":
    main()
