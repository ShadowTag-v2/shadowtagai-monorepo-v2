#!/bin/bash
set -e

PROJECT_ID="shadowtag-omega-v2"
POOL_NAME="github-pool"
PROVIDER_NAME="github-provider"
SA_EMAIL="n-autoresearch/Kosmos/BioAgents-sa@${PROJECT_ID}.iam.gserviceaccount.com"
REPO_NAME="ShadowTag-v2/ShadowTag-v2-fastapi-services" # Derived from git remote

echo "⚡ ANTIGRAVITY GOD MODE: WIF REPAIR"
echo "-------------------------------------"
echo "Project: $PROJECT_ID"
echo "Pool:    $POOL_NAME"
echo "Provider:$PROVIDER_NAME"
echo "SA:      $SA_EMAIL"
echo "Repo:    $REPO_NAME"
echo "-------------------------------------"

# 1. Ensure Pool Exists
if ! gcloud iam workload-identity-pools describe "$POOL_NAME" --location="global" --project="$PROJECT_ID" > /dev/null 2>&1; then
    echo "Creating Pool '$POOL_NAME'..."
    gcloud iam workload-identity-pools create "$POOL_NAME" \
        --project="$PROJECT_ID" --location="global" \
        --display-name="GitHub Pool"
else
    echo "✅ Pool '$POOL_NAME' exists."
fi

# 2. Ensure Provider Exists
if ! gcloud iam workload-identity-pools providers describe "$PROVIDER_NAME" \
    --workload-identity-pool="$POOL_NAME" --location="global" --project="$PROJECT_ID" > /dev/null 2>&1; then
    echo "Creating Provider '$PROVIDER_NAME'..."
    gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_NAME" \
        --workload-identity-pool="$POOL_NAME" --location="global" --project="$PROJECT_ID" \
        --display-name="GitHub Provider" \
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
        --attribute-condition="assertion.repository_owner == 'ShadowTag-v2'" \
        --issuer-uri="https://token.actions.githubusercontent.com"
else
    echo "✅ Provider '$PROVIDER_NAME' exists."
fi

# 3. Ensure Service Account IAM Binding (The "Glue")
# We bind the REPO specifically to act as the Service Account
echo "Binding IAM policy for repo '$REPO_NAME'..."
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
    --project="$PROJECT_ID" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/$POOL_NAME/attribute.repository/$REPO_NAME"

echo "✅ WIF Configuration Repaired."
