# Judge #6 HITL System - Complete Overview

**Binary enforcement engine for high-stakes decision-making with Human-in-the-Loop gates**

## Executive Summary

Judge #6 is a **binary ALLOW/BLOCK enforcement system** that evaluates high-risk actions across four verticals (Financial, Legal Case, Legal Compliance, Fraud) with integrated ATP 5-19 risk assessment and sub-90ms latency targets.

**Decision Framework**: Purpose=AiYouJR • Reason=Doctrine • Brakes=Army RM

**Key Capabilities**:
- **Binary decisions**: ALLOW or BLOCK (no ambiguity)
- **ATP 5-19 risk matrix**: Probability (A-E) × Severity (I-IV) → Risk Level (EH/H/M/L)
- **HITL gates**: Automated routing to appropriate approval authority (CFO, Legal, etc.)
- **Semantic compression**: 10:1 audit trail compression while preserving decision-critical info
- **Sub-90ms latency**: Target p50≈30ms, p99≤90ms for real-time enforcement
- **Compliance-first**: EU AI Act + CA SB 53 transparency built-in

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                   Judge #6 HITL System                          │
│                                                                 │
│  ┌────────────────────┐         ┌────────────────────┐         │
│  │   FastAPI Layer    │         │   Gemini 2.0 Flash │         │
│  │  (API Endpoints)   │◄───────►│  (Risk Enhancement)│         │
│  └──────────┬─────────┘         └────────────────────┘         │
│             │                                                   │
│             ▼                                                   │
│  ┌──────────────────────────────────────────────────┐          │
│  │            Judge Router (JudgeFactory)           │          │
│  └────────┬─────────┬─────────┬─────────┬───────────┘          │
│           │         │         │         │                      │
│     ┌─────▼───┐ ┌───▼────┐ ┌──▼─────┐ ┌▼────────┐            │
│     │FinJudge │ │CaseJudge│ │LawJudge│ │FraudJudge│            │
│     │         │ │         │ │        │ │         │            │
│     │ $50K+   │ │ Legal   │ │ EU AI  │ │ Fraud   │            │
│     │ Wires   │ │ Cases   │ │ Act    │ │ Score   │            │
│     └─────┬───┘ └───┬────┘ └──┬─────┘ └┬────────┘            │
│           │         │         │         │                      │
│           └─────────┴─────────┴─────────┘                      │
│                     │                                           │
│           ┌─────────▼──────────┐                               │
│           │  BaseJudge (ABC)   │                               │
│           │                    │                               │
│           │  • evaluate_action()                               │
│           │  • extract_risk_factors()                          │
│           │  • judge() [core flow]                             │
│           └─────────┬──────────┘                               │
│                     │                                           │
│     ┌───────────────┴───────────────┐                          │
│     │                               │                          │
│     ▼                               ▼                          │
│  ┌──────────────┐         ┌─────────────────────┐             │
│  │ ATP 5-19     │         │ Semantic Compression│             │
│  │ Risk Matrix  │         │  (10:1 ratio)       │             │
│  │              │         │                     │             │
│  │ P(A-E) ×     │         │ Audit Trail Storage │             │
│  │ S(I-IV)      │         │ (7 year retention)  │             │
│  │ → Risk(EH/H/M/L)       └─────────────────────┘             │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
```

### Core Workflow

Every judge follows this flow (implemented in `BaseJudge.judge()`):

1. **Start latency timer** (p99 ≤90ms target)
2. **Evaluate action** (vertical-specific logic)
3. **Extract risk factors** (probability, severity, rationale, mitigations)
4. **Perform ATP 5-19 risk assessment** (matrix lookup)
5. **Determine approval gate** (based on risk level + amount)
6. **Generate semantic audit trail** (10:1 compression)
7. **Return binary decision** (ALLOW or BLOCK)
8. **Create immutable audit record** (7-year retention)

## Judge Verticals

### 1. FinJudge - Financial Transactions

**Primary Use Case**: $50K+ wire transfers requiring CFO approval

**Evaluates**:
- Wire transfers
- Payment authorizations
- Contract financial approvals
- Vendor payments
- Capital expenditures

**Decision Logic**:
- Amount thresholds ($50K CFO approval)
- Vendor verification status (approved/new/unverified)
- Purchase order validation
- Destination country risk
- Pattern anomaly detection

**Example**:
```python
request = JudgeRequest(
    request_id="req_fin_001",
    judge_type=JudgeType.FIN,
    action_type="wire_transfer",
    context={
        "amount_usd": 75000,
        "vendor_status": "new",
        "purchase_order": None,
        "destination_country": "Unknown"
    },
    requested_by="john.doe@company.com"
)

response = judge.judge(request)
# decision: BLOCK
# reasoning: "New vendor without PO requires CFO approval"
# approval_gate: CFO
```

**See**: [FinJudge Specifications](./fin-judge-spec.md)

### 2. CaseJudge - Legal Case Assessment

**Primary Use Cases**: Case acceptance, settlement authorization, litigation strategy

**Evaluates**:
- Case acceptance (new client/matter intake)
- Settlement proposals ($100K+ threshold)
- Litigation strategy changes
- Discovery requests
- Motion filings

**Decision Logic**:
- Case value assessment
- Conflict of interest check
- Risk/reward analysis (probability of success)
- Resource availability
- Statute of limitations urgency

**Example**:
```python
context = {
    "case_value_usd": 500000,
    "case_type": "contract_dispute",
    "conflict_check_passed": False,  # ← CRITICAL
    "probability_of_success": 0.6
}

# decision: BLOCK (conflict check failed)
# reasoning: "Conflict of interest check not passed - BLOCK"
```

**See**: [CaseJudge Specifications](./case-judge-spec.md)

### 3. LawJudge - Legal Compliance Validation

**Primary Use Cases**: EU AI Act compliance, GDPR, CA SB 53, export control

**Evaluates**:
- Regulatory compliance (EU AI Act, GDPR, CCPA)
- Contract legal review
- Policy adherence
- Data privacy compliance (DPIA requirements)
- Export control compliance

**Decision Logic**:
- Regulatory framework identification
- High-risk AI system classification (EU AI Act)
- Documentation validation (legal review, DPIA)
- Transparency disclosure requirements (CA SB 53)
- Export license validation

**High-Risk AI Systems** (EU AI Act):
- Biometric identification
- Critical infrastructure
- Law enforcement
- Education scoring
- Employment decisions

**Example**:
```python
context = {
    "compliance_area": "eu_ai_act",
    "ai_system_type": "biometric_identification",  # ← HIGH RISK
    "legal_review_completed": False
}

# decision: BLOCK
# reasoning: "High-risk AI system requires legal review - BLOCK"
# severity: I (Catastrophic - €30M fine + criminal liability)
```

**See**: [LawJudge Specifications](./law-judge-spec.md)

### 4. FraudJudge - Fraud Detection & Risk Scoring

**Primary Use Cases**: Payment fraud, account takeover, identity verification

**Evaluates**:
- Payment fraud indicators (ML fraud score)
- Account security anomalies
- Identity verification failures
- Transaction pattern deviations
- Vendor fraud risk

**Decision Logic**:
- Fraud score assessment (0.0-1.0, ML-based in production)
- Behavioral anomaly detection (velocity checks)
- Geographic risk factors (geo-mismatch)
- Identity verification status (KYC)
- Multi-indicator analysis

**Thresholds**:
- High fraud: ≥0.7 → BLOCK
- Medium fraud: 0.4-0.7 → Additional verification
- Low fraud: <0.4 → Monitor

**Example**:
```python
context = {
    "fraud_score": 0.75,           # ← HIGH
    "identity_verified": False,
    "geo_location_mismatch": True,
    "velocity_check_failed": True,  # Multiple indicators
    "amount_usd": 5000
}

# decision: BLOCK
# reasoning: "High fraud score + multiple indicators - BLOCK"
# mitigations: ["Trigger MFA", "Contact account holder", "Manual review"]
```

**See**: [FraudJudge Specifications](./fraud-judge-spec.md)

## ATP 5-19 Risk Matrix Integration

All judges use the **Army Techniques Publication 5-19** risk assessment matrix.

### Risk Matrix Lookup

| **Probability** ↓ × **Severity** → | **I (Catastrophic)** | **II (Critical)** | **III (Moderate)** | **IV (Negligible)** |
|------------------------------------|----------------------|-------------------|--------------------|---------------------|
| **A** (Almost Certain, >90%)       | **EH**               | **EH**            | **H**              | **M**               |
| **B** (Likely, 70-90%)             | **EH**               | **H**             | **H**              | **M**               |
| **C** (Possible, 30-70%)           | **EH**               | **H**             | **M**              | **L**               |
| **D** (Unlikely, 10-30%)           | **H**                | **M**             | **M**              | **L**               |
| **E** (Rare, <10%)                 | **M**                | **M**             | **L**              | **L**               |

**Risk Levels**:
- **EH** (Extremely High): Requires immediate action, highest authority approval (C-Suite + Board)
- **H** (High): Requires action, senior authority approval (Senior Executive)
- **M** (Medium): Monitor closely, moderate authority approval (Department Head)
- **L** (Low): Accept with monitoring (Automated)

### Approval Authority Mapping

```python
def determine_approval_authority(risk_level: RiskLevel, amount_usd: float):
    # Financial thresholds
    if amount_usd >= 50_000: return "CFO"
    elif amount_usd >= 10_000: return "Finance Director"

    # Risk-based approval
    if risk_level == RiskLevel.EH: return "C-Suite + Board"
    elif risk_level == RiskLevel.H: return "Senior Executive"
    elif risk_level == RiskLevel.M: return "Department Head"
    else: return "Automated"
```

## Semantic Compression for Audit Trails

Target: **10:1 compression ratio** while preserving decision-critical information.

### Example Compression

**Original Context** (850 bytes):
```json
{
  "amount_usd": 50000,
  "vendor_id": "VND-12345",
  "vendor_status": "new",
  "vendor_name": "Acme Corp",
  "purchase_order": null,
  "destination_country": "Unknown",
  "destination_bank": "Unknown",
  "requested_by": "john.doe@company.com",
  "request_timestamp": "2025-11-17T14:30:00Z",
  "action_type": "wire_transfer",
  ...
}
```

**Semantic Summary** (62 bytes):
```
wire→$50K→new_vendor→no_PO→high_risk→CFO_gate→BLOCK
```

**Compression Ratio**: 850 / 62 = **13.7:1** ✓

### Semantic Trail Format

```
action→amount→vendor_status→PO_status→risk_level→approval_gate→decision
```

**Components**:
- **Action**: Abbreviated action type (wire, contract, legal, fraud)
- **Amount**: Formatted amount ($50K, $2.5M)
- **Context**: Key decision factors (new_vendor, PO_123456, fraud_high)
- **Risk**: Risk level (EH_risk, H_risk, M_risk, L_risk)
- **Gate**: Approval gate (CFO_gate, auto_gate)
- **Decision**: ALLOW or BLOCK

**Validation**: Trails must have ≥3 components including risk indicator and decision.

## Performance Targets

### Latency Requirements

| **Metric** | **Target** | **Measurement** |
|------------|------------|-----------------|
| p50 latency | ~30ms | Median decision time |
| **p99 latency** | **≤90ms** | **99th percentile (HARD REQUIREMENT)** |
| Max latency | <200ms | Absolute ceiling |

**Measurement Method**: `time.perf_counter()` start/end around `judge.judge()` call.

**Validation**: Run 1000 sample decisions, calculate p99. Must be ≤90ms.

### Throughput

- **Target**: 100 decisions/second per judge vertical
- **Scaling**: Horizontal scaling via GKE (stateless judges)
- **Bottlenecks**: Database writes (audit trails) - use async batching

### Availability

- **Target**: 99.9% uptime (≤43 minutes downtime/month)
- **Strategy**: Multi-region GKE deployment, health checks, circuit breakers

## Compliance & Regulatory

### EU AI Act Compliance

**Article 9**: High-risk AI systems require:
- ✅ Risk assessment (ATP 5-19 matrix)
- ✅ Human oversight (HITL gates)
- ✅ Technical documentation (audit trails)
- ✅ Transparency (semantic summaries)

**Article 12**: Logging requirements:
- ✅ Immutable audit trails
- ✅ 7-year retention (2555 days)
- ✅ Decision rationale preservation

**Penalty Avoidance**: Up to €30M or 6% global revenue

### California SB 53

**Transparency Requirements**:
- ✅ AI system documentation (Judge specs)
- ✅ Performance metrics (latency, accuracy)
- ✅ Model cards (risk assessment methodology)
- ✅ Public disclosure (audit trail summaries)

**See**: [EU AI Act + CA SB 53 Compliance](./compliance-documentation.md)

## Gemini 2.0 Flash Integration

**CRITICAL**: Gemini function calling returns **PARAMETERS**, not execution!

### Integration Pattern

```python
# ❌ WRONG: Never let Gemini execute directly
gemini_response = model.generate_content("Execute payment")

# ✅ CORRECT: Gemini returns parameters, WE execute
function_call = gemini_response.function_call
# Returns: {"name": "assess_risk", "args": {...}}

# WE validate and execute:
if validate_params(function_call.args):
    result = our_assess_risk_function(**function_call.args)
```

### Use Cases

1. **Enhanced risk assessment**: Gemini analyzes context, suggests probability/severity
2. **Decision reasoning**: Generate human-readable explanations
3. **Mitigation suggestions**: Context-aware risk mitigations

**See**: `src/utils/gemini_integration.py`

## API Endpoints

### Primary Enforcement Endpoint

**POST** `/judges/evaluate`

Request:
```json
{
  "request_id": "req_20251117_fin_001",
  "judge_type": "FinJudge",
  "action_type": "wire_transfer",
  "context": {...},
  "urgency": "normal",
  "requested_by": "user@company.com"
}
```

Response:
```json
{
  "decision": "BLOCK",
  "risk_assessment": {...},
  "approval_gate": "cfo",
  "reasoning": "...",
  "semantic_trail": "wire→$75K→new_vendor→no_PO→high_risk→CFO_gate→BLOCK",
  "latency_ms": 42.3,
  "next_steps": [...]
}
```

### Audit Trail Retrieval

**GET** `/judges/audit/{request_id}`

Returns immutable audit trail with full context (encrypted).

### Metrics

**GET** `/judges/metrics/{judge_type}`

Returns performance metrics (latency, decision distribution, etc.).

**GET** `/judges/stats/overview`

System-wide statistics across all verticals.

**See**: `src/api/judges.py` for full API documentation.

## Deployment

### Tech Stack

- **Platform**: Google Cloud (Vertex AI Workbench → GKE Native)
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **AI/ML**: Gemini 2.0 Flash (function calling)
- **Database**: PostgreSQL (audit trails, metadata)
- **Storage**: GCS (encrypted full context)

### GKE Deployment

```bash
# Build Docker image
docker build -t gcr.io/PROJECT_ID/judge-hitl:v1.0.0 .

# Deploy to GKE
kubectl apply -f k8s/judge-deployment.yaml

# Expose service
kubectl expose deployment judge-hitl --type=LoadBalancer --port=8001
```

### Scaling Strategy

- **Horizontal**: Scale judge pods (stateless)
- **Vertical**: Increase CPU/memory for complex ML models
- **Database**: Cloud SQL High Availability

### Monitoring

- **Prometheus**: Latency, throughput, error rates
- **Grafana**: Dashboards for each vertical + system overview
- **Alerting**: p99 latency >90ms, error rate >1%, downtime

## Development Principles

1. **"Stupid simple" but functional**: Clear, readable code over cleverness
2. **Ship speed > feature complexity**: MVP first, iterate
3. **Evidence-based targets**: Measure, don't guess (p99 latency validation)
4. **Human checkpoints**: HITL gates for liability/regulatory decisions
5. **Security absolute**: 100% security as operational gate
6. **Bootstrap discipline**: ROI ≥3× @ 18mo, LTV:CAC ≥4:1 @ 12mo

## Next Steps

1. **Latency validation**: Run 1000 sample decisions, measure p99 (target: ≤90ms)
2. **Production database**: Replace in-memory storage with PostgreSQL
3. **Gemini API key**: Configure actual Gemini integration
4. **Load testing**: Validate 100 req/sec throughput
5. **Compliance audit**: External review for EU AI Act + CA SB 53
6. **Enterprise pricing**: $100K+ annual for compliance solutions

## References

- **ATP 5-19**: Army Techniques Publication 5-19 (Risk Management)
- **EU AI Act**: Regulation (EU) 2024/1689
- **CA SB 53**: California Senate Bill 53 (AI Transparency)
- **Source Code**: `/src/judges/`, `/src/risk_matrix/`, `/src/utils/`

---

**Status**: ✅ Pilot Ready (v1.0.0)
**Last Updated**: 2025-11-17
**Maintainer**: AiYou Judge Team
