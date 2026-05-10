# Workload Identity Federation (WIF) Secrets Setup

> **Project:** `shadowtag-omega-v4`
> **Repository:** `ShadowTag-v2/Monorepo-Uphillsnowball`

## Prerequisites

1. GCP project `shadowtag-omega-v4` with Workload Identity Pool configured
2. GitHub repository with Actions enabled
3. `gh` CLI authenticated with repo admin access

## Required GitHub Actions Secrets

Set these via `gh` CLI or GitHub Settings → Secrets → Actions:

```bash
# 1. Workload Identity Pool ID
gh secret set WIF_POOL_ID \
  --repo ShadowTag-v2/Monorepo-Uphillsnowball \
  --body "projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/github-pool"

# 2. Workload Identity Provider ID
gh secret set WIF_PROVIDER_ID \
  --repo ShadowTag-v2/Monorepo-Uphillsnowball \
  --body "projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/github-pool/providers/github-provider"

# 3. GCP Service Account
gh secret set GCP_SERVICE_ACCOUNT \
  --repo ShadowTag-v2/Monorepo-Uphillsnowball \
  --body "github-actions@shadowtag-omega-v4.iam.gserviceaccount.com"
```

## GCP Setup Commands

```bash
# Create Workload Identity Pool
gcloud iam workload-identity-pools create github-pool \
  --project=shadowtag-omega-v4 \
  --location=global \
  --display-name="GitHub Actions Pool"

# Create OIDC Provider
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --project=shadowtag-omega-v4 \
  --location=global \
  --workload-identity-pool=github-pool \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Create Service Account
gcloud iam service-accounts create github-actions \
  --project=shadowtag-omega-v4 \
  --display-name="GitHub Actions SA"

# Grant roles
gcloud projects add-iam-policy-binding shadowtag-omega-v4 \
  --member="serviceAccount:github-actions@shadowtag-omega-v4.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding shadowtag-omega-v4 \
  --member="serviceAccount:github-actions@shadowtag-omega-v4.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding shadowtag-omega-v4 \
  --member="serviceAccount:github-actions@shadowtag-omega-v4.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Allow GitHub Actions to impersonate the SA
gcloud iam service-accounts add-iam-policy-binding \
  github-actions@shadowtag-omega-v4.iam.gserviceaccount.com \
  --project=shadowtag-omega-v4 \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/github-pool/attribute.repository/ShadowTag-v2/Monorepo-Uphillsnowball"
```

## GitHub Actions Usage

```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER_ID }}
    service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}
```

## Verification

```bash
# Verify pool exists
gcloud iam workload-identity-pools describe github-pool \
  --project=shadowtag-omega-v4 --location=global

# Verify provider
gcloud iam workload-identity-pools providers describe github-provider \
  --project=shadowtag-omega-v4 --location=global \
  --workload-identity-pool=github-pool

# Verify SA bindings
gcloud iam service-accounts get-iam-policy \
  github-actions@shadowtag-omega-v4.iam.gserviceaccount.com \
  --project=shadowtag-omega-v4
```
