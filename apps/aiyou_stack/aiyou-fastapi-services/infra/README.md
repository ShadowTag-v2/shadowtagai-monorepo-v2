# PNKLN GKE Infrastructure

Production-ready Terraform configuration for deploying PNKLN Core Stack on GKE with GPU node pools.

## Features

- **GPU Autoscaling**: Scale-to-zero L4 and H100 node pools
- **Cost Optimized**: Spot VMs, autoscaling, GCS FUSE for model loading
- **Private Cluster**: Secure by default with private nodes
- **Workload Identity**: Secure GCS and Secret Manager access
- **Monitoring**: Managed Prometheus + Cloud Monitoring
- **p99 ≤90ms Ready**: Optimized for low-latency inference (Judge 6)

## Prerequisites

1. **GCP Project** with billing enabled
2. **APIs enabled**:
   ```bash
   gcloud services enable container.googleapis.com \
     compute.googleapis.com \
     storage.googleapis.com \
     secretmanager.googleapis.com \
     monitoring.googleapis.com
   ```

3. **GPU Quota**: Request quota increases for:
   - `NVIDIA_L4_GPUS` in `us-central1`: 3
   - `NVIDIA_H100_80GB_GPUS` in `us-central1`: 2

4. **Terraform** >= 1.8.0:
   ```bash
   terraform version
   ```

5. **GCP Authentication**:
   ```bash
   gcloud auth application-default login
   ```

## Quick Start

### 1. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project details
```

**CRITICAL**: Update these values:
- `project_id`: Your GCP project ID
- `model_bucket_name`: Globally unique bucket name
- `master_authorized_networks`: Your Vertex AI Workbench IP ranges

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Plan Deployment

```bash
terraform plan
```

Verify:
- Zero errors
- GPU quota sufficient
- Bucket name unique

### 4. Deploy Infrastructure

```bash
terraform apply
```

**Estimated time**: 15-20 minutes

### 5. Configure kubectl

```bash
# Command from terraform output
gcloud container clusters get-credentials pnkln-gke-cluster \
  --region us-central1 \
  --project YOUR_PROJECT_ID
```

### 6. Verify Cluster

```bash
kubectl get nodes
kubectl get namespaces
```

## Cost Management

### Scale-to-Zero Configuration

GPU node pools automatically scale to zero when idle:

```hcl
min_node_count = 0  # Zero cost when no workloads
max_node_count = 3  # Auto-scale under load
```

### Estimated Monthly Costs

**Idle state** (GPU pools scaled to zero):
- CPU pool (1 node): ~$140/mo
- Networking: ~$20/mo
- GCS storage (100GB models): ~$2/mo
- **Total**: ~$162/mo

**Active state** (example: 12h/day Judge 6 on L4):
- L4 GPU (spot, 12h/day): ~$72/mo
- CPU pool: ~$140/mo
- Networking: ~$50/mo
- **Total**: ~$262/mo

**Production load** (24/7 with H100):
- H100 GPU (1 node 24/7): ~$1,800/mo
- L4 GPU (3 nodes, 50% utilization): ~$432/mo
- CPU pool: ~$140/mo
- **Total**: ~$2,372/mo

**Target budget**: $65K/mo supports ~27 H100 GPUs 24/7

## Security

### Private Cluster

Nodes use private IPs only. Master endpoint configurable:

```hcl
enable_private_nodes    = true
enable_private_endpoint = false  # true requires VPN/bastion
```

### Workload Identity

Secure access to GCS and Secret Manager:

```bash
# Kubernetes SA bound to Google SA
kubectl create serviceaccount pnkln-workload -n pnkln
kubectl annotate serviceaccount pnkln-workload -n pnkln \
  iam.gke.io/gcp-service-account=pnkln-gke-cluster-workload@PROJECT_ID.iam.gserviceaccount.com
```

### Secrets Management

All secrets stored in Secret Manager:

```bash
# Add API key secret
gcloud secrets versions add pnkln-gke-cluster-api-keys \
  --data-file=api-keys.json
```

## GPU Configuration

### L4 (Cost-Optimized Inference)

- **Machine**: g2-standard-4 (4 vCPUs, 16GB RAM)
- **GPU**: NVIDIA L4 (24GB VRAM)
- **Cost**: ~$0.40/hr (spot)
- **Use case**: Judge 6 with p99 ≤90ms SLA

### H100 (High-Performance Production)

- **Machine**: a3-highgpu-1g (12 vCPUs, 85GB RAM)
- **GPU**: NVIDIA H100 80GB
- **Cost**: ~$2.50/hr
- **Use case**: Large model inference, fine-tuning

## Monitoring

### Access Dashboards

```bash
# Get cluster endpoint
terraform output cluster_endpoint

# View metrics in Cloud Console
gcloud monitoring dashboards list
```

### Managed Prometheus

Metrics scraped automatically:
- GPU utilization
- Pod resource usage
- Custom application metrics

Query via Cloud Console or `promtool`.

## Troubleshooting

### GPU Quota Error

```
Error: Quota 'NVIDIA_L4_GPUS' exceeded
```

**Solution**:
```bash
# Request quota increase
gcloud compute regions describe us-central1
# Navigate to: Console > IAM > Quotas > Edit Quotas
```

### Bucket Already Exists

```
Error: googleapi: Error 409: You already own this bucket
```

**Solution**: Change `model_bucket_name` in `terraform.tfvars`

### kubectl Cannot Connect

```bash
# Re-authenticate
gcloud container clusters get-credentials pnkln-gke-cluster \
  --region us-central1 \
  --project YOUR_PROJECT_ID

# Verify master authorized networks include your IP
```

## Cleanup

**WARNING**: This destroys all resources.

```bash
# Remove workloads first
cd ../deploy && kubectl delete -f .

# Destroy infrastructure
cd ../infra
terraform destroy
```

## Next Steps

1. Deploy Kubernetes manifests: `cd ../deploy`
2. Run latency validation: `cd ../validate`
3. Configure CI/CD for automated deployments
4. Set up alerting for SLA violations

## Outputs

After deployment, access key information:

```bash
terraform output cluster_name
terraform output model_bucket_name
terraform output kubectl_config_command
terraform output gpu_node_pools
```

## References

- [GCP Inference Reference Architecture](https://github.com/GoogleCloudPlatform/accelerated-platforms/tree/main/docs/platforms/gke/base/use-cases/inference-ref-arch)
- [GKE GPU Documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus)
- [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
