#!/usr/bin/env bash
# Read hook input from stdin
input=$(cat)

# Extract content being written using jq
content=$(echo "$input" | jq -r '.tool_input.content // .tool_input.new_string // ""')

# Check for common secret patterns (extended for Google/AWS/Azure)
if echo "$content" | grep -qE 'api[_-]?key|password|secret|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z-_]{35}|ghp_[0-9a-zA-Z]{36}'; then
  # Return structured denial to the agent
  cat <<EOF
{
  "decision": "deny",
  "reason": "Security Policy: Potential secret detected in content (API Key / Credential).",
  "systemMessage": "Security scanner blocked operation: Judge 6 enforcement."
}
EOF
  exit 0
fi

# Allow the operation
echo '{"decision": "allow"}'
exit 0
