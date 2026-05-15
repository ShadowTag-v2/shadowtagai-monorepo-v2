#!/usr/bin/env bash

# setup_sonar_integration.sh – Install and run SonarQube scanner for this repo
# ---------------------------------------------------------------
# Prerequisites:
#   * SonarQube server URL (default: http://localhost:9000)
#   * Sonar token with "Execute Analysis" permission (set via SONAR_TOKEN env var)
#   * sonar-scanner binary installed (brew install sonar-scanner on macOS)
#
# This script will:
#   1. Verify required tools are present.
#   2. Generate a minimal sonar-project.properties if missing.
#   3. Run sonar-scanner against the current repository.
#
# Usage: ./scripts/setup_sonar_integration.sh
# ---------------------------------------------------------------
set -euo pipefail

# ---- Configuration ------------------------------------------------
SONAR_HOST_URL="${SONAR_HOST_URL:-http://localhost:9000}"
SONAR_TOKEN="${SONAR_TOKEN:-}"  # Export SONAR_TOKEN in your shell or CI env
PROJECT_KEY="${PROJECT_KEY:-$(basename "$(git rev-parse --show-toplevel)")}"  # default to repo folder name
PROJECT_NAME="${PROJECT_NAME:-$PROJECT_KEY}"

# ---- Helper functions --------------------------------------------
log() { echo "[setup_sonar] $*"; }

check_command() {
  command -v "$1" >/dev/null 2>&1 || { log "ERROR: $1 is not installed. Install it and retry."; exit 1; }
}

# ---- Verify prerequisites ----------------------------------------
check_command git
check_command sonar-scanner

if [[ -z "$SONAR_TOKEN" ]]; then
  log "ERROR: SONAR_TOKEN environment variable is not set."
  log "Export it with a token that has Execute Analysis permission."
  exit 1
fi

# ---- Ensure sonar-project.properties exists ----------------------
if [[ ! -f sonar-project.properties ]]; then
  log "Creating default sonar-project.properties..."
  cat > sonar-project.properties <<EOF
sonar.projectKey=$PROJECT_KEY
sonar.projectName=$PROJECT_NAME
sonar.sources=.
sonar.host.url=$SONAR_HOST_URL
sonar.login=$SONAR_TOKEN
EOF
  log "Created sonar-project.properties"
else
  log "sonar-project.properties already present – using existing file."
fi

# ---- Run analysis ------------------------------------------------
log "Running sonar-scanner..."
sonar-scanner
log "SonarQube analysis completed. Check your server at $SONAR_HOST_URL/dashboard?id=$PROJECT_KEY"
