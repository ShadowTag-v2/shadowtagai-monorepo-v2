# pnkln Judge #6 - GKE Inference Validation Sprint

## Executive Summary

**Objective**: Validate Google Cloud's GKE inference reference architecture against pnkln's strict latency SLA for Judge #6 hybrid governance enforcement.

**Success Criteria**: p99 latency ≤ 90ms for 3-layer hybrid decision pipeline
**Budget**: $5,000 (2-week sprint cap)
**KILL SWITCH**: If p99 > 90ms after 1 week, abort and pivot to ground-up architecture

---

## Architecture Overview

### Judge #6 Hybrid 3-Layer Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Request                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Orchestrator (LangGraph State)                  │
│              Target: Total p99 ≤ 90ms                        │
└─┬─────────────┬─────────────┬─────────────────────────────┬─┘
  │             │             │                               │
  ▼             ▼             ▼                               ▼
┌────────┐  ┌──────────┐  ┌─────────┐                  ┌──────────┐
│ Layer 1│  │ Layer 2  │  │ Layer 3 │                  │ Circuit  │
│ Gemini │  │ PyTorch  │  │  Rules  │                  │ Breaker  │
│ Policy │  │Enforcer  │  │ Engine  │                  │          │
│≤30ms   │  │≤40ms     │  │≤10ms    │                  │≤100ms    │
└────────┘  └──────────┘  └─────────┘                  └──────────┘
     │             │             │                               │
     └─────────────┴─────────────┴───────────────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │   Final Decision     │
                    │   APPROVE / DENY     │
                    └──────────────────────┘
```

### Component Stack

| Component | Technology | SLA Contribution | Scaling Strategy |
|-----------|-----------|------------------|------------------|
| **Layer 1: Gemini** | Vertex AI Gemini 1.5 Pro (tuned) | ≤30ms p99 | GPU node pool (L4) |
| **Layer 2: PyTorch** | Custom enforcement model | ≤40ms p99 | Shared GPU |
| **Layer 3: Rules** | Deterministic logic | ≤10ms p99 | CPU-only |
| **Orchestrator** | LangGraph + FastAPI | ≤10ms overhead | HPA on latency |
| **Infrastructure** | GKE Autopilot + Vertex AI | - | Auto-scaling |

---

## Deployment Guide

### Prerequisites

- GCP project with billing enabled
- Owner or Editor IAM role
- `gcloud` CLI installed and authenticated
- `kubectl` installed
- Budget alert configured at $4K (80% threshold)

### Step 1: Infrastructure Bootstrap

```bash
# Set environment variables
export GCP_PROJECT_ID="pnkln-validation"
export GCP_REGION="us-central1"

# Run bootstrap script
cd infrastructure
./pnkln-gke-bootstrap.sh

# Expected duration: 15-20 minutes
# This will create:
# - GKE Autopilot cluster
# - VPC network with subnets
# - Workload Identity bindings
# - Vertex AI Workbench instance
```

### Step 2: Deploy Judge #6 Components

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/judge/configmap.yaml
kubectl apply -f k8s/judge/rules-config.yaml
kubectl apply -f k8s/judge/deployment.yaml
kubectl apply -f k8s/judge/hpa.yaml
kubectl apply -f k8s/judge/pdb.yaml

# Verify deployment
kubectl get pods -n pnkln-core
kubectl get hpa -n pnkln-core

# Expected: 3 replicas of judge-6-hybrid running
```

### Step 3: Deploy Monitoring Stack

```bash
# Install Prometheus (if not using GKE-managed Prometheus)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n pnkln-monitoring \
  --create-namespace

# Apply monitoring configuration
kubectl apply -f k8s/monitoring/prometheus-servicemonitor.yaml
kubectl apply -f k8s/monitoring/prometheus-rules.yaml

# Import Grafana dashboard
kubectl port-forward -n pnkln-monitoring svc/prometheus-grafana 3000:80
# Navigate to localhost:3000, import k8s/monitoring/grafana-dashboard.json
```

### Step 4: Run Validation Workload

```bash
# Install Python dependencies
cd src/workload-generator
pip install -r requirements.txt

# Configure workload
export JUDGE_ENDPOINT="http://judge-6-service.pnkln-core.svc.cluster.local"
export WORKLOAD_DURATION_SEC=3600  # 1 hour
export BASE_RPS=10
export PEAK_RPS=50
export BURST_RPS=100

# Run synthetic workload
python synthetic_workload.py

# Monitor in real-time
../scripts/monitor-sla.sh
```

---

## Validation Test Plan

### Phase 1: Ramp-Up (Week 1, Days 1-2)

**Objective**: Establish baseline performance under light load

| Metric | Target | Test Duration |
|--------|--------|---------------|
| Request Rate | 10 req/s | 6 hours |
| p99 Latency | ≤90ms | Continuous |
| Error Rate | <1% | Continuous |
| GPU Utilization | 30-50% | Continuous |

**Success Criteria**:
- ✓ p99 ≤ 90ms for 95% of test duration
- ✓ Error rate < 1%
- ✓ No circuit breaker trips

### Phase 2: Steady State (Week 1, Days 3-5)

**Objective**: Validate sustained performance under target load

| Metric | Target | Test Duration |
|--------|--------|---------------|
| Request Rate | 50 req/s | 48 hours |
| p99 Latency | ≤90ms | Continuous |
| Error Rate | <1% | Continuous |
| GPU Utilization | 60-80% | Continuous |
| HPA Scaling | 3-12 replicas | Automatic |

**Success Criteria**:
- ✓ p99 ≤ 90ms for 99% of test duration
- ✓ HPA scaling responsive (<2 min)
- ✓ No OOM errors
- ✓ Cost burn rate ≤ $350/day

### Phase 3: Burst Mode (Week 1, Days 6-7)

**Objective**: Test resilience under peak traffic

| Metric | Target | Test Duration |
|--------|--------|---------------|
| Request Rate | 100 req/s | 4 hours |
| p99 Latency | ≤90ms | Continuous |
| Error Rate | <5% (acceptable degradation) | Continuous |
| GPU Utilization | 80-95% | Continuous |
| HPA Scaling | Up to 20 replicas | Automatic |

**Success Criteria**:
- ✓ p99 ≤ 90ms during burst
- ✓ No pod crashes
- ✓ Circuit breaker activates gracefully if needed
- ✓ Recovery time < 60s after burst

### Phase 4: Kill Switch Evaluation (Week 1, End)

**Decision Point**: PROCEED or ABORT

```
IF p99 ≤ 90ms for ≥95% of Phase 1-3:
    → PROCEED to Week 2 (Architecture Customization)
ELSE:
    → ABORT validation sprint
    → Pivot to ground-up Hypercomputer architecture
    → Document lessons learned
```

### Phase 5: Architecture Customization (Week 2)

**Only execute if Week 1 passes kill switch evaluation**

- Strip KServe to bare Triton + custom logic
- Implement LangGraph state persistence (Cloud Firestore)
- Deploy ShadowTag watermarking at egress
- Integrate NS mesh routing as sidecar
- Re-validate SLA compliance

---

## Monitoring & Alerts

### Real-Time SLA Monitoring

```bash
# Continuous monitoring (run in background)
watch -n 10 ./scripts/monitor-sla.sh

# View Grafana dashboard
kubectl port-forward -n pnkln-monitoring svc/prometheus-grafana 3000:80
# Navigate to: http://localhost:3000/dashboards
```

### Alert Channels

| Alert | Severity | Trigger | Action |
|-------|----------|---------|--------|
| p99 > 90ms for 2min | Critical | SLA breach | Scale up immediately |
| p95 > 60ms for 5min | Warning | Approaching SLA | Investigate layer latency |
| Error rate > 5% | Critical | High failures | Check layer health |
| Circuit breaker trips > 10 in 5min | Warning | Layer timeouts | Increase timeouts or scale |
| Cost > $4K | Critical | Budget alert | Review resource usage |
| GPU util < 30% for 15min | Info | Underutilization | Scale down |

### Key Metrics to Monitor

```promql
# p99 Latency (critical)
histogram_quantile(0.99,
  sum(rate(judge_request_duration_seconds_bucket[1m])) by (le)
)

# Layer breakdown
histogram_quantile(0.99,
  sum(rate(judge_layer_duration_seconds_bucket{layer="gemini"}[1m])) by (le)
)

# Error rate
sum(rate(judge_request_errors_total[5m]))
/
sum(rate(judge_request_total[5m]))

# GPU utilization
avg(nvidia_gpu_duty_cycle{namespace="pnkln-core"})
```

---

## Cost Management

### Budget Breakdown

| Resource | Daily Cost | 2-Week Total | Notes |
|----------|-----------|--------------|-------|
| GKE Autopilot | $50 | $700 | Control plane + base nodes |
| GPU Nodes (L4) | $150 | $2,100 | 3-8 nodes @ $0.85/hr |
| Vertex AI Inference | $80 | $1,120 | Gemini API calls |
| Networking | $20 | $280 | Egress + load balancing |
| Storage | $10 | $140 | Persistent volumes |
| Monitoring | $15 | $210 | Prometheus + logging |
| **Buffer** | $35 | $450 | 10% contingency |
| **TOTAL** | **$360** | **$5,000** | |

### Cost Monitoring

```bash
# Check current spend
./scripts/cost-tracker.sh

# Set up budget alert (one-time)
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="pnkln Validation Sprint" \
  --budget-amount=5000 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100
```

### Cost Optimization Tips

1. **Scale down overnight** (if not running 24/7 tests):
   ```bash
   kubectl scale deployment judge-6-hybrid -n pnkln-core --replicas=1
   ```

2. **Use preemptible GPU nodes** (50% cost reduction, but less reliable):
   ```bash
   # Add to GKE node pool config
   --preemptible
   ```

3. **Enable GKE cluster autoscaling** to zero (Autopilot limitation):
   ```bash
   # Autopilot auto-scales, but won't go to zero
   # Manually delete deployment if pausing for >6 hours
   ```

---

## Troubleshooting

### Common Issues

#### 1. Pods stuck in "Pending" state

**Symptom**: `kubectl get pods -n pnkln-core` shows pods pending
**Cause**: GPU node pool not ready or quota exceeded
**Fix**:
```bash
# Check GPU quota
gcloud compute project-info describe --project=PROJECT_ID

# Request quota increase if needed
# https://console.cloud.google.com/iam-admin/quotas

# Verify GPU nodes
kubectl get nodes -l cloud.google.com/gke-accelerator=nvidia-l4
```

#### 2. p99 latency > 90ms

**Symptom**: SLA breach in monitoring
**Cause**: Layer timeout or insufficient scaling
**Fix**:
```bash
# Check layer latency breakdown
./scripts/monitor-sla.sh

# Identify slow layer, then:
# Option 1: Increase layer timeout
kubectl edit configmap judge-6-config -n pnkln-core

# Option 2: Scale up replicas
kubectl scale deployment judge-6-hybrid -n pnkln-core --replicas=8

# Option 3: Check Gemini quota
gcloud alpha services quota list \
  --service=aiplatform.googleapis.com \
  --filter="metric.type=aiplatform.googleapis.com/quota/online_prediction_requests_per_base_model"
```

#### 3. High error rate (>5%)

**Symptom**: `ERROR_RATE > 5%` in monitoring
**Cause**: Circuit breaker tripping or layer failures
**Fix**:
```bash
# Check pod logs
kubectl logs -n pnkln-core deployment/judge-6-hybrid -c gemini-layer --tail=100
kubectl logs -n pnkln-core deployment/judge-6-hybrid -c pytorch-enforcer --tail=100
kubectl logs -n pnkln-core deployment/judge-6-hybrid -c rules-engine --tail=100

# Check circuit breaker trips
kubectl logs -n pnkln-core deployment/judge-6-hybrid -c orchestrator | grep "Circuit breaker"
```

#### 4. Budget exceeded

**Symptom**: Cost tracker script exits with code 2
**Cause**: Over-provisioned resources or long-running tests
**Fix**:
```bash
# Immediate actions:
# 1. Scale down to minimum
kubectl scale deployment judge-6-hybrid -n pnkln-core --replicas=1

# 2. Delete expensive resources
kubectl delete deployment judge-6-hybrid -n pnkln-core

# 3. (If aborting) Delete entire cluster
gcloud container clusters delete pnkln-core-stack --region=us-central1
```

---

## Success Metrics & Decision Framework

### Week 1 Kill Switch Decision Tree

```
┌─────────────────────────────────────┐
│   Week 1 Testing Complete           │
└────────────┬────────────────────────┘
             │
             ▼
      ┌──────────────┐
      │ p99 ≤ 90ms?  │
      └──┬───────┬───┘
         │       │
         ▼       ▼
        YES     NO
         │       │
         │       ├─► ABORT ────► Document Findings
         │       │                │
         │       │                ▼
         │       │           Pivot to Ground-Up
         │       │           Hypercomputer Build
         │       │
         ▼       ▼
    Cost ≤ $2.5K?
         │
    ┌────┼────┐
    │         │
   YES       NO
    │         │
    │         ├─► CONDITIONAL PROCEED
    │         │   (Optimize costs Week 2)
    │         │
    ▼         ▼
PROCEED ───► Week 2: Architecture Customization
    │
    ▼
Implement:
- LangGraph persistence
- ShadowTag watermarking
- NS mesh integration
```

### Final Recommendation Criteria

| Criterion | Weight | Pass Threshold |
|-----------|--------|----------------|
| **p99 Latency** | 50% | ≤90ms for 95% of time |
| **p95 Latency** | 20% | ≤60ms for 98% of time |
| **Error Rate** | 15% | <1% average |
| **Cost Efficiency** | 10% | ≤$2,500 for Week 1 |
| **Scalability** | 5% | HPA responsive (<2min) |

**Weighted Score Calculation**:
- Score ≥ 80%: **STRONG PROCEED** → Continue to production deployment
- Score 60-79%: **CONDITIONAL PROCEED** → Address gaps in Week 2
- Score < 60%: **ABORT** → Pivot to ground-up architecture

---

## Next Steps After Validation

### If PROCEED:

1. **Week 2 Customization**:
   - Fork Google ref-arch repo
   - Strip unnecessary components (KServe, etc.)
   - Integrate pnkln-specific components
   - Re-validate SLA compliance

2. **Production Readiness**:
   - Multi-region deployment
   - Disaster recovery plan
   - Security hardening (VPC-SC, Binary Authorization)
   - CI/CD pipeline setup

3. **Cost Optimization**:
   - Reserved GPU capacity (40% discount)
   - Committed use discounts
   - Right-size instance types

### If ABORT:

1. **Document Learnings**:
   - What caused SLA breach? (Gemini latency? PyTorch? Orchestration overhead?)
   - What would need to change for Google ref-arch to work?
   - Cost analysis: Was budget realistic?

2. **Pivot to Ground-Up Build**:
   - Design custom inference stack on Hypercomputer
   - A3 Mega instances (H100 8x NVLink)
   - Custom scheduler for parallel layer execution
   - Direct Vertex AI SDK integration (skip KServe)

3. **Timeline Adjustment**:
   - Ground-up: +6 weeks vs. ref-arch fork
   - Budget: +$15K for R&D phase

---

## References

- [Google GKE Inference Reference Architecture](https://github.com/GoogleCloudPlatform/accelerated-platforms/blob/main/docs/platforms/gke/base/use-cases/inference-ref-arch/README.md)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [GKE Autopilot GPU Support](https://cloud.google.com/kubernetes-engine/docs/how-to/autopilot-gpus)
- [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

---

## Contact & Support

**Sprint Lead**: [Your Name]
**Budget Owner**: [Finance Contact]
**Technical Escalation**: [CTO/Tech Lead]
**GCP Support**: Enterprise Support (if applicable)

**Slack Channels**:
- `#pnkln-validation-sprint` - Daily updates
- `#pnkln-sre` - Infrastructure issues
- `#pnkln-incidents` - SLA breaches / budget alerts
