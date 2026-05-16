# PNKLN Core Stack™ - Kubernetes Manifests
**Component:** Gemini Ingestion Layer
**Last Updated:** 2025-11-15

---

## OVERVIEW

This directory contains Kubernetes (GKE) manifests for deploying the Gemini Ingestion Layer nightly CronJob.

**Architecture:**
- **Multi-container pod:** YouTube, Twitter, News collectors + Tier Classifier + Briefing Generator
- **Scheduled:** 3:00 AM daily (configurable via `timeZone` field)
- **Runtime:** ~45 minutes target
- **Output:** 850 items/day, 6:45 AM briefing delivery

---

## DIRECTORY STRUCTURE

```
kubernetes/
├── README.md                 # This file
├── namespace.yaml            # pnkln-ingestion namespace
├── secrets.yaml              # API keys, PostgreSQL credentials (TEMPLATE)
├── configmap.yaml            # Source config, ethics settings, quality gates
├── service-account.yaml      # RBAC for CronJob
├── cronjob.yaml              # Main CronJob manifest (multi-container)
├── monitoring.yaml           # Prometheus ServiceMonitor (optional)
└── cluster-setup.sh          # GKE cluster provisioning script
```

---

## PREREQUISITES

### 1. GCP Project Setup

```bash
# Set your GCP project
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable redis.googleapis.com
```

### 2. GKE Cluster Provisioning

**Option A: Use provided script**
```bash
./kubernetes/cluster-setup.sh
```

**Option B: Manual provisioning**
```bash
# Create GKE cluster (3 nodes, n1-standard-2)
gcloud container clusters create pnkln-core-stack \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 5 \
  --enable-autorepair \
  --enable-autoupgrade \
  --disk-size 50 \
  --disk-type pd-standard

# Get credentials
gcloud container clusters get-credentials pnkln-core-stack --zone us-central1-a
```

### 3. PostgreSQL Setup

**Option A: Cloud SQL (Recommended)**
```bash
# Create Cloud SQL instance
gcloud sql instances create pnkln-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create pnkln_ingestion --instance=pnkln-postgres

# Create user
gcloud sql users create ingestion_user \
  --instance=pnkln-postgres \
  --password=CHANGE_ME_SECURE_PASSWORD
```

**Option B: In-cluster PostgreSQL**
```bash
# Use Helm to deploy PostgreSQL
helm install postgres bitnami/postgresql \
  --namespace pnkln-ingestion \
  --set auth.username=ingestion_user \
  --set auth.password=CHANGE_ME_SECURE_PASSWORD \
  --set auth.database=pnkln_ingestion
```

### 4. Redis Setup (Optional, for caching)

```bash
# Cloud Memorystore
gcloud redis instances create pnkln-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0

# OR in-cluster Redis
helm install redis bitnami/redis \
  --namespace pnkln-ingestion \
  --set auth.enabled=false
```

---

## DEPLOYMENT STEPS

### Step 1: Create Namespace

```bash
kubectl apply -f kubernetes/namespace.yaml
```

**Verify:**
```bash
kubectl get namespace pnkln-ingestion
```

---

### Step 2: Create Secrets

**IMPORTANT:** Edit `secrets.yaml` with real API keys (base64-encoded)

```bash
# Example: Encode YouTube API key
echo -n "YOUR_YOUTUBE_API_KEY" | base64

# Edit secrets.yaml with real values
vi kubernetes/secrets.yaml

# Apply secrets
kubectl apply -f kubernetes/secrets.yaml
```

**Verify:**
```bash
kubectl get secrets -n pnkln-ingestion
kubectl describe secret ingestion-api-keys -n pnkln-ingestion
```

**Security Best Practice:** Use Google Secret Manager instead
```bash
# Create secret in Secret Manager
gcloud secrets create youtube-api-key \
  --data-file=- <<< "YOUR_YOUTUBE_API_KEY"

# Use External Secrets Operator in K8s
# (See https://external-secrets.io/)
```

---

### Step 3: Create ConfigMap

```bash
kubectl apply -f kubernetes/configmap.yaml
```

**Verify:**
```bash
kubectl get configmap ingestion-config -n pnkln-ingestion
kubectl describe configmap ingestion-config -n pnkln-ingestion
```

**To edit config on-the-fly:**
```bash
kubectl edit configmap ingestion-config -n pnkln-ingestion
```

---

### Step 4: Create Service Account (RBAC)

```bash
kubectl apply -f kubernetes/service-account.yaml
```

**Verify:**
```bash
kubectl get serviceaccount ingestion-service-account -n pnkln-ingestion
kubectl get role ingestion-role -n pnkln-ingestion
kubectl get rolebinding ingestion-rolebinding -n pnkln-ingestion
```

---

### Step 5: Deploy CronJob

```bash
kubectl apply -f kubernetes/cronjob.yaml
```

**Verify:**
```bash
# Check CronJob status
kubectl get cronjob gemini-ingestion -n pnkln-ingestion

# Check schedule
kubectl describe cronjob gemini-ingestion -n pnkln-ingestion
```

---

## OPERATIONS

### Manual Job Trigger (Test Before First Run)

```bash
# Create a one-time job from CronJob
kubectl create job --from=cronjob/gemini-ingestion test-run-1 -n pnkln-ingestion

# Watch job progress
kubectl get jobs -n pnkln-ingestion -w

# Check pod logs
kubectl logs -n pnkln-ingestion -l job-name=test-run-1 --all-containers=true -f
```

---

### Monitor CronJob Execution

**Check recent jobs:**
```bash
kubectl get jobs -n pnkln-ingestion

# Example output:
# NAME                            COMPLETIONS   DURATION   AGE
# gemini-ingestion-28389520       1/1           44m        2h
# gemini-ingestion-28389530       1/1           45m        26h
# gemini-ingestion-28389540       1/1           46m        50h
```

**Check individual job:**
```bash
kubectl describe job gemini-ingestion-28389520 -n pnkln-ingestion
```

**View logs (all containers):**
```bash
# Real-time logs
kubectl logs -n pnkln-ingestion \
  -l job-name=gemini-ingestion-28389520 \
  --all-containers=true \
  -f

# Specific container
kubectl logs -n pnkln-ingestion \
  -l job-name=gemini-ingestion-28389520 \
  -c youtube-collector
```

---

### Debugging Failed Jobs

**Get pod status:**
```bash
kubectl get pods -n pnkln-ingestion -l job-name=gemini-ingestion-XXXXXX
```

**Check pod events:**
```bash
kubectl describe pod gemini-ingestion-XXXXXX-XXXXX -n pnkln-ingestion
```

**Common failure modes:**
1. **ImagePullBackOff:** Container image not found
   - Fix: Build and push images to GCR
   - `docker build -t gcr.io/PROJECT_ID/youtube-collector:latest .`
   - `docker push gcr.io/PROJECT_ID/youtube-collector:latest`

2. **CrashLoopBackOff:** Container crashes on startup
   - Fix: Check logs for errors
   - `kubectl logs -n pnkln-ingestion POD_NAME -c CONTAINER_NAME --previous`

3. **Timeout (activeDeadlineSeconds exceeded):** Job took >90 minutes
   - Fix: Optimize collectors or increase deadline in `cronjob.yaml`

4. **Secret not found:** Missing API keys
   - Fix: Verify secrets exist
   - `kubectl get secrets -n pnkln-ingestion`

---

### Update CronJob Configuration

**Change schedule:**
```bash
# Edit CronJob
kubectl edit cronjob gemini-ingestion -n pnkln-ingestion

# Or apply updated manifest
kubectl apply -f kubernetes/cronjob.yaml
```

**Update source configuration:**
```bash
# Edit ConfigMap
kubectl edit configmap ingestion-config -n pnkln-ingestion

# No need to restart CronJob (changes take effect on next run)
```

**Update secrets:**
```bash
# Delete old secret
kubectl delete secret ingestion-api-keys -n pnkln-ingestion

# Create new secret
kubectl apply -f kubernetes/secrets.yaml
```

---

### Suspend/Resume CronJob

**Suspend (temporarily disable):**
```bash
kubectl patch cronjob gemini-ingestion -n pnkln-ingestion \
  -p '{"spec":{"suspend":true}}'
```

**Resume:**
```bash
kubectl patch cronjob gemini-ingestion -n pnkln-ingestion \
  -p '{"spec":{"suspend":false}}'
```

---

### Delete CronJob (Cleanup)

```bash
# Delete CronJob only (keeps completed jobs)
kubectl delete cronjob gemini-ingestion -n pnkln-ingestion

# Delete all jobs
kubectl delete jobs -n pnkln-ingestion --all

# Delete entire namespace (CAUTION: removes everything)
kubectl delete namespace pnkln-ingestion
```

---

## MONITORING & ALERTS

### Prometheus Metrics (Optional)

If using Prometheus Operator, apply ServiceMonitor:
```bash
kubectl apply -f kubernetes/monitoring.yaml
```

**Metrics exposed:**
- `cronjob_succeeded_total`: Total successful job runs
- `cronjob_failed_total`: Total failed job runs
- `cronjob_duration_seconds`: Job duration

### Slack Alerts

Quality gates send alerts to Slack webhook (configured in `configmap.yaml`):
- Items/day < 700
- Tier 1 ratio < 30%
- Cost/item > $0.60
- Runtime > 70 minutes
- Ethical compliance < 100%

**Test alert:**
```bash
# Manually trigger quality gate check (via kubectl exec)
kubectl exec -n pnkln-ingestion POD_NAME -c briefing-generator -- \
  python -m ingestion.quality.gates --test-alert
```

---

## COST MANAGEMENT

### Estimated Monthly Costs

| Component | Type | Cost/Month |
|-----------|------|------------|
| GKE (3 nodes, n1-standard-2) | Compute | $150 |
| Cloud SQL (db-f1-micro) | Database | $10 |
| Cloud Memorystore (1GB Redis) | Cache | $30 |
| API calls (YouTube, Twitter, News) | External | $15 |
| Gemini API (batched NLP) | AI | $12 |
| **TOTAL** | | **$217/month** |

**Optimization tips:**
- Use **preemptible nodes** for GKE (save 60-80%)
- Switch to **in-cluster PostgreSQL** (save $10/mo)
- Batch Gemini calls more aggressively (save $5/mo)
- **Target optimized cost:** $77/month

---

## TROUBLESHOOTING

### Issue: CronJob not running at scheduled time

**Check:**
```bash
kubectl describe cronjob gemini-ingestion -n pnkln-ingestion
```

**Common causes:**
- `suspend: true` (CronJob suspended)
- `concurrencyPolicy: Forbid` + previous job still running
- `startingDeadlineSeconds` exceeded (schedule missed)

**Fix:**
```bash
# Resume if suspended
kubectl patch cronjob gemini-ingestion -n pnkln-ingestion \
  -p '{"spec":{"suspend":false}}'

# Check previous jobs
kubectl get jobs -n pnkln-ingestion
```

---

### Issue: Collectors not finding PostgreSQL

**Check init container logs:**
```bash
kubectl logs -n pnkln-ingestion POD_NAME -c wait-for-postgres
```

**Common causes:**
- PostgreSQL not running
- Wrong credentials in secrets
- Network policy blocking connection

**Fix:**
```bash
# Verify PostgreSQL reachable
kubectl run -n pnkln-ingestion -it --rm debug \
  --image=postgres:15-alpine \
  --restart=Never \
  -- pg_isready -h postgres.pnkln-stack.svc.cluster.local -p 5432
```

---

### Issue: Gemini API quota exceeded

**Symptoms:**
- Tier classifier logs show `429 Too Many Requests`
- Tier 1 ratio drops significantly

**Fix:**
```bash
# Switch to rule-based classification temporarily
kubectl set env deployment tier-classifier \
  -n pnkln-ingestion \
  CLASSIFICATION_MODE=rule-based

# Or increase batching
kubectl edit configmap ingestion-config -n pnkln-ingestion
# Change: batch_size: 50 → batch_size: 100
```

---

## NEXT STEPS

1. **Build Docker images:**
   ```bash
   cd collectors/youtube && docker build -t gcr.io/PROJECT_ID/youtube-collector:latest .
   cd collectors/twitter && docker build -t gcr.io/PROJECT_ID/twitter-collector:latest .
   # ... etc for all collectors
   ```

2. **Push images to GCR:**
   ```bash
   docker push gcr.io/PROJECT_ID/youtube-collector:latest
   docker push gcr.io/PROJECT_ID/twitter-collector:latest
   # ... etc
   ```

3. **Run test job:**
   ```bash
   kubectl create job --from=cronjob/gemini-ingestion test-run -n pnkln-ingestion
   kubectl logs -n pnkln-ingestion -l job-name=test-run --all-containers=true -f
   ```

4. **Verify database:**
   ```bash
   kubectl run -n pnkln-ingestion -it --rm psql \
     --image=postgres:15-alpine \
     --restart=Never \
     -- psql -h postgres.pnkln-stack.svc.cluster.local -U ingestion_user -d pnkln_ingestion

   # In psql:
   SELECT COUNT(*) FROM items;
   SELECT tier, COUNT(*) FROM items GROUP BY tier;
   ```

5. **Check AM briefing delivery:**
   - Email inbox (stakeholders)
   - Slack channel (#intelligence-briefing)
   - Dashboard: https://pnkln.ai/briefing

---

## REFERENCES

- [GKE CronJobs Documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/cronjobs)
- [Kubernetes CronJob Spec](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Gemini Ingestion Layer Inception Analysis](../GEMINI_INGESTION_LAYER_INCEPTION_ANALYSIS.md)
- [PNKLN Roadmap](../PNKLN_ROADMAP.md)
- [Implementation Tickets](../IMPLEMENTATION_TICKETS.md)

---

**VERSION:** 1.0
**STATUS:** Ready for deployment
**LAST UPDATED:** 2025-11-15
