#!/usr/bin/env bash
# DLP Circuit Breaker — Pre-commit Hook
# Prevents proprietary identifiers from leaking into public search queries.
#
# Reference: GEMINI.md epistemic_airgap_doctrine -> DLP Circuit Breaker
# Install: Add to .pre-commit-config.yaml or run manually.
#
# Scans staged files for patterns that indicate corporate/internal identifiers
# that should NEVER appear in public search tools or committed code.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

VIOLATIONS=0

# Patterns that should NEVER appear in committed code or search queries
# These are internal identifiers that could leak IP
BANNED_PATTERNS=(
  # Internal service account emails (except the canonical ones in GEMINI.md)
  'iam\.gserviceaccount\.com'
  # Internal Cloud SQL connection strings
  '/cloudsql/shadowtag-omega-v4:'
  # Internal error trace format
  'File "/app/api/'
  # Raw internal IPs
  '10\.\d+\.\d+\.\d+'
  '172\.(1[6-9]|2[0-9]|3[01])\.'
  '192\.168\.'
)

# Patterns that are ALLOWED (canonical references in doctrine docs)
ALLOWED_FILES=(
  'GEMINI.md'
  'AGENTS.md'
  'BUSINESS_CONTEXT_LOCKED.md'
  'RISK_REGISTER.md'
  '.firebaserc'
  'firebase.json'
  '.betterleaksignore'
  '.gitleaksignore'
  'scripts/load_mcp_secrets.sh'
  'scripts/firebase_auth_health_check.sh'
  'scripts/dlp_circuit_breaker.sh'
  'docs/DEPLOYMENT_RUNBOOK.md'
  'docs/deployment.md'
  # Google Cloud skills reference docs — parameterized SA patterns from official docs
  '.agents/skills/cloud-sql-basics/references/'
  '.agents/skills/gke-basics/references/'
  '.agents/skills/cloud-run-basics/references/'
  '.agents/skills/firebase-basics/references/'
  '.agents/skills/google-cloud-recipe-auth/'
  '.agents/skills/alloydb-basics/references/'
  '.agents/skills/google-cloud-recipe-onboarding/'
)

echo "🔒 DLP Circuit Breaker — Scanning staged files..."

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || echo "")

if [[ -z "$STAGED_FILES" ]]; then
  echo -e "${GREEN}✅ No staged files to scan${NC}"
  exit 0
fi

for pattern in "${BANNED_PATTERNS[@]}"; do
  # Search staged files for the pattern
  while IFS= read -r file; do
    # Skip allowed doctrine files
    SKIP=false
    for allowed in "${ALLOWED_FILES[@]}"; do
      if [[ "$file" == *"$allowed"* ]]; then
        SKIP=true
        break
      fi
    done

    if [[ "$SKIP" == true ]]; then
      continue
    fi

    # Check if the pattern exists in the file's staged content
    if git show ":$file" 2>/dev/null | grep -qE "$pattern"; then
      echo -e "${RED}❌ DLP VIOLATION${NC} in $file"
      echo "   Pattern: $pattern"
      echo "   This file contains an internal identifier that must not be committed."
      echo "   Add to .betterleaksignore or refactor to use env vars."
      ((VIOLATIONS++))
    fi
  done <<< "$STAGED_FILES"
done

if [[ $VIOLATIONS -gt 0 ]]; then
  echo ""
  echo -e "${RED}❌ $VIOLATIONS DLP violations found. Commit blocked.${NC}"
  echo "   Fix: Move internal identifiers to environment variables or GCP Secret Manager."
  echo "   Override: git commit --no-verify (NOT RECOMMENDED)"
  exit 1
else
  echo -e "${GREEN}✅ DLP Circuit Breaker — No violations${NC}"
fi
