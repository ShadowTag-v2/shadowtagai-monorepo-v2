# Production Runbook — CounselConduit + ShadowTag Portfolio

> Last updated: 2026-04-18 | Version: v9.3 | Commit: `7d2a2e180f9`

## Service Inventory

| Service | URL | Runtime | Status |
|---------|-----|---------|--------|
| CounselConduit API | `counselconduit-767252945109.us-central1.run.app` | Cloud Run | ✅ LIVE (v3.1.0) |
| KovelAI Landing | `kovelai.web.app` | Firebase Hosting | ✅ LIVE |
| ShadowTagAI Landing | `shadowtagai.web.app` | Firebase Hosting | ✅ LIVE |
| ShadowTag Omega | `shadowtag-omega-v4.web.app` | Firebase Hosting | ✅ LIVE |
| Firestore (default) | GCP Console | Firestore | ✅ Active |
| Firestore (shadowtag-engine) | GCP Console | Firestore | ✅ Active |

## Critical Credentials

| Credential | Location | Rotation Schedule |
|-----------|----------|-------------------|
| GitHub App PEM | `$SHADOWTAG_PEM` → `~/Downloads/antigravity-shadowtag-*.pem` | On exposure/incident |
| Gemini API Key | GCP Secret Manager → `gemini-api-key` | Quarterly |
| Stripe Secret Key | GCP Secret Manager → `stripe-secret-key` | On exposure/incident |
| Stripe Webhook Secret | GCP Secret Manager → `stripe-webhook-secret` | On exposure/incident |
| Developer Knowledge API Key | GCP Secret Manager → `developer-knowledge-api-key` | Quarterly |

> **Full rotation procedure**: `docs/SECRET_ROTATION.md`

## Deployment Procedures

### Cloud Run (CounselConduit)

```bash
# 1. Verify auth
gcloud auth print-identity-token --quiet

# 2. Deploy from source (NO Docker — per SaaS Architecture Gate)
gcloud run deploy counselconduit \
  --project shadowtag-omega-v4 \
  --region us-central1 \
  --source apps/counselconduit/ \
  --service-account counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com \
  --allow-unauthenticated=false \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10

# 3. Verify
curl -s -o /dev/null -w "%{http_code}" https://counselconduit-767252945109.us-central1.run.app/health
```

### Firebase Hosting (KovelAI / ShadowTagAI)

```bash
# Per Firebase MCP-First Deployment Protocol (GEMINI.md v9.0):
# 1. Verify MCP auth (call firebase_get_environment)
# 2. Read hosting guide (firebase://guides/init/hosting)
# 3. Initialize (firebase_init)
# 4. Deploy

firebase deploy --only hosting:kovelai --project shadowtag-omega-v4
firebase deploy --only hosting:shadowtagai --project shadowtag-omega-v4
```

## Monitoring & Alerts

### GCP Alert Policies (8 active)
| Alert | Threshold | Channel |
|-------|-----------|---------|
| Cloud Run Error Rate | > 5% in 5min | founder@shadowtagai.com |
| Cloud Run Latency | > 2s p95 in 5min | founder@shadowtagai.com |
| Firestore Read Spike | > 10K reads/5min | founder@shadowtagai.com |
| Firestore Write Spike | > 5K writes/5min | founder@shadowtagai.com |
| Secret Access Anomaly | Log metric | founder@shadowtagai.com |
| Budget Alert | 50%/90%/100% | founder@shadowtagai.com |
| Cloud Armor WAF Block | > 100 blocks/5min | founder@shadowtagai.com |
| Uptime Check Failure | 2 consecutive | founder@shadowtagai.com |

### Cloud Armor WAF Rules
| Rule | Action | Priority |
|------|--------|----------|
| Rate limit | 100 req/min/IP, 5min ban | 1000 |
| SQL injection | Block | 2000 |
| XSS | Block | 2001 |
| Remote file inclusion | Block | 2002 |

## Incident Response

### Severity Levels
| Level | Definition | Response Time |
|-------|-----------|---------------|
| P0 — Critical | Service down, data breach, credential exposure | Immediate |
| P1 — High | Degraded service, elevated error rate | 1 hour |
| P2 — Medium | Feature broken, non-critical service issue | 4 hours |
| P3 — Low | Cosmetic, documentation, minor bug | Next business day |

### P0 Response Checklist
1. **Triage**: Check GCP Console → Cloud Run → Logs
2. **Contain**: If credential exposure → rotate immediately (`docs/SECRET_ROTATION.md`)
3. **Communicate**: Alert founder via Google Chat space
4. **Fix**: Hotfix branch → test → deploy
5. **Post-mortem**: Document in `RISK_REGISTER.md`

### Rollback Procedure
```bash
# List revisions
gcloud run revisions list --service counselconduit --project shadowtag-omega-v4

# Route traffic to previous revision
gcloud run services update-traffic counselconduit \
  --project shadowtag-omega-v4 \
  --region us-central1 \
  --to-revisions PREVIOUS_REVISION=100
```

## Infrastructure Verification

### Daily Automated Checks
- Cloud Scheduler: `counselconduit-backup-verify` (weekly probe)
- Pre-commit hooks: Betterleaks + Ruff + Bandit + detect-private-key
- CI: Python tests on push to main

### Manual Verification Cadence
| Check | Frequency | Command |
|-------|-----------|---------|
| OpenTofu drift | Weekly | `cd infra/terraform && tofu plan` |
| Vulture dead code | Per commit (pre-commit) | `bash scripts/dead-code-audit.sh` |
| Bandit security | Per commit (pre-commit) | `bandit -r apps/counselconduit/ -ll` |
| Lighthouse | Per deploy | Browser → Lighthouse audit |
| GitNexus freshness | Weekly | `npx gitnexus analyze .` |
| Secret rotation status | Monthly | Check Secret Manager versions |

## Environment Variables

> **`.env` is DEPRECATED AND DELETED** (2026-04-22). All secrets fetched from GCP Secret Manager via `source scripts/load_mcp_secrets.sh`.
> See `GEMINI.md` §secrets_manager_doctrine for the full configuration map.

## Stripe Configuration

| Item | Value |
|------|-------|
| Account | `acct_1Syh9JEHnWpykeMi` |
| Pro Monthly | `price_1TNKSREHnWpykeMiRMDlVgLl` ($149/mo) |
| Pro Annual | `price_1TNKSjEHnWpykeMi0S9GCVjy` ($1,428/yr) |
| Enterprise | `price_1TNKSREHnWpykeMi8mrDf4rI` ($20K/mo) |
| Beta Coupon | `3wseBY7Z` (50% off, 3 months, max 100) |
| Webhook | `we_1TNKSjEHnWpykeMiQZqmpy3X` |

## Contact Chain

| Role | Contact |
|------|---------|
| Founder / Admin | founder@shadowtagai.com |
| GCP Project | shadowtag-omega-v4 |
| GitHub Org | ShadowTag-v2 |
| Repo | Monorepo-Uphillsnowball |
