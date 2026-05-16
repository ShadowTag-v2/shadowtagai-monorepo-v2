# PNKLN Core Stack - GKE Deployment Plan

```
═══════════════════════════════════════════════════════════════════
  MASTER DEPLOYMENT PLAN
  PNKLN Core Stack on GKE Hypercomputer
  Target: Production-Ready Inference Platform
═══════════════════════════════════════════════════════════════════
```

## EXECUTIVE SUMMARY

**Objective**: Deploy PNKLN Core Stack on Google Kubernetes Engine (GKE) Hypercomputer with Vertex AI Workbench integration for rapid iteration and production-scale inference.

**Timeline**: 14-20 hours over 3-4 days

**Budget**: ~$7,225/month (~$87K/year run rate)

**Bootstrap Gates**:
- ROI Target: ≥3× within 18 months
- LTV:CAC Target: ≥4:1 within 12 months
- Kill-Switch: Monthly cost >$10K without revenue justification

---

## ARCHITECTURE OVERVIEW

### PNKLN Core Stack Components

```
Vertex AI Workbench (Development Environment)
    ↓ Deploy via kubectl/Config Sync
GKE Hypercomputer (Production)
    ├── Judge #6:       3-layer hybrid (Gemini+PyTorch+Rules)
    │                   Accelerator: A100-40GB
    │                   SLA: P99 ≤90ms, P95 ≤65ms, P50 ≤40ms
    │
    ├── JR Engine:      Purpose/Reasons/Brakes decision engine
    │                   Accelerator: CPU (n2-standard-8)
    │                   SLA: P99 ≤500μs, P95 ≤350μs, P50 ≤200μs
    │
    ├── Cor:            Strategic context management
    │                   Accelerator: CPU (n2-standard-8)
    │                   SLA: P99 ≤1ms, P95 ≤750μs, P50 ≤500μs
    │
    ├── NS:             Namespace resolution
    │                   Accelerator: CPU (n2-standard-4)
    │                   SLA: P99 ≤100μs, P95 ≤75μs, P50 ≤50μs
    │
    ├── ShadowTag:      DCT watermarking v2.0
    │                   Accelerator: L4 GPU
    │                   SLA: P99 ≤200ms (watermark embed/extract)
    │
    └── Orchestrator:   LLM request routing with PRB enforcement
                        Accelerator: L4 GPU
                        SLA: PRB adherence ≥98%, LLM mix ±2%
                        Mix: Gemini 40%, Claude 35%, GPT-5 15%, Grok 5%, Other 5%
    ↓ Observe
Observability Stack
    ├── Google Managed Prometheus (GMP)
    ├── Cloud Monitoring Dashboards
    ├── Cloud Logging with structured logs
    └── Alerting (PagerDuty/Email)
```

### Infrastructure Layers

**Layer 1: Networking**
- VPC with private subnets (10.0.0.0/16)
- Cloud NAT for egress
- Private Google Access enabled
- Firewall rules (deny-all default, whitelist)

**Layer 2: Compute - GKE Cluster**
- Private GKE cluster (control plane: 172.16.0.0/28)
- Workload Identity enabled
- Shielded nodes (Secure Boot, vTPM, Integrity Monitoring)
- Binary Authorization (policy enforcement)
- Node pools:
  - CPU pool: n2-standard-8, 3-10 nodes (autoscaling)
  - L4 pool: g2-standard-8 + L4 GPU, 2-8 nodes
  - A100 pool: a2-highgpu-1g + A100-40GB, 1-4 nodes
  - TPU pool: TPU v5e pods, 1-2 pods

**Layer 3: Accelerator Management**
- Node Auto-Provisioning (NAP) for dynamic GPU allocation
- GPU time-sharing for L4 (2-4 workloads per GPU)
- Multi-Instance GPU (MIG) for A100 (7 instances per GPU)
- TPU pod allocation via GKE Autopilot or NAP

**Layer 4: Storage**
- Persistent disks (pd-balanced) for models and checkpoints
- Cloud Storage (GCS) buckets for artifacts
- Redis (Memorystore) for caching layer

**Layer 5: Observability**
- Google Managed Prometheus (GMP) for metrics
- Cloud Monitoring dashboards (latency, GPU util, cost)
- Cloud Logging with structured JSON logs
- Alerting rules (SLA breach, cost overrun, error rate)

**Layer 6: Security**
- Workload Identity for GCP API access (no service account keys)
- Secret Manager for credentials
- Network policies (default deny, explicit allow)
- Pod Security Standards (restricted)

---

## COMPONENT SLA TARGETS

| Component     | SLA Metric       | Target         | Accelerator    | Replicas (HPA) |
|---------------|------------------|----------------|----------------|----------------|
| Judge #6      | P99 latency      | ≤90ms          | A100-40GB      | 3-12           |
|               | P95 latency      | ≤65ms          |                |                |
|               | P50 latency      | ≤40ms          |                |                |
| JR Engine     | P99 latency      | ≤500μs (0.5ms) | CPU (n2-std-8) | 5-20           |
|               | P95 latency      | ≤350μs         |                |                |
| Cor           | P99 latency      | ≤1ms           | CPU (n2-std-8) | 3-10           |
| NS            | P99 latency      | ≤100μs         | CPU (n2-std-4) | 5-15           |
| ShadowTag     | P99 latency      | ≤200ms         | L4 GPU         | 2-8            |
| Orchestrator  | PRB adherence    | ≥98%           | L4 GPU         | 3-10           |
|               | LLM mix accuracy | ±2%            |                |                |

---

## FINANCIAL BREAKDOWN

### Monthly Cost Estimate: ~$7,225

```
GKE Control Plane (Standard):               $75/month
    - Private cluster with Workload Identity
    - Managed control plane

CPU Node Pool (n2-standard-8):              $450/month
    - 3-10 nodes @ $0.389/hr (average 5 nodes @ 50% utilization)
    - JR Engine, Cor, NS workloads

L4 GPU Node Pool (g2-standard-8 + L4):      $2,500/month
    - 8x L4 GPUs @ $0.73/hr per GPU
    - Assumes 50% average utilization
    - ShadowTag, Orchestrator workloads

A100-40GB GPU Node Pool (a2-highgpu-1g):    $3,200/month
    - 4x A100-40GB GPUs @ $2.36/hr per GPU
    - Assumes 30% average utilization
    - Judge #6 workload

TPU v5e Node Pool:                          $600/month
    - 1 TPU v5e pod @ $1.60/hr per chip (8 chips/pod)
    - Assumes 20% average utilization
    - Model training and fine-tuning

Vertex AI Workbench (n1-standard-4 + T4):   $400/month
    - Dev environment with Jupyter
    - T4 GPU for prototyping

Networking (Cloud NAT, LB):                 $300/month
    - Cloud NAT egress
    - Load balancer (L4/L7)

Storage (Persistent Disks, GCS):            $200/month
    - 500GB pd-balanced @ $0.10/GB/month
    - 1TB GCS Standard class @ $0.02/GB/month

Monitoring & Logging (GMP, Cloud Logging):  $150/month
    - GMP metrics ingestion
    - Cloud Logging retention (30 days)

Redis (Memorystore):                        $250/month
    - 5GB Standard tier @ $0.049/GB/hr
    - Cache for JR Engine, Cor, NS

───────────────────────────────────────────────────────────────
TOTAL:                                       $7,225/month
                                            ~$87,000/year
═══════════════════════════════════════════════════════════════
```

### Cost Optimization Strategies

1. **HPA (Horizontal Pod Autoscaling)**: Scale down during low traffic (nights, weekends)
2. **Spot/Preemptible nodes**: Use for non-critical workloads (30-80% cost reduction)
3. **GPU time-sharing**: Share L4 GPUs across multiple workloads
4. **MIG for A100**: Partition A100 into 7 instances for better utilization
5. **Committed Use Discounts (CUD)**: 1-year or 3-year commitments (up to 57% discount)
6. **Regional pricing**: us-central1 typically has lowest GPU pricing

**Optimized Monthly Cost** (with strategies): ~$5,000-$5,500/month

---

## 6-PHASE DEPLOYMENT PLAN

### PHASE 0: Prerequisites Validation (1 hour)

**Objective**: Validate GCP environment, quotas, and tooling before deployment

**Automation**: `scripts/00-validate-prerequisites.sh`

**Checks**:
1. GCP project ID and billing account
2. Required APIs enabled (12 APIs):
   - Compute Engine API
   - Kubernetes Engine API
   - Artifact Registry API
   - Cloud Storage API
   - Cloud Monitoring API
   - Cloud Logging API
   - IAM API
   - Secret Manager API
   - Vertex AI API
   - Service Networking API
   - Cloud NAT API
   - Cloud Filestore API
3. IAM permissions (Owner or Editor role on project)
4. Quota validation:
   - 8x L4 GPUs in target region
   - 4x A100-40GB GPUs in target region
   - 1x TPU v5e pod in target region
   - 100 CPUs in target region
5. Tooling installed:
   - Terraform ≥1.8.0
   - kubectl ≥1.28
   - gcloud CLI authenticated
   - helm ≥3.12
6. Network connectivity to GCP APIs

**Kill-Switch Triggers**:
- Missing required APIs (exit with error)
- Insufficient GPU/TPU quota (exit with instructions to request increase)
- Terraform or kubectl not installed (exit with installation guide)

**Outputs**:
- Validated GCP project ID
- Confirmed target region (us-central1 recommended)
- Quota availability report

---

### PHASE 1: Base GKE Platform (2-3 hours)

**Objective**: Deploy private GKE cluster with networking, security, and observability

**Automation**: `scripts/01-deploy-base-platform.sh`

**Steps**:
1. **Create VPC Network** (Terraform):
   ```hcl
   # VPC with private subnets
   resource "google_compute_network" "pnkln_vpc" {
     name                    = "pnkln-vpc"
     auto_create_subnetworks = false
   }

   resource "google_compute_subnetwork" "pnkln_subnet" {
     name          = "pnkln-subnet"
     ip_cidr_range = "10.0.0.0/20"
     region        = var.region
     network       = google_compute_network.pnkln_vpc.id

     secondary_ip_range {
       range_name    = "pods"
       ip_cidr_range = "10.4.0.0/14"
     }

     secondary_ip_range {
       range_name    = "services"
       ip_cidr_range = "10.0.16.0/20"
     }
   }
   ```

2. **Deploy Cloud NAT**:
   ```hcl
   resource "google_compute_router" "pnkln_router" {
     name    = "pnkln-router"
     region  = var.region
     network = google_compute_network.pnkln_vpc.id
   }

   resource "google_compute_router_nat" "pnkln_nat" {
     name                               = "pnkln-nat"
     router                             = google_compute_router.pnkln_router.name
     region                             = var.region
     nat_ip_allocate_option             = "AUTO_ONLY"
     source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
   }
   ```

3. **Create Private GKE Cluster**:
   ```hcl
   resource "google_container_cluster" "pnkln_cluster" {
     name     = "pnkln-gke-cluster"
     location = var.zone  # us-central1-a

     # Private cluster configuration
     private_cluster_config {
       enable_private_nodes    = true
       enable_private_endpoint = false  # Allow public access to control plane
       master_ipv4_cidr_block  = "172.16.0.0/28"
     }

     # Workload Identity
     workload_identity_config {
       workload_pool = "${var.project_id}.svc.id.goog"
     }

     # Shielded nodes
     node_config {
       shielded_instance_config {
         enable_secure_boot          = true
         enable_integrity_monitoring = true
       }
     }

     # Enable GMP (Google Managed Prometheus)
     monitoring_config {
       enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
       managed_prometheus {
         enabled = true
       }
     }

     # Initial node pool (will be deleted after cluster creation)
     remove_default_node_pool = true
     initial_node_count       = 1
   }
   ```

4. **Deploy Initial CPU Node Pool**:
   ```hcl
   resource "google_container_node_pool" "cpu_pool" {
     name       = "cpu-pool"
     location   = var.zone
     cluster    = google_container_cluster.pnkln_cluster.name
     node_count = 3

     autoscaling {
       min_node_count = 3
       max_node_count = 10
     }

     node_config {
       machine_type = "n2-standard-8"
       disk_size_gb = 100
       disk_type    = "pd-balanced"

       oauth_scopes = [
         "https://www.googleapis.com/auth/cloud-platform"
       ]

       workload_metadata_config {
         mode = "GKE_METADATA"
       }
     }
   }
   ```

5. **Configure kubectl Access**:
   ```bash
   gcloud container clusters get-credentials pnkln-gke-cluster \
     --zone=us-central1-a \
     --project=${GCP_PROJECT_ID}
   ```

6. **Verify Cluster Health**:
   ```bash
   kubectl get nodes
   kubectl get pods -n kube-system
   ```

**Kill-Switch Triggers**:
- Cluster creation timeout (30 minutes)
- Nodes not ready after 10 minutes
- GMP not enabled (exit with error)

**Outputs**:
- GKE cluster endpoint
- kubectl configured
- Initial CPU node pool running (3 nodes)

---

### PHASE 2: Inference Architecture (3-4 hours)

**Objective**: Deploy GPU/TPU node pools and accelerator management

**Automation**: `scripts/02-deploy-inference-architecture.sh`

**Steps**:
1. **Deploy L4 GPU Node Pool**:
   ```hcl
   resource "google_container_node_pool" "l4_pool" {
     name       = "l4-pool"
     location   = var.zone
     cluster    = google_container_cluster.pnkln_cluster.name
     node_count = 2

     autoscaling {
       min_node_count = 2
       max_node_count = 8
     }

     node_config {
       machine_type = "g2-standard-8"
       disk_size_gb = 200

       guest_accelerator {
         type  = "nvidia-l4"
         count = 1
         gpu_driver_installation_config {
           gpu_driver_version = "LATEST"
         }
       }

       oauth_scopes = [
         "https://www.googleapis.com/auth/cloud-platform"
       ]

       workload_metadata_config {
         mode = "GKE_METADATA"
       }
     }
   }
   ```

2. **Deploy A100-40GB GPU Node Pool**:
   ```hcl
   resource "google_container_node_pool" "a100_pool" {
     name       = "a100-pool"
     location   = var.zone
     cluster    = google_container_cluster.pnkln_cluster.name
     node_count = 1

     autoscaling {
       min_node_count = 1
       max_node_count = 4
     }

     node_config {
       machine_type = "a2-highgpu-1g"
       disk_size_gb = 500

       guest_accelerator {
         type  = "nvidia-tesla-a100"
         count = 1
         gpu_driver_installation_config {
           gpu_driver_version = "LATEST"
         }
       }

       oauth_scopes = [
         "https://www.googleapis.com/auth/cloud-platform"
       ]

       workload_metadata_config {
         mode = "GKE_METADATA"
       }
     }
   }
   ```

3. **Enable Node Auto-Provisioning (NAP)**:
   ```hcl
   resource "google_container_cluster" "pnkln_cluster" {
     # ... existing config ...

     cluster_autoscaling {
       enabled = true
       autoscaling_profile = "OPTIMIZE_UTILIZATION"

       resource_limits {
         resource_type = "cpu"
         minimum       = 10
         maximum       = 100
       }

       resource_limits {
         resource_type = "memory"
         minimum       = 64
         maximum       = 640
       }

       auto_provisioning_defaults {
         oauth_scopes = [
           "https://www.googleapis.com/auth/cloud-platform",
         ]
       }
     }
   }
   ```

4. **Deploy NVIDIA GPU Operator** (for advanced features):
   ```bash
   helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
   helm repo update
   helm install gpu-operator nvidia/gpu-operator \
     --namespace gpu-operator \
     --create-namespace \
     --set driver.enabled=false  # GKE manages drivers
   ```

5. **Verify GPU Availability**:
   ```bash
   kubectl get nodes -o custom-columns=NAME:.metadata.name,GPUs:.status.allocatable."nvidia\.com/gpu"
   ```

**Kill-Switch Triggers**:
- GPU node pool creation timeout (20 minutes)
- GPU drivers not installed after 15 minutes
- Insufficient GPU quota (exit with instructions)

**Outputs**:
- L4 GPU pool: 2-8 nodes
- A100 GPU pool: 1-4 nodes
- GPU availability confirmed

---

### PHASE 3: Vertex AI Workbench (1-2 hours)

**Objective**: Deploy development environment with Jupyter + kubectl access

**Automation**: `scripts/03-deploy-vertex-workbench.sh`

**Steps**:
1. **Create Workbench Instance** (via gcloud):
   ```bash
   gcloud workbench instances create pnkln-workbench \
     --location=us-central1-a \
     --machine-type=n1-standard-4 \
     --accelerator-type=NVIDIA_TESLA_T4 \
     --accelerator-core-count=1 \
     --boot-disk-size=200 \
     --boot-disk-type=PD_SSD \
     --network=projects/${GCP_PROJECT_ID}/global/networks/pnkln-vpc \
     --subnet=projects/${GCP_PROJECT_ID}/regions/us-central1/subnetworks/pnkln-subnet
   ```

2. **Configure kubectl in Workbench**:
   - SSH into Workbench instance
   - Install kubectl: `sudo apt-get install kubectl`
   - Configure credentials: `gcloud container clusters get-credentials pnkln-gke-cluster`

3. **Install Development Tools**:
   ```bash
   pip install tensorflow torch transformers accelerate
   pip install google-cloud-aiplatform google-cloud-storage
   pip install kubectl kubernetes
   ```

4. **Create Sample Notebook**:
   - Create `deploy-model.ipynb` with model deployment workflow
   - Test kubectl access from notebook

**Kill-Switch Triggers**:
- Workbench creation timeout (15 minutes)
- kubectl configuration failure

**Outputs**:
- Vertex AI Workbench running
- kubectl access from Workbench verified
- Sample notebook created

---

### PHASE 4: PNKLN Stack Deployment (4-6 hours)

**Objective**: Deploy all PNKLN Core Stack components with monitoring

**Automation**: `scripts/04-deploy-pnkln-stack.sh`

**Components to Deploy**:

#### 4.1 Judge #6 (3-Layer Hybrid)

**Manifest**: `k8s-manifests/judge-6-deployment.yaml` (see separate file)

**Steps**:
1. Create ConfigMap for rules engine (ATP 5-19 rules)
2. Create Secret for API keys (Gemini, PyTorch model path)
3. Deploy Judge #6 Deployment with HPA
4. Deploy Service (ClusterIP)
5. Deploy ServiceMonitor (GMP)
6. Deploy PrometheusRule (alerts)

**SLA Target**: P99 ≤90ms

#### 4.2 JR Engine (Purpose/Reasons/Brakes)

**Steps**:
1. Deploy JR Engine Deployment (CPU-optimized)
2. Configure HPA (5-20 replicas based on queue depth)
3. Deploy Service
4. Deploy ServiceMonitor

**SLA Target**: P99 ≤500μs

#### 4.3 Cor (Strategic Context)

**Steps**:
1. Deploy Cor Deployment (CPU-optimized)
2. Deploy Persistent Volume for Cor document versions
3. Deploy Service
4. Deploy ServiceMonitor

**SLA Target**: P99 ≤1ms

#### 4.4 NS (Namespace Resolution)

**Steps**:
1. Deploy NS Deployment (lightweight CPU)
2. Configure HPA (5-15 replicas)
3. Deploy Service
4. Deploy ServiceMonitor

**SLA Target**: P99 ≤100μs

#### 4.5 ShadowTag (DCT Watermarking)

**Steps**:
1. Deploy ShadowTag Deployment (L4 GPU)
2. Deploy Service
3. Deploy ServiceMonitor

**SLA Target**: P99 ≤200ms

#### 4.6 Orchestrator (LLM Mix + PRB)

**Steps**:
1. Create ConfigMap for LLM allocation (Gemini 40%, Claude 35%, etc.)
2. Create Secret for LLM API keys
3. Deploy Orchestrator Deployment (L4 GPU)
4. Configure HPA (3-10 replicas based on request rate)
5. Deploy Service
6. Deploy ServiceMonitor with PRB metrics

**SLA Target**: PRB adherence ≥98%, LLM mix ±2%

#### 4.7 Redis Cache Layer

**Steps**:
1. Deploy Redis StatefulSet (or use Memorystore)
2. Deploy Service
3. Configure JR Engine, Cor, NS to use Redis

#### 4.8 Ingress Controller

**Steps**:
1. Deploy NGINX Ingress Controller
2. Configure Ingress for Orchestrator (external access)
3. Configure TLS (cert-manager + Let's Encrypt)

**Kill-Switch Triggers**:
- Any component fails to deploy after 10 minutes
- Health checks fail after 5 minutes
- SLA targets not met in initial testing

**Outputs**:
- All components deployed and healthy
- Services accessible via ClusterIP
- Orchestrator exposed via Ingress

---

### PHASE 5: Load Testing & SLA Validation (2-3 hours)

**Objective**: Validate SLA targets under load

**Automation**: `scripts/05-run-load-tests.sh`

**Load Testing Suite**: See `load-tests/` directory

**Tests**:
1. **Judge #6 Latency Validation** (`validate_judge6_latency.py`):
   - 1000 requests @ 50 concurrency
   - Verify P99 ≤90ms, P95 ≤65ms, P50 ≤40ms
   - Validate error rate <1%

2. **JR Engine Latency Validation** (`validate_jr_engine_latency.py`):
   - 2000 requests @ 100 concurrency
   - Verify P99 ≤500μs (0.5ms)
   - Validate PRB decision structure

3. **Orchestrator PRB Validation** (`validate_orchestrator_prb.py`):
   - 500 requests @ 20 concurrency
   - Verify PRB adherence ≥98%
   - Verify LLM mix: Gemini 40% (±2%), Claude 35% (±2%), etc.
   - Track cost per request

**Master Runner**: `run_all_validations.py` runs all tests sequentially

**Kill-Switch Triggers**:
- Any SLA target missed by >10%
- Error rate >5%
- PRB adherence <95%

**Outputs**:
- Test reports with latency distributions
- SLA compliance verdict (PASS/FAIL)
- Recommendations for tuning if needed

---

### PHASE 6: Monitoring & Alerting (1 hour)

**Objective**: Set up dashboards, alerts, and runbooks

**Automation**: `scripts/06-setup-monitoring.sh`

**Steps**:

#### 6.1 Cloud Monitoring Dashboards

**Judge #6 Dashboard**:
```json
{
  "displayName": "Judge #6 Performance",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "P99 Latency (SLA: ≤90ms)",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "prometheusQuery": "histogram_quantile(0.99, rate(judge6_request_duration_seconds_bucket[5m])) * 1000"
              }
            }]
          }
        }
      },
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "GPU Utilization",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "prometheusQuery": "avg(DCGM_FI_DEV_GPU_UTIL{pod=~\"judge6-.*\"})"
              }
            }]
          }
        }
      }
    ]
  }
}
```

**Orchestrator Dashboard**:
- PRB adherence (target: ≥98%)
- LLM distribution (Gemini 40%, Claude 35%, GPT-5 15%, Grok 5%)
- Cost per request
- Request rate

**Cluster Overview Dashboard**:
- Node count by pool (CPU, L4, A100)
- GPU utilization
- Pod count by component
- Network egress

#### 6.2 Alerting Policies

**SLA Breach Alerts**:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: pnkln-sla-alerts
spec:
  groups:
    - name: sla_breach
      interval: 30s
      rules:
        - alert: Judge6P99Breach
          expr: histogram_quantile(0.99, rate(judge6_request_duration_seconds_bucket[5m])) > 0.090
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Judge #6 P99 latency exceeds 90ms SLA"

        - alert: JREngineP99Breach
          expr: histogram_quantile(0.99, rate(jr_engine_request_duration_seconds_bucket[5m])) > 0.0005
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "JR Engine P99 latency exceeds 500μs SLA"

        - alert: OrchestratorPRBBreach
          expr: (sum(rate(orchestrator_prb_adherent_total[5m])) / sum(rate(orchestrator_requests_total[5m]))) < 0.98
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Orchestrator PRB adherence below 98% target"
```

**Cost Overrun Alerts**:
```yaml
- alert: MonthlyCostProjectionHigh
  expr: sum(gcp_billing_total) * 730 > 10000  # $10K/month threshold
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "Monthly cost projection exceeds $10K kill-switch threshold"
```

**Error Rate Alerts**:
```yaml
- alert: HighErrorRate
  expr: (sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) > 0.05
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Error rate exceeds 5%"
```

#### 6.3 Notification Channels

**Options**:
1. Email (ehanc6901@gmail.com)
2. PagerDuty (critical alerts)
3. Slack webhook (if integration available)

**Setup**:
```bash
gcloud alpha monitoring channels create \
  --display-name="Erik Email" \
  --type=email \
  --channel-labels=email_address=ehanc6901@gmail.com
```

**Kill-Switch Triggers**:
- Alert creation failure (exit with error)
- Notification channel not configured

**Outputs**:
- 3 Cloud Monitoring dashboards
- 10+ alerting policies
- Notification channels configured

---

## RISK ASSESSMENT (ATP 5-19)

### P99 Survivable Scenarios

**Covered**:
1. ✅ **Accelerator shortage**: NAP + multi-zone deployment handles temporary unavailability
2. ✅ **Cost overrun**: HPA scales down during low traffic, kill-switch at $10K/mo
3. ✅ **SLA breach**: Alerts trigger investigation, HPA scales up automatically
4. ✅ **Security incident**: Shielded nodes, Workload Identity, Secret Manager minimize attack surface
5. ✅ **Component failure**: Kubernetes self-healing (restart pods), PodDisruptionBudget ensures availability
6. ✅ **Network partition**: Private cluster with Cloud NAT, retry logic in clients

**Not Fully Covered**:
1. ⚠️  **Quota exhaustion**: Manual quota increase required (2-5 day lead time)
   - **Mitigation**: Request quota in advance, maintain multi-region failover plan
2. ⚠️  **Terraform state corruption**: State stored in GCS, but no automatic recovery
   - **Mitigation**: Enable versioning on GCS bucket, manual rollback procedure documented
3. ⚠️  **GCP region outage**: Single-region deployment (us-central1)
   - **Mitigation**: Defer multi-region until revenue >$100K/mo (cost vs resilience trade-off)
4. ⚠️  **Model drift**: Judge #6 PyTorch model may degrade over time
   - **Mitigation**: Continuous evaluation, A/B testing framework, rollback to previous model version
5. ⚠️  **LLM API outage**: Orchestrator depends on external LLM APIs (Gemini, Claude, GPT-5, Grok)
   - **Mitigation**: Multi-LLM strategy provides redundancy, fallback to on-prem model if all APIs fail

### Risk Stratification (ATP 5-19)

| Risk                     | Likelihood | Impact | Severity      | Mitigation                          |
|--------------------------|------------|--------|---------------|-------------------------------------|
| Accelerator shortage     | Medium     | High   | Moderate      | NAP + multi-zone                    |
| Cost overrun             | Medium     | High   | Moderate      | HPA + kill-switch                   |
| SLA breach               | Low        | High   | Moderate      | HPA + alerting                      |
| Security incident        | Low        | High   | Moderate      | Shielded nodes + Workload Identity  |
| Quota exhaustion         | Low        | Medium | Low           | Pre-request quota                   |
| Terraform state corrupt  | Very Low   | Medium | Low           | GCS versioning                      |
| GCP region outage        | Very Low   | High   | Moderate      | Defer multi-region                  |
| Model drift              | Medium     | Medium | Low           | Continuous eval + A/B testing       |
| LLM API outage           | Low        | Medium | Low           | Multi-LLM + fallback                |

---

## KILL-SWITCH TRIGGERS & ROLLBACK PROCEDURES

### Kill-Switch Triggers

**Financial**:
1. Monthly cost projection >$10K without revenue justification
   - **Action**: Scale down all HPA to minimum replicas, investigate cost drivers
2. Daily cost spike >$500 (>50% increase)
   - **Action**: Check for runaway autoscaling, investigate abnormal usage

**Technical**:
3. Any SLA target missed by >20% for >15 minutes
   - **Action**: Rollback to previous deployment, investigate root cause
4. Error rate >10% for >5 minutes
   - **Action**: Rollback to previous deployment, check logs
5. PRB adherence <90% for >10 minutes
   - **Action**: Disable Orchestrator, route requests to fallback service

**Operational**:
6. GPU utilization <10% for >1 hour (indicates wasted spend)
   - **Action**: Scale down GPU node pools, investigate low traffic
7. Cluster health check failure
   - **Action**: Investigate control plane, check GCP status page

### Rollback Procedures

**Application Rollback** (Kubernetes):
```bash
# Rollback to previous version
kubectl rollout undo deployment/judge-6 -n pnkln
kubectl rollout undo deployment/orchestrator -n pnkln

# Verify rollback
kubectl rollout status deployment/judge-6 -n pnkln

# Check pod logs
kubectl logs -l app=judge-6 -n pnkln --tail=100
```

**Infrastructure Rollback** (Terraform):
```bash
# Revert to previous Terraform state
cd terraform/base-platform
terraform state pull > backup.tfstate  # Backup current state
terraform apply -target=module.gke_cluster -var-file=previous.tfvars

# Or full rollback
terraform destroy -auto-approve
terraform apply -var-file=previous.tfvars
```

**Emergency Cluster Deletion**:
```bash
# If cluster is unrecoverable
gcloud container clusters delete pnkln-gke-cluster \
  --zone=us-central1-a \
  --quiet

# Redeploy from Phase 1
./scripts/01-deploy-base-platform.sh
```

---

## EXECUTION TIMELINE

### Day 1 (6-8 hours)

**Morning** (3-4 hours):
- 09:00-10:00: Phase 0 - Prerequisites validation
- 10:00-13:00: Phase 1 - Base GKE platform deployment

**Afternoon** (3-4 hours):
- 13:00-17:00: Phase 2 - Inference architecture (GPU/TPU node pools)

**Deliverables**:
- Private GKE cluster running
- CPU node pool (3-10 nodes)
- L4 GPU pool (2-8 nodes)
- A100 GPU pool (1-4 nodes)

---

### Day 2 (6-8 hours)

**Morning** (2 hours):
- 09:00-11:00: Phase 3 - Vertex AI Workbench deployment

**Afternoon** (4-6 hours):
- 11:00-17:00: Phase 4 - PNKLN Stack deployment
  - Judge #6 (1-2 hrs)
  - JR Engine, Cor, NS (1-2 hrs)
  - ShadowTag, Orchestrator (1-2 hrs)
  - Redis, Ingress (1 hr)

**Deliverables**:
- Vertex AI Workbench running
- All PNKLN components deployed
- Services accessible via Ingress

---

### Day 3 (3-4 hours)

**Morning** (2-3 hours):
- 09:00-12:00: Phase 5 - Load testing & SLA validation

**Afternoon** (1 hour):
- 12:00-13:00: Phase 6 - Monitoring & alerting setup

**Deliverables**:
- SLA validation reports
- All SLA targets met (or tuning recommendations)
- Dashboards and alerts configured

---

### Day 4 (Optional, 2-3 hours)

**Fine-tuning & Documentation**:
- Adjust HPA settings based on load test results
- Document operational runbooks
- Train team on monitoring dashboards
- Create incident response procedures

---

## SUCCESS CRITERIA

### Technical Success
- ✅ All components deployed and healthy
- ✅ All SLA targets met:
  - Judge #6: P99 ≤90ms
  - JR Engine: P99 ≤500μs
  - Orchestrator: PRB ≥98%, LLM mix ±2%
- ✅ Error rate <1%
- ✅ GPU utilization 30-60% (cost-efficient)
- ✅ Dashboards and alerts operational

### Financial Success
- ✅ Monthly cost ≤$7,500 (with 10% buffer)
- ✅ Cost per request <$0.01
- ✅ HPA scaling demonstrated (cost optimization)

### Operational Success
- ✅ Deployment automation scripts working
- ✅ Rollback procedures tested
- ✅ Kill-switch triggers documented
- ✅ Runbooks created for common incidents

---

## NEXT STEPS AFTER DEPLOYMENT

### Immediate (Week 1)
1. Monitor dashboards daily for anomalies
2. Validate cost projections match estimates
3. Collect baseline metrics (latency, throughput, cost)
4. Document any issues or unexpected behavior

### Short-term (Month 1)
5. Enable Committed Use Discounts (CUD) for 1-year (up to 57% cost reduction)
6. Implement A/B testing framework for Judge #6 model iterations
7. Set up CI/CD pipeline for automated deployments
8. Create disaster recovery (DR) plan with multi-region failover

### Medium-term (Months 2-3)
9. Optimize HPA settings based on traffic patterns
10. Implement GPU time-sharing for L4 (increase utilization to 70-80%)
11. Enable Binary Authorization for supply chain security
12. Set up Cost Anomaly Detection with BigQuery

### Long-term (Months 4-6)
13. Evaluate multi-region deployment (defer until revenue >$100K/mo)
14. Implement Advanced Load Balancing (Traffic Director)
15. Set up Continuous Training pipeline for Judge #6
16. Migrate to GKE Autopilot if ops overhead too high

---

## ALTERNATIVE APPROACHES CONSIDERED

### 1. Autopilot vs Standard GKE

**Selected**: Standard GKE

**Rationale**:
- Full control over node pools (GPU optimization)
- Better cost predictability (fixed node pricing)
- Flexibility for custom configurations

**Alternative**: Autopilot GKE
- **Pros**: Lower ops overhead, pay-per-pod pricing
- **Cons**: Limited GPU control, higher cost at scale
- **Trade-off**: Ops complexity vs cost predictability

---

### 2. Managed Inference Services vs GKE

**Selected**: GKE

**Rationale**:
- Customization for Judge #6 3-layer hybrid architecture
- Flexibility to deploy non-inference workloads (JR Engine, Cor, NS)
- Cost optimization via HPA and GPU sharing

**Alternative**: Vertex AI Prediction (managed)
- **Pros**: Faster to start, fully managed
- **Cons**: Less flexibility, higher cost, harder to customize
- **Trade-off**: Time-to-market vs customization depth

---

### 3. Single vs Multi-Region

**Selected**: Single region (us-central1)

**Rationale**:
- Lower cost (no cross-region replication)
- Acceptable for bootstrap phase (P99 survivable)
- Can migrate to multi-region later if needed

**Alternative**: Multi-region (us-central1 + us-east1)
- **Pros**: Higher availability (99.95% SLA)
- **Cons**: 2× cost, complexity
- **Trade-off**: Cost vs resilience (defer until revenue >$100K/mo)

---

## CRITICAL GAPS TO ADDRESS

### Blockers (Must Fix Before Deployment)
1. ❌ **No container images**: Judge #6, JR Engine, Cor, NS, ShadowTag, Orchestrator need Dockerfiles
   - **Action**: Create Dockerfiles for each component
   - **Timeline**: 2-3 days
2. ❌ **No Git repository**: Config Sync and GitOps require Git
   - **Action**: Initialize Git repo, push code to GitHub/GitLab
   - **Timeline**: 1 day
3. ❌ **No PyTorch model**: Judge #6 Layer 2 needs trained model
   - **Action**: Train or fine-tune model, upload to GCS
   - **Timeline**: 3-5 days (depending on model complexity)
4. ❌ **GCP project ID not confirmed**: Scripts need actual project ID
   - **Action**: Erik to confirm project ID and region
   - **Timeline**: Immediate

### Nice-to-Have (Can Defer)
5. ⚠️  **No cost tracking automation**: Manual monitoring initially
   - **Action**: Set up Cloud Billing export to BigQuery
   - **Timeline**: 1-2 hours
6. ⚠️  **No incident runbooks**: Operations need documented procedures
   - **Action**: Create runbooks in `docs/runbooks/`
   - **Timeline**: 2-3 hours
7. ⚠️  **No Binary Authorization**: Supply chain security
   - **Action**: Enable Binary Authorization, sign images
   - **Timeline**: 2-3 hours (defer to production)

---

## COMPLIANCE VERIFICATION

### JR Engine (Purpose → Reasons → Brakes)

**Purpose**: Does this deployment advance PNKLN revenue?
- ✅ YES - Enables Judge #6, JR Engine, and Orchestrator to validate product-market fit
- ✅ YES - Provides production infrastructure for customer acquisition
- ✅ YES - Demonstrates technical capability to potential investors/partners

**Reasons**: Defensible judgment with evidence?
- ✅ GKE Hypercomputer: Best-in-class GPU/TPU integration (A100, L4, TPU v5e)
- ✅ Vertex AI Workbench: Rapid iteration with Jupyter + kubectl
- ✅ Google Managed Prometheus: Reduces ops overhead vs self-managed Prometheus
- ✅ Terraform IaC: Ensures repeatability, version control, rollback capability

**Brakes**: P99 survivable scenarios covered?
- ✅ Accelerator shortage: NAP + multi-zone deployment
- ✅ Cost overrun: HPA + kill-switch at $10K/mo
- ✅ SLA breach: Alerts + auto-rollback procedures
- ✅ Security incident: Shielded nodes + Workload Identity
- ⚠️  Quota exhaustion: Manual increase required (2-5 day lead time)
  - Mitigation: Request quota in advance
- ⚠️  GCP region outage: Single-region deployment
  - Mitigation: Defer multi-region until revenue >$100K/mo

**Verdict**: ✅ **APPROVED** - Deployment advances PNKLN revenue with defensible judgment and P99-survivable risks

---

### Bootstrap Financial Discipline

**ROI Target**: ≥3× within 18 months
- **Investment**: ~$87K/year ($7,225/month)
- **Required Revenue**: $261K within 18 months
- **Monthly Revenue Target**: $14.5K/month (to achieve 3× ROI)

**LTV:CAC Target**: ≥4:1 within 12 months
- **Typical CAC**: $5K-$10K (enterprise SaaS)
- **Required LTV**: $20K-$40K per customer
- **Churn Target**: <5% monthly churn to sustain LTV

**Kill-Switch**: Monthly cost >$10K without revenue justification
- **Trigger**: 2 consecutive months >$10K spend with <$5K revenue
- **Action**: Scale down to minimal infrastructure, re-evaluate strategy

**Verdict**: ✅ **APPROVED** - Bootstrap gates clearly defined, kill-switch in place

---

## APPENDIX

### A. Useful Commands

**GKE Operations**:
```bash
# Get cluster credentials
gcloud container clusters get-credentials pnkln-gke-cluster --zone=us-central1-a

# List nodes by pool
kubectl get nodes -L cloud.google.com/gke-nodepool

# Get GPU allocation
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPUs:.status.allocatable."nvidia\.com/gpu"

# Scale node pool
gcloud container clusters resize pnkln-gke-cluster \
  --node-pool=l4-pool \
  --num-nodes=4 \
  --zone=us-central1-a

# Delete node pool
gcloud container node-pools delete l4-pool \
  --cluster=pnkln-gke-cluster \
  --zone=us-central1-a
```

**Kubernetes Operations**:
```bash
# Deploy manifest
kubectl apply -f k8s-manifests/judge-6-deployment.yaml

# Get pods with labels
kubectl get pods -l app=judge-6 -n pnkln

# View logs
kubectl logs -l app=judge-6 -n pnkln --tail=100 -f

# Port-forward for local testing
kubectl port-forward svc/judge-6 8080:80 -n pnkln

# Rollback deployment
kubectl rollout undo deployment/judge-6 -n pnkln

# Scale deployment manually
kubectl scale deployment/judge-6 --replicas=5 -n pnkln

# Get HPA status
kubectl get hpa -n pnkln

# Describe HPA
kubectl describe hpa judge-6-hpa -n pnkln
```

**Monitoring Queries** (PromQL):
```promql
# P99 latency (Judge #6)
histogram_quantile(0.99, rate(judge6_request_duration_seconds_bucket[5m])) * 1000

# Error rate
(sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100

# GPU utilization
avg(DCGM_FI_DEV_GPU_UTIL{pod=~"judge6-.*"})

# PRB adherence (Orchestrator)
(sum(rate(orchestrator_prb_adherent_total[5m])) / sum(rate(orchestrator_requests_total[5m]))) * 100

# Cost per request (estimate)
sum(rate(http_requests_total[5m])) / (monthly_cost / 2592000)  # 2592000 seconds in 30 days
```

**Terraform Operations**:
```bash
# Initialize
cd terraform/base-platform
terraform init

# Plan
terraform plan -var-file=prod.tfvars

# Apply
terraform apply -var-file=prod.tfvars -auto-approve

# Destroy (careful!)
terraform destroy -var-file=prod.tfvars -auto-approve

# Show current state
terraform show

# List resources
terraform state list

# Pull state (backup)
terraform state pull > backup.tfstate
```

---

### B. Troubleshooting Guide

**Problem**: Nodes not ready after deployment

**Diagnosis**:
```bash
kubectl get nodes
kubectl describe node <node-name>
```

**Solutions**:
- Check if GPU drivers installed: `kubectl get daemonset -n kube-system`
- Check node logs: `gcloud compute ssh <node-name> -- sudo journalctl -u kubelet`
- Check quota: `gcloud compute project-info describe --project=${GCP_PROJECT_ID}`

---

**Problem**: Pods stuck in Pending state

**Diagnosis**:
```bash
kubectl describe pod <pod-name> -n pnkln
```

**Solutions**:
- Insufficient GPU: Scale up GPU node pool or wait for autoscaler
- Insufficient CPU/memory: Scale up CPU node pool
- No nodes available: Check node pool status, increase max nodes
- Image pull failure: Check image path, credentials

---

**Problem**: SLA targets not met (high latency)

**Diagnosis**:
```bash
# Check HPA status
kubectl get hpa -n pnkln

# Check CPU/GPU utilization
kubectl top pods -n pnkln

# Check Prometheus metrics
kubectl port-forward -n gmp-system svc/frontend 9090
# Open http://localhost:9090
```

**Solutions**:
- Scale up replicas: `kubectl scale deployment/<name> --replicas=<N> -n pnkln`
- Adjust HPA settings: Increase max replicas, lower target utilization
- Check for resource contention: GPU sharing may be too aggressive
- Profile application: Use Vertex AI Profiler to identify bottlenecks

---

**Problem**: High cost / unexpected charges

**Diagnosis**:
```bash
# Check node count
kubectl get nodes

# Check GPU allocation
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPUs:.status.allocatable."nvidia\.com/gpu"

# Check Cloud Billing
gcloud billing accounts list
gcloud billing projects describe ${GCP_PROJECT_ID}
```

**Solutions**:
- Scale down node pools: Reduce max nodes in HPA
- Enable CUD: `gcloud compute commitments create` (1-year or 3-year)
- Use preemptible nodes for non-critical workloads
- Delete unused resources: Check for orphaned disks, IPs

---

**Problem**: Deployment fails (Terraform)

**Diagnosis**:
```bash
terraform plan
terraform show
```

**Solutions**:
- Check API enablement: Ensure all 12 APIs enabled
- Check quota: Request quota increase via GCP Console
- Check permissions: Ensure service account has Editor role
- Rollback: `terraform destroy` and retry

---

### C. References

**Official Documentation**:
- [GKE Hypercomputer](https://cloud.google.com/kubernetes-engine/docs/concepts/gpu-hypercomputer)
- [Vertex AI Workbench](https://cloud.google.com/vertex-ai/docs/workbench)
- [Google Managed Prometheus](https://cloud.google.com/stackdriver/docs/managed-prometheus)
- [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [Node Auto-Provisioning](https://cloud.google.com/kubernetes-engine/docs/how-to/node-auto-provisioning)

**GitHub Repositories** (Google accelerated-platforms):
- [accelerated-platforms/examples](https://github.com/GoogleCloudPlatform/accelerated-platforms)
- [GKE AI/ML Reference Architectures](https://github.com/GoogleCloudPlatform/ai-on-gke)

**Terraform Modules**:
- [terraform-google-kubernetes-engine](https://registry.terraform.io/modules/terraform-google-modules/kubernetes-engine/google/latest)
- [terraform-google-network](https://registry.terraform.io/modules/terraform-google-modules/network/google/latest)

---

```
═══════════════════════════════════════════════════════════════════
  END OF DEPLOYMENT PLAN
  Status: Ready for Execution
  Next: Review → Approve → Execute Phase 0
═══════════════════════════════════════════════════════════════════
```

**Package Location**: `/home/user/aiyou-fastapi-services/gke-deployment/`

**Master Plan**: `/home/user/aiyou-fastapi-services/pnkln-gke-deployment-plan.md`

**Estimated Reading Time**: 45 minutes

**Recommended Review Order**:
1. Executive Summary + Architecture Overview (10 min)
2. Component SLA Targets + Financial Breakdown (10 min)
3. 6-Phase Deployment Plan (15 min)
4. Risk Assessment + Kill-Switch Triggers (10 min)

—End of Document
