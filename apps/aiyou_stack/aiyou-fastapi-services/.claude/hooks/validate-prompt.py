#!/usr/bin/env python3
"""UserPromptSubmit hook - Validate user prompts and add context
"""

import datetime
import json
import re
import sys


def main():
    try:
        # Load input from stdin
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    prompt = input_data.get("prompt", "")

    # Check for sensitive patterns that might expose secrets
    sensitive_patterns = [
        (
            r"(?i)\b(password|api[_-]?key|secret[_-]?key|private[_-]?key|token)\s*[:=]\s*['\"]?[\w\-]+",
            "Prompt appears to contain hardcoded credentials",
        ),
        (r"(?i)-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----", "Prompt contains a private key"),
    ]

    for pattern, message in sensitive_patterns:
        if re.search(pattern, prompt):
            # Block the prompt for security
            output = {
                "decision": "block",
                "reason": f"Security policy violation: {message}. Please rephrase without including sensitive data.",
            }
            print(json.dumps(output))
            sys.exit(0)

    # Add helpful context
    context_parts = [
        f"Current timestamp: {datetime.datetime.now().isoformat()}",
    ]

    # Add project-specific context based on prompt content
    if re.search(r"(?i)\b(fastapi|api|endpoint|route)", prompt):
        context_parts.append(
            "Note: This is a FastAPI project. Use async/await patterns and FastAPI best practices.",
        )

    if re.search(r"(?i)\b(claude|agent|sdk)", prompt):
        context_parts.append(
            "Note: Project uses @anthropic-ai/claude-agent-sdk (npm 0.1.30) and claude-agent-sdk (pip 0.1.6).",
        )

    # Output context for Claude
    if context_parts:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "\n".join(context_parts),
            },
        }
        print(json.dumps(output))

    # Allow the prompt to proceed
    sys.exit(0)


if __name__ == "__main__":
    main()
