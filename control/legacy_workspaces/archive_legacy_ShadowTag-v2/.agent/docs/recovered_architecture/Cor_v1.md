# Cor v1.0 - Pnkln Operating System

**Last Updated**: 2025-11-14
**Status**: Master Framework Document
**Purpose**: Portable source of truth for all Pnkln strategic, technical, and operational context

---

## SYSTEM OVERVIEW

This document serves as the **master reference** for Pnkln's operational framework across all Claude conversations and environments. It defines decision-making protocols, bootstrap constraints, technical standards, and strategic priorities.

**Core Principle**: Every strategic decision, technical architecture choice, and financial commitment must pass through validation frameworks defined here.

---

## CORE FRAMEWORKS

### 1. JR_ENGINE (Justification-Reasoning Engine)

**Purpose → Reasons → Brakes validation pathway**

Every significant decision flows through:


1. **PURPOSE**: What strategic outcome does this serve?

   - Must align with bootstrap mission (profitable exit $60-65K burn)

   - Must contribute to core value proposition

   - Must have measurable success criteria


2. **REASONS**: Evidence hierarchy supporting the decision

   - **Tier 1**: Direct user feedback, production metrics, financial data

   - **Tier 2**: Industry benchmarks, competitive analysis, advisor input

   - **Tier 3**: First principles reasoning, analogies, best practices

   - **Tier 4**: Speculation, intuition, assumptions (flag clearly)


3. **BRAKES**: Kill-switch criteria and constraints

   - Bootstrap gates (see BOOTSTRAP_GATES.md)

   - Technical SLAs (see TECHNICAL_SLA.md)

   - Risk framework triggers (see RISK_FRAMEWORK.md)

   - Strategic misalignment flags

**Application**: Use JR_ENGINE for:

- Feature prioritization decisions

- Technical architecture choices

- Resource allocation (time, money, people)

- Partnership/vendor selection

- Pivot considerations

---

### 2. BOOTSTRAP_GATES

**Financial constraints and validation metrics**

**Burn Constraint**: $60,000 - $65,000 maximum
**Exit Requirement**: Profitable, sustainable business

**Key Metrics**:

- **ROI Threshold**: ≥3× return on invested capital

- **LTV:CAC Ratio**: ≥4:1 (lifetime value to customer acquisition cost)

- **Runway Decision Point**: 6 months remaining → activate contingency

- **Monthly Burn Rate**: Track weekly, flag if trending >$11K/month

**Gate Questions** (must answer "yes" before major spend):

1. Does this directly increase revenue or decrease CAC?

2. Is there cheaper validation possible?

3. Can we defer this 90 days without material impact?

4. Is ROI measurable within 6 months?

5. Does this survive worst-case revenue scenarios?

**Reference**: See BOOTSTRAP_GATES.md for full specification

---

### 3. TECHNICAL_SLA

**Performance standards and core stack specifications**

**Primary System: Judge #6 (Cor Decision Engine)**

- **p99 Latency**: ≤90ms (99th percentile response time)

- **p50 Latency**: ≤30ms (median response time)

- **Availability**: 99.9% uptime (measured monthly)

- **Error Rate**: <0.1% of requests

- **Concurrency**: Support 100 concurrent decisions

**Core Stack Requirements**:

- **Language**: Python 3.11+ (primary), TypeScript 5.0+ (tooling)

- **Framework**: FastAPI for APIs, React for interfaces

- **Database**: PostgreSQL 15+ (primary), Redis for caching

- **Infrastructure**: Cloud-agnostic (avoid vendor lock-in)

- **Observability**: Structured logging, distributed tracing, metrics

**Architecture Principles**:

- Modularity: Components testable in isolation

- Resilience: Graceful degradation, circuit breakers

- Efficiency: Optimize for p99 latency, not just average

- Simplicity: Prefer boring technology, avoid premature optimization

**Reference**: See TECHNICAL_SLA.md for full specification

---

### 4. RISK_FRAMEWORK

**ATP 5-19 gates and kill-switch protocols**

**Based on**: ATP 5-19 (Army Risk Management doctrine)

**Risk Assessment Gates**:

1. **Identify Hazards**: What could go wrong?

2. **Assess Hazards**: Probability × Severity = Risk Level

3. **Develop Controls**: Mitigation strategies

4. **Implement Controls**: Execution plan

5. **Supervise & Evaluate**: Ongoing monitoring

**Kill-Switch Triggers** (immediate halt required):

- **Financial**: Monthly burn exceeds $12K for 2 consecutive months

- **Technical**: p99 latency >200ms for 7 consecutive days

- **Legal**: Potential IP infringement or compliance violation

- **Strategic**: Core assumption invalidated (market fit, competition)

- **Team**: Key person departure without succession plan

**Risk Categories**:

- **Extreme**: Stop immediately, escalate

- **High**: Mitigate before proceeding

- **Moderate**: Monitor, have contingency

- **Low**: Accept, document

**Reference**: See RISK_FRAMEWORK.md for full framework

---

## STRATEGIC_LOAD (Current Priorities)

### Active Projects

#### 1. Gulfstream ERCOT Integration

**Status**: In development
**Purpose**: Real-time energy price optimization for Texas grid
**Target**: ERCOT market participants
**Success Metric**: $50K ARR from first 10 customers

**Key Decisions Pending**:

- API rate limiting strategy (awaiting ERCOT specs)

- Pricing model: SaaS vs. revenue share

- Go-to-market: Direct vs. channel partners

#### 2. Judge #6 Performance Optimization

**Status**: Active development
**Purpose**: Achieve p99≤90ms latency target
**Current**: p99=~150ms (67ms over target)
**Timeline**: 30-day sprint

**Optimization Areas**:

- Database query optimization (Est. 30ms reduction)

- Caching layer (Est. 25ms reduction)

- Algorithm efficiency (Est. 15ms reduction)

### Strategic Backlog


- ShadowTag integration (deferred pending Gulfstream validation)

- Multi-region deployment (deferred to post-revenue)

- Enterprise features (deferred until 50 customers)

---

## COMMS_PROTOCOL

### Communication Standards

**Format Requirements**:

- Use monospace code blocks for technical specs

- Include validation footer on strategic recommendations

- Exercise **objection duty**: Challenge assumptions, flag risks

**Validation Footer Template**:

```

VALIDATION
==========
JR_ENGINE:   [Purpose/Reasons/Brakes assessment]
GATES:       [Bootstrap gates passed/failed]
RISKS:       [Risk level + mitigation]
EVIDENCE:    [Tier 1-4 classification]
DECISION:    [Recommend/Defer/Reject]

```

**Objection Duty**:
Claude must actively challenge:

- Unfounded optimism

- Weak evidence (Tier 3-4 without acknowledgment)

- Scope creep vs. bootstrap constraints

- Technical complexity without clear ROI

- "Shiny object" syndrome

**Monospace Preference**:
Use code blocks for:

- Technical specifications

- Financial projections

- Decision frameworks

- Status reports

---

## TOKEN ECONOMICS

**Context Re-use Strategy**:

- **Projects approach**: Upload full docs (this file + references)

- **Estimated baseline**: ~15-20KB compressed

- **Session savings**: 40-60% vs. re-explaining context

- **Trade-off**: Richer context, no 500-line skill limit

**Best Practices**:

- Reference specific sections (e.g., "JR_ENGINE framework")

- Link to detailed docs for deep dives

- Keep Cor_vX.md updated as source of truth

- Version docs clearly (v1.0, v1.1, etc.)

---

## VERSION HISTORY

**v1.0** (2025-11-14):

- Initial framework consolidation

- JR_ENGINE, BOOTSTRAP_GATES, TECHNICAL_SLA, RISK_FRAMEWORK defined

- Strategic load: Gulfstream ERCOT, Judge #6 optimization

- Comms protocol standardized

---

## QUICK REFERENCE

**Before any major decision, ask**:

1. What's the PURPOSE? (JR_ENGINE)

2. What EVIDENCE supports it? (Tier 1-4)

3. Which GATES does it pass/fail? (Bootstrap)

4. What RISKS exist? (ATP 5-19)

5. What are the BRAKES? (Kill-switch criteria)

**For technical work**:

- Judge #6: p99≤90ms, p50≤30ms

- Core stack: Python 3.11+, FastAPI, PostgreSQL 15+

- Cloud-agnostic, modular, resilient

**For financial decisions**:

- Burn limit: $60-65K

- ROI threshold: ≥3×

- LTV:CAC: ≥4:1

**Strategic priorities** (in order):

1. Gulfstream ERCOT → Revenue validation

2. Judge #6 optimization → Technical foundation

3. Backlog deferred until revenue proven

---

## RELATED DOCUMENTS


- [JR_ENGINE.md](./JR_ENGINE.md) - Full decision framework specification

- [BOOTSTRAP_GATES.md](./BOOTSTRAP_GATES.md) - Financial constraints detail

- [TECHNICAL_SLA.md](./TECHNICAL_SLA.md) - Performance standards

- [RISK_FRAMEWORK.md](./RISK_FRAMEWORK.md) - ATP 5-19 implementation

- [PROJECT_SETUP.md](./PROJECT_SETUP.md) - Claude Projects integration guide

---

**END Cor_v1.md**
