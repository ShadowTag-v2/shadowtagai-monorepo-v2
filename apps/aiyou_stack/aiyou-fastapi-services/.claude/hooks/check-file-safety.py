#!/usr/bin/env python3
"""PreToolUse hook for Write/Edit - Check file operations for safety"""

import json
import os
import re
import sys

# Files and patterns to protect from modification
PROTECTED_PATTERNS = [
    r"\.env$",
    r"\.env\..*$",
    r"credentials\.json$",
    r"\.pem$",
    r"\.key$",
    r"id_rsa",
    r"\.ssh/",
]

# Directories that should be protected
PROTECTED_DIRS = [
    ".git/config",
    ".git/hooks",
]


def is_protected_file(file_path: str) -> tuple[bool, str]:
    """Check if a file is protected from modification.
    Returns (is_protected, reason) tuple.
    """
    # Check for path traversal
    if ".." in file_path:
        return True, "Path traversal detected (..) - security risk"

    # Normalize path
    normalized = os.path.normpath(file_path)

    # Check against protected patterns
    for pattern in PROTECTED_PATTERNS:
        if re.search(pattern, normalized):
            return True, f"File matches protected pattern: {pattern}"

    # Check against protected directories
    for protected_dir in PROTECTED_DIRS:
        if protected_dir in normalized:
            return True, f"File is in protected directory: {protected_dir}"

    return False, ""


def check_content_safety(content: str, file_path: str) -> tuple[bool, str]:
    """Check if file content contains potentially dangerous or sensitive data.
    Returns (has_issue, warning) tuple.
    """
    warnings = []

    # Check for potential secrets in code
    if re.search(r"(?i)(password|api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"][\w\-]{8,}", content):
        warnings.append("Content may contain hardcoded credentials")

    # Check for private keys
    if re.search(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----", content):
        warnings.append("Content contains a private key")

    # Warn about world-writable permissions in scripts
    if file_path.endswith(".sh") and re.search(r"chmod\s+777", content):
        warnings.append("Script sets world-writable permissions (777)")

    return len(warnings) > 0, "\n".join(warnings)


def main():
    try:
        # Load input from stdin
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        raise SystemExit(1)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only process Write/Edit tool calls
    if tool_name not in ["Write", "Edit"]:
        raise SystemExit(0)

    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "") or tool_input.get("new_string", "")

    if not file_path:
        raise SystemExit(0)

    # Check if file is protected
    is_protected, reason = is_protected_file(file_path)
    if is_protected:
        # Block the operation
        print(f"❌ File operation blocked: {reason}", file=sys.stderr)
        print(f"   File: {file_path}", file=sys.stderr)
        raise SystemExit(2)

    # Check content safety
    has_issue, warning = check_content_safety(content, file_path)
    if has_issue:
        # Show warning but allow operation
        output = {
            "systemMessage": f"⚠️  Content safety warning:\n{warning}\n\nConsider reviewing the file before committing.",
        }
        print(json.dumps(output))

    # Allow the operation
    raise SystemExit(0)


if __name__ == "__main__":
    main()
