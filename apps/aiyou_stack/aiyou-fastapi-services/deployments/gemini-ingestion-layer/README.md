# Gemini Ingestion Layer — GKE Deployment

## Overview

Nightly intelligence collection pipeline feeding PNKLN Core Stack™ with ethically-sourced, tier-classified data.

**Architecture:** GKE CronJob (multi-container pod)
**Schedule:** Daily 2:00 AM Pacific (10:00 UTC)
**Target Runtime:** 45 minutes
**Monthly Cost:** ~$77

## Prerequisites

1. **GKE Cluster** with Workload Identity enabled
2. **GPU Node Pool** with T4 GPUs (for classifier)
3. **Preemptible Node Pool** (cost optimization)
4. **Cloud Storage Bucket:** `gs://pnkln-ingestion-daily/`
5. **Pub/Sub Topic:** `ingestion-complete`
6. **Container Registry:** Images at `gcr.io/pnkln/`

## Deployment Steps

### 1. Create GCP Resources

```bash
# Create storage bucket
gsutil mb -p pnkln-prod -l us-central1 gs://pnkln-ingestion-daily/

# Create Pub/Sub topic
gcloud pubsub topics create ingestion-complete --project=pnkln-prod

# Create IAM service account (see 05-iam.yaml for full commands)
gcloud iam service-accounts create gemini-ingestion-sa \
  --display-name="Gemini Ingestion Layer SA" \
  --project=pnkln-prod

# Grant permissions (see 05-iam.yaml for full list)
# ... storage.objectAdmin, pubsub.publisher, aiplatform.user
```

### 2. Update API Credentials

Edit `02-storage.yaml` with actual API keys:

```bash
kubectl create secret generic api-credentials \
  --from-literal=youtube-api-key=YOUR_YOUTUBE_KEY \
  --from-literal=twitter-api-key=YOUR_TWITTER_KEY \
  --from-literal=twitter-api-secret=YOUR_TWITTER_SECRET \
  --from-literal=newsapi-key=YOUR_NEWSAPI_KEY \
  --namespace=gke-training-system
```

### 3. Apply Manifests

```bash
# Apply in order (dependencies)
kubectl apply -f 01-namespace.yaml
kubectl apply -f 02-storage.yaml
kubectl apply -f 05-iam.yaml
kubectl apply -f 03-cronjob.yaml
kubectl apply -f 04-monitoring.yaml
```

### 4. Verify Deployment

```bash
# Check CronJob created
kubectl get cronjob -n gke-training-system

# Trigger manual run (testing)
kubectl create job --from=cronjob/gemini-ingestion manual-test-1 \
  -n gke-training-system

# Watch job progress
kubectl get jobs -n gke-training-system -w

# Check logs
kubectl logs -n gke-training-system -l app=gemini-ingestion --all-containers
```

### 5. Validate Outputs

```bash
# Check Cloud Storage for output
gsutil ls gs://pnkln-ingestion-daily/

# Example output file
gsutil cat gs://pnkln-ingestion-daily/2025-11-15-briefing.json | jq .

# Verify Pub/Sub message sent
gcloud pubsub subscriptions pull ingestion-complete-sub --limit=1
```

## Quality Gates

The pipeline enforces these thresholds (see `quality_gates` in ConfigMap):

| Metric          | Minimum | Target  | Alert   |
| --------------- | ------- | ------- | ------- |
| Items/day       | 10,000  | 50,000  | <8,000  |
| Relevance score | 0.70    | 0.80    | <0.65   |
| Tier 1 %        | 20%     | 30%     | <15%    |
| Cost/item       | -       | $0.0005 | >$0.001 |
| Runtime         | -       | 45 min  | >55 min |

**Rollback Trigger:** 3 consecutive days failing quality gates

## Ethical Compliance

**Zero-tolerance policies:**

- ✅ `robots.txt` honored 100% (auto-abort on violation)
- ✅ Rate limiting: ≤2 req/sec default
- ✅ Transparent user-agent: `PNKLNBot/1.0 (+https://pnkln.ai/bot)`
- ✅ Contact: `crawler@pnkln.ai` in headers

**Monitoring:**

```bash
# Check for ethics violations (should be ZERO)
kubectl logs -n gke-training-system -l app=gemini-ingestion \
  | grep -i "robots.txt violation"
```

## Cost Optimization

**Preemptible Nodes:**

- Job tolerates preemption (will restart)
- ~60% cost savings vs on-demand
- `concurrencyPolicy: Forbid` prevents overlapping jobs

**GPU Usage:**

- Classifier runs parallel to crawler (not sequential)
- T4 GPU: $0.35/hr × 0.25 hr = $5.25/month
- Could downgrade to CPU-only if latency acceptable

**API Costs:**

- YouTube: $30/month (daily quota)
- Twitter: $20/month (basic tier)
- NewsAPI: $15/month (developer plan)

**Total:** ~$77/month (99% cheaper than Judge 6 stack)

## Integration with Judge 6

**Data Flow:**

```
Gemini Ingestion (2:00-2:45 AM)
    ↓
Cloud Storage (gs://pnkln-ingestion-daily/YYYY-MM-DD-briefing.json)
    ↓ (Pub/Sub trigger)
Judge 6 (loads new data into Redis cache)
    ↓
Services (validated queries using fresh intelligence)
```

**Failure Handling:**

- If ingestion fails, Judge 6 uses previous day's data
- Alert fired to PagerDuty for manual investigation
- Services continue operating (degraded, stale data)

## Monitoring & Alerts

**Prometheus Metrics:**

```promql
# Items ingested
ingestion_items_total{tier="1"}
ingestion_items_total{tier="2"}
ingestion_items_total{tier="3"}

# Quality scores
ingestion_relevance_score_avg
ingestion_completeness_percentage

# Cost tracking
ingestion_cost_per_item
ingestion_monthly_cost_usd

# Runtime
ingestion_runtime_minutes

# Ethics
ingestion_robots_txt_violations_total  # MUST be 0
```

**Alerts** (see `04-monitoring.yaml`):

- Critical: Job stale (>24h), ethics violation
- Warning: Low volume, low quality, cost overrun, slow runtime

## Troubleshooting

### Job fails with "ImagePullBackOff"

```bash
# Check image exists
gcloud container images list --repository=gcr.io/pnkln

# Verify Workload Identity
kubectl describe sa gemini-ingestion-sa -n gke-training-system
```

### Job fails with API rate limit errors

```bash
# Check API quotas
gcloud services quota list --service=youtube.googleapis.com

# Reduce crawl rate in ConfigMap
kubectl edit configmap ingestion-config -n gke-training-system
# Set max_requests_per_second: 1
```

### Output file missing in Cloud Storage

```bash
# Check pod logs
kubectl logs -n gke-training-system -l app=gemini-ingestion -c quality-gate

# Verify IAM permissions
gcloud projects get-iam-policy pnkln-prod \
  --flatten="bindings[].members" \
  --filter="bindings.members:gemini-ingestion-sa@pnkln-prod.iam.gserviceaccount.com"
```

### GPU not available

```bash
# Check GPU node pool exists
kubectl get nodes -l cloud.google.com/gke-accelerator=nvidia-tesla-t4

# If missing, create node pool
gcloud container node-pools create gpu-pool \
  --cluster=pnkln-cluster \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --machine-type=n1-standard-4 \
  --num-nodes=1 \
  --enable-autoscaling --min-nodes=0 --max-nodes=3
```

## Production Readiness Checklist

Pre-Production (Q4 2025):

- [ ] All API credentials configured
- [ ] GCP IAM roles granted
- [ ] Workload Identity bound
- [ ] Cloud Storage bucket created
- [ ] Pub/Sub topic created
- [ ] GPU node pool available
- [ ] Monitoring/alerting configured
- [ ] 30-day pilot run completed
- [ ] Quality gates validated
- [ ] Ethics compliance verified (zero violations)

Production (Q2 2026):

- [ ] Multi-region failover configured
- [ ] Cost tracking dashboard deployed
- [ ] Tier classification accuracy ≥90%
- [ ] Integration with Judge 6 tested end-to-end
- [ ] Runbook documented
- [ ] On-call rotation assigned

## References

- [Architecture Doc](../../docs/PNKLN-Core-Stack-Dual-System-Architecture.md)
- [GKE CronJob Docs](https://cloud.google.com/kubernetes-engine/docs/how-to/cronjobs)
- [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [Vertex AI Integration](https://cloud.google.com/vertex-ai/docs/workbench/managed/introduction)

---

**Status:** Ready for staging deployment
**Owner:** PNKLN Core Stack™ team
**Cost:** ~$77/month
**Next Gate:** 30-day pilot with quality validation
