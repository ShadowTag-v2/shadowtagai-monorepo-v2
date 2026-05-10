# Omega GKE GPU Infrastructure - Terraform

This directory contains Terraform configurations for deploying Omega's GPU infrastructure on Google Kubernetes Engine (GKE).

## Overview

This Terraform configuration creates:

- GKE regional cluster with private nodes

- Multiple GPU node pools (L4, A100, H100, Spot)

- NVIDIA GPU Operator via Helm

- Workload Identity setup

- GCS buckets for models and checkpoints

- Service accounts with IAM bindings

- Budget alerts

- Monitoring and logging

## Prerequisites


1. **Install Tools**:
   ```bash
   # Terraform >= 1.5.0
   brew install terraform

   # gcloud CLI
   brew install google-cloud-sdk

   # kubectl
   brew install kubectl

   # helm
   brew install helm
   ```


2. **GCP Authentication**:
   ```bash
   gcloud auth application-default login
   gcloud config set project omega-production
   ```


3. **Enable Required APIs**:
   ```bash
   gcloud services enable \
     container.googleapis.com \
     compute.googleapis.com \
     storage-api.googleapis.com \
     iam.googleapis.com \
     cloudresourcemanager.googleapis.com \
     billingbudgets.googleapis.com
   ```


4. **Create GCS Bucket for Terraform State**:
   ```bash
   gsutil mb -p omega-production -l us-central1 gs://omega-terraform-state
   gsutil versioning set on gs://omega-terraform-state
   ```


5. **Request GPU Quota** (if needed):
   ```bash
   # Check current quotas
   gcloud compute project-info describe --project=omega-production

   # Request quota increase via GCP Console:
   # IAM & Admin > Quotas > Filter: "NVIDIA" > Request increase
   ```

## Quick Start

### 1. Initialize Configuration

```bash
cd k8s/terraform

# Copy and edit variables

cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Fill in your values

# Initialize Terraform

terraform init

```

### 2. Review Plan

```bash

# See what will be created

terraform plan

# Review GPU node pools, networking, IAM

```

### 3. Deploy Infrastructure

```bash

# Apply configuration

terraform apply

# Type 'yes' when prompted

# Deployment takes ~15-20 minutes

```

### 4. Configure kubectl

```bash

# Get cluster credentials

gcloud container clusters get-credentials omega-production-gpu \
  --region us-central1 \
  --project omega-production

# Verify connection

kubectl get nodes
kubectl get pods -n gpu-operator

```

### 5. Verify GPU Availability

```bash

# Check GPU nodes

kubectl get nodes -l cloud.google.com/gke-accelerator -o wide

# Check GPU resources

kubectl describe node <node-name> | grep nvidia.com/gpu

# Check GPU Operator

kubectl get pods -n gpu-operator

```

## Project Structure

```

k8s/terraform/
├── main.tf                     # Main configuration
├── variables.tf                # Input variables
├── outputs.tf                  # Output values
├── terraform.tfvars.example    # Example variables
├── README.md                   # This file
└── modules/
    ├── gke-gpu-cluster/        # GKE cluster module
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── gke-gpu-node-pool/      # GPU node pool module
        ├── main.tf
        ├── variables.tf
        └── outputs.tf

```

## GPU Node Pools

The configuration creates 4 GPU node pools:

| Pool Name | GPUs | Machine Type | Use Case | Cost/hr |
|-----------|------|--------------|----------|---------|
| **inference-l4-pool** | 1× L4 | g2-standard-4 | Inference | ~$0.70 |
| **finetune-a100-2g-pool** | 2× A100 40GB | a2-highgpu-2g | Fine-tuning | ~$6.00 |
| **training-a100-8g-pool** | 8× A100 80GB | a2-ultragpu-8g | Training | ~$28.00 |
| **spot-a100-pool** | 1× A100 | a2-highgpu-1g | Batch (spot) | ~$1.50 |

All pools start with 0 nodes and auto-scale based on demand.

## Cost Management

### Budget Alerts

Budget alerts are configured in `main.tf`:

- 50% threshold: Warning

- 80% threshold: Urgent warning

- 100% threshold: Critical alert

Modify `budget_amount` in `terraform.tfvars` to set monthly cap.

### Cost Tracking

```bash

# View current costs

gcloud billing accounts list
gcloud billing projects describe omega-production

# Export to BigQuery for analysis

# (Enabled by default in cluster configuration)

```

### Manual Scaling

```bash

# Scale down a node pool

gcloud container clusters resize omega-production-gpu \
  --node-pool inference-l4-pool \
  --num-nodes 0 \
  --region us-central1

# Scale up

gcloud container clusters resize omega-production-gpu \
  --node-pool inference-l4-pool \
  --num-nodes 5 \
  --region us-central1

```

## Workload Identity

Service accounts are configured with Workload Identity:

**Training SA** (`training-sa`):

- Namespace: `ml-training`

- GCP SA: `redacted@shadowtag-v4.local`

- Permissions: `roles/storage.objectAdmin`

**Inference SA** (`inference-sa`):

- Namespace: `production`

- GCP SA: `redacted@shadowtag-v4.local`

- Permissions: `roles/storage.objectViewer`

## Monitoring

### Cloud Monitoring

```bash

# View GKE metrics in Cloud Console

https://console.cloud.google.com/monitoring/dashboards

# GPU-specific metrics available:

# - kubernetes.io/container/accelerator/duty_cycle

# - kubernetes.io/container/accelerator/memory_used

```

### DCGM Metrics (Prometheus)

GPU Operator installs DCGM exporter. Metrics available at:

- `DCGM_FI_DEV_GPU_UTIL` - GPU utilization %

- `DCGM_FI_DEV_GPU_TEMP` - Temperature

- `DCGM_FI_DEV_POWER_USAGE` - Power usage

- `DCGM_FI_DEV_FB_USED` - Memory used

## Updating Infrastructure

### Modify Node Pool Limits

Edit `main.tf` in the `locals` block:

```hcl
inference_l4 = {
  # ...
  max_nodes = 30  # Increase from 20
}

```

Then apply:

```bash
terraform plan
terraform apply

```

### Add New Node Pool

Add to `gpu_node_pools` in `main.tf`:

```hcl
new_pool_name = {
  name              = "new-pool"
  machine_type      = "a2-highgpu-4g"
  accelerator_type  = "nvidia-tesla-a100"
  accelerator_count = 4
  # ... other settings
}

```

Apply changes:

```bash
terraform apply

```

## Maintenance

### Upgrade Cluster

```bash

# Check available versions

gcloud container get-server-config --region us-central1

# Upgrade (or let auto-upgrade handle it)

gcloud container clusters upgrade omega-production-gpu \
  --region us-central1 \
  --cluster-version 1.28.5-gke.1200

```

### Backup Terraform State

```bash

# State is automatically backed up to GCS

gsutil ls gs://omega-terraform-state/gke-gpu-cluster/

# Download backup

gsutil cp gs://omega-terraform-state/gke-gpu-cluster/default.tfstate ./backup/

```

## Troubleshooting

### Issue: Quota Exceeded

```

Error: googleapi: Error 403: Quota 'NVIDIA_A100_GPUS' exceeded

```

**Solution**: Request quota increase in GCP Console (IAM & Admin > Quotas).

### Issue: Node Pool Not Scaling

```bash

# Check cluster autoscaler status

kubectl get cm cluster-autoscaler-status -n kube-system -o yaml

# Check node pool events

kubectl describe nodepool <pool-name>

```

### Issue: GPU Not Detected

```bash

# Check GPU Operator logs

kubectl logs -n gpu-operator -l app=nvidia-device-plugin-daemonset

# Restart device plugin

kubectl delete pod -n gpu-operator -l app=nvidia-device-plugin-daemonset

```

## Cleanup

**WARNING**: This will destroy all resources!

```bash

# Delete Kubernetes workloads first

kubectl delete all --all -n production
kubectl delete all --all -n ml-training

# Destroy Terraform-managed infrastructure

terraform destroy

# Type 'yes' to confirm

```

## Next Steps


1. Deploy sample GPU workloads (see `../manifests/`)

2. Set up CI/CD pipelines to deploy to GKE

3. Configure monitoring dashboards

4. Review and optimize costs after 30 days

## Related Documentation


- [GKE GPU Integration Guide](../../docs/architecture/gke-gpu-integration.md)

- [GPU Infrastructure Strategy](../../docs/architecture/gpu-infrastructure-strategy.md)

- [GPU TCO Analysis](../../docs/architecture/gpu-tco-analysis.md)

## Support

For issues or questions:

- **Internal**: #gpu-infrastructure Slack channel

- **External**: [GKE GPU Documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus)
