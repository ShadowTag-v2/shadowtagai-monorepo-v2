#!/usr/bin/env bash
# Antigravity Loop Hook (Ralph Implementation)
# Ensures persistence by reinjecting the Master Plan context.

set -euo pipefail

# Read input
input=$(cat)

# Define the directive (Master Plan Injection)
read -r -d '' DIRECTIVE <<EOF || true
<executive_intervention>
CRITICAL CONTEXT:
You are operating in Antigravity "Heavy Lift" Mode.
Your persistence layer (Judge 6) requires you to complete the tasks in 'task.md'.

CURRENT OBJECTIVE:
Deploy Kafka Scaler & Push 200+ Repositories.

If you have completed a step, mark it in task.md.
If you are waiting for a long-running process, explain the monitoring plan.
DO NOT STOP until task.md is fully reconciled.
</executive_intervention>
EOF

# Output JSON
jq -n --arg directive "$DIRECTIVE" \
  '{
    decision: "allow",
    hookSpecificOutput: {
        hookEventName: "BeforeAgent",
        additionalContext: $directive
    }
  }'
