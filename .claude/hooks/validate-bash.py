#!/usr/bin/env python3
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
    # === Original patterns ===
    r"\brm\s+-rf\s+/",
    r"\bsudo\s+rm\s+-rf",
    r"\bchmod\s+-R\s+777",
    # === Production DB destruction (Faramesh-style enforcement) ===
    r"\bDROP\s+(DATABASE|TABLE|SCHEMA)\b",
    r"\bTRUNCATE\s+TABLE\b",
    r"\bDELETE\s+FROM\s+\w+\s*;",  # Unqualified DELETE (no WHERE)
    # === Infrastructure destruction ===
    r"\bterraform\s+destroy\b",
    r"\bkubectl\s+delete\s+(namespace|ns|cluster)",
    r"\bgcloud\s+.*\s+delete\s+",
    r"\baws\s+.*\s+delete-",
    # === Secret exfiltration ===
    r"\bcat\s+.*\.env\s*\|.*curl\b",
    r"\bcurl\s+.*--data.*\$\(",
    r"\bbase64\s+.*\.env\b",
    r"/proc/.*/environ",
    # === Kernel/system modification ===
    r"\bzmodload\b",
    r"\binsmod\b",
    r"\bmodprobe\b",
    # === LD injection ===
    r"\bLD_PRELOAD=",
    r"\bDYLD_INSERT_LIBRARIES=",
    r"\bLD_LIBRARY_PATH=.*\bcurl\b",
]

# === 50-SUBCOMMAND COMPOUND COMMAND CHECK ===
# Source: bashPermissions.ts:103 — MAX_SUBCOMMANDS_FOR_SECURITY_CHECK = 50
# Above 50 subcommands, Claude Code falls to 'ask' mode (safe default).
# The Adversa vulnerability: auto-rejection rules don't apply beyond 50.
# We defensively BLOCK compound commands with >50 subcommands.
MAX_COMPOUND_SUBCOMMANDS = 50



def validate_command(command: str) -> tuple[list[str], bool]:
    """
    Validate a bash command.

    Returns:
        tuple: (list of issues, should_block)
    """
    issues = []
    should_block = False

    # === ADVERSA VULNERABILITY MITIGATION ===
    # Check compound command subcommand count (bashPermissions.ts:103)
    # Beyond 50 subcommands, auto-rejection rules don't apply
    subcommands = re.split(r'\s*(?:&&|\|\||;|\|)\s*', command)
    if len(subcommands) > MAX_COMPOUND_SUBCOMMANDS:
        should_block = True
        issues.append(
            f"BLOCKED: Compound command has {len(subcommands)} subcommands "
            f"(max {MAX_COMPOUND_SUBCOMMANDS}). "
            "This bypasses the auto-rejection pipeline."
        )

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
