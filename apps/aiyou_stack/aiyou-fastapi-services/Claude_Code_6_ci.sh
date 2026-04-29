#!/bin/bash
# Judge Six: The CI Gatekeeper (Adapted from Gemini CLI Reviewer)
# Runs inside Cloud Build / GitHub Actions

echo ">>> ⚖️ JUDGE SIX IS IN SESSION."

# 1. Install Gemini CLI (if not present)
# Note: Using npx if installed, or checking global
if ! command -v gemini &> /dev/null; then
    echo "Gemini CLI not found. Installing..."
    npm install -g @google/gemini-cli
fi

# 2. Authenticate (Uses WIF/ADC - No Keys!)
echo "Authenticating via ADC..."
# Assumes 'gcloud auth login' or WIF is active on the host

# 3. Run The Review (YOLO Mode - Non-Interactive)
# It reads the diff and checks against your "Global Rules"
gemini --yolo <<EOF
You are Judge Six. Review the code changes in the current directory.
Reference the compliance rules in 'knowledge/compliance.md'.

Rules:
1. NO hardcoded secrets.
2. NO 'print' statements in production code (use BigLakeLogger).
3. Verify that 'JudgeSixLite' was called in any new 'Direct Write' logic.

If violations are found, EXIT with status 1.
If clean, output "VERDICT: APPROVED" and EXIT with status 0.
EOF
