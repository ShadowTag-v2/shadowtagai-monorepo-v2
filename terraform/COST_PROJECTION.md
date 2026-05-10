# GCP Infrastructure Cost Projection

## Current Monthly Costs (Estimated)

| Service | Resource | Monthly Cost (USD) |
|---------|----------|-------------------|
| **Cloud Run** | counselconduit (1 min, 10 max, 1vCPU, 512Mi) | $15-45 |
| **Cloud Run** | kovelai (0 min, 5 max) | $5-15 |
| **Firestore** | (default) database | $0-25 (free tier covers most) |
| **Cloud Scheduler** | 12 jobs | $0 (free tier: 3 jobs free, $0.10/job) |
| **Cloud Monitoring** | 9 uptime checks + 19 alert policies | $0 (free tier) |
| **Cloud Armor** | 3 WAF policies | $5/policy + $0.75/M requests ≈ $15-20 |
| **Secret Manager** | ~15 secrets | $0.06/secret × 15 ≈ $1 |
| **Cloud Storage** | Logs, backups | $1-5 |
| **Cloud Logging** | Log routing to BQ | $0.50/GiB (first 50GiB free) ≈ $0-10 |
| **BigQuery** | 6 log tables | $0 (first 10GiB free storage) |
| **Artifact Registry** | Docker images | $0.10/GiB ≈ $1-2 |
| **Cloud Tasks** | GDPR delete queue | $0 (first 1M free) |
| **Cloud Build** | CI/CD | $0 (first 120 min/day free) |
| **Total Base** | | **$43-128/mo** |

## Cost Optimization Opportunities

| Optimization | Savings | Effort |
|-------------|---------|--------|
| Scale counselconduit min_instances to 0 off-hours | $10-20/mo | Low |
| Use committed use discounts (if sustained) | 15-25% | Medium |
| Move BQ log tables to long-term storage tier | $3-5/mo | Low |
| Consolidate Cloud Armor policies → 1 | $10/mo | Medium |
| Use GCS Nearline for backup bucket | $2-3/mo | Low |

## Projected Growth (3 Months)

| Scenario | Monthly Cost |
|----------|-------------|
| **Current** (2 services, 12 scheduler, low traffic) | $43-128 |
| **+10 customers** (higher traffic) | $80-200 |
| **+50 customers** (moderate scale) | $150-400 |
| **+200 customers** (high scale, need scaling) | $400-1,200 |

## Free Tier Maximization

| Service | Free Tier | Currently Using |
|---------|-----------|----------------|
| Cloud Run | 2M requests/mo, 360K vCPU-s | ~5-10% |
| Firestore | 50K reads/day, 20K writes/day | ~10-30% |
| Cloud Scheduler | 3 free jobs | 12 (9 paid) |
| Cloud Monitoring | 150 MB ingestion | Well under |
| Cloud Build | 120 min/day | Well under |
| BigQuery | 10 GiB storage | Well under |
| Cloud Tasks | 1M operations/mo | Well under |

## Terraform IaC Overhead

| Item | Cost |
|------|------|
| GCS state bucket (versioned) | <$1/mo |
| Terraform Cloud (if used) | $0 (free tier: 500 resources) |
| OpenTofu | $0 (open source) |
| Terragrunt | $0 (open source) |
| Checkov | $0 (open source) |
| **Total IaC cost** | **<$1/mo** |

---

*Generated: 2026-04-21 | Based on GCP pricing as of April 2026*
