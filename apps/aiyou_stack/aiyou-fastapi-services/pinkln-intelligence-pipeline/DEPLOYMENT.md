# PNKLN Intelligence Pipeline — Production Deployment

**ID:** `claude/pnkln-intelligence-pipeline-deployment-011CUvwKSmyxTgTWmc7WaHUR`
**Purpose:** Production-grade GKE deployment for nightly intelligence ingestion
**Target:** $77/month operational cost, 45-minute runtime, 6+ sources
**Integration:** Feeds Tier 1 intelligence → Pinkln Ultrathink agents

---

## 🎯 Overview

This document covers the **production deployment** of the PNKLN Core Stack™, the data ingestion layer that collects, classifies, and feeds intelligence to the Pinkln reasoning engine.

**Architecture:**

```

┌────────────────────────────────────────────────────┐
│          GitHub Actions (CI/CD)                    │
│  • Build Docker image                              │
│  • Push to Artifact Registry                       │
│  • Deploy to GKE                                   │
└────────────┬───────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────┐
│      Google Kubernetes Engine (GKE)                │
│  ┌──────────────────────────────────────────────┐  │
│  │   CronJob: pnkln-ingestion-nightly           │  │
│  │   Schedule: "0 2 * * *" (2am daily)          │  │
│  │   Resources: 1 CPU, 2GB RAM                  │  │
│  │   Runtime: ~45 minutes                       │  │
│  └──────────────┬───────────────────────────────┘  │
│                 │                                   │
│      ┌──────────┼──────────┐                       │
│      │          │          │                       │
│  ┌───▼───┐  ┌───▼───┐  ┌───▼───┐                  │
│  │Source1│  │Source2│  │Source3│                  │
│  │YouTube│  │Twitter│  │Reddit │  (6+ sources)   │
│  └───────┘  └───────┘  └───────┘                  │
└────────────────┬───────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│        Cloud Storage (Tier Classification)         │
│  • Tier 1: High-value intelligence                 │
│  • Tier 2: Medium-value content                    │
│  • Tier 3: Low-value/noise                         │
└────────────┬───────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────┐
│      Pinkln Reasoning Engine (Consumer)            │
│  • Panel debates on Tier 1 items                   │
│  • Agent training on Tier 2/3                      │
│  • Glicko rating updates                           │
└────────────────────────────────────────────────────┘

```

---

## 🚀 Quick Deploy

### Prerequisites

```bash

# Required tools

gcloud components install gke-gcloud-auth-plugin kubectl

# Environment variables

export PROJECT_ID="shadowtag_v4-pnkln-prod"
export CLUSTER_NAME="pnkln-cluster"
export REGION="us-central1"
export GOOGLE_AI_API_KEY="your-gemini-api-key"

```

### One-Command Deploy

```bash

# Run deployment script

./scripts/deploy.sh

```

---

## 📦 Container Setup

### Dockerfile

**Location:** `Dockerfile`

```dockerfile

# Multi-stage build for minimal image size

FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage

FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder

COPY --from=builder /root/.local /root/.local

# Copy application code

COPY src/ ./src/
COPY config/ ./config/

# Set environment

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Run ingestion

CMD ["python", "-m", "src.api.ingestion", "--mode", "batch"]

```

### Build and Push

```bash

# Build image

docker build -t gcr.io/${PROJECT_ID}/pnkln-ingestion:latest .

# Push to Artifact Registry

docker push gcr.io/${PROJECT_ID}/pnkln-ingestion:latest

```

---

## ☸️ Kubernetes Deployment

### GKE Cluster Setup

**File:** `k8s/cluster.yaml`

```yaml
apiVersion: container.cnrm.cloud.google.com/v1beta1
kind: ContainerCluster
metadata:
  name: pnkln-cluster
spec:
  location: us-central1
  initialNodeCount: 1

  # Autopilot mode (cost-optimized, managed)
  enableAutopilot: true

  # Release channel (regular updates)
  releaseChannel:
    channel: REGULAR

  # Workload Identity (secure credential access)
  workloadIdentityConfig:
    workloadPool: ${PROJECT_ID}.svc.id.goog

  # Binary authorization (security)
  binaryAuthorization:
    evaluationMode: PROJECT_SINGLETON_POLICY_ENFORCE

```

**Create cluster:**

```bash
gcloud container clusters create-auto ${CLUSTER_NAME} \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --release-channel=regular \
  --enable-autoupgrade \
  --enable-autorepair

```

**Cost:** ~$50/month (Autopilot, 1 CPU, 2GB RAM, ~45min/day runtime)

---

### CronJob Configuration

**File:** `k8s/ingestion-cronjob.yaml`

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: pnkln-ingestion-nightly
  namespace: pnkln
spec:
  # Run at 2am UTC daily
  schedule: "0 2 * * *"

  # Keep last 3 successful, 1 failed job for debugging
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1

  # Don't run concurrent jobs
  concurrencyPolicy: Forbid

  jobTemplate:
    spec:
      # Job timeout: 1 hour
      activeDeadlineSeconds: 3600

      template:
        metadata:
          labels:
            app: pnkln-ingestion
            tier: data-layer
        spec:
          restartPolicy: OnFailure

          # Service account for Workload Identity
          serviceAccountName: pnkln-ingestion-sa

          containers:


          - name: ingestion
            image: gcr.io/shadowtag_v4-pnkln-prod/pnkln-ingestion:latest
            imagePullPolicy: Always

            # Resource limits (cost optimization)
            resources:
              requests:
                cpu: "1000m"
                memory: "2Gi"
              limits:
                cpu: "2000m"
                memory: "4Gi"

            # Environment variables
            env:


            - name: GOOGLE_AI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: pnkln-secrets
                  key: gemini-api-key



            - name: INGESTION_MODE
              value: "batch"



            - name: TIER_CLASSIFICATION_ENABLED
              value: "true"



            - name: OUTPUT_BUCKET
              value: "gs://pnkln-intelligence-prod"



            - name: LOG_LEVEL
              value: "INFO"

            # Health check
            livenessProbe:
              exec:
                command:


                - cat


                - /tmp/healthy
              initialDelaySeconds: 60
              periodSeconds: 30

```

**Deploy:**

```bash
kubectl apply -f k8s/ingestion-cronjob.yaml

```

---

## 🔐 Secrets Management

### Create Kubernetes Secrets

```bash

# Create namespace

kubectl create namespace pnkln

# Create secret for Gemini API key

kubectl create secret generic pnkln-secrets \
  --namespace=pnkln \
  --from-literal=gemini-api-key=${GOOGLE_AI_API_KEY}

# Verify

kubectl get secrets -n pnkln

```

### Workload Identity Setup

**Service Account:**

```bash

# Create GCP service account

gcloud iam service-accounts create pnkln-ingestion-sa \
  --project=${PROJECT_ID}

# Grant storage permissions

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:pnkln-ingestion-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Bind Kubernetes SA to GCP SA

gcloud iam service-accounts add-iam-policy-binding \
  pnkln-ingestion-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[pnkln/pnkln-ingestion-sa]"

# Create Kubernetes service account

kubectl create serviceaccount pnkln-ingestion-sa -n pnkln

# Annotate for Workload Identity

kubectl annotate serviceaccount pnkln-ingestion-sa -n pnkln \
  iam.gke.io/gcp-service-account=pnkln-ingestion-sa@${PROJECT_ID}.iam.gserviceaccount.com

```

---

## 📊 Monitoring & Alerting

### Cloud Logging

**Query for ingestion logs:**

```

resource.type="k8s_container"
resource.labels.namespace_name="pnkln"
resource.labels.container_name="ingestion"

```

**Useful filters:**

```bash

# Errors only

severity>=ERROR

# Tier 1 classifications

jsonPayload.tier="1"

# Runtime performance

jsonPayload.duration_seconds>0

```

### Cloud Monitoring Dashboards

**File:** `monitoring/dashboard.json`

```json
{
  "displayName": "PNKLN Ingestion Dashboard",
  "gridLayout": {
    "widgets": [
      {
        "title": "Job Success Rate (Last 7 Days)",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "resource.type=\"k8s_job\" AND resource.labels.namespace_name=\"pnkln\"",
                "aggregation": {
                  "alignmentPeriod": "86400s",
                  "perSeriesAligner": "ALIGN_RATE"
                }
              }
            }
          }]
        }
      },
      {
        "title": "Items Collected (Daily)",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "metric.type=\"custom.googleapis.com/pnkln/items_collected\"",
                "aggregation": {
                  "alignmentPeriod": "86400s",
                  "perSeriesAligner": "ALIGN_SUM"
                }
              }
            }
          }]
        }
      },
      {
        "title": "Tier 1 Classification Rate",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "metric.type=\"custom.googleapis.com/pnkln/tier1_ratio\"",
                "aggregation": {
                  "alignmentPeriod": "86400s",
                  "perSeriesAligner": "ALIGN_MEAN"
                }
              }
            }
          }]
        }
      },
      {
        "title": "Gemini API Cost (Monthly)",
        "scorecard": {
          "timeSeriesQuery": {
            "timeSeriesFilter": {
              "filter": "metric.type=\"custom.googleapis.com/pnkln/api_cost\"",
              "aggregation": {
                "alignmentPeriod": "2592000s",
                "perSeriesAligner": "ALIGN_SUM"
              }
            }
          }
        }
      }
    ]
  }
}

```

**Deploy dashboard:**

```bash
gcloud monitoring dashboards create --config-from-file=monitoring/dashboard.json

```

### Alerting Policies

**File:** `monitoring/alerts.yaml`

```yaml

# Alert if job fails

apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: pnkln-ingestion-alerts
  namespace: pnkln
spec:
  groups:


  - name: ingestion
    interval: 5m
    rules:

    # Job failure


    - alert: PNKLNIngestionFailed
      expr: kube_job_status_failed{namespace="pnkln", job_name=~"pnkln-ingestion-nightly.*"} > 0
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "PNKLN ingestion job failed"
        description: "Job {{ $labels.job_name }} has failed. Check logs."

    # Low Tier 1 rate


    - alert: PNKLNLowTier1Rate
      expr: (sum(rate(pnkln_tier1_items[24h])) / sum(rate(pnkln_total_items[24h]))) < 0.05
      for: 1h
      labels:
        severity: warning
      annotations:
        summary: "PNKLN Tier 1 classification rate too low"
        description: "Only {{ $value | humanizePercentage }} of items classified as Tier 1 (expected >5%)"

    # High API cost


    - alert: PNKLNHighAPICost
      expr: sum(increase(pnkln_api_cost_dollars[30d])) > 100
      for: 1h
      labels:
        severity: warning
      annotations:
        summary: "PNKLN API costs exceeding budget"
        description: "Monthly Gemini API cost is ${{ $value }}, exceeding $77 target"

    # Long runtime


    - alert: PNKLNLongRuntime
      expr: max(pnkln_ingestion_duration_seconds) > 3600
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "PNKLN ingestion taking too long"
        description: "Job runtime is {{ $value | humanizeDuration }}, exceeding 1-hour limit"

```

**Create alerts:**

```bash
kubectl apply -f monitoring/alerts.yaml

```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

**File:** `.github/workflows/deploy-pnkln.yml`

```yaml
name: Deploy PNKLN Ingestion

on:
  push:
    branches:


      - main


      - 'claude/shadowtag_v4-verified-mesh-*'
    paths:


      - 'src/**'


      - 'config/**'


      - 'k8s/**'


      - 'Dockerfile'

  # Manual trigger
  workflow_dispatch:

env:
  PROJECT_ID: shadowtag_v4-pnkln-prod
  REGION: us-central1
  CLUSTER_NAME: pnkln-cluster
  IMAGE: gcr.io/shadowtag_v4-pnkln-prod/pnkln-ingestion

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    permissions:
      contents: read
      id-token: write

    steps:


    - name: Checkout code
      uses: actions/checkout@v4



    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
        service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}



    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2



    - name: Configure Docker
      run: |
        gcloud auth configure-docker



    - name: Build image
      run: |
        docker build -t ${IMAGE}:${GITHUB_SHA} -t ${IMAGE}:latest .



    - name: Run tests
      run: |
        docker run --rm ${IMAGE}:${GITHUB_SHA} python -m pytest tests/



    - name: Push image
      run: |
        docker push ${IMAGE}:${GITHUB_SHA}
        docker push ${IMAGE}:latest



    - name: Get GKE credentials
      run: |
        gcloud container clusters get-credentials ${CLUSTER_NAME} --region=${REGION}



    - name: Deploy to GKE
      run: |
        kubectl set image cronjob/pnkln-ingestion-nightly \
          ingestion=${IMAGE}:${GITHUB_SHA} \
          -n pnkln

        kubectl rollout status cronjob/pnkln-ingestion-nightly -n pnkln



    - name: Verify deployment
      run: |
        kubectl get cronjobs -n pnkln
        kubectl get jobs -n pnkln --sort-by=.metadata.creationTimestamp | tail -5

```

### Manual Deployment

```bash

# Build

docker build -t gcr.io/${PROJECT_ID}/pnkln-ingestion:$(git rev-parse --short HEAD) .

# Push

docker push gcr.io/${PROJECT_ID}/pnkln-ingestion:$(git rev-parse --short HEAD)

# Deploy

kubectl set image cronjob/pnkln-ingestion-nightly \
  ingestion=gcr.io/${PROJECT_ID}/pnkln-ingestion:$(git rev-parse --short HEAD) \
  -n pnkln

```

---

## 💰 Cost Optimization

### Target: $77/month

**Breakdown:**

| Component | Cost | Optimization |
|-----------|------|--------------|
| **GKE Autopilot** | ~$50/mo | Only runs 45 min/day, scales to zero |
| **Gemini API** | ~$20/mo | Batch processing, caching, tier-based |
| **Cloud Storage** | ~$5/mo | Lifecycle policies, compression |
| **Networking** | ~$2/mo | Regional egress only |
| **Total** | **~$77/mo** | |

### Optimization Strategies

**1. Compute (GKE)**

```yaml

# Use burstable resources

resources:
  requests:
    cpu: "500m"    # Start small
    memory: "1Gi"
  limits:
    cpu: "2000m"   # Burst if needed
    memory: "4Gi"

```

**2. Gemini API**

```python

# config/gemini-optimization.yaml

api:
  # Cache expensive classifications
  cache_enabled: true
  cache_ttl_hours: 24

  # Batch requests (10 items/call)
  batch_size: 10

  # Use cheaper models for Tier 2/3
  tier1_model: "gemini-2.0-flash-exp"  # $0.003/1K tokens
  tier2_model: "gemini-1.5-flash"      # $0.00015/1K tokens

  # Early exit for obvious Tier 3
  pre_filter_enabled: true
  pre_filter_keywords: ["spam", "advertisement", "clickbait"]

```

**3. Storage**

```bash

# Lifecycle policy for GCS bucket

gcloud storage buckets update gs://pnkln-intelligence-prod \
  --lifecycle-file=config/storage-lifecycle.json

```

**`config/storage-lifecycle.json`:**

```json
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "SetStorageClass", "storageClass": "NEARLINE"},
        "condition": {"age": 30}
      },
      {
        "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
        "condition": {"age": 90}
      },
      {
        "action": {"type": "Delete"},
        "condition": {"age": 365, "matchesPrefix": ["tier3/"]}
      }
    ]
  }
}

```

**4. Networking**



- Use regional GCS bucket (same region as GKE)


- Avoid cross-region traffic


- Compress data before upload

---

## 🔗 Integration with Pinkln

### Data Flow

```python

# pinkln-reasoning-engine/integrations/pnkln.py

from google.cloud import storage
import asyncio
from debate.panel import PanelDebate
from agents.registry import AgentRegistry

class PNKLNPinklnBridge:
    """
    Bridge between PNKLN ingestion and Pinkln reasoning



    1. Read Tier 1 items from GCS


    2. Run panel debates on high-value intelligence


    3. Update agent Glicko ratings based on performance


    4. Store analyses back to GCS with ShadowTag attestation
    """

    def __init__(self, bucket_name: str = "pnkln-intelligence-prod"):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)
        self.registry = AgentRegistry()

    async def analyze_tier1_items(self, limit: int = 10):
        """
        Analyze latest Tier 1 intelligence with panel debates
        """
        # Get latest Tier 1 items
        blobs = self.bucket.list_blobs(prefix="tier1/", max_results=limit)
        items = [self._load_item(blob) for blob in blobs]

        # Get panel of top-rated agents
        panel = self.registry.get_panel(
            specializations=["research", "analysis"],
            n=5,
            min_rating=1600
        )

        debate = PanelDebate(agents=panel, framework="RCR-MAD")

        results = []
        for item in items:
            # Run debate
            result = await debate.debate(
                topic=f"Analyze significance of: {item['content']}"
            )

            # Store analysis
            analysis = {
                "item_id": item["id"],
                "consensus": result.consensus,
                "confidence": result.confidence,
                "agent_ratings": result.agent_contributions,
                "timestamp": result.timestamp
            }

            results.append(analysis)

            # Save to GCS
            self._save_analysis(analysis)

        return results

    def _load_item(self, blob):
        """Load and parse item from GCS"""
        import json
        content = blob.download_as_text()
        return json.loads(content)

    def _save_analysis(self, analysis):
        """Save analysis back to GCS"""
        import json
        blob = self.bucket.blob(f"analyses/{analysis['item_id']}.json")
        blob.upload_from_string(
            json.dumps(analysis, indent=2),
            content_type="application/json"
        )


# Usage in CronJob

if __name__ == "__main__":
    bridge = PNKLNPinklnBridge()
    results = asyncio.run(bridge.analyze_tier1_items(limit=10))

    print(f"Analyzed {len(results)} Tier 1 items")
    for r in results:
        print(f"  {r['item_id']}: {r['confidence']:.0%} confidence")

```

### Deployment

```yaml

# k8s/pinkln-analysis-cronjob.yaml

apiVersion: batch/v1
kind: CronJob
metadata:
  name: pnkln-analysis-nightly
  namespace: pnkln
spec:
  # Run 1 hour after ingestion completes
  schedule: "0 3 * * *"

  jobTemplate:
    spec:
      template:
        spec:
          containers:


          - name: analysis
            image: gcr.io/shadowtag_v4-pnkln-prod/pinkln-reasoning:latest
            command:


            - python


            - -m


            - pinkln-reasoning-engine.integrations.pnkln

            env:


            - name: GCS_BUCKET
              value: "pnkln-intelligence-prod"



            - name: ANALYSIS_LIMIT
              value: "10"

```

---

## 🧪 Testing

### Local Testing

```bash

# Build image

docker build -t pnkln-ingestion:test .

# Run with test config

docker run --rm \
  -e GOOGLE_AI_API_KEY=${GOOGLE_AI_API_KEY} \
  -e INGESTION_MODE=test \
  -v $(pwd)/test-output:/tmp/output \
  pnkln-ingestion:test

```

### Integration Tests

**File:** `tests/integration/test_deployment.py`

```python
import pytest
from google.cloud import storage
from kubernetes import client, config

def test_cronjob_exists():
    """Verify CronJob is deployed"""
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()

    cronjobs = batch_v1.list_namespaced_cron_job("pnkln")
    assert any(cj.metadata.name == "pnkln-ingestion-nightly" for cj in cronjobs.items)

def test_gcs_bucket_accessible():
    """Verify GCS bucket is accessible"""
    storage_client = storage.Client()
    bucket = storage_client.bucket("pnkln-intelligence-prod")

    assert bucket.exists()

    # Check lifecycle policy
    lifecycle = bucket.lifecycle_rules
    assert any(rule.action.type == "SetStorageClass" for rule in lifecycle)

def test_secrets_configured():
    """Verify Kubernetes secrets exist"""
    config.load_kube_config()
    core_v1 = client.CoreV1Api()

    secret = core_v1.read_namespaced_secret("pnkln-secrets", "pnkln")
    assert "gemini-api-key" in secret.data

@pytest.mark.asyncio
async def test_pinkln_bridge():
    """Test PNKLN→Pinkln integration"""
    from pinkln-reasoning-engine.integrations.pnkln import PNKLNPinklnBridge

    bridge = PNKLNPinklnBridge()
    results = await bridge.analyze_tier1_items(limit=1)

    assert len(results) > 0
    assert "consensus" in results[0]
    assert results[0]["confidence"] > 0

```

### Manual Job Trigger

```bash

# Trigger job manually (don't wait for cron)

kubectl create job --from=cronjob/pnkln-ingestion-nightly pnkln-test-$(date +%s) -n pnkln

# Watch logs

kubectl logs -f job/pnkln-test-XXXXX -n pnkln

```

---

## 📈 Performance Tuning

### Runtime Optimization

**Target: 45 minutes**

```python

# src/api/ingestion.py

import asyncio
from concurrent.futures import ThreadPoolExecutor

class OptimizedIngestion:
    """
    Parallel ingestion with rate limiting
    """

    def __init__(self, max_workers: int = 6):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def ingest_all_sources(self):
        """
        Ingest from all sources in parallel
        """
        sources = [
            self.ingest_youtube,
            self.ingest_twitter,
            self.ingest_reddit,
            self.ingest_hackernews,
            self.ingest_github,
            self.ingest_arxiv
        ]

        # Run all in parallel
        results = await asyncio.gather(*[source() for source in sources])

        return results

    async def ingest_youtube(self):
        """Ingest from YouTube with rate limiting"""
        # ... implementation
        pass

```

### Gemini API Batching

```python

# src/classification/batch.py

async def classify_batch(items: List[dict], batch_size: int = 10):
    """
    Classify items in batches to reduce API calls
    """
    import google.generativeai as genai

    batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]

    results = []
    for batch in batches:
        # Single API call for entire batch
        prompt = "Classify these items into Tier 1/2/3:\n\n"
        for idx, item in enumerate(batch):
            prompt += f"{idx+1}. {item['title']}: {item['summary']}\n"

        response = await genai.generate_text_async(
            model="gemini-2.0-flash-exp",
            prompt=prompt
        )

        # Parse response
        classifications = parse_batch_response(response.text, len(batch))
        results.extend(classifications)

    return results

```

---

## 🚨 Troubleshooting

### Common Issues

**1. Job Fails with OOMKilled**

```bash

# Increase memory limit

kubectl edit cronjob pnkln-ingestion-nightly -n pnkln

# Update:

resources:
  limits:
    memory: "6Gi"  # Increase from 4Gi

```

**2. Gemini API Rate Limits**

```python

# config/gemini-optimization.yaml

api:
  rate_limit_rpm: 50  # Reduce from 60
  retry_enabled: true
  retry_max_attempts: 3
  retry_backoff_seconds: 5

```

**3. GCS Permission Errors**

```bash

# Verify service account permissions

gcloud projects get-iam-policy ${PROJECT_ID} \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:pnkln-ingestion-sa@*"

# Add missing role

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:pnkln-ingestion-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

```

**4. CronJob Not Running**

```bash

# Check CronJob status

kubectl describe cronjob pnkln-ingestion-nightly -n pnkln

# Check recent jobs

kubectl get jobs -n pnkln --sort-by=.metadata.creationTimestamp

# Manually trigger

kubectl create job --from=cronjob/pnkln-ingestion-nightly manual-run -n pnkln

```

---

## 📊 Metrics & KPIs

### Key Performance Indicators

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| **Job success rate** | 100% | < 95% |
| **Runtime** | 45 min | > 60 min |
| **Items collected** | 500-1000/day | < 200/day |
| **Tier 1 rate** | 5-10% | < 3% |
| **API cost** | $20/month | > $30/month |
| **Storage cost** | $5/month | > $10/month |
| **Total cost** | $77/month | > $100/month |

### Custom Metrics

```python

# src/metrics/custom.py

from google.cloud import monitoring_v3

class PNKLNMetrics:
    """
    Custom metrics for Cloud Monitoring
    """

    def __init__(self, project_id: str):
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"

    def record_items_collected(self, count: int, tier: int):
        """Record items collected by tier"""
        series = monitoring_v3.TimeSeries()
        series.metric.type = "custom.googleapis.com/pnkln/items_collected"
        series.metric.labels["tier"] = str(tier)

        point = monitoring_v3.Point()
        point.value.int64_value = count
        point.interval.end_time.seconds = int(time.time())

        series.points = [point]
        self.client.create_time_series(name=self.project_name, time_series=[series])

```

---

## 🎯 Production Checklist

### Pre-Launch



- [ ] GKE cluster created with Autopilot


- [ ] Workload Identity configured


- [ ] Kubernetes secrets created (Gemini API key)


- [ ] CronJob deployed and scheduled


- [ ] GCS bucket created with lifecycle policies


- [ ] Monitoring dashboard deployed


- [ ] Alerting policies configured


- [ ] CI/CD pipeline configured


- [ ] Integration tests passing


- [ ] Cost monitoring enabled

### Post-Launch



- [ ] Verify first job runs successfully


- [ ] Check logs for errors


- [ ] Verify Tier 1 items written to GCS


- [ ] Test Pinkln integration (analyses generated)


- [ ] Monitor costs daily for first week


- [ ] Review Gemini API usage


- [ ] Optimize batch sizes if needed


- [ ] Document any issues encountered

---

## 📚 Additional Resources



- [PNKLN Core Stack Documentation](../docs/architecture/)


- [Pinkln Reasoning Engine](../pinkln-reasoning-engine/README.md)


- [ShadowTag-v4 Global Edge Fabric](../shadowtag_v4-global-edge-fabric/docs/)


- [Gemini API Pricing](https://ai.google.dev/pricing)


- [GKE Autopilot Documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)

---

**Status:** ✅ Deployment architecture complete
**Target Launch:** Q1 2026
**Estimated Cost:** $77/month
**Integration:** Feeds Pinkln reasoning layer with Tier 1 intelligence

---

**Last Updated:** 2025-11-17
**Version:** 1.0-Production
