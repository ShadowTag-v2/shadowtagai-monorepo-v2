# GKE GPU Integration Guide for ShadowTag

> **Google Cloud Native GPU Infrastructure**
> **Date**: 2025-11-17
> **Version**: 1.0
> **Platform**: Google Kubernetes Engine (GKE) Exclusive

---

## Executive Summary

This document provides the complete implementation guide for deploying ShadowTag's GPU infrastructure on **Google Kubernetes Engine (GKE)**. It translates the strategic GPU infrastructure plan into concrete GCP-native implementations, leveraging GKE's managed Kubernetes capabilities, NVIDIA GPU support, and integration with Vertex AI.

### Why GKE for GPU Workloads

**Strategic Advantages**:

- ✅ **Fully Managed**: Google handles control plane, upgrades, security patches
- ✅ **GPU Native**: First-class support for NVIDIA GPUs (T4, V100, A100, H100, L4)
- ✅ **Auto-Scaling**: Node auto-provisioning for GPU nodes
- ✅ **Vertex AI Integration**: Seamless connection to Vertex AI Workbench, Pipelines, Training
- ✅ **Cost Optimization**: Spot VMs, committed use discounts, sustained use discounts
- ✅ **Multi-Region**: Deploy across zones for high availability
- ✅ **IAM Integration**: Fine-grained access control via Google Cloud IAM

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [GKE Cluster Configuration](#gke-cluster-configuration)
3. [GPU Node Pools](#gpu-node-pools)
4. [NVIDIA GPU Operator Setup](#nvidia-gpu-operator-setup)
5. [Workload Deployment](#workload-deployment)
6. [Auto-Scaling Configuration](#auto-scaling-configuration)
7. [Cost Optimization](#cost-optimization)
8. [Vertex AI Integration](#vertex-ai-integration)
9. [Monitoring & Observability](#monitoring--observability)
10. [Security & Compliance](#security--compliance)
11. [Migration Path](#migration-path)
12. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Google Cloud Platform                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              GKE Cluster (ShadowTag-production)             │ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │ │
│  │  │ System Pool  │  │  CPU Pool    │  │  GPU Pools   │  │ │
│  │  │ (e2-medium)  │  │ (n2-standard)│  │ (Multi-type) │  │ │
│  │  │              │  │              │  │              │  │ │
│  │  │ • Monitoring │  │ • API        │  │ • Training   │  │ │
│  │  │ • Logging    │  │ • Web        │  │ • Inference  │  │ │
│  │  │ • System     │  │ • Workers    │  │ • Fine-tune  │  │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │ │
│  │                                                          │ │
│  │  GPU Pool Types:                                        │ │
│  │  ├─ a2-highgpu-1g  (1× A100 40GB) - Inference          │ │
│  │  ├─ a2-highgpu-2g  (2× A100 40GB) - Fine-tuning        │ │
│  │  ├─ a2-ultragpu-1g (1× A100 80GB) - Large models       │ │
│  │  ├─ a2-ultragpu-8g (8× A100 80GB) - Distributed train  │ │
│  │  ├─ a3-highgpu-8g  (8× H100 80GB) - Peak performance   │ │
│  │  └─ g2-standard-4  (1× L4 24GB)   - Cost-optimized     │ │
│  │                                                          │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   Supporting Services                   │ │
│  │                                                          │ │
│  │  • Cloud Storage (GCS) - Model & data storage          │ │
│  │  • Artifact Registry - Container images                │ │
│  │  • Cloud Monitoring - Metrics & dashboards             │ │
│  │  • Cloud Logging - Centralized logs                    │ │
│  │  • Vertex AI - ML platform integration                 │ │
│  │  • Secret Manager - Credentials & API keys             │ │
│  │  • Cloud IAM - Access control                          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

```
Application Layer
├─ Model Training Jobs (Kubeflow, Vertex AI Pipelines)
├─ Inference Services (KServe, TensorFlow Serving)
├─ Fine-Tuning Workflows (RAG, Custom trainers)
└─ Batch Processing (Apache Beam on Dataflow)

Orchestration Layer
├─ Kubernetes Scheduler (GPU-aware)
├─ NVIDIA GPU Operator (Device plugin, DCGM)
├─ Kueue (Job queueing for multi-tenancy)
└─ Cluster Autoscaler (Node auto-provisioning)

Infrastructure Layer
├─ GKE Control Plane (Managed by Google)
├─ GPU Node Pools (A100, H100, L4)
├─ Standard Node Pools (CPU workloads)
└─ Networking (VPC, Private clusters, Cloud NAT)

Data & Storage Layer
├─ Google Cloud Storage (Models, datasets, checkpoints)
├─ Persistent Disks (Ephemeral fast storage)
├─ Filestore (Shared NFS for multi-node training)
└─ Artifact Registry (Container images)
```

---

## GKE Cluster Configuration

### Cluster Specifications

**Recommended Configuration**:

| Setting                   | Value                  | Rationale                           |
| ------------------------- | ---------------------- | ----------------------------------- |
| **Cluster Name**          | `ShadowTag-production-gpu` | Clear naming convention             |
| **Region**                | `us-central1`          | A100/H100 availability, low latency |
| **Release Channel**       | `REGULAR`              | Balance stability & new features    |
| **Control Plane Version** | Auto (latest stable)   | Managed updates                     |
| **Network Mode**          | VPC-native             | Required for private clusters       |
| **Private Cluster**       | Yes                    | Enhanced security                   |
| **Workload Identity**     | Enabled                | Secure GCP service access           |
| **Binary Authorization**  | Enabled                | Image signing enforcement           |
| **Shielded Nodes**        | Enabled                | Boot integrity verification         |

### Cluster Creation (gcloud CLI)

```bash
#!/bin/bash
# Create GKE cluster optimized for GPU workloads

export PROJECT_ID="ShadowTag-production"
export CLUSTER_NAME="ShadowTag-production-gpu"
export REGION="us-central1"
export NETWORK="ShadowTag-vpc"
export SUBNETWORK="ShadowTag-gpu-subnet"

gcloud container clusters create ${CLUSTER_NAME} \
  --region=${REGION} \
  --project=${PROJECT_ID} \
  --release-channel=regular \
  --enable-ip-alias \
  --network=${NETWORK} \
  --subnetwork=${SUBNETWORK} \
  --enable-private-nodes \
  --enable-private-endpoint \
  --master-ipv4-cidr=172.16.0.0/28 \
  --enable-master-authorized-networks \
  --master-authorized-networks=10.0.0.0/8 \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-autoscaling \
  --enable-vertical-pod-autoscaling \
  --workload-pool=${PROJECT_ID}.svc.id.goog \
  --enable-shielded-nodes \
  --shielded-secure-boot \
  --shielded-integrity-monitoring \
  --enable-binauthz \
  --addons=HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver \
  --logging=SYSTEM,WORKLOAD \
  --monitoring=SYSTEM,WORKLOAD \
  --enable-stackdriver-kubernetes \
  --maintenance-window-start=2025-01-01T00:00:00Z \
  --maintenance-window-duration=4h \
  --maintenance-window-recurrence="FREQ=WEEKLY;BYDAY=SU" \
  --node-locations=${REGION}-a,${REGION}-b,${REGION}-c \
  --num-nodes=1 \
  --machine-type=e2-medium \
  --disk-type=pd-standard \
  --disk-size=100 \
  --node-labels=pool=system \
  --node-taints=CriticalAddonsOnly=true:NoSchedule
```

**What This Creates**:

- Regional cluster across 3 zones (high availability)
- Private cluster (nodes have no external IPs)
- Workload Identity enabled (secure GCP access)
- System node pool (1 node, for critical add-ons only)
- Auto-upgrade and auto-repair enabled
- Binary Authorization (only signed images can run)
- Comprehensive logging and monitoring

---

## GPU Node Pools

### Node Pool Strategy

Create **separate node pools** for different GPU workload types:

1. **Inference Pool** (L4, cost-optimized, high throughput)
2. **Fine-Tuning Pool** (A100 2-GPU, balanced cost/performance)
3. **Training Pool** (A100 8-GPU or H100 8-GPU, maximum performance)
4. **Spot Pool** (Preemptible, for fault-tolerant workloads)

### 1. Inference Pool (L4 GPUs)

**Best For**: High-throughput, cost-sensitive inference

```bash
gcloud container node-pools create inference-l4-pool \
  --cluster=${CLUSTER_NAME} \
  --region=${REGION} \
  --machine-type=g2-standard-4 \
  --accelerator=type=nvidia-l4,count=1 \
  --num-nodes=0 \
  --min-nodes=0 \
  --max-nodes=20 \
  --enable-autoscaling \
  --enable-autorepair \
  --enable-autoupgrade \
  --disk-type=pd-balanced \
  --disk-size=200 \
  --node-labels=workload=inference,gpu=l4,pool=inference-l4 \
  --node-taints=nvidia.com/gpu=present:NoSchedule \
  --metadata=google-logging-enabled=true,google-monitoring-enabled=true \
  --tags=gpu-node,inference \
  --enable-gvnic
```

**Cost**: ~$0.70/hr per node (1× L4 + g2-standard-4)
**Use Cases**: Real-time inference, API serving, batch inference

### 2. Fine-Tuning Pool (A100 2-GPU)

**Best For**: Model fine-tuning, RAG optimization

```bash
gcloud container node-pools create finetune-a100-2g-pool \
  --cluster=${CLUSTER_NAME} \
  --region=${REGION} \
  --machine-type=a2-highgpu-2g \
  --accelerator=type=nvidia-tesla-a100,count=2 \
  --num-nodes=0 \
  --min-nodes=0 \
  --max-nodes=10 \
  --enable-autoscaling \
  --enable-autorepair \
  --enable-autoupgrade \
  --disk-type=pd-ssd \
  --disk-size=500 \
  --node-labels=workload=fine-tuning,gpu=a100,pool=finetune-a100-2g \
  --node-taints=nvidia.com/gpu=present:NoSchedule \
  --metadata=google-logging-enabled=true,google-monitoring-enabled=true,install-gpu-driver=true \
  --tags=gpu-node,fine-tuning \
  --enable-gvnic
```

**Cost**: ~$6.00/hr per node (2× A100 40GB + CPU/RAM)
**Use Cases**: LoRA fine-tuning, adapter training, PEFT methods

### 3. Training Pool (A100 8-GPU)

**Best For**: Distributed training, foundation model training

```bash
gcloud container node-pools create training-a100-8g-pool \
  --cluster=${CLUSTER_NAME} \
  --region=${REGION} \
  --machine-type=a2-ultragpu-8g \
  --accelerator=type=nvidia-a100-80gb,count=8 \
  --num-nodes=0 \
  --min-nodes=0 \
  --max-nodes=4 \
  --enable-autoscaling \
  --enable-autorepair \
  --enable-autoupgrade \
  --disk-type=pd-ssd \
  --disk-size=1000 \
  --node-labels=workload=training,gpu=a100-80gb,pool=training-a100-8g \
  --node-taints=nvidia.com/gpu=present:NoSchedule \
  --metadata=google-logging-enabled=true,google-monitoring-enabled=true,install-gpu-driver=true \
  --tags=gpu-node,training \
  --enable-gvnic \
  --placement-type=COMPACT
```

**Cost**: ~$28.00/hr per node (8× A100 80GB + CPU/RAM)
**Use Cases**: Foundation model training, multi-node distributed training

### 4. H100 Pool (Premium Performance)

**Best For**: Bleeding-edge performance, Transformer-optimized

```bash
gcloud container node-pools create training-h100-8g-pool \
  --cluster=${CLUSTER_NAME} \
  --region=${REGION} \
  --machine-type=a3-highgpu-8g \
  --accelerator=type=nvidia-h100-80gb,count=8 \
  --num-nodes=0 \
  --min-nodes=0 \
  --max-nodes=2 \
  --enable-autoscaling \
  --enable-autorepair \
  --enable-autoupgrade \
  --disk-type=pd-ssd \
  --disk-size=1000 \
  --node-labels=workload=training,gpu=h100,pool=training-h100-8g \
  --node-taints=nvidia.com/gpu=present:NoSchedule \
  --metadata=google-logging-enabled=true,google-monitoring-enabled=true,install-gpu-driver=true \
  --tags=gpu-node,training-premium \
  --enable-gvnic \
  --placement-type=COMPACT
```

**Cost**: ~$40.00/hr per node (8× H100 80GB + CPU/RAM)
**Use Cases**: Frontier model training, maximum throughput inference

### 5. Spot Pool (Cost-Optimized)

**Best For**: Fault-tolerant training, batch jobs

```bash
gcloud container node-pools create spot-a100-pool \
  --cluster=${CLUSTER_NAME} \
  --region=${REGION} \
  --machine-type=a2-highgpu-1g \
  --accelerator=type=nvidia-tesla-a100,count=1 \
  --spot \
  --num-nodes=0 \
  --min-nodes=0 \
  --max-nodes=10 \
  --enable-autoscaling \
  --enable-autorepair \
  --disk-type=pd-balanced \
  --disk-size=200 \
  --node-labels=workload=batch,gpu=a100,pool=spot-a100,preemptible=true \
  --node-taints=nvidia.com/gpu=present:NoSchedule,cloud.google.com/gke-spot=true:NoSchedule \
  --metadata=google-logging-enabled=true,google-monitoring-enabled=true,install-gpu-driver=true \
  --tags=gpu-node,spot \
  --enable-gvnic
```

**Cost**: ~$1.50/hr per node (60-70% discount vs. on-demand)
**Use Cases**: Research, experimentation, checkpoint-resumable training

---

## NVIDIA GPU Operator Setup

### Why GPU Operator?

The **NVIDIA GPU Operator** automates:

- GPU driver installation
- CUDA toolkit provisioning
- NVIDIA Container Toolkit
- DCGM (Data Center GPU Manager) for monitoring
- Device plugin for Kubernetes

### Installation via Helm

```bash
#!/bin/bash
# Install NVIDIA GPU Operator on GKE

# Add NVIDIA Helm repo
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm repo update

# Install GPU Operator
helm install gpu-operator nvidia/gpu-operator \
  --namespace gpu-operator \
  --create-namespace \
  --set driver.enabled=false \
  --set toolkit.enabled=true \
  --set dcgm.enabled=true \
  --set dcgmExporter.enabled=true \
  --set devicePlugin.enabled=true \
  --set mig.strategy=single \
  --set operator.defaultRuntime=containerd \
  --set gfd.enabled=true \
  --wait

# Verify installation
kubectl get pods -n gpu-operator
kubectl get nodes -o json | jq '.items[].status.capacity | select(."nvidia.com/gpu" != null)'
```

**Key Settings**:

- `driver.enabled=false`: GKE pre-installs drivers
- `dcgm.enabled=true`: Enable GPU monitoring
- `devicePlugin.enabled=true`: Kubernetes GPU scheduling

### Verify GPU Availability

```bash
# Check GPU nodes
kubectl get nodes -l cloud.google.com/gke-accelerator -o wide

# Describe node to see GPU resources
kubectl describe node <node-name> | grep -A 5 Capacity

# Expected output:
# Capacity:
#   nvidia.com/gpu: 8  # For 8-GPU nodes
```

---

## Workload Deployment

### Example: Inference Deployment (KServe)

**Deployment Manifest** (`inference-deployment.yaml`):

```yaml
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: ShadowTag-llm-inference
  namespace: production
spec:
  predictor:
    serviceAccountName: kserve-sa
    containers:
      - name: kserve-container
        image: gcr.io/ShadowTag-production/llm-inference:latest
        resources:
          requests:
            cpu: "4"
            memory: "16Gi"
            nvidia.com/gpu: "1"
          limits:
            cpu: "8"
            memory: "32Gi"
            nvidia.com/gpu: "1"
        env:
          - name: MODEL_NAME
            value: "llama-70b-instruct"
          - name: STORAGE_URI
            value: "gs://ShadowTag-models/llama-70b-instruct"
          - name: MAX_BATCH_SIZE
            value: "32"
    nodeSelector:
      workload: inference
      gpu: l4
    tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
```

**Deploy**:

```bash
kubectl apply -f inference-deployment.yaml

# Check status
kubectl get inferenceservice ShadowTag-llm-inference -n production

# Get endpoint
kubectl get ksvc ShadowTag-llm-inference-predictor -n production -o jsonpath='{.status.url}'
```

### Example: Training Job (Kubeflow)

**Training Job Manifest** (`training-job.yaml`):

```yaml
apiVersion: kubeflow.org/v1
kind: PyTorchJob
metadata:
  name: llama-finetune-job
  namespace: ml-training
spec:
  pytorchReplicaSpecs:
    Master:
      replicas: 1
      restartPolicy: OnFailure
      template:
        metadata:
          annotations:
            sidecar.istio.io/inject: "false"
        spec:
          serviceAccountName: training-sa
          containers:
            - name: pytorch
              image: gcr.io/ShadowTag-production/pytorch-training:latest
              command:
                - python
                - /workspace/train.py
                - --model=llama-7b
                - --dataset=gs://ShadowTag-data/fine-tune-dataset
                - --epochs=3
                - --batch-size=32
              resources:
                requests:
                  nvidia.com/gpu: "2"
                  memory: "64Gi"
                  cpu: "16"
                limits:
                  nvidia.com/gpu: "2"
                  memory: "128Gi"
                  cpu: "32"
              volumeMounts:
                - name: dshm
                  mountPath: /dev/shm
                - name: checkpoint-storage
                  mountPath: /workspace/checkpoints
          volumes:
            - name: dshm
              emptyDir:
                medium: Memory
                sizeLimit: "32Gi"
            - name: checkpoint-storage
              persistentVolumeClaim:
                claimName: training-checkpoints-pvc
          nodeSelector:
            workload: fine-tuning
            gpu: a100
          tolerations:
            - key: nvidia.com/gpu
              operator: Exists
              effect: NoSchedule
    Worker:
      replicas: 3
      restartPolicy: OnFailure
      template:
        spec:
          # Same as Master but without command (uses default entrypoint)
          serviceAccountName: training-sa
          containers:
            - name: pytorch
              image: gcr.io/ShadowTag-production/pytorch-training:latest
              resources:
                requests:
                  nvidia.com/gpu: "2"
                  memory: "64Gi"
                  cpu: "16"
                limits:
                  nvidia.com/gpu: "2"
                  memory: "128Gi"
                  cpu: "32"
          nodeSelector:
            workload: fine-tuning
            gpu: a100
          tolerations:
            - key: nvidia.com/gpu
              operator: Exists
              effect: NoSchedule
```

**Deploy**:

```bash
kubectl apply -f training-job.yaml

# Monitor progress
kubectl logs -n ml-training -l job-name=llama-finetune-job -f

# Check GPU utilization during training
kubectl exec -it <pod-name> -n ml-training -- nvidia-smi
```

---

## Auto-Scaling Configuration

### Cluster Autoscaler

**Enable Node Auto-Provisioning** (automatic pool creation):

```bash
gcloud container clusters update ${CLUSTER_NAME} \
  --enable-autoprovisioning \
  --min-cpu=4 \
  --max-cpu=1000 \
  --min-memory=16 \
  --max-memory=10000 \
  --min-accelerator=type=nvidia-tesla-a100,count=0 \
  --max-accelerator=type=nvidia-tesla-a100,count=64 \
  --autoprovisioning-scopes=https://www.googleapis.com/auth/cloud-platform \
  --region=${REGION}
```

### Horizontal Pod Autoscaler (HPA)

**For Inference Services**:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: inference-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ShadowTag-llm-inference
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Pods
      pods:
        metric:
          name: requests_per_second
        target:
          type: AverageValue
          averageValue: "100"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 50
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30
        - type: Pods
          value: 4
          periodSeconds: 30
      selectPolicy: Max
```

### Vertical Pod Autoscaler (VPA)

**For Right-Sizing GPU Workloads**:

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: training-vpa
  namespace: ml-training
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: training-deployment
  updatePolicy:
    updateMode: "Recreate" # Recreate pods with new resources
  resourcePolicy:
    containerPolicies:
      - containerName: "*"
        minAllowed:
          cpu: "2"
          memory: "8Gi"
        maxAllowed:
          cpu: "64"
          memory: "256Gi"
        controlledResources:
          - cpu
          - memory
```

---

## Cost Optimization

### 1. Committed Use Discounts (CUDs)

**Reserve GPU capacity for 1-year or 3-year terms**:

```bash
# Purchase 1-year commitment for 10× A100 GPUs
gcloud compute commitments create a100-gpu-commitment \
  --region=us-central1 \
  --resources=accelerator=nvidia-tesla-a100,count=10 \
  --plan=12-month \
  --type=ACCELERATOR_OPTIMIZED

# Savings: Up to 37% for 1-year, 55% for 3-year
```

**When to Use**:

- After 90 days of usage data shows consistent demand
- When utilization ≥40% sustained

### 2. Spot VMs (Preemptible)

**Already configured in Spot Pool above**

**Best Practices**:

- Use for fault-tolerant workloads
- Implement checkpoint/resume every 5-10 minutes
- Set `--spot` flag on node pools
- Savings: 60-91% vs. on-demand

### 3. Auto-Shutdown Idle Workloads

**Deployment with Idle Detection**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inference-service
  annotations:
    idleAfterSeconds: "1800" # 30 minutes
    scaleToZeroEnabled: "true"
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: inference
          # ... container spec
```

**Custom Controller** (scale to zero after idle):

```python
# idle-scaler-controller.py
import time
from kubernetes import client, config

config.load_incluster_config()
v1 = client.AppsV1Api()

def scale_down_idle_deployments():
    deployments = v1.list_deployment_for_all_namespaces()
    for dep in deployments.items:
        if 'scaleToZeroEnabled' in dep.metadata.annotations:
            idle_threshold = int(dep.metadata.annotations.get('idleAfterSeconds', 900))
            # Check metrics, scale to 0 if idle
            # Implementation details...
```

### 4. GCS Lifecycle Policies

**Auto-delete old checkpoints**:

```json
{
  "lifecycle": {
    "rule": [
      {
        "action": { "type": "Delete" },
        "condition": {
          "age": 30,
          "matchesPrefix": ["checkpoints/"]
        }
      },
      {
        "action": { "type": "SetStorageClass", "storageClass": "NEARLINE" },
        "condition": {
          "age": 7,
          "matchesPrefix": ["models/"]
        }
      }
    ]
  }
}
```

### 5. Budget Alerts

```bash
# Create budget alert
gcloud billing budgets create \
  --billing-account=<BILLING_ACCOUNT_ID> \
  --display-name="GPU Compute Budget" \
  --budget-amount=50000 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100 \
  --notification-channel-ids=<CHANNEL_ID>
```

---

## Vertex AI Integration

### Architecture

```
┌─────────────────────────────────────────────┐
│           Vertex AI Workbench               │
│  (Development, Experimentation, Notebooks)  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│        Vertex AI Training Jobs              │
│  (Managed training with custom containers)  │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│         Vertex AI Pipelines                 │
│   (Kubeflow Pipelines, orchestration)       │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│        GKE Cluster (Execution)              │
│  (GPU workloads run here)                   │
└─────────────────────────────────────────────┘
```

### 1. Connect Vertex AI to GKE

**Enable APIs**:

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  notebooks.googleapis.com \
  ml.googleapis.com
```

**Configure Workbench**:

```bash
# Create Vertex AI Workbench instance with GPU
gcloud notebooks instances create ShadowTag-workbench \
  --location=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator-type=NVIDIA_TESLA_T4 \
  --accelerator-core-count=1 \
  --install-gpu-driver \
  --network=${NETWORK} \
  --subnet=${SUBNETWORK} \
  --metadata="proxy-mode=service_account"
```

### 2. Submit Training Job to GKE via Vertex AI

**Python SDK**:

```python
from google.cloud import aiplatform

aiplatform.init(project='ShadowTag-production', location='us-central1')

# Create custom training job that runs on GKE
job = aiplatform.CustomContainerTrainingJob(
    display_name='llama-finetune',
    container_uri='gcr.io/ShadowTag-production/pytorch-training:latest',
    command=['python', 'train.py'],
    model_serving_container_image_uri='gcr.io/ShadowTag-production/llm-serve:latest',
)

# Run on GKE cluster
model = job.run(
    replica_count=1,
    machine_type='a2-highgpu-2g',
    accelerator_type='NVIDIA_TESLA_A100',
    accelerator_count=2,
    sync=True,
)

print(f'Model deployed: {model.resource_name}')
```

### 3. Vertex AI Pipelines on GKE

**Pipeline Definition** (Kubeflow):

```python
from kfp.v2 import dsl, compiler

@dsl.component
def preprocess_data(input_path: str, output_path: str):
    # Data preprocessing component
    pass

@dsl.component(
    base_image='gcr.io/ShadowTag-production/pytorch-training:latest',
    gpu_limit='2'
)
def train_model(data_path: str, model_output: str):
    # Training component with GPU
    pass

@dsl.pipeline(name='llama-training-pipeline')
def training_pipeline(input_data: str):
    preprocess_task = preprocess_data(
        input_path=input_data,
        output_path='gs://ShadowTag-data/preprocessed'
    )

    train_task = train_model(
        data_path=preprocess_task.outputs['output_path'],
        model_output='gs://ShadowTag-models/llama-finetuned'
    )

# Compile and run
compiler.Compiler().compile(pipeline_func=training_pipeline, package_path='pipeline.json')

# Submit to Vertex AI
from google.cloud import aiplatform
pipeline_job = aiplatform.PipelineJob(
    display_name='llama-training-pipeline',
    template_path='pipeline.json',
    pipeline_root='gs://ShadowTag-pipelines',
    parameter_values={'input_data': 'gs://ShadowTag-data/raw'}
)
pipeline_job.run()
```

---

## Monitoring & Observability

### 1. Cloud Monitoring Dashboard

**Create GPU Dashboard**:

```bash
# dashboard-config.json
{
  "displayName": "GPU Cluster Monitoring",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "GPU Utilization %",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"kubernetes.io/container/accelerator/duty_cycle\" resource.type=\"k8s_container\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        }
      },
      {
        "xPos": 6,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "GPU Memory Used",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "metric.type=\"kubernetes.io/container/accelerator/memory_used\" resource.type=\"k8s_container\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        }
      }
    ]
  }
}

# Create dashboard
gcloud monitoring dashboards create --config-from-file=dashboard-config.json
```

### 2. DCGM Exporter (Prometheus Metrics)

**Already installed via GPU Operator**

**Grafana Dashboard**:

```yaml
# grafana-gpu-dashboard.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: gpu-dashboard
  namespace: monitoring
data:
  gpu-dashboard.json: |
    {
      "dashboard": {
        "title": "NVIDIA GPU Metrics",
        "panels": [
          {
            "title": "GPU Utilization",
            "targets": [{
              "expr": "DCGM_FI_DEV_GPU_UTIL",
              "legendFormat": "{{gpu}}"
            }]
          },
          {
            "title": "GPU Temperature",
            "targets": [{
              "expr": "DCGM_FI_DEV_GPU_TEMP",
              "legendFormat": "{{gpu}}"
            }]
          },
          {
            "title": "GPU Power Usage",
            "targets": [{
              "expr": "DCGM_FI_DEV_POWER_USAGE",
              "legendFormat": "{{gpu}}"
            }]
          }
        ]
      }
    }
```

### 3. Cost Attribution

**Export Billing Data to BigQuery**:

```sql
-- Query: GPU cost per workload
SELECT
  DATE(usage_start_time) AS date,
  labels.value AS workload_type,
  SUM(cost) AS total_cost,
  SUM(usage.amount) AS gpu_hours
FROM
  `ShadowTag-production.billing.gcp_billing_export_v1_*`
CROSS JOIN
  UNNEST(labels) AS labels
WHERE
  service.description = 'Compute Engine'
  AND sku.description LIKE '%GPU%'
  AND labels.key = 'workload'
GROUP BY
  date, workload_type
ORDER BY
  date DESC, total_cost DESC
```

---

## Security & Compliance

### 1. Workload Identity

**Bind Kubernetes SA to GCP SA**:

```bash
# Create GCP service account
gcloud iam service-accounts create gke-training-sa \
  --display-name="GKE Training Service Account"

# Grant GCS access
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:gke-training-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Create Kubernetes SA
kubectl create serviceaccount training-sa -n ml-training

# Bind Workload Identity
gcloud iam service-accounts add-iam-policy-binding \
  gke-training-sa@${PROJECT_ID}.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[ml-training/training-sa]"

# Annotate Kubernetes SA
kubectl annotate serviceaccount training-sa \
  -n ml-training \
  iam.gke.io/gcp-service-account=gke-training-sa@${PROJECT_ID}.iam.gserviceaccount.com
```

### 2. Binary Authorization

**Policy** (only allow signed images):

```yaml
# binary-authorization-policy.yaml
admissionWhitelistPatterns:
  - namePattern: gcr.io/ShadowTag-production/*
defaultAdmissionRule:
  requireAttestationsBy:
    - projects/ShadowTag-production/attestors/image-signer
  evaluationMode: REQUIRE_ATTESTATION
  enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
```

**Apply**:

```bash
gcloud container binauthz policy import binary-authorization-policy.yaml
```

### 3. Network Policies

**Restrict GPU pod egress**:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: gpu-workload-policy
  namespace: ml-training
spec:
  podSelector:
    matchLabels:
      workload: training
  policyTypes:
    - Egress
  egress:
    # Allow GCS access
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: TCP
          port: 443
    # Allow internal cluster DNS
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
      ports:
        - protocol: UDP
          port: 53
```

---

## Migration Path

### Phase 1: Development Environment (Week 1-2)

```bash
# 1. Create dev cluster
gcloud container clusters create ShadowTag-dev-gpu \
  --region=us-central1 \
  --num-nodes=1 \
  --machine-type=e2-medium

# 2. Add single GPU node pool
gcloud container node-pools create dev-gpu-pool \
  --cluster=ShadowTag-dev-gpu \
  --machine-type=g2-standard-4 \
  --accelerator=type=nvidia-l4,count=1 \
  --num-nodes=1

# 3. Deploy sample workload
kubectl apply -f sample-inference.yaml

# 4. Validate GPU scheduling works
```

### Phase 2: Production Cluster (Week 3-4)

```bash
# 1. Create production cluster (see "Cluster Creation" section)
# 2. Add all node pools (inference, fine-tuning, training, spot)
# 3. Install GPU Operator
# 4. Configure monitoring
# 5. Set up Workload Identity
```

### Phase 3: Workload Migration (Week 5-6)

```bash
# 1. Migrate inference workloads
kubectl apply -f inference-deployments/ --namespace=production

# 2. Migrate training pipelines
kubectl apply -f training-jobs/ --namespace=ml-training

# 3. Set up CI/CD to deploy to GKE
# 4. Configure autoscaling
# 5. Enable cost tracking
```

### Phase 4: Optimization (Week 7-8)

```bash
# 1. Analyze 2-week cost data
# 2. Right-size node pools
# 3. Purchase committed use discounts if utilization >40%
# 4. Fine-tune autoscaling policies
# 5. Implement advanced monitoring
```

---

## Troubleshooting

### Issue 1: Pods Stuck in Pending (Insufficient GPUs)

**Symptom**:

```
kubectl describe pod <pod-name>
# Events: 0/5 nodes are available: 5 Insufficient nvidia.com/gpu
```

**Solution**:

```bash
# Check if GPU node pool has capacity
kubectl get nodes -l cloud.google.com/gke-accelerator

# Scale up node pool manually
gcloud container clusters resize ${CLUSTER_NAME} \
  --node-pool=inference-l4-pool \
  --num-nodes=5 \
  --region=${REGION}

# Or increase autoscaling max
gcloud container node-pools update inference-l4-pool \
  --cluster=${CLUSTER_NAME} \
  --enable-autoscaling \
  --max-nodes=20 \
  --region=${REGION}
```

### Issue 2: GPU Not Detected in Pod

**Symptom**:

```bash
kubectl exec <pod-name> -- nvidia-smi
# NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver
```

**Solution**:

```bash
# Check GPU Operator status
kubectl get pods -n gpu-operator

# Restart device plugin
kubectl delete pod -n gpu-operator -l app=nvidia-device-plugin-daemonset

# Verify node has GPUs
kubectl describe node <node-name> | grep nvidia.com/gpu
```

### Issue 3: High GPU Cost

**Symptom**: Monthly bill shows unexpected GPU charges

**Solution**:

```bash
# Check for idle GPU nodes
kubectl get nodes -l cloud.google.com/gke-accelerator -o json | \
  jq '.items[] | {name: .metadata.name, pods: (.status.allocatable."nvidia.com/gpu" | tonumber) - (.status.capacity."nvidia.com/gpu" | tonumber)}'

# Scale down unused node pools
gcloud container node-pools update <pool-name> \
  --cluster=${CLUSTER_NAME} \
  --num-nodes=0 \
  --region=${REGION}

# Review BigQuery cost data (see "Cost Attribution" section)
```

---

## Next Steps

### Immediate Actions (This Week)

- [ ] Review GKE cluster configuration requirements
- [ ] Provision VPC and subnets for private cluster
- [ ] Create GCP service accounts for Workload Identity
- [ ] Request GPU quota increase (if needed)
- [ ] Set up billing exports to BigQuery

### Week 1-2: Development Environment

- [ ] Create dev GKE cluster with single GPU node
- [ ] Install GPU Operator
- [ ] Deploy sample inference workload
- [ ] Validate GPU scheduling and monitoring

### Week 3-4: Production Cluster

- [ ] Create production GKE cluster
- [ ] Configure all GPU node pools
- [ ] Set up Vertex AI integration
- [ ] Implement security policies

### Week 5-6: Workload Migration

- [ ] Migrate inference services to GKE
- [ ] Migrate training pipelines
- [ ] Configure CI/CD for GKE deployments
- [ ] Enable cost tracking dashboards

---

## Appendix

### GPU Types Available on GCP

| GPU Type             | Memory | Use Case                  | GCP Machine Family | Approx. Cost/hr |
| -------------------- | ------ | ------------------------- | ------------------ | --------------- |
| **NVIDIA L4**        | 24GB   | Inference, video          | g2-standard        | $0.70           |
| **NVIDIA T4**        | 16GB   | Inference, light training | n1-standard        | $0.40           |
| **NVIDIA V100**      | 16GB   | Training, inference       | n1-standard        | $2.50           |
| **NVIDIA A100 40GB** | 40GB   | Training, fine-tuning     | a2-highgpu         | $3.00           |
| **NVIDIA A100 80GB** | 80GB   | Large model training      | a2-ultragpu        | $3.50           |
| **NVIDIA H100**      | 80GB   | Peak performance          | a3-highgpu         | $5.00           |

### GCP Regions with GPU Availability

| Region          | A100 | H100 | L4  | Notes             |
| --------------- | ---- | ---- | --- | ----------------- |
| us-central1     | ✅   | ✅   | ✅  | Best availability |
| us-east1        | ✅   | ❌   | ✅  | Good availability |
| us-west1        | ✅   | ❌   | ✅  | Limited H100      |
| europe-west4    | ✅   | ✅   | ✅  | EU region         |
| asia-southeast1 | ✅   | ❌   | ✅  | APAC region       |

### Related Documents

- [GPU Infrastructure Strategy](./gpu-infrastructure-strategy.md)
- [GPU TCO Analysis](./gpu-tco-analysis.md)
- [GPU Compute Configuration](../../config/gpu-compute-config.yaml)
- [Tech Blueprint](./tech-blueprint-completion.md)

### External Resources

- [GKE GPU Documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/gpus)
- [NVIDIA GPU Operator](https://docs.nvidia.com/datacenter/cloud-native/gpu-operator/getting-started.html)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)

---

**Document Status**: ✅ Ready for Implementation
**Last Updated**: 2025-11-17
**Owner**: Platform Engineering Team
**Reviewers**: ML Platform, DevOps, FinOps
