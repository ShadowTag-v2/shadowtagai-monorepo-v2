# Pnkln Core Stack - GKE + File Search Integration

> **Complete Terraform configuration for deploying GKE with Vertex AI File Search API integration for Judge #6 hybrid policy enforcement**

## 🎯 Overview

This Terraform configuration deploys a production-grade GKE cluster integrated with Google's Vertex AI File Search API, enabling context-aware policy enforcement across 30 industry verticals with regulatory compliance automation.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER QUERY                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COR BRAIN (Orchestrator)                     │
│                      [GKE Deployment]                           │
└─────┬───────────────────────────────────┬───────────────────────┘
      │                                   │
      │ Parallel Execution                │
      │                                   │
      ▼                                   ▼
┌──────────────────────┐          ┌────────────────────────────┐
│ FILE SEARCH API      │          │ JUDGE #6 - LAYER 1         │
│ (Vertex AI RAG)      │          │ (Gemini Fine-tuned)        │
│                      │          │ ≤40ms                      │
│ Policy Context:      │          │                            │
│ - HIPAA regs         │          │ ATP 5-19 Risk Signals      │
│ - ITAR controls      │          │                            │
│ - Org policies       │          └────────────┬───────────────┘
│                      │                       │
│ ~500-800ms (p99)     │                       │
└──────────┬───────────┘                       │
           │                                   │
           └───────────────┬───────────────────┘
                           │
                           ▼
                  ┌────────────────────────┐
                  │ JUDGE #6 - LAYER 2     │
                  │ (PyTorch Model)        │
                  │ ~30ms                  │
                  └──────────┬─────────────┘
                             │
                             ▼
                  ┌────────────────────────┐
                  │ JUDGE #6 - LAYER 3     │
                  │ (Rules Engine)         │
                  │ ~20ms                  │
                  └──────────┬─────────────┘
                             │
                             ▼
                  ┌────────────────────────┐
                  │ ENFORCEMENT DECISION   │
                  │ Total: ≤90ms (Judge)   │
                  │ + 500-800ms (Context)  │
                  └────────────────────────┘
```

### Key Features

- **30 Industry Verticals** - Pre-configured policy corpora for defense, healthcare, finance, etc.
- **Regulatory Compliance as Code** - HIPAA, ITAR, CMMC, FINRA, GDPR, and more
- **Workload Identity** - Secure, keyless authentication between GKE and GCP services
- **Auto-scaling** - HPA and cluster autoscaling for cost optimization
- **Monitoring & Alerting** - Cloud Monitoring integration with SLA alerts
- **High Availability** - Multi-zone deployment with pod anti-affinity

## 📋 Prerequisites

1. **Google Cloud SDK**
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   gcloud init
   ```

2. **Terraform** (>= 1.5.0)
   ```bash
   # Install via Homebrew (macOS)
   brew install terraform

   # Or download from: https://www.terraform.io/downloads
   ```

3. **kubectl**
   ```bash
   # Install via gcloud
   gcloud components install kubectl
   ```

4. **Python 3.8+** (for corpus management scripts)
   ```bash
   python3 --version
   ```

5. **GCP Project Setup**
   ```bash
   # Set your project ID
   export PROJECT_ID="your-project-id"

   # Enable required APIs
   gcloud services enable \
     container.googleapis.com \
     aiplatform.googleapis.com \
     storage.googleapis.com \
     compute.googleapis.com \
     --project=$PROJECT_ID
   ```

## 🚀 Quick Start

### Step 1: Clone and Configure

```bash
# Navigate to terraform directory
cd terraform/gke-file-search

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your configuration
vim terraform.tfvars
```

**Key variables to customize:**
- `project_id` - Your GCP project ID
- `region` - GCP region (recommend `us-central1` for Hypercomputer)
- `cluster_name` - GKE cluster name
- `node_pool_config` - Adjust based on workload requirements

### Step 2: Initialize Terraform

```bash
# Initialize Terraform providers
terraform init

# Review planned changes
terraform plan

# Apply configuration
terraform apply
```

**Expected deployment time:** ~10-15 minutes

### Step 3: Configure kubectl

```bash
# Get cluster credentials
gcloud container clusters get-credentials pnkln-core-cluster \
  --region us-central1 \
  --project your-project-id

# Verify cluster access
kubectl get nodes
```

### Step 4: Deploy Kubernetes Resources

```bash
# Create namespace
kubectl apply -f k8s-manifests/namespace.yaml

# Deploy service account (Workload Identity)
kubectl apply -f k8s-manifests/service-account.yaml

# Deploy example orchestrator (customize as needed)
kubectl apply -f k8s-manifests/deployment-example.yaml

# Verify deployment
kubectl get pods -n pnkln-core
```

### Step 5: Initialize RAG Corpora

```bash
# Run corpus initialization script
./scripts/setup_file_search.sh \
  --project your-project-id \
  --region us-central1
```

This creates RAG corpora for all 30 verticals in Vertex AI.

### Step 6: Upload Policy Documents

```bash
# Example: Upload ITAR regulations for defense vertical
gsutil cp /path/to/itar_regulations.pdf \
  gs://pnkln-policy-corpus-defense/regulatory/

# Import into RAG corpus
python3 scripts/corpus_import.py \
  --vertical defense \
  --path gs://pnkln-policy-corpus-defense/regulatory/*.pdf \
  --project your-project-id
```

## 📁 Repository Structure

```
terraform/gke-file-search/
├── main.tf                 # Root module configuration
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── provider.tf             # Provider configuration
├── terraform.tfvars.example # Example variables file
├── README.md              # This file
│
├── modules/
│   ├── gke/               # GKE cluster module
│   │   ├── main.tf
│   │   └── variables.tf
│   ├── vertex-ai/         # Vertex AI configuration
│   │   ├── main.tf
│   │   └── variables.tf
│   ├── gcs/               # GCS corpus buckets
│   │   ├── main.tf
│   │   └── variables.tf
│   └── iam/               # IAM & Workload Identity
│       ├── main.tf
│       └── variables.tf
│
├── scripts/
│   ├── setup_file_search.sh   # Corpus initialization
│   └── corpus_import.py       # Document import tool
│
└── k8s-manifests/
    ├── namespace.yaml
    ├── service-account.yaml
    └── deployment-example.yaml
```

## 🔧 Configuration Reference

### Vertical Definitions

The configuration includes 30 pre-configured industry verticals:

| Vertical | Regulations | Description |
|----------|------------|-------------|
| `defense` | ITAR, CMMC, NISPOM | Defense and aerospace |
| `healthcare` | HIPAA, FDA 21 CFR Part 11 | Healthcare and medical devices |
| `finance` | FINRA, SOX, GDPR, PCI-DSS | Financial services |
| `insurance` | State Insurance Regs, NAIC | Insurance and underwriting |
| ... | ... | *See main.tf for full list* |

### Node Pool Configurations

**Production (Default):**
```hcl
node_pool_config = {
  machine_type   = "n2-standard-8"   # 8 vCPU, 32GB RAM
  min_nodes      = 3
  max_nodes      = 10
  disk_size_gb   = 100
  disk_type      = "pd-ssd"
  preemptible    = false
  spot           = false
}
```

**Development (Cost-Optimized):**
```hcl
node_pool_config = {
  machine_type   = "n2-standard-4"   # 4 vCPU, 16GB RAM
  min_nodes      = 1
  max_nodes      = 3
  disk_size_gb   = 50
  disk_type      = "pd-standard"
  preemptible    = true
  spot           = true
}
```

### Latency SLA Configuration

```hcl
latency_sla = {
  judge_p99           = 90    # Judge #6 p99 latency (ms)
  file_search_p99     = 1000  # File Search p99 latency (ms)
  total_acceptable    = 850   # Total acceptable latency (ms)
}
```

## 🔐 Security Features

### Workload Identity

Secure, keyless authentication between GKE pods and GCP services:

```yaml
# Kubernetes ServiceAccount annotation
apiVersion: v1
kind: ServiceAccount
metadata:
  name: pnkln-file-search-sa
  namespace: pnkln-core
  annotations:
    iam.gke.io/gcp-service-account: pnkln-gke-sa@your-project.iam.gserviceaccount.com
```

### IAM Permissions

The GKE service account is granted:
- `roles/aiplatform.user` - Vertex AI access
- `roles/ml.developer` - RAG corpus management
- `roles/storage.objectViewer` - Read corpus buckets
- `roles/logging.logWriter` - Cloud Logging
- `roles/monitoring.metricWriter` - Cloud Monitoring

### Binary Authorization

Container image verification enabled by default:
```hcl
enable_binary_authorization = true
```

### Shielded GKE Nodes

Hardware-level security with Secure Boot and integrity monitoring:
```hcl
enable_shielded_nodes = true
```

## 📊 Monitoring & Alerting

### Built-in Alerts

1. **File Search Latency Alert**
   - Triggers when p99 latency > 1000ms
   - Duration: 5 minutes
   - Action: Email notification

2. **File Search Error Rate Alert**
   - Triggers when error rate > 5%
   - Duration: 5 minutes
   - Action: Email notification

### Custom Dashboards

Access Cloud Monitoring dashboard:
```bash
# Get dashboard URL
terraform output monitoring_dashboard_url
```

### View Metrics

```bash
# GKE cluster metrics
gcloud monitoring dashboards list --project=your-project-id

# File Search API metrics
gcloud monitoring time-series list \
  --filter='metric.type="aiplatform.googleapis.com/prediction/latencies"' \
  --project=your-project-id
```

## 💰 Cost Estimation

### Monthly Costs (Approximate)

| Component | Cost (USD) |
|-----------|------------|
| GKE Cluster (3-10 nodes, n2-standard-8) | $200-500 |
| Vertex AI API Calls | $100-300 |
| GCS Storage (10GB corpus) | $50-100 |
| Networking (egress, LB) | $50-150 |
| **Total Estimated** | **$400-1,050/month** |

### Cost Optimization Tips

1. **Use Spot/Preemptible instances** for dev/staging
2. **Enable cluster autoscaling** to scale down during low traffic
3. **Set budget alerts**:
   ```hcl
   budget_alert_threshold = 5000  # Alert at $5,000/month
   ```
4. **Use Standard disks** instead of SSD for non-critical workloads
5. **Implement lifecycle rules** for GCS bucket versioning

## 🛠️ Operational Tasks

### Update Policy Documents

```bash
# Upload new version
gsutil cp updated-policy.pdf \
  gs://pnkln-policy-corpus-vertical/regulatory/

# Re-import to corpus
python3 scripts/corpus_import.py \
  --vertical defense \
  --path gs://pnkln-policy-corpus-defense/regulatory/updated-policy.pdf
```

### Query Corpus (Testing)

```bash
# Test File Search retrieval
python3 scripts/corpus_import.py \
  --vertical defense \
  --query "What are ITAR export control requirements for AI models?" \
  --top-k 5
```

### Scale Cluster

```bash
# Manual scaling
gcloud container clusters resize pnkln-core-cluster \
  --num-nodes 5 \
  --region us-central1

# Update HPA
kubectl autoscale deployment pnkln-orchestrator \
  --min=3 --max=15 --cpu-percent=70 \
  -n pnkln-core
```

### View Logs

```bash
# Application logs
kubectl logs -f deployment/pnkln-orchestrator -n pnkln-core

# Cloud Logging
gcloud logging read "resource.type=k8s_cluster AND resource.labels.cluster_name=pnkln-core-cluster" \
  --limit 50 \
  --format json
```

## 🐛 Troubleshooting

### Issue: Terraform apply fails with "quota exceeded"

**Solution:**
```bash
# Check quotas
gcloud compute project-info describe --project=your-project-id

# Request quota increase
# Navigate to: https://console.cloud.google.com/iam-admin/quotas
```

### Issue: Workload Identity not working

**Solution:**
```bash
# Verify IAM binding
gcloud iam service-accounts get-iam-policy \
  pnkln-gke-sa@your-project.iam.gserviceaccount.com

# Re-apply Kubernetes ServiceAccount
kubectl apply -f k8s-manifests/service-account.yaml

# Test from pod
kubectl run -it --rm debug --image=google/cloud-sdk:slim \
  --serviceaccount=pnkln-file-search-sa \
  -n pnkln-core \
  -- gcloud auth list
```

### Issue: High File Search latency (>1000ms)

**Solution:**
1. Check corpus size (max 10GB per corpus)
2. Reduce `chunk_size` and `chunk_overlap`
3. Optimize queries to be more specific
4. Consider sharding large corpora

### Issue: Cannot access GCS buckets from GKE

**Solution:**
```bash
# Verify service account permissions
gcloud projects get-iam-policy your-project-id \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:pnkln-gke-sa@your-project.iam.gserviceaccount.com"

# Grant missing permissions
gcloud projects add-iam-policy-binding your-project-id \
  --member=serviceAccount:pnkln-gke-sa@your-project.iam.gserviceaccount.com \
  --role=roles/storage.objectViewer
```

## 📚 Additional Resources

- [Vertex AI File Search Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/rag/overview)
- [GKE Workload Identity Guide](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [Terraform Google Provider Docs](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Claude Agent SDK Documentation](https://docs.claude.com/en/api/agent-sdk/overview)

## 🤝 Contributing

For internal Pnkln development:

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Run `terraform fmt` and `terraform validate`
4. Submit PR for review

## 📄 License

Proprietary - Pnkln Core Stack © 2025

---

**Deployment Status:** ✅ Production Ready

**Last Updated:** 2025-11-07

**Maintainer:** Pnkln Core Engineering Team
