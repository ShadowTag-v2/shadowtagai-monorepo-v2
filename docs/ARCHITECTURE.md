# System Architecture

Complete technical architecture documentation for the shadowtagai orchestrator system.

## Overview

The shadowtagai orchestrator is a production-grade, GKE-native AI orchestration platform that combines multiple AI models (Claude via Vertex AI, Gemini, GPT) to deliver intelligent, revenue-optimized solutions.

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                          INTERNET                                       │
└───────────────────────────────┬────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   GOOGLE CLOUD LOAD BALANCER                            │
│                    (Global HTTPS Load Balancer)                         │
│                    - SSL Termination (Managed Cert)                     │
│                    - Cloud Armor Security Policy                        │
└───────────────────────────────┬────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      GKE INGRESS CONTROLLER                             │
│                         (NEG-based)                                     │
└───────────────────────────────┬────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   KUBERNETES SERVICE (ClusterIP)                        │
└───────────────────────────────┬────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│              KUBERNETES DEPLOYMENT (shadowtagai-orchestrator)                 │
│              ┌──────────────────────────────────────────┐              │
│              │          POD (3-50 replicas)             │              │
│              │  ┌────────────────────────────────────┐  │              │
│              │  │  Express.js HTTP Server (8080)     │  │              │
│              │  │  ├─ /api/execute                   │  │              │
│              │  │  ├─ /health                        │  │              │
│              │  │  ├─ /ready                         │  │              │
│              │  │  └─ /metrics (Prometheus)          │  │              │
│              │  └────────────────────────────────────┘  │              │
│              │  ┌────────────────────────────────────┐  │              │
│              │  │  ShadowTagAi Core                        │  │              │
│              │  │  ├─ IntentClassifier               │  │              │
│              │  │  ├─ VertexOrchestrator             │  │              │
│              │  │  └─ WealthEngine                   │  │              │
│              │  └────────────────────────────────────┘  │              │
│              └──────────────────────────────────────────┘              │
└────────────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
┌──────────────────────────────┐  ┌───────────────────────────┐
│    VERTEX AI (Claude)        │  │    GCP SERVICES           │
│    - Intent Classification   │  │    - Secret Manager       │
│    - THINK mode execution    │  │    - Cloud Monitoring     │
│    - BUILD mode execution    │  │    - Cloud Logging        │
│    - SCALE mode execution    │  │    - Cloud Trace          │
└──────────────────────────────┘  └───────────────────────────┘
```

## Component Details

### 1. Frontend Layer

#### Global HTTPS Load Balancer

- **Purpose**: Single global entry point with SSL termination
- **Features**:
  - Managed SSL certificates (auto-renewal)
  - Cloud Armor for DDoS protection
  - Global anycast IP for low latency
  - Health checks to backend services
- **Configuration**: `k8s/base/ingress.yaml`, `k8s/base/backendconfig.yaml`

### 2. Kubernetes Layer

#### GKE Cluster

- **Type**: Regional cluster with Workload Identity
- **Configuration**:
  - Private cluster (private nodes, public endpoint)
  - Release channel: REGULAR
  - Binary authorization enabled
  - Workload Identity for pod-level IAM
- **Node Pools**:
  1. **Spot Pool** (cost-optimized):
     - Machine type: e2-standard-4
     - Preemptible instances
     - Auto-scaling: 1-10 nodes
     - 60-90% cost savings
  2. **On-Demand Pool** (critical workloads):
     - Machine type: e2-standard-4
     - Standard instances
     - Tainted for specific workloads
     - Auto-scaling: 1-5 nodes

#### Deployment

- **Replicas**: 3 minimum, 50 maximum (HPA controlled)
- **Strategy**: RollingUpdate (maxSurge: 1, maxUnavailable: 0)
- **Resources**:
  - Requests: 1 CPU, 2Gi memory
  - Limits: 2 CPU, 4Gi memory
- **Health Checks**:
  - Liveness: /health (every 10s)
  - Readiness: /ready (every 5s)
  - Startup: /health (max 5 minutes)

#### Horizontal Pod Autoscaler (HPA)

- **Metrics**:
  - CPU: Scale at 70% utilization
  - Memory: Scale at 80% utilization
  - Custom: Requests per second
- **Behavior**:
  - Scale up: Aggressive (100% every 30s)
  - Scale down: Conservative (50% every 60s)
  - Stabilization: 5 minutes for scale down

### 3. Application Layer

#### Express.js Server

- **Framework**: Express 4.x
- **Middleware**:
  - Helmet (security headers)
  - CORS (cross-origin)
  - Compression (gzip)
  - JSON body parser (10MB limit)
- **Endpoints**:
  - `POST /api/execute`: Main execution endpoint
  - `GET /health`: Health check
  - `GET /ready`: Readiness check
  - `GET /metrics`: Prometheus metrics
  - `GET /`: API information

#### Core Modules

##### 1. ShadowTagAi (Main Orchestrator)

**File**: `src/core/shadowtagai.ts`

**Responsibilities**:

- Coordinate all subsystems
- Handle user requests end-to-end
- Format responses
- Error handling

**Flow**:

```
User Request
    ↓
IntentClassifier.classify()
    ↓
WealthEngine.optimize(
    VertexOrchestrator.execute()
)
    ↓
Format Response
    ↓
Return to User
```

##### 2. Intent Classifier

**File**: `src/core/intent-classifier.ts`

**Purpose**: Determine which mode to use (THINK/BUILD/SCALE)

**Algorithm**:

1. Call Claude via Vertex AI with classification prompt
2. Parse JSON response
3. Fallback to heuristic if parsing fails
4. Return: mode + confidence + reasoning

**Modes**:

- **THINK**: Strategic reasoning, analysis, recommendations
- **BUILD**: Implementation, code generation, deployment
- **SCALE**: Growth optimization, resource scaling

##### 3. Vertex Orchestrator

**File**: `src/core/vertex-orchestrator.ts`

**Purpose**: Interface with Claude via Vertex AI

**Features**:

- Workload Identity authentication (no keys!)
- Automatic retry logic
- Token usage tracking
- Latency monitoring
- Context-aware prompting

**Model**: `claude-opus-4-1@20250805`
**Max Tokens**: 20,000

##### 4. Wealth Engine

**File**: `src/core/wealth-engine.ts`

**Purpose**: Revenue optimization for every operation

**Process**:

```
BEFORE:
- Scan for revenue opportunities
- Capture baseline metrics

DURING:
- Execute operation
- Track costs

AFTER:
- Calculate revenue impact
- Run Monte Carlo simulation
- Generate recommendations
- Apply Business Judgment Rule
```

**Business Rules**:

- LTV:CAC ≥ 4:1
- ROI ≥ 3× in 18 months
- Confidence ≥ 70%

##### 5. Metrics System

**File**: `src/utils/metrics.ts`

**Prometheus Metrics**:

- `shadowtagai_requests_total`: Counter (by mode, status)
- `shadowtagai_request_duration_seconds`: Histogram (p50, p95, p99)
- `shadowtagai_vertex_calls_total`: Counter (API calls)
- `shadowtagai_vertex_tokens_total`: Counter (token usage)
- `shadowtagai_revenue_dollars`: Gauge (cumulative revenue)
- `shadowtagai_cost_dollars`: Gauge (cumulative cost)
- `shadowtagai_profit_dollars`: Gauge (net profit)

##### 6. Logging System

**File**: `src/utils/logger.ts`

**Features**:

- Structured JSON logging
- Winston library
- GCP Cloud Logging integration
- Automatic trace correlation
- Log levels: error, warn, info, debug

### 4. External Services

#### Vertex AI (Claude)

- **Authentication**: Workload Identity
- **Region**: us-central1 (configurable)
- **Model**: Claude Opus 4.1
- **Usage**:
  - Intent classification
  - Strategic reasoning (THINK)
  - Code generation (BUILD)
  - Scaling analysis (SCALE)

#### GCP Services

##### Secret Manager

- **Purpose**: Secure secret storage
- **Secrets**:
  - `anthropic-vertex-project-id`: Vertex AI project ID
- **Access**: Via Workload Identity (no keys)

##### Cloud Monitoring

- **Metrics**: Prometheus metrics via Managed Prometheus
- **Dashboards**: Custom dashboard with 6+ charts
- **Uptime Checks**: HTTP health endpoint monitoring

##### Cloud Logging

- **Logs**:
  - Application logs (Winston)
  - Kubernetes logs (stdout/stderr)
  - System logs (GKE)
- **Retention**: 30 days (default)
- **Sinks**: Optional long-term storage in GCS

##### Artifact Registry

- **Purpose**: Container image storage
- **Repository**: `us-central1-docker.pkg.dev/PROJECT_ID/shadowtagai`
- **Cleanup Policies**:
  - Keep 10 recent versions
  - Delete untagged images after 30 days

### 5. Security Architecture

#### Network Security

```
Internet
    ↓
[Cloud Armor] ← DDoS protection
    ↓
[HTTPS Load Balancer] ← SSL termination
    ↓
[GKE Master] ← Private endpoint option
    ↓
[Private Nodes] ← No public IPs
    ↓
[Cloud NAT] → Internet (egress only)
```

#### Pod Security

- **Service Account**: Custom SA with minimal permissions
- **Workload Identity**: No service account keys
- **Security Context**:
  - Non-root user (UID 1001)
  - Read-only root filesystem
  - No privilege escalation
  - Dropped all capabilities

#### Network Policies

- **Ingress**: Only from ingress controller
- **Egress**: Only to:
  - DNS (port 53)
  - HTTPS (port 443)
  - Vertex AI endpoints

#### Binary Authorization

- **Enabled**: All images must be signed/verified
- **Policy**: Project-level enforcement

### 6. Observability

#### Metrics Pipeline

```
Application (Prometheus client)
    ↓
/metrics endpoint
    ↓
GCP Managed Prometheus
    ↓
Cloud Monitoring
    ↓
Custom Dashboards + Alerts
```

#### Logging Pipeline

```
Application (Winston)
    ↓
stdout/stderr
    ↓
Cloud Logging Agent
    ↓
Cloud Logging
    ↓
(Optional) Log Sink → GCS
```

#### Tracing Pipeline

```
Application (Cloud Trace SDK)
    ↓
Cloud Trace API
    ↓
Cloud Trace Console
```

### 7. CI/CD Pipeline

```
GitHub Push
    ↓
Cloud Build Trigger
    ↓
┌──────────────────────────┐
│ 1. npm test              │
│ 2. docker build          │
│ 3. Container scan        │
│ 4. docker push           │
│ 5. GKE deploy            │
│ 6. Rollout verify        │
│ 7. Smoke test            │
└──────────────────────────┘
    ↓
Deployment Complete
```

**Environments**:

- **Main branch**: Automatic deployment to production
- **Pull requests**: Build + test only (no deployment)

### 8. Data Flow

#### Request Flow

```
1. User → Load Balancer → Ingress → Service → Pod
2. Pod → IntentClassifier.classify() → Vertex AI
3. Vertex AI → Response (mode: THINK|BUILD|SCALE)
4. Pod → VertexOrchestrator.execute(mode) → Vertex AI
5. Vertex AI → Response (solution)
6. Pod → WealthEngine.optimize() → Revenue analysis
7. Pod → Format response → User
```

#### Metrics Flow

```
1. Application → Prometheus metrics (in-memory)
2. GCP Managed Prometheus → Scrape /metrics (every 15s)
3. Cloud Monitoring → Store time-series data
4. Dashboard → Query + visualize
5. Alerting → Evaluate rules
6. Notification → Email/SMS/PagerDuty
```

## Performance Characteristics

### Latency

- **p50**: < 1 second
- **p95**: < 3 seconds
- **p99**: < 5 seconds

_Depends on Vertex AI API latency_

### Throughput

- **Single pod**: ~10-20 requests/second
- **Auto-scaled**: 100+ requests/second

### Availability

- **Target SLA**: 99.9% (3 nines)
- **Mechanisms**:
  - Multi-pod deployment (min 3 replicas)
  - PodDisruptionBudget (min 2 available)
  - Health checks + auto-restart
  - Regional cluster (multi-zone)

### Cost Efficiency

- **Spot VMs**: 60-90% cost reduction vs on-demand
- **Auto-scaling**: Only pay for what you use
- **Efficient caching**: Reduce redundant API calls

## Disaster Recovery

### Backup Strategy

- **Infrastructure**: Terraform state in GCS
- **Configuration**: Git repository
- **Secrets**: Secret Manager (auto-replicated)
- **Logs**: Cloud Logging (30-day retention + optional GCS sink)

### Recovery Procedures

1. **Pod failure**: Automatic restart (Kubernetes)
2. **Node failure**: Automatic rescheduling
3. **Zone failure**: Multi-zone deployment handles
4. **Region failure**: Manual failover to different region
5. **Complete disaster**: Rebuild from Terraform + Git

### RTO/RPO

- **Recovery Time Objective (RTO)**: < 15 minutes
- **Recovery Point Objective (RPO)**: < 5 minutes

## Scalability

### Horizontal Scaling

- **Current**: 3-50 pods via HPA
- **Future**: Can scale to 100s of pods
- **Limitation**: Vertex AI quota

### Vertical Scaling

- **Current**: 2 CPU / 4Gi RAM per pod
- **Future**: Can increase to 8 CPU / 32Gi RAM
- **Use Case**: Memory-intensive operations

### Geographic Scaling

- **Current**: Single region (us-central1)
- **Future**: Multi-region with global load balancing
- **Regions**: us-east1, europe-west1, asia-east1

## Future Enhancements

### Planned

1. **Multi-region deployment** for global availability
2. **Request caching** for faster responses
3. **Batch processing** for bulk operations
4. **WebSocket support** for streaming responses
5. **GraphQL API** alongside REST
6. **Custom model fine-tuning** for specialized tasks

### Under Consideration

1. **Edge deployments** via Cloudflare Workers
2. **Mobile SDK** for direct integration
3. **A/B testing framework** for prompt optimization
4. **Data lake** for analytics and ML training

---

**Last Updated**: 2025-01-08
**Version**: 1.0.0
