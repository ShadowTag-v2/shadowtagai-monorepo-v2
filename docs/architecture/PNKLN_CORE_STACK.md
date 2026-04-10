# PNKLN Core Stack™ Architecture

## Overview

The PNKLN Core Stack™ is an intelligence collection and processing pipeline designed for automated data ingestion, validation, and delivery. The stack operates on Google Kubernetes Engine (GKE) with a microservices architecture spanning multiple namespaces.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     PNKLN Core Stack™                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────┐         ┌──────────────────────┐       │
│  │  Gemini Ingestion   │────────>│     Judge #6         │       │
│  │       Layer         │         │  Validation Layer    │       │
│  │                     │         │                      │       │
│  │  • Multi-source     │         │  • ATP 5-19 Rules    │       │
│  │  • Ethical crawling │         │  • JR Validation     │       │
│  │  • Tier classification       │  • FP/FN Detection   │       │
│  │  • GKE CronJob      │         │  • Hybrid AI         │       │
│  └─────────────────────┘         └──────────────────────┘       │
│           │                                │                     │
│           └────────────────┬───────────────┘                     │
│                            │                                     │
│                            ▼                                     │
│                 ┌──────────────────────┐                         │
│                 │  Processing Services │                         │
│                 │  (4 Namespaces)      │                         │
│                 └──────────────────────┘                         │
│                            │                                     │
│                            ▼                                     │
│                 ┌──────────────────────┐                         │
│                 │   AM Briefing        │                         │
│                 │   Delivery           │                         │
│                 └──────────────────────┘                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Gemini Ingestion Layer

**Role**: Proactive data collector and initial processor
**Type**: Upstream/preventive component
**Architecture**: GKE CronJob with multi-container setup
**Execution**: Nightly batch processing (~45 min runtime)

**Key Responsibilities**:

- Multi-source data collection (YouTube, Twitter, News, etc.)
- Ethical web crawling with robots.txt compliance
- Rate limiting and transparency
- Tier classification (Tier 1/2/3 prioritization)
- Cost-efficient operations (~$77/month)

**Quality Gates**:

- Daily items ingested (volume tracking)
- Source diversity metrics
- Cost per item efficiency
- Relevance scoring

**Documentation**: See [Gemini Ingestion Layer Specifications](./GEMINI_INGESTION_LAYER.md)

---

### 2. Judge #6 Validation Layer

**Role**: Reactive validator and enforcement system
**Type**: Downstream/reactive component
**Architecture**: Hybrid Gemini + PyTorch inference
**Execution**: Real-time processing with sub-90ms p99 latency

**Key Responsibilities**:

- ATP 5-19 compliance validation
- JR (Joint Resolution) validation
- False positive/negative detection
- Service call validation across 4 namespaces

**Quality Gates**:

- 98% test coverage requirement
- p99 latency ≤ 90ms
- Block rate monitoring
- API call cost tracking per validation

**Documentation**: See [Judge #6 Specifications](./JUDGE_SIX.md)

---

### 3. Processing Services

**Deployment**: 4 Kubernetes namespaces
**Integration Pattern**: Both layers call and are called by these services

**Namespaces**:

1. `ingestion-processing` - Raw data normalization
2. `validation-enforcement` - Rule application
3. `intelligence-analysis` - Pattern detection
4. `delivery-orchestration` - Output formatting

---

### 4. AM Briefing Delivery

**Purpose**: Morning intelligence summaries from processed data
**Inputs**: Validated, processed intelligence from the full stack
**Output Format**: Structured briefing documents
**Delivery SLA**: Pre-configured morning delivery time

**Effectiveness Metrics**:

- Timeliness (on-time delivery %)
- Completeness (coverage of expected topics)
- Format compliance
- User engagement tracking

---

## Data Flow

```
1. COLLECTION (Gemini Ingestion Layer)
   ↓
   - YouTube API queries
   - Twitter stream processing
   - News feed aggregation
   - Web crawling (ethical)
   ↓
   Tier Classification
   ↓

2. VALIDATION (Judge #6)
   ↓
   - ATP 5-19 rule checks
   - JR validation
   - Quality scoring
   ↓
   FP/FN Analysis
   ↓

3. PROCESSING (Service Layer)
   ↓
   - Namespace 1: Normalization
   - Namespace 2: Enforcement
   - Namespace 3: Analysis
   - Namespace 4: Orchestration
   ↓

4. DELIVERY (AM Briefing)
   ↓
   - Format generation
   - Distribution
   - Tracking
```

## Key Architectural Principles

### Separation of Concerns

- **Ingestion**: Focuses on ethical, broad collection
- **Validation**: Focuses on quality and compliance
- **Processing**: Focuses on transformation and analysis
- **Delivery**: Focuses on user experience

### Complementary Design

- Ingestion operates in **batch mode** (nightly cron) for efficiency
- Validation operates in **real-time mode** (sub-90ms) for responsiveness
- Different metrics optimize for different goals (volume vs. accuracy)

### Cost Optimization

- Ingestion: Monthly operational budget (~$77)
- Validation: Per-API-call cost model
- Combined: Sustainable at scale

### Quality Assurance

- Multi-layered validation (ingestion tier classification + Judge #6 validation)
- Comprehensive metrics at each stage
- End-to-end tracking from collection to delivery

---

## Technology Stack

### Infrastructure

- **Orchestration**: Google Kubernetes Engine (GKE)
- **Scheduling**: CronJob controllers
- **Containerization**: Multi-container pods

### AI/ML

- **Ingestion**: Gemini 2.0 Pro for content analysis
- **Validation**: Hybrid Gemini + PyTorch models
- **Analysis**: Custom pattern detection algorithms

### Data Sources

- YouTube API
- Twitter API
- News aggregation feeds
- Ethical web crawling targets

### Monitoring

- Runtime efficiency tracking
- Cost per item/operation
- Quality gate metrics
- Delivery SLA tracking

---

## Operational Metrics

### System-Wide KPIs

| Metric                                    | Target      | Current |
| ----------------------------------------- | ----------- | ------- |
| End-to-end latency (ingestion → delivery) | ≤ 12 hours  | -       |
| Daily items processed                     | ≥ 1000      | -       |
| Cost per intelligence item                | ≤ $0.10     | -       |
| AM Briefing on-time delivery              | ≥ 95%       | -       |
| Source diversity index                    | ≥ 5 sources | -       |

### Component-Specific Metrics

See individual component documentation for detailed metrics.

---

## Pre-Production Status

**Current Phase**: Analysis and optimization
**Target**: Production deployment Q1 2026

### Completed

- [x] Architecture design
- [x] Component specifications
- [x] Gemini analysis prompt development
- [x] Judge #6 analysis prompt development

### In Progress

- [ ] Performance benchmarking
- [ ] Cost modeling refinement
- [ ] Integration testing
- [ ] Documentation completion

### Planned

- [ ] Production deployment
- [ ] Real-world telemetry collection
- [ ] Continuous optimization
- [ ] Scaling plan execution

---

## Analysis Framework

Both core components (Ingestion Layer and Judge #6) are analyzed using Gemini 2.0 Pro with specialized prompts:

- **Gemini Ingestion Layer Analysis**: Focuses on collection efficiency, ethical compliance, tier classification
- **Judge #6 Analysis**: Focuses on validation accuracy, latency, coverage

**Confidence Targets**:

- Pre-production (spec-based): ≥60% confidence
- Production (telemetry-based): ≥70% confidence

See [Analysis Prompts](../prompts/) for full prompt specifications.

---

## Integration Points

### Inter-Component Communication

```
Services in Namespace 1-4
    ↓ (trigger)
Gemini Ingestion Layer
    ↓ (data handoff)
Services in Namespace 1-4
    ↓ (trigger)
Judge #6 Validation
    ↓ (validated data)
Services in Namespace 1-4
    ↓ (processed intelligence)
AM Briefing Delivery
```

### External Integrations

- **Data Sources**: APIs and crawling targets (see multi-source coverage)
- **Monitoring**: Prometheus/Grafana for metrics
- **Alerting**: PagerDuty for operational issues
- **Cost Tracking**: GCP billing integration

---

## Security & Compliance

### Ethical Crawling Standards

- robots.txt compliance
- Rate limiting per source
- Transparency in data collection
- Attribution and licensing respect

### Data Privacy

- PII detection and redaction
- Compliance with data retention policies
- Secure storage and transmission
- Access control and audit logging

### Operational Security

- Kubernetes security policies
- Secret management via GCP Secret Manager
- Network policies between namespaces
- Regular security audits

---

## Future Enhancements

### Phase 2 Capabilities

- Real-time ingestion for time-sensitive sources
- Advanced ML for tier classification
- Expanded source coverage (Reddit, LinkedIn, etc.)
- Multi-language support

### Scalability Improvements

- Auto-scaling for variable data volumes
- Multi-region deployment
- Advanced caching strategies
- Cost optimization via spot instances

### Intelligence Quality

- Sentiment analysis integration
- Entity extraction and linking
- Trend detection algorithms
- Predictive analytics

---

## References

- [Gemini Ingestion Layer Specifications](./GEMINI_INGESTION_LAYER.md)
- [Judge #6 Specifications](./JUDGE_SIX.md)
- [Analysis Prompts](../prompts/README.md)
- [Deployment Guide](../deployment/README.md)
- [Cost Model Documentation](./COST_MODEL.md)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-15
**Maintained By**: PNKLN Core Stack Team
