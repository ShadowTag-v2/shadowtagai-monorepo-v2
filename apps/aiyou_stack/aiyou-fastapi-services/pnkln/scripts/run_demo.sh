#!/usr/bin/env bash
set -euo pipefail

echo "[pnkln] Running demo flow"
# Render a small prompt using env variables or defaults
INDUSTRY=${INDUSTRY:-"Healthcare"}
OUTCOME=${OUTCOME:-"Cut onboarding time by 50%"}

cat <<EOF > /tmp/pnkln_demo_prompt.txt
[ROLE]
You are a solutions engineer preparing a Vertex AI Studio demo.

[TASK]
Generate a 5-bullet outline for a demo focused on:
- ${INDUSTRY}
- ${OUTCOME}

[CONSTRAINTS]
- Keep total words under 120.
- Prefer concrete actions and measurable outcomes.
EOF

echo "[pnkln] Demo prompt written to /tmp/pnkln_demo_prompt.txt"
wc -w /tmp/pnkln_demo_prompt.txt || true
echo "[pnkln] Demo complete."
