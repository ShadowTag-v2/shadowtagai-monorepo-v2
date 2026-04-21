# Custom Domain SSL — CounselConduit API

## Current State
- API served at: `counselconduit-767252945109.us-central1.run.app` (Google-managed SSL)
- No custom domain configured

## Setting Up Custom Domain

### Option A: Cloud Run Domain Mapping (Simple)
```bash
gcloud beta run domain-mappings create \
  --service=counselconduit \
  --domain=api.counselconduit.com \
  --region=us-central1

# Follow DNS verification instructions from output
# Add CNAME record: api.counselconduit.com → ghs.googlehosted.com
```

### Option B: Global Load Balancer (Advanced)
Better for multi-region, custom WAF, and CDN:

```bash
# 1. Create NEG (serverless)
gcloud compute network-endpoint-groups create counselconduit-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=counselconduit

# 2. Create backend service
gcloud compute backend-services create counselconduit-backend \
  --global --load-balancing-scheme=EXTERNAL_MANAGED
gcloud compute backend-services add-backend counselconduit-backend \
  --global --network-endpoint-group=counselconduit-neg \
  --network-endpoint-group-region=us-central1

# 3. Create URL map
gcloud compute url-maps create counselconduit-urlmap \
  --default-service=counselconduit-backend

# 4. Create managed SSL certificate
gcloud compute ssl-certificates create counselconduit-ssl \
  --domains=api.counselconduit.com \
  --global

# 5. Create HTTPS proxy and forwarding rule
gcloud compute target-https-proxies create counselconduit-proxy \
  --ssl-certificates=counselconduit-ssl \
  --url-map=counselconduit-urlmap
gcloud compute forwarding-rules create counselconduit-https \
  --global --target-https-proxy=counselconduit-proxy \
  --ports=443
```

### DNS Configuration
| Record | Type | Value |
|--------|------|-------|
| `api.counselconduit.com` | CNAME | `ghs.googlehosted.com` (Option A) |
| `api.counselconduit.com` | A | Load balancer IP (Option B) |

### SSL Features (Google-Managed)
- Auto-renewed certificates
- TLS 1.2+ only
- HSTS header via Cloud Run
- No certificate management needed

## Prerequisites
1. Domain `counselconduit.com` must be registered and verified
2. DNS must be pointed to appropriate Google endpoint
3. Certificate provisioning takes 15-30 minutes
