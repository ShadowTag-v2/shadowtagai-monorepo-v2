#!/bin/bash
# Configures Workload Identity Federation + IAM for the Antigravity orchestrator SA.
# Usage: bash scripts/setup_wif.sh
set -euo pipefail

PROJECT="${GCP_PROJECT:-shadowtag-omega-v4}"
SA_NAME="antigravity-stitch-bot"
SA_EMAIL="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"

echo "🔧 Configuring Workload Identity Federation (ADC) for ${PROJECT}..."

# Create SA if it doesn't exist
gcloud iam service-accounts create "${SA_NAME}" \
    --description="Antigravity Autonomous Orchestrator — MCP + CI/CD" \
    --display-name="Antigravity Stitch Bot" \
    --project="${PROJECT}" 2>/dev/null || true

# Bind REAL GCP IAM roles (roles/jules.mcpInvoker was fabricated — replaced with actual roles)
ROLES=(
    "roles/run.invoker"                # Invoke Cloud Run services
    "roles/cloudfunctions.invoker"     # Invoke Cloud Functions (Gen2)
    "roles/firebasehosting.admin"      # Deploy to Firebase Hosting
    "roles/datastore.user"             # Read/write Firestore documents
    "roles/secretmanager.secretAccessor" # Access secrets from Secret Manager
    "roles/logging.logWriter"          # Write structured logs
    "roles/monitoring.metricWriter"    # Write custom metrics
)

for ROLE in "${ROLES[@]}"; do
    echo "  → Binding ${ROLE}..."
    gcloud projects add-iam-policy-binding "${PROJECT}" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="${ROLE}" \
        --condition=None \
        --quiet 2>/dev/null || echo "  ⚠️  ${ROLE} binding failed (may already exist)"
done

echo "✅ IAM bindings configured for ${SA_EMAIL}"
echo ""
echo "To verify:"
echo "  gcloud projects get-iam-policy ${PROJECT} --flatten='bindings[].members' --filter='bindings.members:${SA_EMAIL}' --format='table(bindings.role)'"
