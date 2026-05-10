# Judge 6 Integration: GKE Inference Deployment

This document outlines how the GKE inference deployment scripts integrate with the Judge 6 framework for AI/ML decision-making and governance.

## Judge 6 Framework Overview

Judge 6 implements a systematic approach to complex decisions:

```
PURPOSE → REASONS → BRAKES → PRECISION → EXECUTION
```

Applied to GKE inference deployment:

1. **PURPOSE**: Deploy scalable, cost-effective AI inference
2. **REASONS**: Performance, reliability, observability requirements
3. **BRAKES**: Resource limits, cost constraints, security policies
4. **PRECISION**: Exact GPU types, model sizes, scaling parameters
5. **EXECUTION**: Automated deployment with verification

## Architecture Alignment

### 1. Purpose-Driven Design

Each script has a clear, singular purpose:

| Script | Purpose |
|--------|---------|
| 00-setup-environment.sh | Configure deployment environment |
| 01-enable-gcp-services.sh | Enable required GCP APIs |
| 02-setup-infrastructure.sh | Provision GKE cluster and storage |
| 03-setup-huggingface.sh | Secure model access credentials |
| 04-download-model.sh | Retrieve models to Cloud Storage |
| 05-deploy-vllm-inference.sh | Deploy inference workload |
| 06-test-inference.sh | Validate deployment health |
| 07-monitor-deployment.sh | Continuous observability |
| 99-cleanup.sh | Resource cleanup and cost control |

### 2. Reason-Based Configuration

The scripts enforce explicit reasoning for configuration choices:

```bash
# GPU Selection Matrix (Reason: Performance vs. Cost)
case "${ACCELERATOR_TYPE}" in
    "l4")   # Reason: Cost-effective for <32B models
        MACHINE_TYPE="g2-standard-96"
        ;;
    "h100") # Reason: High performance for all models
        MACHINE_TYPE="a3-highgpu-1g"
        ;;
    "h200") # Reason: Maximum memory for frontier models
        MACHINE_TYPE="a3-ultragpu-8g"
        ;;
esac
```

### 3. Brake Mechanisms

Built-in constraints prevent over-provisioning:

**Cost Brakes:**
```bash
# HPA limits prevent runaway scaling
maxReplicas: 5  # Brake: Max 5 instances
behavior:
  scaleUp:
    periodSeconds: 180  # Brake: Gradual scale-up
```

**Resource Brakes:**
```bash
# Quota checks before deployment
GPU_QUOTA=$(gcloud compute project-info describe \
    --format="value(quotas.filter(metric:NVIDIA_H100).limit)")

if [ "$GPU_QUOTA" -lt "$REQUIRED_GPUS" ]; then
    echo "BRAKE: Insufficient GPU quota"
    exit 1
fi
```

**Security Brakes:**
```bash
# Workload Identity enforcement
if ! kubectl get sa model-downloader -n model-download &>/dev/null; then
    echo "BRAKE: Service account not configured"
    exit 1
fi
```

### 4. Precision Requirements

The deployment enforces exact specifications:

```yaml
# Exact GPU requirements
resources:
  requests:
    nvidia.com/gpu: "8"  # Precise count, not approximate
  limits:
    nvidia.com/gpu: "8"  # Hard limit enforced

nodeSelector:
  cloud.google.com/gke-accelerator: nvidia-l4  # Exact GPU type
```

### 5. Execution Verification

Every step includes verification:

```bash
# Pattern: Action → Verify → Proceed
gcloud services enable compute.googleapis.com

# Verify enablement
if gcloud services list --enabled | grep -q compute.googleapis.com; then
    echo "✓ Service enabled"
else
    echo "✗ Enablement failed"
    exit 1
fi
```

## Judge 6 Decision Points

### Decision Point 1: Cluster Mode Selection

**PURPOSE**: Balance management overhead vs. control

**REASONS**:
- Autopilot: Fully managed, optimized resource utilization
- Standard: Fine-grained control, custom node configurations

**BRAKES**:
- Autopilot: Cannot customize node OS, kernel versions
- Standard: Requires ongoing cluster management

**PRECISION**:
```bash
if [ "$CLUSTER_MODE" = "autopilot" ]; then
    gcloud container clusters create-auto "${CLUSTER_NAME}" \
        --region="${REGION}" \
        --enable-autoscaling \
        # ... precise autopilot flags
else
    gcloud container clusters create "${CLUSTER_NAME}" \
        --machine-type=n1-standard-4 \
        --min-nodes=1 \
        --max-nodes=10 \
        # ... precise standard flags
fi
```

**EXECUTION**: Cluster creation with 30-minute timeout and health checks

### Decision Point 2: GPU Accelerator Selection

**PURPOSE**: Optimize performance per dollar

**REASONS**:
| GPU | Use Case | Performance | Cost |
|-----|----------|-------------|------|
| L4 | <32B models | Good | $$ |
| H100 | All models | Excellent | $$$ |
| H200 | Frontier models | Maximum | $$$$ |

**BRAKES**:
- Model size limits per GPU memory
- Quota availability checks
- Cost per hour thresholds

**PRECISION**:
```bash
# Model-GPU compatibility matrix
MODEL_GPU_MATRIX=(
    "gemma-3-1b-it:l4"
    "gemma-3-27b-it:l4,h100,h200"
    "llama-3.3-70b:h100,h200"  # NOT l4
)
```

**EXECUTION**: Automated GPU selection with validation

### Decision Point 3: Scaling Configuration

**PURPOSE**: Match capacity to demand

**REASONS**:
- HPA metrics: CPU, memory, custom inference metrics
- Scale-up speed: Balance responsiveness vs. cost
- Scale-down delay: Avoid flapping

**BRAKES**:
```yaml
spec:
  minReplicas: 1              # Brake: Always >= 1 for availability
  maxReplicas: 5              # Brake: Cost control
  behavior:
    scaleUp:
      periodSeconds: 180      # Brake: Gradual increase
    scaleDown:
      stabilizationWindowSeconds: 300  # Brake: Prevent flapping
```

**PRECISION**:
```yaml
metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Precise threshold
```

**EXECUTION**: Real-time HPA monitoring and adjustment

### Decision Point 4: Model Storage Strategy

**PURPOSE**: Fast model loading, cost-effective storage

**REASONS**:
- Cloud Storage: Scalable, durable, multi-region
- GCS FUSE: Direct mounting in pods
- Cache configuration: Balance speed vs. memory

**BRAKES**:
- Storage class: Regional (not multi-region) for cost
- Lifecycle policies: Delete old versions after 30 days
- Cache size limits: Max 100GB per pod

**PRECISION**:
```yaml
volumeAttributes:
  bucketName: ${MODEL_BUCKET}
  mountOptions: "implicit-dirs,max-conns-per-host=100"
  fileCacheCapacity: "100Gi"          # Precise cache size
  fileCacheForRangeRead: "true"
  metadataStatCacheCapacity: "50000"  # Precise metadata cache
```

**EXECUTION**: Automated bucket creation with lifecycle policies

## Integration with Judge 6 Principles

### 1. Bootstrap Discipline

**Apply**: Clone only required repos, not all 440+ GCP repos

```bash
# Selective clone (Judge 6 aligned)
git clone --depth=1 \
  https://github.com/GoogleCloudPlatform/accelerated-platforms.git

# NOT: Bulk clone all GoogleCloudPlatform repos
```

### 2. Productive Paranoia

**Apply**: Verify every step, fail fast on errors

```bash
set -euo pipefail  # Fail on any error

# Verify before proceeding
check_quota() {
    local required=$1
    local available=$(get_gpu_quota)

    if [ "$available" -lt "$required" ]; then
        echo "PARANOIA CHECK FAILED: Insufficient quota"
        echo "Required: $required, Available: $available"
        exit 1
    fi
}
```

### 3. Zoom In/Zoom Out

**Apply**: Monitor at multiple levels

```bash
# Zoom Out: Cluster-level metrics
kubectl top nodes

# Zoom In: Pod-level metrics
kubectl top pod -n inference-online-gpu

# Zoom In Further: Container-level GPU metrics
kubectl exec <pod> -- nvidia-smi
```

### 4. Empirical Evidence

**Apply**: Test-driven deployment

```bash
# Evidence: Actual inference test
curl http://localhost:8000/v1/chat/completions \
  -d '{"model": "...", "messages": [...]}' | \
  jq '.choices[0].message.content'

# NOT: Assume deployment works without testing
```

## Judge 6 Audit Checklist

Before deployment, verify:

- [ ] **PURPOSE**: Deployment goals clearly defined
- [ ] **REASONS**: GPU type justified by model requirements
- [ ] **BRAKES**: Cost limits, quota checks, security policies in place
- [ ] **PRECISION**: Exact resource requests/limits specified
- [ ] **EXECUTION**: Automated testing validates deployment

During deployment:

- [ ] Each script exits with status code indicating success/failure
- [ ] Verification steps confirm expected state before proceeding
- [ ] Resource creation logged with timestamps
- [ ] Error messages provide actionable guidance

After deployment:

- [ ] Inference tests pass with acceptable latency
- [ ] GPU utilization matches expectations
- [ ] Cost per request calculated and within budget
- [ ] Monitoring dashboards show healthy metrics

## Judge 6 Decision Log

Track deployment decisions in structured format:

```bash
# Example decision log entry
cat >> deployment-decisions.log << EOF
---
Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Decision: GPU Selection for Gemma 3 27B
Purpose: Cost-effective inference for 27B model
Reasons:
  - Model size: 27B parameters
  - Expected QPS: 10-50 requests/sec
  - Budget constraint: <$10k/month
Options Considered:
  1. L4 x8: $8,760/month, adequate performance
  2. H100 x1: $10,950/month, better performance
  3. H200 x1: $15,330/month, overkill for requirements
Brakes Applied:
  - Budget cap: $10k/month → Rules out H200
  - Performance requirement: p99 < 2s → Rules out CPU-only
Selected: L4 x8 (g2-standard-96)
Precision:
  - Exact GPU count: 8x NVIDIA L4
  - Machine type: g2-standard-96
  - Tensor parallel size: 8
Verification:
  - Quota check: ✓ 8 L4 GPUs available
  - Cost estimate: $8,760/month ✓
  - Latency test: p99 = 1.2s ✓
EOF
```

## Integration with ShadowTag-v2 Platform

The GKE inference deployment integrates with ShadowTag-v2's FastAPI services:

```python
# shadowtag_v4-fastapi-services/app/services/inference_client.py

class GKEInferenceClient:
    """
    Client for GKE-deployed inference workloads.
    Applies Judge 6 framework for request routing.
    """

    def select_endpoint(self, model_id: str, requirements: InferenceRequirements):
        """
        PURPOSE: Route request to optimal endpoint
        REASONS: Latency, cost, availability
        BRAKES: Rate limits, cost budgets
        PRECISION: Exact endpoint selection
        EXECUTION: Request with timeout and retry
        """
        # Judge 6 decision logic here
        pass
```

## Conclusion

The GKE inference deployment scripts embody Judge 6 principles:

1. **Purpose-driven**: Each component has clear objectives
2. **Reason-based**: Decisions backed by performance/cost data
3. **Brake-enabled**: Built-in constraints prevent errors
4. **Precision-focused**: Exact specifications, no approximations
5. **Execution-verified**: Automated testing validates success

This alignment ensures the deployment is:
- **Reliable**: Systematic verification at each step
- **Cost-effective**: Brakes prevent over-provisioning
- **Maintainable**: Clear purpose for each component
- **Auditable**: Decision logs track rationale

## References

- GoogleCloudPlatform/accelerated-platforms: [inference-ref-arch](https://github.com/GoogleCloudPlatform/accelerated-platforms/tree/main/docs/platforms/gke/base/use-cases/inference-ref-arch)
- Judge 6 Framework: See project documentation
- ShadowTag-v2 Platform: FastAPI services integration
