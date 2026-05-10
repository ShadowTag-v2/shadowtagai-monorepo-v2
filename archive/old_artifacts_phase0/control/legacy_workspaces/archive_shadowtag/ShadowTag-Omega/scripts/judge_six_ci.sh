#!/bin/bash
# Judge Six: The CI Gatekeeper
if ! command -v gemini &> /dev/null; then npm install -g @google/gemini-cli-beta; fi
gemini --yolo <<EOF
You are Judge Six. Review staged changes. Ref 'docs/codex/VOL_10_JUDGE_SIX.md'.
Rules: 1. NO hardcoded secrets. 2. NO 'print' statements. 3. Check for 'JudgeSixLite'.
Output: VERDICT: [APPROVED | REJECTED]
EOF
