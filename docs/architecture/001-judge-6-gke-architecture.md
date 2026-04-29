# Architecture Design: Judge 6 on GKE with Vertex AI

## Status

**PROPOSED** - Ready for implementation

## Date

2025-11-07

## Executive Summary

Production-ready inference architecture for deploying Judge 6 (Pnkln's AI governance agent) on Google Kubernetes Engine with Vertex AI integration, LangGraph orchestration, and Document AI for AiURCM compliance automation.

**Key Performance Targets:**

- **Cost Reduction**: >30% vs. baseline deployment
- **Latency**: 60% reduction in tail latency (p99)
- **Throughput**: 40% increase via optimized batching
- **Availability**: 99.9% uptime with auto-healing

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PNKLN CORE STACK                             │
│                    Judge 6 Inference System                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Client     │
│ Application  │──────┐
└──────────────┘      │
                      │
┌──────────────┐      │         ┌─────────────────────────────┐
│  Document    │      │         │   GKE INFERENCE GATEWAY      │
│  Storage     │──────┼────────>│  (Gen-AI Aware LB)          │
│ (Cloud       │      │         │  - Prefix-aware routing      │
│  Storage)    │      │         │  - KV cache optimization     │
└──────────────┘      │         │  - Traffic splitting         │
                      │         └──────────┬──────────────────┘
┌──────────────┐      │                    │
│  Document AI │      │                    │
│  Processors  │──────┘                    │
└──────────────┘                           │
                                           ▼
                    ┌────────────────────────────────────────┐
                    │      GKE AUTOPILOT CLUSTER             │
                    │                                        │
                    │  ┌──────────────────────────────────┐ │
                    │  │   LangGraph Orchestrator Pod     │ │
                    │  │   (Supervisor Pattern)           │ │
                    │  │                                  │ │
                    │  │   ┌──────────────────────────┐  │ │
                    │  │   │  Judge 6 Coordinator    │  │ │
                    │  │   │  (State Graph Manager)   │  │ │
                    │  │   └──────────┬───────────────┘  │ │
                    │  │              │                  │ │
                    │  │    ┌─────────┴─────────┐       │ │
                    │  │    ▼         ▼         ▼       │ │
                    │  │  ┌────┐   ┌────┐   ┌────┐     │ │
                    │  │  │J#6 │   │J#6 │   │J#6 │     │ │
                    │  │  │ A  │   │ B  │   │ C  │     │ │
                    │  │  └────┘   └────┘   └────┘     │ │
                    │  │  Specialist Agents             │ │
                    │  └──────────────────────────────────┘ │
                    │                                        │
                    │  ┌──────────────────────────────────┐ │
                    │  │   Vertex AI Model Serving Pods   │ │
                    │  │                                  │ │
                    │  │   ┌────────────────────────┐    │ │
                    │  │   │  vLLM Server (Primary) │    │ │
                    │  │   │  - Gemini 2.0 Flash    │    │ │
                    │  │   │  - PagedAttention      │    │ │
                    │  │   │  - Dynamic Batching    │    │ │
                    │  │   └────────────────────────┘    │ │
                    │  │                                  │ │
                    │  │   ┌────────────────────────┐    │ │
                    │  │   │  Model Weights Storage │    │ │
                    │  │   │  (Cloud Storage FUSE)  │    │ │
                    │  │   │  - Parallel downloads  │    │ │
                    │  │   │  - Image streaming     │    │ │
                    │  │   └────────────────────────┘    │ │
                    │  └──────────────────────────────────┘ │
                    │                                        │
                    │  ┌──────────────────────────────────┐ │
                    │  │   Horizontal Pod Autoscaler      │ │
                    │  │   (Custom Metrics)               │ │
                    │  │   - QPS-based scaling            │ │
                    │  │   - Latency-based scaling        │ │
                    │  │   - GPU utilization              │ │
                    │  └──────────────────────────────────┘ │
                    └────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌────────────────────────────────────────┐
                    │   Google Cloud Observability           │
                    │   - Cloud Monitoring                   │
                    │   - Cloud Logging                      │
                    │   - Cloud Trace                        │
                    └────────────────────────────────────────┘
```

---

## Component Design

### 1. GKE Infrastructure Layer

#### 1.1 Cluster Configuration

**Mode**: GKE Autopilot

- **Rationale**: Offload node management to Google Cloud, reduce operational overhead
- **Benefits**:
  - Automatic node provisioning and scaling
  - Built-in security best practices
  - No manual node pool management
  - Cost optimization (pay only for pod resources)

**Security**:

- Private cluster (no public IP on nodes)
- Shielded GKE Nodes (Secure Boot, vTPM, integrity monitoring)
- Workload Identity for service authentication
- Binary Authorization for container image validation

**Networking**:

- VPC-native cluster with alias IPs
- Network policies for pod-to-pod communication
- Private Google Access for GCP API calls
- Cloud NAT for egress traffic

#### 1.2 Node Configuration

**Accelerators**:

- **GPU**: NVIDIA L4 GPUs for inference workloads
  - Optimized for LLM inference
  - Lower cost per inference vs. A100/H100
  - Tensor Core acceleration
- **TPU**: TPU v5e for batch processing (future)

**Compute Classes**:

- Custom compute classes for precise hardware matching
- Node Auto-Provisioning (NAP) for automatic resource allocation

**Storage**:

- **Cloud Storage FUSE**: Lazy-loading model weights
  - Parallel downloads
  - Local caching
  - Reduces pod start time by 70%
- **Hyperdisk ML** (alternative): Ultra-low latency persistent storage

### 2. Vertex AI Model Serving

#### 2.1 Model Server Architecture

**Primary Server**: vLLM

- **Version**: Latest Google custom image (us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20250202_0916_RC00)
- **Features**:
  - PagedAttention for efficient KV cache management
  - Continuous batching for throughput optimization
  - Tensor parallelism support for large models
  - OpenAI-compatible API

**Model Configuration**:

```yaml
Model: google/gemini-2.0-flash-thinking-exp-1219 # Judge 6 base model
Quantization: FP16 (baseline), INT8 (cost optimization)
Batch Size: Dynamic (adaptive to QPS)
Max Sequence Length: 32,768 tokens
KV Cache: PagedAttention with 90% GPU memory allocation
```

#### 2.2 Endpoint Strategy

**Deployment Pattern**: Multi-Model Single Endpoint

- Deploy Judge 6 variants to same endpoint
- Traffic splitting: 90% production / 10% canary
- Gradual rollout for model updates

**Endpoint Types**:

- **Dedicated Endpoint**: Judge 6 production traffic
- **Shared Endpoint**: Development/testing

**Scaling**:

- Min replicas: 2 (high availability)
- Max replicas: 20 (cost cap)
- Target QPS: 100 req/sec per replica

### 3. LangGraph Orchestration

#### 3.1 Multi-Agent Architecture

**Pattern**: Hierarchical Supervisor

```python
# State Graph Structure
class Cor.Claude_Code_6State(TypedDict):
    """Shared state across all Judge 6 agents"""
    document_id: str
    document_content: str
    compliance_framework: str  # FDA, SEC, ITAR, etc.
    extracted_policies: List[Dict]
    violations: List[Dict]
    recommendations: List[Dict]
    current_step: str
    agent_outputs: Dict[str, Any]

# Graph Definition
workflow = StateGraph(Cor.Claude_Code_6State)

# Nodes (Agents)
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("document_parser", document_parser_agent)
workflow.add_node("policy_extractor", policy_extractor_agent)
workflow.add_node("compliance_checker", compliance_checker_agent)
workflow.add_node("recommendation_engine", recommendation_engine_agent)

# Edges (Control Flow)
workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges(
    "supervisor",
    route_to_next_agent,  # Function determines next agent
    {
        "document_parser": "document_parser",
        "policy_extractor": "policy_extractor",
        "compliance_checker": "compliance_checker",
        "recommendation_engine": "recommendation_engine",
        "finish": END
    }
)
```

#### 3.2 Agent Specialization

| Agent                     | Responsibility                    | Model                     | Latency Budget |
| ------------------------- | --------------------------------- | ------------------------- | -------------- |
| **Supervisor**            | Orchestrate workflow, route tasks | Gemini 2.0 Flash          | <500ms         |
| **Document Parser**       | Extract structure from documents  | Gemini 2.0 Flash          | <2s            |
| **Policy Extractor**      | Identify compliance policies      | Gemini 2.0 Flash Thinking | <5s            |
| **Compliance Checker**    | Validate against frameworks       | Gemini 2.0 Flash          | <3s            |
| **Recommendation Engine** | Generate remediation steps        | Gemini 2.0 Flash Thinking | <5s            |

**Parallel Execution**:

- Document Parser + Policy Extractor (independent)
- Multiple Compliance Checkers (different frameworks)
- Scatter-gather pattern for comprehensive analysis

#### 3.3 State Management

**Persistence**:

- **In-Memory**: Redis for active workflows (<1hr TTL)
- **Durable**: Cloud Firestore for audit trail (permanent)
- **Checkpointing**: LangGraph built-in checkpointing for resume capability

**State Schema**:

```json
{
  "workflow_id": "uuid",
  "created_at": "timestamp",
  "status": "running|completed|failed",
  "state": {
    "document_id": "...",
    "current_step": "policy_extractor",
    "agent_outputs": {...}
  },
  "checkpoints": [
    {"step": "document_parser", "timestamp": "...", "state_snapshot": {...}}
  ]
}
```

### 4. Document AI Integration (AiURCM Pipeline)

#### 4.1 Processor Configuration

**Processor Types**:

1. **Document Classifier**: Route documents to correct compliance framework
   - Form Parser Processor
   - Custom trained classifier (future)
2. **Document OCR**: Extract text from PDFs/images
   - OCR Processor (General)
   - Specialized processors for forms
3. **Entity Extraction**: Identify key compliance entities
   - Custom Document Extractor

**Processing Flow**:

```
Cloud Storage → Document AI Processor → LangGraph Orchestrator → Judge 6
```

#### 4.2 Integration Architecture

**Trigger**: Cloud Storage bucket notification
**Workflow**:

1. Document uploaded to `gs://pnkln-compliance-docs/intake/`
2. Cloud Function triggered on object finalization
3. Document AI processes document (async)
4. Parsed output sent to Pub/Sub topic
5. LangGraph consumer picks up message
6. Judge 6 workflow initiated

**Code Structure**:

```python
# Cloud Function Handler
def process_document(event, context):
    """Triggered by Cloud Storage upload"""
    file_path = event['name']
    bucket = event['bucket']

    # Call Document AI
    doc_ai_result = document_ai_client.process_document(
        name=PROCESSOR_NAME,
        raw_document=RawDocument(
            content=storage_client.download_blob(bucket, file_path),
            mime_type='application/pdf'
        )
    )

    # Publish to Pub/Sub for LangGraph
    pubsub_client.publish(
        topic=LANGGRAPH_TOPIC,
        data=json.dumps({
            'document_id': file_path,
            'parsed_content': doc_ai_result.document.text,
            'entities': extract_entities(doc_ai_result),
            'framework': classify_framework(doc_ai_result)
        }).encode('utf-8')
    )
```

### 5. GKE Inference Gateway

#### 5.1 Load Balancing Strategy

**Features**:

- **Prefix-aware routing**: Cache KV pairs for repeated prefixes (96% TTFT improvement)
- **LoRA affinity**: Route requests to pods with specific fine-tuned adapters
- **Priority routing**: Critical compliance checks get priority lanes
- **Cross-regional failover**: Route to secondary region on failure

**Configuration**:

```yaml
apiVersion: networking.gke.io/v1
kind: InferenceGateway
metadata:
  name: judge-6-gateway
spec:
  routing:
    prefixCache:
      enabled: true
      maxCacheSize: 10GB
    priority:
      enabled: true
      levels:
        - name: critical
          weight: 100
        - name: standard
          weight: 50
    backends:
      - name: judge-6-primary
        weight: 90
      - name: judge-6-canary
        weight: 10
```

#### 5.2 Traffic Splitting

**Use Cases**:

- **A/B Testing**: 90/10 split for new Judge 6 versions
- **Multi-Model Serving**: Route by compliance framework
  - FDA → Judge 6 Pharma variant
  - SEC → Judge 6 Finance variant
- **Cost Optimization**: Route low-priority to INT8 quantized models

### 6. Scaling & Performance

#### 6.1 Horizontal Pod Autoscaler (HPA)

**Custom Metrics**:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: judge-6-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: judge-6-deployment
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Pods
      pods:
        metric:
          name: inference_qps
        target:
          type: AverageValue
          averageValue: "100" # 100 QPS per pod
    - type: Pods
      pods:
        metric:
          name: p99_latency_ms
        target:
          type: AverageValue
          averageValue: "500" # p99 < 500ms
    - type: External
      external:
        metric:
          name: pubsub.googleapis.com|subscription|num_undelivered_messages
          selector:
            matchLabels:
              resource.labels.subscription_id: judge-6-workqueue
        target:
          type: AverageValue
          averageValue: "100" # Max 100 queued per pod
```

**Scaling Behavior**:

- Scale up: Add pod when QPS >100 for 30s
- Scale down: Remove pod when QPS <50 for 5min (conservative)
- Cooldown: 3min between scale-up events

#### 6.2 Performance Benchmarks

**Target Metrics** (per-request):

- **TTFT**: <200ms (p50), <500ms (p99)
- **Inter-token Latency**: <20ms (p50), <50ms (p99)
- **Throughput**: 10,000 tokens/sec per pod
- **Cost**: <$0.005 per 1K tokens (vs. $0.015 API baseline)

**Optimization Techniques**:

1. **Quantization**: INT8 reduces cost by 40%, latency penalty <10%
2. **Batching**: Continuous batching improves throughput 3x
3. **KV Cache**: PagedAttention reduces memory by 50%
4. **Model Parallelism**: Tensor parallelism for >13B models

### 7. Observability & Monitoring

#### 7.1 Metrics Collection

**Infrastructure Metrics**:

- Node CPU/GPU utilization
- Pod memory/GPU memory
- Network I/O
- Disk I/O (model loading)

**Application Metrics**:

- Request rate (QPS)
- Latency (TTFT, inter-token, total)
- Error rate (4xx, 5xx)
- Token throughput

**Business Metrics**:

- Documents processed per hour
- Compliance violations detected
- Cost per document
- SLA adherence (99.9% uptime)

**Dashboards**:

- **Operations**: GKE cluster health, pod status, autoscaler behavior
- **Performance**: Latency heatmaps, throughput trends, error spikes
- **Business**: Document processing funnel, cost tracking, ROI metrics

#### 7.2 Logging Strategy

**Log Levels**:

- **DEBUG**: LangGraph state transitions, agent outputs
- **INFO**: Request/response, scaling events, model loads
- **WARN**: Latency degradation, rate limits approaching
- **ERROR**: Model failures, OOM errors, API errors

**Structured Logging**:

```json
{
  "timestamp": "2025-11-07T12:34:56Z",
  "severity": "INFO",
  "trace": "projects/pnkln/traces/abc123",
  "workflow_id": "wf-uuid",
  "agent": "policy_extractor",
  "event": "agent_completed",
  "duration_ms": 4235,
  "tokens_used": 8192,
  "cost_usd": 0.041
}
```

**Log Retention**:

- **Hot**: 30 days in Cloud Logging
- **Warm**: 1 year in Cloud Storage (compliance audit)
- **Cold**: 7 years in Cloud Storage Archive (regulatory)

#### 7.3 Tracing & Debugging

**Cloud Trace Integration**:

- End-to-end request tracing
- LangGraph agent call tree
- Model inference latency breakdown

**Trace Spans**:

```
Request → Document AI → Pub/Sub → LangGraph Orchestrator
  ├─ Supervisor Agent (50ms)
  ├─ Document Parser (1.8s)
  │  └─ Model Inference (1.6s)
  ├─ Policy Extractor (4.2s)
  │  └─ Model Inference (3.9s)
  └─ Compliance Checker (2.5s)
     └─ Model Inference (2.2s)
```

### 8. Security & Compliance

#### 8.1 Data Governance

**Encryption**:

- **At Rest**: Customer-managed encryption keys (CMEK)
- **In Transit**: TLS 1.3 for all communication
- **In Use**: Confidential GKE (future, for confidential computing)

**Access Control**:

- **IAM**: Least-privilege service accounts
- **Workload Identity**: Pod-level GCP authentication
- **Binary Authorization**: Only signed images deployed

**Audit**:

- **Cloud Audit Logs**: All API calls logged
- **Workflow Provenance**: Complete audit trail from intake → recommendation
- **Model Lineage**: Track which model version processed each document

#### 8.2 Compliance Certifications

**Required for AiURCM**:

- **SOC 2 Type II**: Google Cloud provides infrastructure certification
- **ISO 27001**: GKE and Vertex AI certified
- **HIPAA**: Business Associate Agreement (BAA) with Google
- **FedRAMP**: GCP FedRAMP Moderate (defense/government customers)
- **CMMC**: Self-attestation for Level 1, prep for Level 2

**Data Residency**:

- **US-only**: `us-central1` region for all data processing
- **EU**: `europe-west1` for EU customers (GDPR)
- **Sovereign**: GCP Assured Workloads for government

### 9. Cost Optimization

#### 9.1 Cost Model

**Infrastructure**:
| Component | Unit | Cost | Monthly (baseline) |
|-----------|------|------|--------------------|
| GKE Autopilot | vCPU-hour | $0.05 | $360 (2 pods × 24/7) |
| NVIDIA L4 GPU | GPU-hour | $0.85 | $1,224 (2 GPUs × 24/7) |
| Cloud Storage FUSE | GB-month | $0.02 | $20 (1TB models) |
| Egress | GB | $0.12 | $120 (1TB/month) |
| **Total** | | | **$1,724/month** |

**Model Inference**:
| Model | Cost per 1M tokens | Baseline | Self-hosted |
|-------|-------------------|----------|-------------|
| Gemini 2.0 Flash API | $15.00 | ✓ | |
| Self-hosted (FP16) | $5.00 | | ✓ |
| Self-hosted (INT8) | $3.00 | | ✓ |
| **Savings** | | | **67-80%** |

**Break-even Analysis**:

- Break-even at **115M tokens/month** (vs. API)
- AiURCM target: **500M tokens/month** → **$6K/month savings**

#### 9.2 Optimization Strategies

1. **Quantization**: INT8 for non-critical workloads (40% cost reduction)
2. **Spot VMs**: Use Spot for batch processing (60-90% discount)
3. **Autoscaling**: Scale to zero during off-hours (weekends)
4. **Model Caching**: Share base model across multiple LoRA adapters
5. **Request Batching**: Increase batch size during low-traffic periods

**Cost Alerts**:

- Budget alert at 80% of monthly forecast
- Anomaly detection for cost spikes
- Per-document cost tracking for ROI analysis

### 10. Disaster Recovery

#### 10.1 High Availability

**Cluster**:

- Multi-zonal deployment (3 zones in `us-central1`)
- Cross-region failover to `us-east1` (future)

**Data**:

- Cloud Storage: Geo-redundant by default
- Firestore: Multi-region replication
- Redis: MemoryStore with automatic failover

**RPO/RTO**:

- **RPO**: 0 seconds (synchronous replication)
- **RTO**: 5 minutes (automated failover)

#### 10.2 Backup & Recovery

**Backups**:

- **State**: Firestore automatic daily backups (35-day retention)
- **Logs**: Cloud Logging 30-day retention + Cloud Storage archive
- **Configurations**: Git-versioned Infrastructure-as-Code

**Recovery Testing**:

- Monthly DR drill
- Chaos engineering with Chaos Mesh
- Automated recovery runbooks

---

## Implementation Roadmap

### Phase 1: MVP (Weeks 1-2)

- [ ] Set up GKE Autopilot cluster
- [ ] Deploy vLLM model server with Gemini 2.0 Flash
- [ ] Implement basic LangGraph supervisor pattern
- [ ] Document AI integration (single processor)
- [ ] Basic monitoring dashboard

### Phase 2: Production Hardening (Weeks 3-4)

- [ ] GKE Inference Gateway integration
- [ ] HPA with custom metrics
- [ ] Multi-agent LangGraph orchestration
- [ ] Cloud Storage FUSE for fast model loading
- [ ] Comprehensive observability

### Phase 3: Optimization (Weeks 5-6)

- [ ] INT8 quantization for cost optimization
- [ ] Prefix caching optimization
- [ ] Batch processing pipeline
- [ ] Security hardening (Binary Authorization, CMEK)
- [ ] DR testing and runbooks

### Phase 4: Scale & Revenue (Weeks 7-8)

- [ ] Multi-vertical deployment (Pharma, Finance, Defense)
- [ ] LoRA fine-tuning for compliance frameworks
- [ ] Customer onboarding automation
- [ ] SLA monitoring and alerting
- [ ] Cost attribution per customer

---

## Decision Rationale

### Why GKE over Cloud Run?

- **GPU Support**: Cloud Run doesn't support GPUs (required for LLM inference)
- **Cost**: GKE more cost-effective at scale (>100M tokens/month)
- **Control**: Fine-grained control over autoscaling, networking, storage

### Why Vertex AI Integration?

- **Model Garden**: Access to latest Google models
- **Managed Infrastructure**: Reduce operational overhead
- **Compliance**: Pre-certified for HIPAA, FedRAMP
- **Ecosystem**: Native integration with Document AI, BigQuery

### Why LangGraph over LangChain?

- **State Management**: Built-in state graphs for complex workflows
- **Checkpointing**: Resume workflows after failures
- **Observability**: Better debugging for multi-agent systems
- **Performance**: Lower overhead vs. LangChain LCEL

### Why vLLM Server?

- **Performance**: Industry-leading throughput (PagedAttention)
- **Compatibility**: OpenAI API compatibility
- **Google Support**: Official Google custom images
- **Features**: Continuous batching, tensor parallelism, LoRA support

---

## Success Metrics

### Technical KPIs

- **Latency**: p99 TTFT <500ms
- **Throughput**: 10K tokens/sec per pod
- **Availability**: 99.9% uptime
- **Cost**: <$0.005 per 1K tokens

### Business KPIs

- **Processing Speed**: 100 documents/hour per pod
- **Accuracy**: >95% compliance policy extraction
- **Cost per Document**: <$0.50 (vs. manual review at $50)
- **Customer SLA**: 99.9% adherence

### Revenue Impact

- **Target**: 10 customers × 1000 docs/month = 10K docs/month
- **Pricing**: $5/document
- **Revenue**: $50K/month
- **Infrastructure Cost**: $2K/month
- **Gross Margin**: 96%

---

## References

- [GKE Inference Reference Architecture](https://cloud.google.com/blog/topics/developers-practitioners/supercharge-your-ai-gke-inference-reference-architecture-your-blueprint-for-production-ready-inference)
- [GKE AI/ML Inference Concepts](https://cloud.google.com/kubernetes-engine/docs/concepts/machine-learning/inference)
- [LangGraph Multi-Agent Workflows](https://blog.langchain.dev/langgraph-multi-agent-workflows/)
- [Vertex AI Model Deployment](https://cloud.google.com/vertex-ai/docs/general/deployment)
- [Document AI Overview](https://cloud.google.com/document-ai/docs/overview)

---

## Appendix: Terraform Modules

See `infrastructure/terraform/` for complete Infrastructure-as-Code:

- `gke-cluster/`: GKE Autopilot cluster configuration
- `vertex-ai/`: Model serving endpoints
- `document-ai/`: Document AI processors
- `networking/`: VPC, firewall rules, Cloud NAT
- `observability/`: Monitoring dashboards, alerts

---

**Author**: Claude (Pnkln Core Stack Architect)
**Reviewers**: [To be assigned]
**Approved**: [Pending]
**Last Updated**: 2025-11-07
