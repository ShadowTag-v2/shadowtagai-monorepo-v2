#!/bin/bash
set -e

# Configuration
PROJECT_ID="acquired-jet-478701-b3"
REPO_OWNER="pikeymickey"
REPO_NAME="ShadowTag-v2-fastapi-services"
REGION="us-central1"

print_header() {
    echo "============================================================"
    echo "$1"
    echo "============================================================"
}

print_header "Cloud Build Trigger Setup"
echo "Project ID: $PROJECT_ID"
echo "Repository: $REPO_OWNER/$REPO_NAME"
echo "Region: $REGION"
echo ""

# Check for gcloud
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud is not installed or not in PATH."
    exit 1
fi

# Set project
echo "Setting project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

print_header "Creating 'antigravity-cd-main' Trigger"
echo "This trigger deploys the Orchestrator on push to 'main'."

# Explanation of the command:
# - name: Unique name for the trigger
# - repo-owner/repo-name: GitHub repository connection
# - branch-pattern: Regex for branch to match (^main$)
# - build-config: Path to the cloudbuild YAML file inside the repo
# - filters: specific substitutions or exclusions (ignored here)

gcloud builds triggers create github \
    --name="antigravity-cd-main" \
    --repo-owner="$REPO_OWNER" \
    --repo-name="$REPO_NAME" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild-antigravity.yaml" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --description="Deploy Antigravity Orchestrator on push to main" \
    --substitutions="_GEMINI_API_KEY=needs-manual-update" # Placeholder

echo "✅ Trigger 'antigravity-cd-main' created (or attempted)."

print_header "Creating 'antigravity-ci-pr' Trigger"
echo "This trigger runs CI checks on Pull Requests."

gcloud builds triggers create github \
    --name="antigravity-ci-pr" \
    --repo-owner="$REPO_OWNER" \
    --repo-name="$REPO_NAME" \
    --pull-request-pattern="^main$" \
    --build-config="cloudbuild.pr.yaml" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --description="Run CI checks on PRs targeting main"

echo "✅ Trigger 'antigravity-ci-pr' created (or attempted)."

print_header "Next Steps"
echo "1. Go to https://console.cloud.google.com/cloud-build/triggers?project=$PROJECT_ID"
echo "2. Verify the triggers are present and connected to the correct repository."
echo "3. Update any substitution variables (e.g. valid API keys or secrets) if needed."
echo "   - For 'antigravity-cd-main', check if any secrets are required."
