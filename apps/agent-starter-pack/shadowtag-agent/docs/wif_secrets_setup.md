# WIF Secrets Setup Guide

## Required GitHub Actions Secrets

Navigate to your repository settings:
**GitHub → ShadowTag-v2/Monorepo-Uphillsnowball → Settings → Secrets and variables → Actions**

### Secrets (sensitive, encrypted)

| Secret Name | Value Source | Description |
|---|---|---|
| `WIF_POOL_ID` | `gcloud iam workload-identity-pools list --location=global --project=shadowtag-omega-v4` | Workload Identity Federation pool ID |
| `WIF_PROVIDER_ID` | `gcloud iam workload-identity-pools providers list --location=global --workload-identity-pool=<POOL_ID> --project=shadowtag-omega-v4` | WIF provider ID (GitHub OIDC) |
| `GCP_SERVICE_ACCOUNT` | Service account email | e.g. `github-actions@shadowtag-omega-v4.iam.gserviceaccount.com` |

### Variables (non-sensitive, plain text)

| Variable Name | Value | Description |
|---|---|---|
| `GCP_PROJECT_NUMBER` | `gcloud projects describe shadowtag-omega-v4 --format='value(projectNumber)'` | Numeric project ID |
| `CICD_PROJECT_ID` | `shadowtag-omega-v4` | GCP project for CI/CD |
| `STAGING_PROJECT_ID` | `shadowtag-omega-v4` | GCP project for staging |
| `PROD_PROJECT_ID` | `shadowtag-omega-v4` | GCP project for production |
| `REGION` | `us-central1` | GCP region |
| `ARTIFACT_REGISTRY_REPO_NAME` | `shadowtag-agent` | Artifact Registry repo |
| `CONTAINER_NAME` | `shadowtag-agent` | Docker container name |
| `LOGS_BUCKET_NAME_STAGING` | `shadowtag-omega-v4-staging-logs` | GCS bucket for load test results |

## Setup Commands

```bash
# 1. Create WIF pool (if not exists)
gcloud iam workload-identity-pools create github-actions \
  --location=global \
  --display-name="GitHub Actions Pool" \
  --project=shadowtag-omega-v4

# 2. Create OIDC provider for GitHub
gcloud iam workload-identity-pools providers create-oidc github \
  --location=global \
  --workload-identity-pool=github-actions \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='ShadowTag-v2/Monorepo-Uphillsnowball'" \
  --project=shadowtag-omega-v4

# 3. Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions SA" \
  --project=shadowtag-omega-v4

# 4. Grant required roles
gcloud projects add-iam-policy-binding shadowtag-omega-v4 \
  --member="serviceAccount:github-actions@shadowtag-omega-v4.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding shadowtag-omega-v4 \
  --member="serviceAccount:github-actions@shadowtag-omega-v4.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding shadowtag-omega-v4 \
  --member="serviceAccount:github-actions@shadowtag-omega-v4.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# 5. Allow WIF pool to impersonate the service account
gcloud iam service-accounts add-iam-policy-binding \
  github-actions@shadowtag-omega-v4.iam.gserviceaccount.com \
  --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe shadowtag-omega-v4 --format='value(projectNumber)')/locations/global/workloadIdentityPools/github-actions/attribute.repository/ShadowTag-v2/Monorepo-Uphillsnowball" \
  --role="roles/iam.workloadIdentityUser" \
  --project=shadowtag-omega-v4

# 6. Get the values to populate in GitHub
echo "WIF_POOL_ID: github-actions"
echo "WIF_PROVIDER_ID: github"
echo "GCP_SERVICE_ACCOUNT: github-actions@shadowtag-omega-v4.iam.gserviceaccount.com"
```
