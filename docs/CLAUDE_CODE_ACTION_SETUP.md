# GitHub Secrets Required for Claude Code Action

## Required GitHub Secrets

### For GCP Vertex AI (OIDC) Authentication
These are needed for the Claude Code Action to authenticate via Vertex AI:

```
GCP_WORKLOAD_IDENTITY_PROVIDER  →  projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/<POOL_ID>/providers/<PROVIDER_ID>
GCP_SERVICE_ACCOUNT             →  claude-code-action@shadowtag-omega-v4.iam.gserviceaccount.com
```

### For GitHub App Token Generation
These use the existing ShadowTag GitHub App:

```
SHADOWTAG_APP_ID   →  3018200  (set as GitHub Actions variable, not secret)
SHADOWTAG_APP_PEM  →  <contents of antigravity-shadowtag-manager PEM>
```

## Setup Steps

### 1. Create GCP Service Account
```bash
gcloud iam service-accounts create claude-code-action \
  --display-name="Claude Code Action CI" \
  --project=shadowtag-omega-v4
```

### 2. Grant Vertex AI Permissions
```bash
gcloud projects add-iam-policy-binding shadowtag-omega-v4 \
  --member="serviceAccount:claude-code-action@shadowtag-omega-v4.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### 3. Create Workload Identity Pool
```bash
gcloud iam workload-identity-pools create github-actions-pool \
  --location="global" \
  --display-name="GitHub Actions Pool" \
  --project=shadowtag-omega-v4

gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location="global" \
  --workload-identity-pool="github-actions-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --project=shadowtag-omega-v4
```

### 4. Bind Service Account to Workload Identity
```bash
gcloud iam service-accounts add-iam-policy-binding \
  claude-code-action@shadowtag-omega-v4.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/ShadowTag-v2/Monorepo-Uphillsnowball" \
  --project=shadowtag-omega-v4
```

### 5. Set GitHub Secrets
```bash
# In GitHub repo settings → Secrets and variables → Actions
# Secrets:
#   GCP_WORKLOAD_IDENTITY_PROVIDER = <full provider path from step 3>
#   GCP_SERVICE_ACCOUNT = claude-code-action@shadowtag-omega-v4.iam.gserviceaccount.com
#   SHADOWTAG_APP_PEM = <PEM file contents>
# Variables:
#   SHADOWTAG_APP_ID = 3018200
```

### 6. Generate GitHub Token for Local MCP
For the local GitHub MCP server, generate a token:
```bash
# Option A: Use the GitHub App to generate an installation token
python3 scripts/auth_github_app.py --token-only

# Option B: Create a fine-grained PAT for local MCP use only
# Scopes: repo, issues:write, pull-requests:write
# Store in .env as GITHUB_PERSONAL_ACCESS_TOKEN
```
