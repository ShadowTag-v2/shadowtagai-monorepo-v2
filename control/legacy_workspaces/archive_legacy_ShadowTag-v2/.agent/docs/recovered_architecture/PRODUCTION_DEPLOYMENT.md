# Production Deployment Guide

**Complete guide for deploying Consensus Orchestrator to Pnkln GKE**

---

## Quick Start (5 Minutes)

```bash

# 1. Clone and navigate

cd ~/aiyou-fastapi-services/voice_consensus

# 2. Set your project

export GOOGLE_CLOUD_PROJECT=pnkln-production

# 3. Deploy!

./deploy.sh

```

That's it! But read below for full setup...

---

## Table of Contents



1. [Prerequisites](#prerequisites)


2. [Initial Setup](#initial-setup)


3. [Build and Deploy](#build-and-deploy)


4. [Memory Sync Pipeline](#memory-sync-pipeline)


5. [Testing](#testing)


6. [Monitoring](#monitoring)


7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

```bash

# Install gcloud SDK

curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate

gcloud auth login
gcloud auth configure-docker

# Install kubectl

gcloud components install kubectl

# Verify installations

gcloud version
kubectl version --client
docker --version

```

### GCP Project Setup

```bash

# Set project

export GOOGLE_CLOUD_PROJECT=pnkln-production
gcloud config set project $GOOGLE_CLOUD_PROJECT

# Enable APIs

gcloud services enable \
  container.googleapis.com \
  storage.googleapis.com \
  cloudbuild.googleapis.com \
  compute.googleapis.com

```

---

## Initial Setup

### 1. Create GKE Cluster

```bash

# Create production cluster

gcloud container clusters create consensus-cluster \
  --region us-central1 \
  --num-nodes 2 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10 \
  --enable-autorepair \
  --enable-autoupgrade \
  --addons HorizontalPodAutoscaling,HttpLoadBalancing \
  --workload-pool=$GOOGLE_CLOUD_PROJECT.svc.id.goog

# Get credentials

gcloud container clusters get-credentials consensus-cluster --region us-central1

```

**Cost:** ~$150-300/month (2-10 nodes, n1-standard-2)

### 2. Create GCS Bucket for Memory

```bash

# Create bucket

gsutil mb -p $GOOGLE_CLOUD_PROJECT -l us-central1 gs://pnkln-consensus-memory

# Enable versioning

gsutil versioning set on gs://pnkln-consensus-memory

# Set lifecycle (optional: keep 10 versions, delete after 90 days)

cat > lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "numNewerVersions": 10,
          "isLive": false
        }
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://pnkln-consensus-memory

```

**Cost:** ~$0.026/month (1GB storage)

### 3. Create Service Account

```bash

# Create service account

gcloud iam service-accounts create consensus-sa \
  --display-name="Consensus Orchestrator"

# Grant GCS access

gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member="serviceAccount:consensus-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Enable workload identity

gcloud iam service-accounts add-iam-policy-binding \
  consensus-sa@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$GOOGLE_CLOUD_PROJECT.svc.id.goog[consensus/consensus-sa]"

```

### 4. Create API Keys Secret

```bash

# Set API keys as environment variables

export GOOGLE_API_KEY="your-google-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export XAI_API_KEY="your-xai-api-key"
export PERPLEXITY_API_KEY="your-perplexity-api-key"
export API_KEYS="client-key-1,client-key-2,client-key-3"

# Create namespace first

kubectl create namespace consensus

# Create secret

kubectl create secret generic api-keys \
  --from-literal=google-api-key=$GOOGLE_API_KEY \
  --from-literal=anthropic-api-key=$ANTHROPIC_API_KEY \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  --from-literal=xai-api-key=$XAI_API_KEY \
  --from-literal=perplexity-api-key=$PERPLEXITY_API_KEY \
  --from-literal=api-keys=$API_KEYS \
  --namespace=consensus

# Verify

kubectl get secret api-keys -n consensus

```

---

## Build and Deploy

### Option 1: Automated Deployment (Recommended)

```bash
cd ~/aiyou-fastapi-services/voice_consensus

# Deploy everything

./deploy.sh

```

The script will:


1. Build Docker image


2. Push to GCR


3. Update Kubernetes manifests


4. Deploy to GKE


5. Wait for rollout


6. Display external IP

### Option 2: Manual Deployment

```bash
cd ~/aiyou-fastapi-services/voice_consensus

# 1. Build Docker image

docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/consensus-orchestrator:v1.0 .

# 2. Push to GCR

docker push gcr.io/$GOOGLE_CLOUD_PROJECT/consensus-orchestrator:v1.0

# 3. Update manifests with project ID

find k8s/ -name "*.yaml" -exec sed -i "s/PROJECT_ID/$GOOGLE_CLOUD_PROJECT/g" {} \;

# 4. Apply manifests in order

kubectl apply -f k8s/01-namespace.yaml
kubectl apply -f k8s/02-serviceaccount.yaml
kubectl apply -f k8s/03-pvc.yaml
kubectl apply -f k8s/04-configmap.yaml

# Secrets already created above

kubectl apply -f k8s/06-deployment.yaml
kubectl apply -f k8s/07-service.yaml
kubectl apply -f k8s/08-hpa.yaml

# 5. Wait for deployment

kubectl rollout status deployment/consensus-orchestrator -n consensus

# 6. Get external IP

kubectl get service consensus-orchestrator -n consensus

```

---

## Memory Sync Pipeline

### Setup Automated Sync

```bash
cd ~/aiyou-fastapi-services/voice_consensus

# Setup daily cron job (runs at 8 PM)

./setup_cron.sh

```

This configures:


- **Local → GitHub**: Personal memory sync


- **Local → GCS**: Team memory upload


- **GCS → K8s**: ConfigMap update


- **K8s**: Pod restart to load new memory

### Manual Sync

```bash

# Sync everything

./sync_memory.sh

# Or step-by-step:

# 1. Extract patterns

python claude_code_memory.py sync 7

# 2. Upload to GCS

python vertex_gke_deployment.py sync-to-gcs

# 3. Update ConfigMap

python vertex_gke_deployment.py create-configmap
kubectl apply -f k8s/memory-configmap.yaml

# 4. Restart pods

kubectl rollout restart deployment/consensus-orchestrator -n consensus

```

### Verify Memory Loaded

```bash

# Check init container logs

POD=$(kubectl get pods -n consensus -l app=consensus-orchestrator -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD -n consensus -c memory-sync

# Check memory file in pod

kubectl exec -it $POD -n consensus -- cat /memory/memory.md | head -20

```

---

## Testing

### 1. Health Check

```bash

# Get external IP

EXTERNAL_IP=$(kubectl get service consensus-orchestrator -n consensus -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Health check

curl http://$EXTERNAL_IP/health | jq .

```

**Expected:**

```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T...",
  "version": "1.0.0",
  "memory_loaded": true,
  "models_available": {
    "gemini": true,
    "claude": true,
    "gpt": true,
    "perplexity": true,
    "grok": true
  }
}

```

### 2. Test Query

```bash

# Simple query

curl -X POST http://$EXTERNAL_IP/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: client-key-1" \
  -d '{
    "message": "Design a scalable authentication system for FastAPI",
    "max_threads": 4,
    "tags": ["architecture", "auth"]
  }' | jq .

```

**Expected:**

```json
{
  "query_id": "123",
  "final_output": "...",
  "threads": [...],
  "execution_summary": {
    "total_threads": 4,
    "successful_threads": 4,
    "success_rate": 1.0
  },
  "cost_breakdown": {
    "total_cost": 1.23,
    "api_calls_made": 45
  },
  "timestamp": "2025-11-17T..."
}

```

### 3. Load Test

```bash

# Install hey (load testing tool)

go install github.com/rakyll/hey@latest

# 100 requests, 10 concurrent

hey -n 100 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: client-key-1" \
  -d '{"message":"Test query"}' \
  http://$EXTERNAL_IP/query

```

---

## Monitoring

### View Logs

```bash

# Tail logs

kubectl logs -f deployment/consensus-orchestrator -n consensus

# Logs from specific pod

kubectl logs -f $POD -n consensus

# Logs from init container

kubectl logs $POD -n consensus -c memory-sync

# Previous pod logs (after crash)

kubectl logs $POD -n consensus --previous

```

### Watch Pods

```bash

# Watch pod status

kubectl get pods -n consensus -w

# Describe pod (for troubleshooting)

kubectl describe pod $POD -n consensus

# Pod events

kubectl get events -n consensus --sort-by='.lastTimestamp'

```

### Metrics

```bash

# Get metrics

curl http://$EXTERNAL_IP/metrics \
  -H "X-API-Key: client-key-1" | jq .

```

**Expected:**

```json
{
  "total_queries": 145,
  "total_cost": 187.23,
  "avg_response_time": 8.5,
  "uptime_seconds": 86400
}

```

### HPA Status

```bash

# Check autoscaler

kubectl get hpa -n consensus

# Describe HPA

kubectl describe hpa consensus-orchestrator-hpa -n consensus

```

---

## Troubleshooting

### Pods Not Starting

```bash

# Check pod status

kubectl get pods -n consensus

# Describe pod

kubectl describe pod $POD -n consensus

# Common issues:

# 1. Image pull failure → Check GCR permissions

# 2. Secret not found → Recreate secrets

# 3. Init container failing → Check GCS access

```

### Memory Not Loading

```bash

# Check init container logs

kubectl logs $POD -n consensus -c memory-sync

# Verify GCS bucket

gsutil ls -lh gs://pnkln-consensus-memory/memories/

# Upload memory manually

python vertex_gke_deployment.py sync-to-gcs

```

### API Returning 503

```bash

# Check readiness probe

kubectl get pods -n consensus

# Check logs for model initialization

kubectl logs $POD -n consensus | grep "Models available"

# Verify secrets

kubectl get secret api-keys -n consensus -o yaml

```

### High Costs

```bash

# Check metrics

curl http://$EXTERNAL_IP/metrics -H "X-API-Key: client-key-1"

# View query history

kubectl logs deployment/consensus-orchestrator -n consensus | grep "\[Cost\]"

# Reduce max_threads to lower costs per query

```

---

## Updating the Deployment

### Update Code

```bash
cd ~/aiyou-fastapi-services/voice_consensus

# 1. Build new image

docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/consensus-orchestrator:v1.1 .

# 2. Push

docker push gcr.io/$GOOGLE_CLOUD_PROJECT/consensus-orchestrator:v1.1

# 3. Update deployment

kubectl set image deployment/consensus-orchestrator \
  orchestrator=gcr.io/$GOOGLE_CLOUD_PROJECT/consensus-orchestrator:v1.1 \
  -n consensus

# 4. Wait for rollout

kubectl rollout status deployment/consensus-orchestrator -n consensus

# Rollback if needed

kubectl rollout undo deployment/consensus-orchestrator -n consensus

```

### Update Configuration

```bash

# Update ConfigMap

kubectl edit configmap consensus-config -n consensus

# Update Secrets

kubectl delete secret api-keys -n consensus
kubectl create secret generic api-keys \
  --from-literal=google-api-key=$NEW_GOOGLE_API_KEY \
  ... \
  --namespace=consensus

# Restart pods to pick up changes

kubectl rollout restart deployment/consensus-orchestrator -n consensus

```

---

## Cost Breakdown

### Infrastructure (Monthly)

| Component | Cost | Notes |
|-----------|------|-------|
| GKE Cluster (2 nodes) | $150 | Base cost |
| Autoscaling (up to 10) | +$600 | Peak load only |
| Load Balancer | $18 | Static IP + forwarding |
| GCS Storage | $0.026 | 1GB memory storage |
| **Base Total** | **~$170/month** | Typical usage |
| **Peak Total** | **~$770/month** | During high load |

### API Usage (Variable)

| Volume | Cost per Query | Monthly Total |
|--------|----------------|---------------|
| 100 queries/day | $0.50-$2.00 | $1,500-$6,000 |
| 500 queries/day | $0.50-$2.00 | $7,500-$30,000 |

**Total: $170 + API costs**

---

## Security Best Practices

### 1. Rotate API Keys

```bash

# Update secrets

kubectl create secret generic api-keys-new \
  --from-literal=... \
  --namespace=consensus

# Update deployment to use new secret

kubectl edit deployment consensus-orchestrator -n consensus

# Delete old secret

kubectl delete secret api-keys -n consensus

```

### 2. Enable Network Policies

```bash

# Restrict ingress to load balancer only

kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: consensus-netpol
  namespace: consensus
spec:
  podSelector:
    matchLabels:
      app: consensus-orchestrator
  policyTypes:


  - Ingress
  ingress:


  - from:


    - namespaceSelector: {}
    ports:


    - protocol: TCP
      port: 8000
EOF

```

### 3. Enable Pod Security

```bash

# Apply Pod Security Standards

kubectl label namespace consensus \
  pod-security.kubernetes.io/enforce=baseline \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted

```

---

## Production Checklist

Before going live:



- [ ] GKE cluster created with autoscaling


- [ ] GCS bucket created with versioning


- [ ] Service account with proper IAM roles


- [ ] Secrets created with all API keys


- [ ] Docker image built and pushed to GCR


- [ ] All K8s manifests applied


- [ ] Health checks passing


- [ ] Test query successful


- [ ] Memory sync pipeline configured


- [ ] Monitoring dashboards set up


- [ ] Cost alerts configured


- [ ] Team access documented


- [ ] Backup strategy in place

---

## Summary

**You now have:**

✅ **Production API** on GKE with autoscaling
✅ **Memory persistence** via GCS
✅ **Automated sync** pipeline (local → GitHub → GCS → K8s)
✅ **Health checks** and monitoring
✅ **Load balancer** with external IP
✅ **Cost tracking** and metrics

**Access your API:**

```bash
http://<EXTERNAL_IP>/docs

```

**Monitor in real-time:**

```bash
kubectl get pods -n consensus -w
kubectl logs -f deployment/consensus-orchestrator -n consensus

```

**Your production deployment is complete!**
