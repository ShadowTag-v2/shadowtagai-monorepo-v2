# Secret Manager Rotation Procedure
# CounselConduit / ShadowTag-Omega-v4

## Overview

Secret Manager stores 23 secrets. Rotation is triggered by:
- **Automatic**: PubSub topic `secret-rotation-notifications` (when configured)
- **Manual**: Personnel change, exposure, or scheduled rotation
- **Incident**: Any suspected compromise → immediate rotation

## Rotation Steps

### 1. API Keys (GEMINI_API_KEY, STITCH_API_KEY, DEVELOPER_KNOWLEDGE_API_KEY)

```bash
# 1. Generate new key in respective console
# 2. Add new version to SM
gcloud secrets versions add <SECRET_NAME> --data-file=/dev/stdin --project=shadowtag-omega-v4
# 3. Test new key against production
# 4. Deploy Cloud Run with new key
gcloud run services update counselconduit --region=us-central1 --update-env-vars="..."
# 5. Disable old key in console
# 6. After 24h: Delete old key
```

### 2. Stripe Keys (stripe-secret-key, stripe-webhook-secret, stripe-publishable-key)

```bash
# 1. Roll in Stripe Dashboard → Developers → API keys
# 2. Update SM
echo "sk_live_..." | gcloud secrets versions add stripe-secret-key --data-file=- --project=shadowtag-omega-v4
echo "whsec_..." | gcloud secrets versions add stripe-webhook-secret --data-file=- --project=shadowtag-omega-v4
# 3. Redeploy Cloud Run
# 4. Verify webhook signature: POST /webhooks/stripe with test event
```

### 3. GitHub App PEMs (github-app-shadowtag-v2-pem, github-app-ehanc69-pem)

```bash
# 1. GitHub → Settings → Developer settings → GitHub Apps → Generate private key
# 2. Download new PEM
# 3. Upload to SM
gcloud secrets versions add github-app-shadowtag-v2-pem \
  --data-file=new-key.pem --project=shadowtag-omega-v4
# 4. Test: python scripts/auth_github_app.py --refresh
# 5. Delete old PEM from Downloads
# 6. Disable old key in GitHub App settings
```

### 4. OAuth Client (oauth-client-secret-gws-desktop)

```bash
# 1. GCP Console → APIs & Services → Credentials → Edit OAuth client
# 2. Click "Reset Secret"
# 3. Download new JSON
# 4. Upload: gcloud secrets versions add oauth-client-secret-gws-desktop \
#      --data-file=client_secret_*.json --project=shadowtag-omega-v4
# 5. Re-authenticate: gws auth login --client-file=new_client_secret.json
```

## Rotation Schedule

| Secret Category | Rotation Period | Trigger |
|----------------|----------------|---------|
| API Keys | 90 days | Calendar + exposure |
| Stripe Keys | 180 days | Calendar + exposure |
| GitHub PEMs | 365 days | Calendar + personnel |
| OAuth Client | On exposure only | Incident |

## Automation (Future)

- PubSub topic `secret-rotation-notifications` is created
- Cloud Function to handle rotation events (tofu `rotation` block)
- Alert on failed rotation attempts via Monitoring

## Verification

```bash
# List all secrets with versions
gcloud secrets list --project=shadowtag-omega-v4 --format="table(name,createTime)"

# Check version count
gcloud secrets versions list <SECRET_NAME> --project=shadowtag-omega-v4

# Validate active version
gcloud secrets versions access latest --secret=<SECRET_NAME> --project=shadowtag-omega-v4 | head -c 20
```
