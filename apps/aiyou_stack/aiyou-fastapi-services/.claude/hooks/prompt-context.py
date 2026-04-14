#!/usr/bin/env python3
"""UserPromptSubmit hook - Adds contextual information to user prompts
"""

import json
import re
import sys
from datetime import datetime


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    prompt = input_data.get("prompt", "")

    # Check for sensitive patterns that should be blocked
    sensitive_patterns = [
        (r"(?i)\bpassword\s*[:=]\s*['\"]?[\w]+", "Prompt contains a password"),
        (r"(?i)\bapi[_-]?key\s*[:=]\s*['\"]?[\w]+", "Prompt contains an API key"),
        (r"(?i)\bsecret\s*[:=]\s*['\"]?[\w]+", "Prompt contains a secret"),
        (r"(?i)\btoken\s*[:=]\s*['\"]?[\w-]+", "Prompt contains a token"),
    ]

    for pattern, message in sensitive_patterns:
        if re.search(pattern, prompt):
            # Block the prompt and show reason to user
            output = {
                "decision": "block",
                "reason": f"🔒 Security policy violation: {message}. Please rephrase your request without including sensitive credentials.",
            }
            print(json.dumps(output))
            sys.exit(0)

    # Add contextual information
    context_parts = []

    # Add timestamp
    now = datetime.now()
    context_parts.append(f"[Timestamp: {now.strftime('%Y-%m-%d %H:%M:%S')}]")

    # Add project context
    context_parts.append("[Project: Claude Agent SDK Integration]")

    # Combine context
    context = "\n".join(context_parts)

    # Output context (will be added to the conversation)
    print(context)

    # Allow the prompt to proceed
    sys.exit(0)


if __name__ == "__main__":
    main()
