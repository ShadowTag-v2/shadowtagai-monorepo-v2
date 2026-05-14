# GKE Deployment Guide

**Nightly Intel Pipeline - Google Kubernetes Engine CronJob Deployment**

This guide covers deploying the Nightly Intel Pipeline as a GKE CronJob for automated nightly execution.

## Prerequisites

1. **GKE Cluster**
   ```bash
   gcloud container clusters create nightly-intel-cluster \
     --zone=us-central1-a \
     --num-nodes=1 \
     --machine-type=e2-standard-2 \
     --enable-autoscaling \
     --min-nodes=1 \
     --max-nodes=3
   ```

2. **Docker Image Registry**
   - Enable Google Container Registry (GCR)
   - Or use Artifact Registry

3. **API Keys**
   - GitHub Personal Access Token
   - Anthropic API Key

## Deployment Steps

### 1. Build and Push Docker Image

```bash
# Set your GCP project ID
export PROJECT_ID="your-gcp-project-id"

# Build the Docker image
docker build -t gcr.io/${PROJECT_ID}/nightly-intel-pipeline:latest .

# Configure Docker for GCR
gcloud auth configure-docker

# Push to GCR
docker push gcr.io/${PROJECT_ID}/nightly-intel-pipeline:latest
```

### 2. Update Kubernetes Manifests

Replace `PROJECT_ID` in the following files:
- `cronjob.yaml`: Line 49 (image reference)
- `service-account.yaml`: Line 9 (GCP service account annotation)

```bash
# Quick replacement script
sed -i "s/PROJECT_ID/${PROJECT_ID}/g" kubernetes/*.yaml
```

### 3. Create Secrets

**Option A: Using kubectl**
```bash
kubectl create secret generic intel-pipeline-secrets \
  --from-literal=github-token='YOUR_GITHUB_TOKEN' \
  --from-literal=anthropic-api-key='YOUR_ANTHROPIC_KEY' \
  --namespace=default
```

**Option B: Using secret.yaml**
```bash
# Copy example and edit with actual values
cp kubernetes/secret.yaml.example kubernetes/secret.yaml
nano kubernetes/secret.yaml  # Add real credentials

# Apply (be careful not to commit this file!)
kubectl apply -f kubernetes/secret.yaml
```

### 4. Deploy Resources

```bash
# Apply in order
kubectl apply -f kubernetes/service-account.yaml
kubectl apply -f kubernetes/pvc.yaml
kubectl apply -f kubernetes/cronjob.yaml
```

### 5. Verify Deployment

```bash
# Check CronJob status
kubectl get cronjobs

# Check persistent volume claims
kubectl get pvc

# View CronJob details
kubectl describe cronjob nightly-intel-pipeline
```

## Configuration

### Schedule Adjustment

To change the execution time, edit `cronjob.yaml`:
```yaml
spec:
  schedule: "0 2 * * *"  # 2 AM UTC daily
  timeZone: "UTC"
```

**Examples**:
- Every 6 hours: `"0 */6 * * *"`
- Twice daily (2 AM, 2 PM): `"0 2,14 * * *"`
- Weekdays only: `"0 2 * * 1-5"`

### Resource Limits

Adjust resources in `cronjob.yaml`:
```yaml
resources:
  requests:
    cpu: "1000m"     # Increase for faster processing
    memory: "2Gi"
  limits:
    cpu: "2000m"
    memory: "4Gi"
```

### Storage Size

Modify PVC sizes in `pvc.yaml`:
```yaml
resources:
  requests:
    storage: 50Gi  # Increase if flattening many repos
```

## Monitoring

### Manual Trigger (Testing)

```bash
# Create a one-time job from CronJob
kubectl create job --from=cronjob/nightly-intel-pipeline manual-run-1
```

### View Logs

```bash
# List recent jobs
kubectl get jobs

# Get pod name from latest job
POD_NAME=$(kubectl get pods --selector=job-name=nightly-intel-pipeline-<job-id> -o jsonpath='{.items[0].metadata.name}')

# Stream logs
kubectl logs -f $POD_NAME
```

### Check Job History

```bash
# Successful runs
kubectl get jobs --selector=app=nightly-intel-pipeline --field-selector status.successful=1

# Failed runs
kubectl get jobs --selector=app=nightly-intel-pipeline --field-selector status.failed=1
```

## Data Access

### Retrieve Briefings

```bash
# Get pod name from latest successful job
POD_NAME=$(kubectl get pods --selector=app=nightly-intel-pipeline --field-selector status.phase=Succeeded --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')

# Copy briefing to local machine
kubectl cp ${POD_NAME}:/app/data/briefings/latest.md ./briefing.md
```

### Access Database

```bash
# Port-forward to access SQLite database (requires running pod)
kubectl port-forward $POD_NAME 8080:8080

# Or copy database file
kubectl cp ${POD_NAME}:/app/storage/intel_pipeline.db ./intel_pipeline.db
```

## Cost Optimization

### Current Estimate: ~$77/Month

**Breakdown**:
- **GKE Compute**: $10-15/month (e2-standard-2, nightly runs)
- **Persistent Storage**: $2-5/month (65GB total)
- **Claude API**: $15-60/month (depends on volume)

### Optimization Tips

1. **Use Preemptible Nodes** (50-80% cheaper)
   ```bash
   gcloud container node-pools create preemptible-pool \
     --cluster=nightly-intel-cluster \
     --preemptible \
     --num-nodes=1
   ```

2. **Reduce Storage Costs**
   - Use nearline storage for old briefings
   - Clean up old repos/papers periodically

3. **Optimize Runtime**
   - Parallelize API calls (already implemented)
   - Cache robots.txt longer
   - Reduce `max_repos_per_topic` in config

## Troubleshooting

### CronJob Not Running

```bash
# Check CronJob events
kubectl describe cronjob nightly-intel-pipeline

# Check for schedule issues
kubectl get cronjobs -o yaml
```

### Pod Failures

```bash
# View pod logs
kubectl logs -l app=nightly-intel-pipeline --tail=100

# Check resource constraints
kubectl top pods -l app=nightly-intel-pipeline
```

### Storage Issues

```bash
# Check PVC status
kubectl get pvc
kubectl describe pvc intel-pipeline-data-pvc

# View storage usage
kubectl exec -it $POD_NAME -- df -h /app/data
```

### Secret Not Found

```bash
# Verify secret exists
kubectl get secrets intel-pipeline-secrets -o yaml

# Recreate if missing
kubectl delete secret intel-pipeline-secrets
kubectl create secret generic intel-pipeline-secrets \
  --from-literal=github-token='TOKEN' \
  --from-literal=anthropic-api-key='KEY'
```

## Security Best Practices

1. **Secret Management**
   - Never commit `secret.yaml` with real credentials
   - Use Google Secret Manager for production
   - Rotate API keys regularly

2. **Network Policies**
   - Restrict egress to only required APIs
   - Implement pod security policies

3. **RBAC**
   - Use least-privilege service accounts
   - Audit role bindings regularly

## Integration with Services

The Ingestion Layer is called by 4 namespace services:

```yaml
# Example: Service calling the ingestion layer
apiVersion: v1
kind: Service
metadata:
  name: intel-consumer-service
spec:
  selector:
    app: consumer
  ports:
  - protocol: TCP
    port: 80
```

**Access Pattern**:
Services can trigger manual runs via:
```bash
kubectl create job --from=cronjob/nightly-intel-pipeline triggered-by-service-a
```

## Metrics and Observability

### Key Metrics to Monitor

1. **Runtime Duration**: Target ≤45 minutes
   - Alert if >60 minutes

2. **Items Ingested**: Daily volume
   - GitHub repos: ~30-50
   - arXiv papers: ~15-25

3. **Tier Distribution**:
   - Tier 1: 10-15%
   - Tier 2: 35-40%

4. **Cost per Item**: Target ≤$2.50
   - Monthly cost / total items

5. **Failure Rate**: Target <5%

### Setup Monitoring (GCP)

```bash
# Enable Cloud Logging
gcloud logging read "resource.type=k8s_container AND resource.labels.container_name=intel-pipeline" --limit 50

# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com
```

## Cleanup

```bash
# Delete all resources
kubectl delete cronjob nightly-intel-pipeline
kubectl delete pvc --selector=app=nightly-intel-pipeline
kubectl delete secret intel-pipeline-secrets
kubectl delete serviceaccount nightly-intel-sa
kubectl delete role nightly-intel-role
kubectl delete rolebinding nightly-intel-rolebinding

# Delete GKE cluster (if no longer needed)
gcloud container clusters delete nightly-intel-cluster --zone=us-central1-a
```

## Next Steps

1. **Test Deployment**: Run manual job and verify output
2. **Monitor First Week**: Check runtime, costs, quality metrics
3. **Tune Configuration**: Adjust tier thresholds based on results
4. **Integrate with Judge #6**: Set up data handoff pipeline
5. **Enable Alerting**: Configure Cloud Monitoring alerts

---

**Deployment Status**: Ready for GKE
**Target Runtime**: ~45 minutes/night
**Monthly Cost**: ~$77
**Confidence Level**: ≥60% (pre-production specs)
