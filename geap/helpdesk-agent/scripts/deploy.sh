#!/usr/bin/env bash
# GEAP Part 3-4 Deployment Script
# Deploys the IT Helpdesk Agent to Vertex AI Agent Runtime
#
# Usage:
#   # With Service Account (Part 3):
#   bash scripts/deploy.sh
#
#   # With Agent Identity (Part 4 - production):
#   bash scripts/deploy.sh --agent-identity
#
# Prerequisites:
#   1. gcloud configured with shadowtag-omega-v4
#   2. helpdesk-agent-sa service account created (Part 3)
#   3. agents-cli installed (pip install google-agents-cli)
#
# Reference: GEAP Tutorial Parts 3-4

set -euo pipefail

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-shadowtag-omega-v4}"
REGION="${GOOGLE_CLOUD_REGION:-us-central1}"
SA_NAME="helpdesk-agent-sa"

echo "=== GEAP Helpdesk Agent Deployment ==="
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo ""

# --- Step 1: Ensure Service Account exists (Part 3) ---
echo "[1/4] Checking service account..."
if ! gcloud iam service-accounts describe "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --project="$PROJECT_ID" &>/dev/null; then
    echo "  Creating service account: $SA_NAME"
    gcloud iam service-accounts create "$SA_NAME" \
        --description="Service account for IT Helpdesk Agent" \
        --display-name="Helpdesk Agent SA" \
        --project="$PROJECT_ID"

    # Grant Vertex AI User
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/aiplatform.user" \
        --quiet

    # Grant Datastore User (Firestore)
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --role="roles/datastore.user" \
        --quiet

    echo "  ✅ Service account created with aiplatform.user + datastore.user"
else
    echo "  ✅ Service account already exists"
fi

# --- Step 2: Deploy ---
echo ""
if [[ "${1:-}" == "--agent-identity" ]]; then
    echo "[2/4] Deploying with Agent Identity (Part 4 — SPIFFE)..."
    CI=true agents-cli deploy \
        --agent-identity \
        --region "$REGION" \
        --non-interactive
else
    echo "[2/4] Deploying with Service Account (Part 3)..."
    CI=true agents-cli deploy \
        --service-account "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
        --region "$REGION" \
        --non-interactive
fi

# --- Step 3: Extract Runtime ID ---
echo ""
echo "[3/4] Deployment metadata:"
if [ -f deployment_metadata.json ]; then
    cat deployment_metadata.json
    RUNTIME_ID=$(python3 -c "import json; print(json.load(open('deployment_metadata.json'))['remote_agent_runtime_id'])" 2>/dev/null || echo "unknown")
    echo ""
    echo "  Agent Runtime ID: $RUNTIME_ID"
else
    echo "  ⚠️ deployment_metadata.json not found"
fi

# --- Step 4: Summary ---
echo ""
echo "[4/4] ✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "  1. Test in Playground: https://console.cloud.google.com/vertex-ai/agents"
echo "  2. Check Sessions tab for automatic session persistence"
echo "  3. Check Memories tab (30-60s delay for extraction)"
echo "  4. Verify in Agent Registry for auto-registration"
if [[ "${1:-}" == "--agent-identity" ]]; then
    echo "  5. Grant Agent Identity IAM roles for tool access:"
    echo "     - Copy Principal ID from Identity tab"
    echo "     - Grant Cloud Datastore User in IAM"
fi
