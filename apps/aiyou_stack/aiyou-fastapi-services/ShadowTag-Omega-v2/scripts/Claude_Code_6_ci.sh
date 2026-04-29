#!/bin/bash
# Judge Six: CI Gatekeeper (Gemini CLI Wrapper)
echo ">>> ⚖️ JUDGE SIX: REVIEWING DIFF..."
if ! command -v gemini &> /dev/null; then npm install -g @google/gemini-cli-beta; fi

# The "YOLO" prompt from the Medium Article
gemini --yolo <<EOF
You are Judge Six. Review these changes.
Reference 'docs/doctrine/COMPLIANCE.md'.
Rules:
1. NO Hardcoded Secrets.
2. NO 'print' in Prod.
3. Verify 'JudgeSixLite' usage.
Output: VERDICT: [APPROVED | REJECTED]
EOF
