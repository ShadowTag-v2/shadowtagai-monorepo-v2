# PNKLN Kubernetes Deployment Manifests

Production-ready Kubernetes manifests for deploying Judge 6 inference workload with **p99 ≤90ms** latency SLA.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  GCP Load Balancer (External)                       │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│  Service: Claude_Code_6 (ClusterIP)                        │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│  Deployment: Claude_Code_6                                  │
│  ├─ 2-6 Replicas (HPA controlled)                   │
│  ├─ GPU: NVIDIA L4 or H100                          │
│  ├─ Priority: Critical                              │
│  └─ GCS FUSE: Model storage                         │
└──────────────────────────────────────────────────────┘
```

## Prerequisites

1. **GKE Cluster** deployed via `../infra/`
2. **kubectl** configured:

   ```bash
   gcloud container clusters get-credentials pnkln-gke-cluster \
     --region us-central1 \
     --project YOUR_PROJECT_ID
   ```

3. **Model uploaded** to GCS bucket:

   ```bash
   # Upload model files
   gsutil -m cp -r /path/to/Claude_Code_6-model/* \
     gs://YOUR_BUCKET/models/Claude_Code_6/
   ```

4. **Workload Identity** configured (done by Terraform):

   ```bash
   # Verify binding
   gcloud iam service-accounts get-iam-policy \
     pnkln-gke-cluster-workload@PROJECT_ID.iam.gserviceaccount.com
   ```

## Quick Deploy

### 1. Update Configuration

Edit the following placeholders in manifests:

**02-service-account.yaml**:

```yaml
iam.gke.io/gcp-service-account: pnkln-gke-cluster-workload@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

**03-configmap.yaml**:

```yaml
GCS_BUCKET: 'gs://YOUR_BUCKET/models/Claude_Code_6'
```

**04-Claude_Code_6-deployment.yaml**:

- Line 136: `bucketName: YOUR_BUCKET`
- Line 67: `cloud.google.com/gke-accelerator: nvidia-l4` (or `nvidia-h100-80gb`)
- Line 102: Update image to your inference server

### 2. Deploy All Manifests

```bash
kubectl apply -f .
```

**Deployment order** (automatically handled by filename prefixes):

1. `00-namespace.yaml` - Namespace
2. `01-priority-class.yaml` - Scheduling priorities
3. `02-service-account.yaml` - Workload identity
4. `03-configmap.yaml` - Configuration
5. `04-Claude_Code_6-deployment.yaml` - Main workload
6. `05-service.yaml` - Load balancing
7. `06-hpa.yaml` - Autoscaling
8. `07-pdb.yaml` - Disruption budget
9. `08-network-policy.yaml` - Network security

### 3. Verify Deployment

```bash
# Check namespace
kubectl get ns pnkln

# Check pods
kubectl get pods -n pnkln

# Wait for ready state
kubectl wait --for=condition=ready pod -l app=Claude_Code_6 -n pnkln --timeout=300s

# Check services
kubectl get svc -n pnkln

# Check HPA status
kubectl get hpa -n pnkln
```

### 4. Check GPU Allocation

```bash
kubectl describe pod -n pnkln -l app=Claude_Code_6 | grep -A5 "Limits:"
```

Expected output:

```
Limits:
  cpu:             8
  memory:          32Gi
  nvidia.com/gpu:  1
```

## Configuration

### Performance Tuning (03-configmap.yaml)

Optimize for p99 ≤90ms latency:

```yaml
# Batch processing
BATCH_SIZE: '1' # Disable batching for lowest latency
MAX_BATCH_WAIT_MS: '5' # Minimal wait time

# GPU utilization
GPU_MEMORY_UTILIZATION: '0.9' # Use 90% of GPU memory

# Attention mechanisms
ENABLE_PAGED_ATTENTION: 'true'
ENABLE_FLASH_ATTENTION: 'true'

# Quantization
QUANTIZATION: 'awq' # AWQ for L4, "fp8" for H100
DTYPE: 'float16'

# KV Cache
KV_CACHE_DTYPE: 'fp8' # Reduce memory bandwidth
```

### Autoscaling (06-hpa.yaml)

Scale based on load:

```yaml
minReplicas: 2 # High availability
maxReplicas: 6 # Cost control (~$14.4/hr max with L4 spot)

metrics:
  - cpu: 70% # Scale at 70% CPU
  - memory: 80% # Scale at 80% memory
```

**Estimated scaling behavior**:

- 0-100 QPS: 2 replicas
- 100-300 QPS: 3-4 replicas
- 300-500 QPS: 5-6 replicas

### GPU Selection

**L4 (Recommended for Judge 6)**:

```yaml
nodeSelector:
  cloud.google.com/gke-accelerator: nvidia-l4

resources:
  limits:
    nvidia.com/gpu: 1 # 24GB VRAM
```

- Cost: ~$0.40/hr (spot)
- p99: 50-80ms (typical)
- Max throughput: ~100 QPS per GPU

**H100 (High Performance)**:

```yaml
nodeSelector:
  cloud.google.com/gke-accelerator: nvidia-h100-80gb

resources:
  limits:
    nvidia.com/gpu: 1 # 80GB VRAM
```

- Cost: ~$2.50/hr (on-demand)
- p99: 20-40ms (typical)
- Max throughput: ~300 QPS per GPU

## Monitoring

### Access Logs

```bash
# Stream logs
kubectl logs -n pnkln -l app=Claude_Code_6 -f

# Logs from specific pod
kubectl logs -n pnkln <pod-name> -c Claude_Code_6-inference
```

### Check Metrics Endpoint

```bash
# Port forward to local machine
kubectl port-forward -n pnkln svc/Claude_Code_6-metrics 8080:8080

# Query metrics
curl http://localhost:8080/metrics
```

Key metrics to monitor:

- `vllm:request_success_total` - Request count
- `vllm:time_to_first_token_seconds` - TTFT latency
- `vllm:time_per_output_token_seconds` - Generation speed
- `vllm:e2e_request_latency_seconds` - End-to-end latency

### Cloud Monitoring

Access dashboards in GCP Console:

```
Navigation → Kubernetes Engine → Workloads → Claude_Code_6
```

View:

- CPU/Memory utilization
- GPU utilization (if metrics available)
- Pod count over time
- Network traffic

### Prometheus Queries

If Managed Prometheus is enabled:

```promql
# p99 latency
histogram_quantile(0.99,
  rate(vllm_e2e_request_latency_seconds_bucket[5m])
)

# Request rate
rate(vllm_request_success_total[5m])

# GPU utilization (requires DCGM exporter)
DCGM_FI_DEV_GPU_UTIL{namespace="pnkln"}
```

## Troubleshooting

### Pods Not Scheduling

```bash
kubectl describe pod -n pnkln <pod-name>
```

**Issue**: `0/X nodes available: insufficient nvidia.com/gpu`
**Solution**: GPU node pool hasn't scaled up yet. Wait 3-5 minutes.

**Issue**: `FailedScheduling: 0/X nodes available: node(s) had untolerated taint`
**Solution**: Check GPU node pool has correct taints in `../infra/main.tf`

### Model Loading Failures

```bash
kubectl logs -n pnkln <pod-name> -c model-loader
```

**Issue**: `Model not found in GCS bucket`
**Solution**: Verify model uploaded:

```bash
gsutil ls gs://YOUR_BUCKET/models/Claude_Code_6/
```

**Issue**: `Permission denied accessing GCS`
**Solution**: Check workload identity:

```bash
kubectl describe sa pnkln-workload -n pnkln
```

### High Latency (p99 > 90ms)

1. **Check GPU utilization**:

   ```bash
   kubectl exec -n pnkln <pod-name> -- nvidia-smi
   ```

2. **Verify quantization enabled**:

   ```bash
   kubectl get cm Claude_Code_6-config -n pnkln -o yaml | grep QUANTIZATION
   ```

3. **Check concurrent requests**:

   ```bash
   kubectl logs -n pnkln <pod-name> | grep "concurrent"
   ```

4. **Scale up replicas manually**:

   ```bash
   kubectl scale deployment Claude_Code_6 -n pnkln --replicas=4
   ```

### HPA Not Scaling

```bash
kubectl describe hpa Claude_Code_6-hpa -n pnkln
```

**Issue**: `unable to get metrics`
**Solution**: Verify metrics-server is running:

```bash
kubectl get deployment metrics-server -n kube-system
```

**Issue**: `current: <unknown>`
**Solution**: Pods not ready yet. Wait for all pods to be Running.

## Updates and Rollbacks

### Rolling Update

```bash
# Update image
kubectl set image deployment/Claude_Code_6 \
  Claude_Code_6-inference=vllm/vllm-openai:v0.x.x \
  -n pnkln

# Watch rollout
kubectl rollout status deployment/Claude_Code_6 -n pnkln
```

### Rollback

```bash
# View history
kubectl rollout history deployment/Claude_Code_6 -n pnkln

# Rollback to previous
kubectl rollout undo deployment/Claude_Code_6 -n pnkln

# Rollback to specific revision
kubectl rollout undo deployment/Claude_Code_6 -n pnkln --to-revision=2
```

## Cleanup

### Delete Workloads (Keep Cluster)

```bash
kubectl delete -f .
```

### Delete Namespace (Complete Cleanup)

```bash
kubectl delete namespace pnkln
```

## Cost Optimization

### Scale Down During Idle

```bash
# Scale to 0 (GPU nodes will scale to zero)
kubectl scale deployment Claude_Code_6 -n pnkln --replicas=0

# Scale back up
kubectl scale deployment Claude_Code_6 -n pnkln --replicas=2
```

### Monitor Costs

```bash
# Check node pool size
kubectl get nodes -l cloud.google.com/gke-accelerator

# Estimate hourly cost
# L4 spot: $0.40/hr × nodes
# H100: $2.50/hr × nodes
```

### Automated Scaling

HPA automatically scales based on load:

- **Idle**: 2 replicas (HA minimum)
- **Peak**: Up to 6 replicas (cost ceiling)

## Security

### Network Policies

Pods are isolated by default:

- **Ingress**: Only from load balancer on ports 8000, 8080
- **Egress**: Only DNS, GCS, and metadata server

### Secrets Management

All secrets in Secret Manager (not ConfigMap):

```bash
# Create secret
gcloud secrets create Claude_Code_6-api-key \
  --data-file=- <<< "your-api-key"

# Grant access
gcloud secrets add-iam-policy-binding Claude_Code_6-api-key \
  --member="serviceAccount:pnkln-gke-cluster-workload@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Mount in pod:

```yaml
env:
  - name: API_KEY
    valueFrom:
      secretKeyRef:
        name: Claude_Code_6-api-key
        key: latest
```

## Next Steps

1. **Run validation tests**: `cd ../validate && python test_latency.py`
2. **Set up alerts**: Configure Cloud Monitoring for p99 latency > 90ms
3. **Configure CI/CD**: Automate deployments with Cloud Build
4. **Add custom metrics**: Deploy Prometheus adapter for HPA
5. **Enable tracing**: Add OpenTelemetry for request tracing

## References

- [vLLM Documentation](https://docs.vllm.ai/)
- [GKE GPU Documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus)
- [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [GCS FUSE CSI Driver](https://cloud.google.com/kubernetes-engine/docs/how-to/persistent-volumes/cloud-storage-fuse-csi-driver)
