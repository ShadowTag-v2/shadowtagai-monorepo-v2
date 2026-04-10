# Deployment Guide

## GKE Deployment for Pnkln File Search

### Prerequisites

1. **GCP Project Setup**
   - Project ID: `pnkln-core-gke`
   - Region: `us-central1`
   - Vertex AI API enabled
   - GCS bucket created: `pnkln-policy-corpus`

2. **Service Account**

   ```bash
   # Create service account
   gcloud iam service-accounts create pnkln-file-search \
     --display-name="Pnkln File Search Service"

   # Grant permissions
   gcloud projects add-iam-policy-binding pnkln-core-gke \
     --member="serviceAccount:redacted@shadowtag-v4.local" \
     --role="roles/aiplatform.user"

   gcloud projects add-iam-policy-binding pnkln-core-gke \
     --member="serviceAccount:redacted@shadowtag-v4.local" \
     --role="roles/storage.objectViewer"
   ```

3. **GKE Cluster**

   ```bash
   # Create cluster (if not exists)
   gcloud container clusters create pnkln-core \
     --region us-central1 \
     --num-nodes 3 \
     --machine-type n1-standard-4 \
     --enable-autoscaling \
     --min-nodes 3 \
     --max-nodes 10 \
     --enable-workload-identity

   # Get credentials
   gcloud container clusters get-credentials pnkln-core --region us-central1
   ```

### Step 1: Build and Push Docker Image

```bash
# Authenticate with GCR
gcloud auth configure-docker

# Build image
docker build -t gcr.io/pnkln-core-gke/file-search:latest .

# Tag with version
docker tag gcr.io/pnkln-core-gke/file-search:latest \
  gcr.io/pnkln-core-gke/file-search:v0.1.0

# Push to GCR
docker push gcr.io/pnkln-core-gke/file-search:latest
docker push gcr.io/pnkln-core-gke/file-search:v0.1.0
```

### Step 2: Setup Workload Identity

```bash
# Bind Kubernetes SA to GCP SA
gcloud iam service-accounts add-iam-policy-binding \
  redacted@shadowtag-v4.local \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:pnkln-core-gke.svc.id.goog[pnkln-core/pnkln-file-search]"
```

### Step 3: Initialize Corpora

```bash
# Upload policy documents to GCS
gsutil -m cp -r policy_docs/* gs://pnkln-policy-corpus/

# Run initialization script
export GCP_PROJECT_ID=pnkln-core-gke
export GCP_REGION=us-central1
export GCP_STORAGE_BUCKET=gs://pnkln-policy-corpus

./scripts/setup_file_search.sh
```

### Step 4: Deploy to GKE

```bash
# Create namespace
kubectl create namespace pnkln-core

# Deploy application
kubectl apply -f k8s/deployment.yaml

# Deploy autoscaling
kubectl apply -f k8s/hpa.yaml

# Deploy ingress
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get pods -n pnkln-core
kubectl logs -f deployment/pnkln-file-search -n pnkln-core
```

### Step 5: Verify Health

```bash
# Port forward for testing
kubectl port-forward -n pnkln-core svc/pnkln-file-search 8000:80

# Check health
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/monitoring/health

# Test query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Test query",
    "vertical": "defense"
  }'
```

## Monitoring Setup

### Prometheus

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Service monitor for file-search
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: pnkln-file-search
  namespace: pnkln-core
spec:
  selector:
    matchLabels:
      app: pnkln-file-search
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
EOF
```

### Grafana Dashboard

Import dashboard from `monitoring/grafana-dashboard.json`

Key panels:

- File search latency (p50, p95, p99)
- Judge #6 enforcement latency
- Error rates
- Kill switch state
- Request throughput

## Scaling

### Horizontal Pod Autoscaling

Already configured in `k8s/hpa.yaml`:

- Min replicas: 3
- Max replicas: 10
- CPU target: 70%
- Memory target: 80%

### Vertical Scaling

Update resource limits in `k8s/deployment.yaml`:

```yaml
resources:
  requests:
    cpu: 1000m # Increase from 500m
    memory: 1Gi # Increase from 512Mi
  limits:
    cpu: 4000m # Increase from 2000m
    memory: 4Gi # Increase from 2Gi
```

## Rollback

```bash
# View rollout history
kubectl rollout history deployment/pnkln-file-search -n pnkln-core

# Rollback to previous version
kubectl rollout undo deployment/pnkln-file-search -n pnkln-core

# Rollback to specific revision
kubectl rollout undo deployment/pnkln-file-search -n pnkln-core --to-revision=2
```

## Disaster Recovery

### Backup Corpora

```bash
# Export corpus metadata
kubectl exec -n pnkln-core deployment/pnkln-file-search -- \
  python -c "
import asyncio
from pnkln_file_search.corpus.manager import CorpusManager

async def backup():
    manager = CorpusManager()
    await manager.initialize()
    corpora = await manager.list_corpora()
    print(corpora)

asyncio.run(backup())
" > corpus-backup.json
```

### Restore from Backup

```bash
# Re-run setup script with existing documents
./scripts/setup_file_search.sh
```

## Production Checklist

- [ ] Service account with minimal permissions
- [ ] Workload Identity configured
- [ ] Resource limits set appropriately
- [ ] HPA configured
- [ ] Health checks configured
- [ ] Prometheus monitoring enabled
- [ ] Logging to Cloud Logging
- [ ] Alerting rules configured
- [ ] Backup strategy in place
- [ ] Rollback plan tested
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] Runbook created

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n pnkln-core

# Check logs
kubectl logs <pod-name> -n pnkln-core

# Common issues:
# - Workload Identity not configured
# - Service account permissions missing
# - Image pull errors
```

### High latency

```bash
# Check metrics
kubectl port-forward -n pnkln-core svc/pnkln-file-search 8000:80
curl http://localhost:8000/metrics | grep latency

# Check kill switch status
curl http://localhost:8000/api/v1/monitoring/health

# Scale up if needed
kubectl scale deployment pnkln-file-search -n pnkln-core --replicas=6
```

### File search errors

```bash
# Check Vertex AI quotas
gcloud alpha services quota list \
  --service=aiplatform.googleapis.com \
  --filter="aiplatform.googleapis.com"

# Check GCS bucket access
kubectl exec -n pnkln-core deployment/pnkln-file-search -- \
  gsutil ls gs://pnkln-policy-corpus/
```

## Cost Optimization

1. **Right-size pods**: Monitor actual resource usage and adjust requests/limits
2. **Use Preemptible nodes**: For non-critical environments
3. **Optimize corpus size**: Remove duplicate documents
4. **Adjust HPA**: Tune min/max replicas based on traffic patterns
5. **Use caching**: Implement Redis for frequent queries

## Security Best Practices

1. **Network Policies**

   ```bash
   kubectl apply -f k8s/network-policy.yaml
   ```

2. **Pod Security Policies**
   - Non-root user
   - Read-only root filesystem
   - No privilege escalation

3. **Secrets Management**
   - Use Secret Manager for sensitive data
   - Rotate service account keys regularly

4. **TLS/HTTPS**
   - Use cert-manager for TLS certificates
   - Enforce HTTPS in ingress
