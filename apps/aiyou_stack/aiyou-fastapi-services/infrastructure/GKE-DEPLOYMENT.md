# PNKLN CORE STACK™ GKE INFERENCE DEPLOYMENT

**AI Operating Posture Framework Implementation**
**Version**: 1.0
**Target SLA**: p99 ≤ 90ms end-to-end latency
**Cost Target**: $60-65K/month (includes GPU/TPU + networking)
**Deployment**: Terraform IaC + GitOps (4 namespaces)
**Timeline**: 120-150 minutes full deployment

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Detailed Deployment](#detailed-deployment)
5. [Configuration](#configuration)
6. [Validation](#validation)
7. [Cost Optimization](#cost-optimization)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              PNKLN CORE STACK™ GKE CLUSTER               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐         │
│  │ System Pool│  │ Judge GPU  │  │ LLM Routing│         │
│  │ (n2-std-4) │  │ (g2-std-16)│  │ (n2-std-32)│         │
│  │  3 nodes   │  │ 0-4 nodes  │  │ 1-10 nodes │         │
│  └────────────┘  └────────────┘  └────────────┘         │
│                                                          │
│  Namespaces:                                            │
│  ├─ ShadowTag-v2jr-governance    (Judge 6 enforcement)        │
│  ├─ autogen-orchestration (Multi-agent)                 │
│  ├─ cognitive-stack-v5    (LLM routing)                 │
│  └─ shadowtag-v2          (Watermarking)                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Key Components

1. **Judge 6 Hybrid Enforcement System**
   - 3-layer hybrid: Gemini + PyTorch + Rules
   - p99 latency budget: 90ms
   - Coverage target: 98%

2. **LLM Routing Layer**
   - Multi-model distribution (Gemini 40%, Claude 35%, GPT-5 15%, Grok 5%, Llama 5%)
   - Fallback strategy: latency-optimized
   - Max retry: 3

3. **Infrastructure**
   - VPC with jumbo frames (MTU 8896) for model loading
   - Private GKE cluster with Workload Identity
   - Node auto-provisioning for dynamic scaling
   - GCS FUSE for model weight streaming

---

## Prerequisites

### Required Tools

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install Terraform >= 1.8.0
curl -O https://releases.hashicorp.com/terraform/1.8.0/terraform_1.8.0_linux_amd64.zip
unzip terraform_1.8.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install kubectl
gcloud components install kubectl gke-gcloud-auth-plugin

# Verify installations
gcloud version
terraform version
kubectl version --client
```

### GCP Project Setup

```bash
# Set project ID
export PROJECT_ID="pnkln-core-stack"
export REGION="us-central1"

# Authenticate
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project ${PROJECT_ID}

# Enable required APIs
gcloud services enable \
    container.googleapis.com \
    compute.googleapis.com \
    aiplatform.googleapis.com \
    artifactregistry.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com \
    storage.googleapis.com \
    networkservices.googleapis.com \
    certificatemanager.googleapis.com
```

### Terraform State Bucket

```bash
# Create GCS bucket for Terraform state
gsutil mb -l ${REGION} gs://${PROJECT_ID}-tfstate

# Enable versioning
gsutil versioning set on gs://${PROJECT_ID}-tfstate
```

---

## Quick Start

### 1. Clone and Configure

```bash
cd infrastructure/terraform

# Review and customize variables
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Plan Deployment

```bash
terraform plan -out=tfplan
```

### 4. Deploy Infrastructure

```bash
terraform apply tfplan
```

### 5. Configure kubectl

```bash
gcloud container clusters get-credentials pnkln-inference-prod \
    --region=us-central1 \
    --project=${PROJECT_ID}

# Verify cluster access
kubectl get nodes
```

---

## Detailed Deployment

### Phase 1: Network Infrastructure (5-10 minutes)

The Terraform configuration creates:

- **VPC Network**: Custom VPC with MTU 8896 for large model transfers
- **Subnet**: /20 network with secondary ranges for pods (/14) and services (/20)
- **Cloud NAT**: For private node egress
- **Firewall Rules**: Implicit via GKE

```bash
# Verify network creation
gcloud compute networks list
gcloud compute networks subnets list --network=pnkln-inference-prod-vpc
```

### Phase 2: GKE Cluster (15-20 minutes)

Creates a regional GKE cluster with:

- **Control Plane**: Regional (3 masters across zones)
- **Dataplane V2**: Advanced networking for better performance
- **Workload Identity**: Secure GCP service access
- **Binary Authorization**: Container security enforcement
- **Managed Prometheus**: Built-in monitoring

```bash
# Monitor cluster creation
watch gcloud container clusters list

# Once ready, check cluster info
kubectl cluster-info
kubectl get nodes
```

### Phase 3: Node Pools (10-15 minutes)

#### System Pool (Always-On)
- **Machine Type**: n2-standard-4
- **Node Count**: 3 (fixed)
- **Purpose**: Cluster services, DaemonSets, system workloads

#### Judge GPU Pool (Auto-Scaling)
- **Machine Type**: g2-standard-16 (4x NVIDIA L4 GPUs)
- **Scaling**: 0-4 nodes
- **Spot Instances**: Enabled (60-91% cost savings)
- **Local SSDs**: 2x for model caching

#### LLM Routing Pool (Auto-Scaling)
- **Machine Type**: n2-standard-32 (high CPU)
- **Scaling**: 1-10 nodes
- **Purpose**: LLM routing logic, orchestration

```bash
# Verify node pools
kubectl get nodes -L cloud.google.com/gke-nodepool
```

### Phase 4: Storage (2-5 minutes)

#### Artifact Registry
- **Purpose**: Container images
- **Location**: Regional (us-central1)
- **Cleanup**: Manual (immutable tags disabled for flexibility)

#### GCS Buckets
- **Model Weights**: Versioned, lifecycle policies (Nearline@30d, Coldline@90d)
- **Logs**: Versioned, auto-delete@90d

```bash
# Verify Artifact Registry
gcloud artifacts repositories list

# Verify GCS buckets
gsutil ls -L gs://${PROJECT_ID}-model-weights
gsutil ls -L gs://${PROJECT_ID}-logs
```

---

## Configuration

### Terraform Variables

Create `terraform.tfvars`:

```hcl
# Project Configuration
project_id  = "pnkln-core-stack"
region      = "us-central1"
environment = "production"

# Cluster Configuration
cluster_name     = "pnkln-inference-prod"
release_channel  = "RAPID"  # RAPID for latest features, REGULAR for stability

# Security
enable_binary_authorization = true
enable_private_nodes       = true
enable_private_endpoint    = false  # Set true after initial setup

# Node Pools
system_node_count = 3

judge_gpu_min_nodes       = 0
judge_gpu_max_nodes       = 4
judge_gpu_use_spot        = true
judge_gpu_local_ssd_count = 2

llm_routing_min_nodes = 1
llm_routing_max_nodes = 10

# Monitoring
enable_managed_prometheus = true
enable_backup            = true

# Cost Optimization
enable_node_autoprovisioning = true
```

### Advanced Customization

#### Master Authorized Networks

```hcl
master_authorized_networks = [
  {
    cidr_block   = "203.0.113.0/24"
    display_name = "Corporate Network"
  },
  {
    cidr_block   = "198.51.100.0/24"
    display_name = "VPN"
  }
]
```

#### Custom Autoscaling Limits

```hcl
autoscaling_resource_limits = [
  {
    resource_type = "cpu"
    minimum       = 10
    maximum       = 2000
  },
  {
    resource_type = "memory"
    minimum       = 32
    maximum       = 8000
  },
  {
    resource_type = "nvidia-l4"
    minimum       = 0
    maximum       = 32
  }
]
```

---

## Validation

### Post-Deployment Validation Script

```bash
#!/bin/bash
# validate-deployment.sh

set -euo pipefail

echo "════════════════════════════════════════════════"
echo "  PNKLN CORE STACK™ - Deployment Validation    "
echo "════════════════════════════════════════════════"

# 1. Cluster Access
echo "▶ Testing cluster access..."
if kubectl cluster-info &>/dev/null; then
    echo "✓ Cluster accessible"
else
    echo "✗ Cannot access cluster"
    exit 1
fi

# 2. Node Pools
echo "▶ Verifying node pools..."
EXPECTED_POOLS=("system-pool" "judge-l4-pool" "llm-routing-pool")
for pool in "${EXPECTED_POOLS[@]}"; do
    if kubectl get nodes -l cloud.google.com/gke-nodepool=$pool &>/dev/null; then
        echo "✓ Node pool: $pool"
    else
        echo "⚠ Node pool not found: $pool"
    fi
done

# 3. Storage
echo "▶ Verifying storage..."
if gsutil ls gs://${PROJECT_ID}-model-weights &>/dev/null; then
    echo "✓ Model weights bucket exists"
fi

if gcloud artifacts repositories describe pnkln-inference --location=${REGION} &>/dev/null; then
    echo "✓ Artifact Registry exists"
fi

# 4. Workload Identity
echo "▶ Verifying Workload Identity..."
if gcloud iam service-accounts describe ${CLUSTER_NAME}-node-sa@${PROJECT_ID}.iam.gserviceaccount.com &>/dev/null; then
    echo "✓ Node service account exists"
fi

# 5. Monitoring
echo "▶ Checking monitoring..."
if gcloud container clusters describe ${CLUSTER_NAME} --region=${REGION} --format="value(monitoringConfig.managedPrometheusConfig.enabled)" | grep -q "true"; then
    echo "✓ Managed Prometheus enabled"
fi

echo "════════════════════════════════════════════════"
echo "  Validation Complete                          "
echo "════════════════════════════════════════════════"
```

Run validation:

```bash
chmod +x scripts/validate-deployment.sh
./scripts/validate-deployment.sh
```

---

## Cost Optimization

### Monthly Cost Breakdown

```
ESTIMATED MONTHLY COST: $62,500

Infrastructure:
├─ GKE Control Plane:              $500
├─ Node Pools:
│  ├─ System (3x n2-std-4):        $360
│  ├─ Judge GPU (spot, avg 2):     $8,000
│  └─ LLM Routing (avg 5):         $3,000
├─ Network (Load Balancers, NAT):  $2,000
├─ Storage (GCS, Artifact Reg):    $500
└─ Auto-provisioned nodes:         $15,000

LLM API Costs:
├─ Gemini (40%):                   $12,000
├─ Claude (35%):                   $10,500
├─ GPT-5 (15%):                    $7,500
├─ Grok (5%):                      $2,500
└─ Llama (5%):                     $1,500

Total:                             $62,860/month
```

### Cost Reduction Strategies

1. **Spot Instances**: Already enabled for GPU nodes (60-91% savings)
2. **Node Auto-Provisioning**: Scale to zero when not needed
3. **Committed Use Discounts**: 57% savings for predictable workloads
4. **Rightsizing**: Monitor actual usage and adjust machine types

```bash
# Get cost optimization recommendations
gcloud recommender recommendations list \
    --project=${PROJECT_ID} \
    --recommender=google.compute.commitment.UsageCommitmentRecommender \
    --location=us-central1

# View current resource usage
kubectl top nodes
kubectl top pods --all-namespaces
```

---

## Troubleshooting

### Common Issues

#### Issue: Terraform State Lock

```bash
# Force unlock (use with caution)
terraform force-unlock <LOCK_ID>
```

#### Issue: kubectl Cannot Connect

```bash
# Re-authenticate
gcloud container clusters get-credentials ${CLUSTER_NAME} \
    --region=${REGION} \
    --project=${PROJECT_ID}

# Verify credentials
kubectl config current-context
```

#### Issue: GPU Nodes Not Scaling

```bash
# Check node pool status
kubectl describe nodes | grep -A5 "Taints"

# Ensure pods have correct tolerations
kubectl get pods -n ShadowTag-v2jr-governance -o yaml | grep -A2 tolerations
```

#### Issue: Out of IP Addresses

```bash
# Check IP usage
gcloud compute networks subnets describe ${SUBNET_NAME} \
    --region=${REGION} \
    --format="get(ipCidrRange,secondaryIpRanges)"

# Solution: Expand secondary ranges or create new subnet
```

### Logs and Debugging

```bash
# View cluster events
kubectl get events --all-namespaces --sort-by='.lastTimestamp'

# Check GKE audit logs
gcloud logging read "resource.type=k8s_cluster" --limit 50

# View node logs
gcloud compute ssh <NODE_NAME> --command="sudo journalctl -u kubelet"
```

---

## Next Steps

After infrastructure deployment, proceed to:

1. **Deploy Kubernetes Manifests** (`/kubernetes/README.md`)
   - Namespaces
   - Judge 6 enforcement system
   - LLM routing layer
   - Monitoring stack

2. **Configure GitOps** (Config Sync)
   - Automated deployments
   - Policy enforcement
   - Drift detection

3. **Set Up CI/CD** (Cloud Build + Cloud Deploy)
   - Automated testing
   - Canary deployments
   - Rollback automation

4. **Enable Disaster Recovery**
   - Multi-region setup
   - Backup policies
   - Failover testing

---

## References

- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [GKE Accelerated Platforms](https://cloud.google.com/kubernetes-engine/docs/how-to/gpu-bandwidth)
- [AI Operating Posture Framework](../docs/framework/AI-OPERATING-POSTURE.md)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-08
**Owner**: Infrastructure Team
