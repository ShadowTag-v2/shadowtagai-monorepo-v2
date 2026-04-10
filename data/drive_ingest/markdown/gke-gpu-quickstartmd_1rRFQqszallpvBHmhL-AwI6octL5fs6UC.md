# GKE GPU Infrastructure - Quick Start Guide

> **Get ShadowTag's GPU infrastructure running on GKE in under 30 minutes**
> **Platform**: Google Kubernetes Engine (GKE)
> **Date**: 2025-11-17

---

## Overview

This quick start guide provides a streamlined path to deploy ShadowTag's GPU infrastructure on Google Kubernetes Engine (GKE). Follow these steps to go from zero to running GPU workloads.

### What You'll Deploy

- ✅ GKE regional cluster with private nodes
- ✅ 4 GPU node pools (L4, A100 2-GPU, A100 8-GPU, Spot)
- ✅ NVIDIA GPU Operator
- ✅ Workload Identity for secure GCP access
- ✅ GCS buckets for models and checkpoints
- ✅ Budget alerts and cost tracking
- ✅ Example inference and training workloads

### Time Estimate

- **Prerequisites**: 15 minutes
- **Infrastructure Deployment**: 20 minutes
- **Validation**: 5 minutes
- **Total**: ~40 minutes

---

## Prerequisites

### 1. Install Required Tools

```bash
# Terraform (>= 1.5.0)
brew install terraform

# gcloud CLI
brew install google-cloud-sdk

# kubectl
brew install kubectl

# helm
brew install helm
```

Verify installations:

```bash
terraform version  # Should be >= 1.5.0
gcloud version
kubectl version --client
helm version
```

### 2. Set Up GCP Project

```bash
# Set project
export PROJECT_ID="ShadowTag-production"
gcloud config set project $PROJECT_ID

# Authenticate
gcloud auth application-default login

# Get project number
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
```

### 3. Enable Required APIs

```bash
gcloud services enable \
  container.googleapis.com \
  compute.googleapis.com \
  storage-api.googleapis.com \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com \
  billingbudgets.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com
```

### 4. Check GPU Quotas

```bash
# Check current GPU quotas
gcloud compute project-info describe --project=$PROJECT_ID | grep -A 5 "NVIDIA"

# You need at least:
# - NVIDIA_L4_GPUS: 20 (for inference pool)
# - NVIDIA_A100_GPUS: 32 (for training pools)

# If quotas are insufficient, request increases:
# https://console.cloud.google.com/iam-admin/quotas
```

### 5. Create Terraform State Bucket

```bash
# Create bucket for Terraform state
gsutil mb -p $PROJECT_ID -l us-central1 gs://${PROJECT_ID}-terraform-state

# Enable versioning
gsutil versioning set on gs://${PROJECT_ID}-terraform-state

# Verify
gsutil ls gs://${PROJECT_ID}-terraform-state
```

---

## Step 1: Configure Terraform Variables

### 1.1 Navigate to Terraform Directory

```bash
cd k8s/terraform
```

### 1.2 Create terraform.tfvars

```bash
# Copy example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
cat > terraform.tfvars <<EOF
project_id   = "${PROJECT_ID}"
project_name = "ShadowTag"
region       = "us-central1"
environment  = "production"

master_authorized_networks = [
  {
    cidr_block   = "10.0.0.0/8"
    display_name = "Internal Network"
  }
]

enable_prometheus = true

# Budget configuration (optional)
billing_account_id = "ABCDEF-123456-789012"  # Replace with your billing account ID
budget_amount      = 50000  # $50,000/month cap

# Notification channels (create in GCP Console first)
budget_notification_channels = []
EOF
```

**Get Billing Account ID**:

```bash
gcloud billing accounts list
```

---

## Step 2: Deploy Infrastructure with Terraform

### 2.1 Initialize Terraform

```bash
terraform init

# Should see:
# Terraform has been successfully initialized!
```

### 2.2 Review Deployment Plan

```bash
terraform plan

# Review the output:
# - GKE cluster
# - 4 GPU node pools
# - VPC and networking
# - Service accounts
# - GCS buckets
# - Budget alerts
```

Key resources to note:
- **GKE Cluster**: `ShadowTag-production-gpu` (regional, 3 zones)
- **Node Pools**: inference-l4, finetune-a100-2g, training-a100-8g, spot-a100
- **GCS Buckets**: models, checkpoints
- **Service Accounts**: training-sa, inference-sa

### 2.3 Deploy Infrastructure

```bash
terraform apply

# Review plan one more time
# Type 'yes' to proceed

# Deployment takes ~15-20 minutes
# Get coffee ☕
```

### 2.4 Save Terraform Outputs

```bash
# Save important outputs
terraform output -json > outputs.json

# View cluster name
terraform output cluster_name

# View kubectl config command
terraform output configure_kubectl
```

---

## Step 3: Configure kubectl

### 3.1 Get Cluster Credentials

```bash
# Get credentials
gcloud container clusters get-credentials ShadowTag-production-gpu \
  --region us-central1 \
  --project $PROJECT_ID

# Verify connection
kubectl cluster-info
kubectl get nodes
```

### 3.2 Verify GPU Operator

```bash
# Check GPU Operator pods
kubectl get pods -n gpu-operator

# All pods should be Running:
# - gpu-operator-*
# - gpu-feature-discovery-*
# - nvidia-device-plugin-daemonset-*
# - nvidia-dcgm-exporter-*

# Wait until all are Running (may take 2-3 minutes)
kubectl wait --for=condition=Ready pods --all -n gpu-operator --timeout=5m
```

---

## Step 4: Validate GPU Infrastructure

### 4.1 Check GPU Nodes

```bash
# Wait for GPU node pool to scale up (first time)
# This may take 5-7 minutes

# Check nodes
kubectl get nodes -l cloud.google.com/gke-accelerator -o wide

# If no nodes appear, manually scale up one node pool:
gcloud container clusters resize ShadowTag-production-gpu \
  --node-pool finetune-a100-2g-pool \
  --num-nodes 1 \
  --region us-central1
```

### 4.2 Verify GPU Resources

```bash
# Pick a GPU node
GPU_NODE=$(kubectl get nodes -l cloud.google.com/gke-accelerator -o jsonpath='{.items[0].metadata.name}')

# Check GPU capacity
kubectl describe node $GPU_NODE | grep -A 5 "Capacity:"

# Should see:
# nvidia.com/gpu: 2  (for A100 2-GPU node)
```

### 4.3 Run GPU Test Pod

```bash
# Deploy test pod
kubectl apply -f ../../manifests/gpu-workloads/gpu-test-pod.yaml

# Wait for completion
kubectl wait --for=condition=Ready pod/gpu-test -n ml-training --timeout=5m

# View output
kubectl logs gpu-test -n ml-training

# Expected output:
# - nvidia-smi showing GPU details
# - CUDA samples passing

# Clean up
kubectl delete -f ../../manifests/gpu-workloads/gpu-test-pod.yaml
```

---

## Step 5: Deploy Example Workloads

### 5.1 Deploy Inference Service

```bash
# Navigate to manifests
cd ../../manifests/gpu-workloads

# Deploy inference service
kubectl apply -f example-inference-deployment.yaml

# Check deployment
kubectl get deployments -n production
kubectl get pods -n production
kubectl get svc -n production

# Wait for pods to be Ready
kubectl wait --for=condition=Ready pods -l app=llm-inference -n production --timeout=10m

# View logs
kubectl logs -n production -l app=llm-inference --tail=50
```

### 5.2 Test Inference Endpoint

```bash
# Port-forward to access locally
kubectl port-forward -n production svc/llm-inference-service 8080:80 &

# Wait a few seconds, then test
curl -X POST http://localhost:8080/health

# Expected: {"status": "healthy"}

# Stop port-forward
pkill -f "port-forward.*llm-inference"
```

### 5.3 Run Training Job (Optional)

```bash
# Deploy training job
kubectl apply -f example-training-job.yaml

# Check status
kubectl get pytorchjob -n ml-training

# View logs
kubectl logs -n ml-training llama-finetune-job-master-0 -f

# Clean up when done
kubectl delete -f example-training-job.yaml
```

---

## Step 6: Monitor and Optimize

### 6.1 Check Resource Usage

```bash
# Node usage
kubectl top nodes

# Pod usage
kubectl top pods -n production
kubectl top pods -n ml-training

# GPU utilization (from any GPU pod)
POD_NAME=$(kubectl get pods -n production -l app=llm-inference -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n production $POD_NAME -- nvidia-smi
```

### 6.2 View Cloud Monitoring

```bash
# Open GKE dashboard
echo "https://console.cloud.google.com/kubernetes/clusters/details/us-central1/ShadowTag-production-gpu/observability?project=$PROJECT_ID"

# Open GPU metrics dashboard
echo "https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"
```

### 6.3 Check Costs

```bash
# View current month costs
gcloud billing accounts list

# View detailed costs in BigQuery
# (Billing export enabled by default)

# Estimated monthly costs (if running continuously):
# - Inference (2 L4 pods): ~$1,000/month
# - Training (4 A100 2-GPU): ~$17,000/month
# - Spot workloads: ~60-70% discount

# To minimize costs when not in use:
# Scale down all node pools to 0
for pool in inference-l4-pool finetune-a100-2g-pool training-a100-8g-pool spot-a100-pool; do
  gcloud container clusters resize ShadowTag-production-gpu \
    --node-pool $pool \
    --num-nodes 0 \
    --region us-central1 \
    --quiet
done
```

---

## Troubleshooting

### Issue 1: Terraform Apply Fails

**Error**: `Error creating Network: googleapi: Error 409: alreadyExists`

**Solution**: Resource already exists. Import it:

```bash
terraform import google_compute_network.vpc projects/$PROJECT_ID/global/networks/ShadowTag-vpc
terraform apply
```

### Issue 2: GPU Quota Exceeded

**Error**: `Quota 'NVIDIA_A100_GPUS' exceeded`

**Solution**: Request quota increase:

```bash
echo "https://console.cloud.google.com/iam-admin/quotas?project=$PROJECT_ID"

# Filter: "NVIDIA_A100_GPUS"
# Request increase to 32
```

### Issue 3: Pods Stuck in Pending

**Symptom**: `kubectl describe pod` shows `0/X nodes are available: X Insufficient nvidia.com/gpu`

**Solution**: Scale up node pool manually:

```bash
gcloud container clusters resize ShadowTag-production-gpu \
  --node-pool finetune-a100-2g-pool \
  --num-nodes 2 \
  --region us-central1
```

### Issue 4: GPU Not Detected

**Symptom**: `nvidia-smi: command not found` in pod

**Solution**: Check GPU Operator:

```bash
# Check operator logs
kubectl logs -n gpu-operator -l app=nvidia-device-plugin-daemonset

# Restart device plugin
kubectl delete pod -n gpu-operator -l app=nvidia-device-plugin-daemonset

# Wait and retry
sleep 60
kubectl apply -f gpu-test-pod.yaml
```

---

## Next Steps

### 1. Customize for Your Use Case

- **Edit inference deployment**: Update model name, path, resources
- **Configure training job**: Adjust dataset, hyperparameters, GPUs
- **Set up CI/CD**: Deploy models automatically via GitHub Actions

### 2. Optimize Costs

- **Use committed use discounts** after 30 days of usage data
- **Enable spot instances** for fault-tolerant workloads
- **Auto-scale to zero** when not in use
- **Monitor utilization** and right-size node pools

### 3. Enhance Monitoring

- **Set up Grafana dashboards** for GPU metrics
- **Configure alerts** for cost overruns, failures
- **Export metrics to BigQuery** for analysis

### 4. Security Hardening

- **Enable Binary Authorization**: Only signed images can run
- **Implement Network Policies**: Restrict pod-to-pod traffic
- **Rotate Service Account Keys**: Regular key rotation
- **Scan Images**: Automated vulnerability scanning in CI/CD

---

## Cost Summary

### Monthly Estimates (24/7 Operation)

| Component | Configuration | Monthly Cost |
|-----------|---------------|--------------|
| **GKE Cluster** | Control plane | $73 |
| **Inference** | 2× L4 nodes (24/7) | $1,008 |
| **Fine-Tuning** | 2× A100 2-GPU (8h/day) | $2,880 |
| **Training** | 1× A100 8-GPU (4h/day) | $3,360 |
| **Networking** | Egress, load balancers | $100 |
| **Storage** | GCS models + checkpoints | $50 |
| **Total** | | **~$7,471/month** |

**Cost Optimization Potential**:
- **Spot instances**: Save 60-70% on training
- **Auto-scaling**: Only pay when workloads run
- **Committed use**: Save 37-55% on sustained workloads
- **Right-sizing**: Reduce over-provisioned resources

**Optimized Estimate**: ~$3,000-4,000/month for moderate usage

---

## Support and Documentation

### Documentation

- **[GKE GPU Integration Guide](./gke-gpu-integration.md)**: Complete technical guide
- **[GPU Infrastructure Strategy](./gpu-infrastructure-strategy.md)**: Strategic overview
- **[GPU TCO Analysis](./gpu-tco-analysis.md)**: Financial analysis
- **[Terraform README](../../k8s/terraform/README.md)**: Terraform details
- **[Manifests README](../../k8s/manifests/gpu-workloads/README.md)**: Kubernetes examples

### External Resources

- [GKE GPU Documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus)
- [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/)
- [Kubeflow on GKE](https://www.kubeflow.org/docs/distributions/gke/)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)

### Getting Help

- **Internal**: #gpu-infrastructure Slack channel
- **GCP Support**: [Google Cloud Support](https://cloud.google.com/support)
- **Community**: [GKE Community](https://cloud.google.com/community)

---

## Cleanup

**WARNING**: This will destroy all resources and data!

```bash
# Delete Kubernetes workloads
kubectl delete namespace production ml-training --wait=true

# Destroy infrastructure
cd k8s/terraform
terraform destroy

# Verify cleanup
gcloud container clusters list --project=$PROJECT_ID
```

---

## Summary

You've successfully deployed ShadowTag's GPU infrastructure on GKE! 🎉

**What you have**:
- ✅ Production-ready GKE cluster with GPU support
- ✅ Auto-scaling GPU node pools (L4, A100, H100)
- ✅ Secure Workload Identity for GCP access
- ✅ Cost tracking and budget alerts
- ✅ Example inference and training workloads

**What's next**:
1. Deploy your actual models and datasets
2. Set up CI/CD for automated deployments
3. Monitor costs and optimize node pools
4. Scale to multi-region for high availability

---

**Document Status**: ✅ Production Ready
**Last Updated**: 2025-11-17
**Version**: 1.0