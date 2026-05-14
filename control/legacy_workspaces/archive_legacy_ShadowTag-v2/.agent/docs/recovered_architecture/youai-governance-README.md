# YouAi Governance Service

Full governance, compliance, and infrastructure management service implementing EU AI Act, DSA, NIST RMF, ISO 42001, and adtech standards.

## Overview

The YouAi Governance Service provides comprehensive compliance and governance capabilities for AI-driven content platforms. All AI personas run at **IQ 160** for maximum foresight, innovation depth, and risk detection.

### Key Features



- **🏛️ EU AI Act Compliance**: Risk classification, transparency, human oversight


- **📋 DSA VLOP**: Systemic risk assessments, recommender explainability


- **🔒 NIST AI RMF 1.0**: Govern, Map, Measure, Manage framework


- **✅ ISO/IEC 42001**: AI management system controls


- **📺 Adtech Standards**: VAST 4.x, OM SDK, Privacy Sandbox, SKAdNetwork


- **🔐 Content Provenance**: C2PA integration and chain of custody


- **♿ Accessibility**: WCAG 2.2, COPPA, Age Appropriate Design Code


- **📊 Monitoring**: OpenTelemetry, metrics, KPI tracking

## Quick Start

### Local Deployment (Docker)



1. **Clone and navigate to the repository**

```bash
cd aiyou-fastapi-services

```



2. **Copy environment configuration**

```bash
cp .env.example .env

```



3. **Start services with Docker Compose**

```bash
docker-compose up -d

```



4. **Verify services are running**

```bash
docker-compose ps

```



5. **Access the API**


- API Documentation: http://localhost:8000/docs


- Health Check: http://localhost:8000/health


- KPI Dashboard: http://localhost:8000/api/v1/kpi/dashboard

### Local Development (Python)



1. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```



2. **Install dependencies**

```bash
pip install -r requirements.txt

```



3. **Run the service**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

```

## API Endpoints

### Governance



- `POST /api/v1/governance/assess` - Comprehensive governance assessment


- `POST /api/v1/governance/eu-ai-act/assess` - EU AI Act specific assessment


- `POST /api/v1/governance/nist-rmf/assess` - NIST RMF assessment


- `POST /api/v1/governance/iso-42001/assess` - ISO 42001 assessment

### Adtech Compliance



- `POST /api/v1/adtech/vast/validate` - VAST XML validation


- `POST /api/v1/adtech/omsdk/verify` - OM SDK verification


- `POST /api/v1/adtech/privacy-sandbox/check` - Privacy Sandbox compliance


- `POST /api/v1/adtech/brand-safety/check` - Brand safety verification

### Content Provenance



- `POST /api/v1/content/c2pa/verify` - Verify C2PA credentials


- `POST /api/v1/content/provenance/create` - Create provenance record


- `GET /api/v1/content/provenance/{content_id}` - Get provenance

### Accessibility



- `POST /api/v1/accessibility/wcag/audit` - WCAG 2.2 audit


- `POST /api/v1/accessibility/coppa/check` - COPPA compliance


- `POST /api/v1/accessibility/aadc/check` - AADC compliance

### Recommender



- `POST /api/v1/recommender/explain` - Explain recommendation (DSA Article 27)


- `POST /api/v1/recommender/config/update` - Update user preferences


- `POST /api/v1/recommender/non-profiled` - Non-profiled feed

### KPI Tracking



- `GET /api/v1/kpi/dashboard` - Comprehensive KPI dashboard


- `GET /api/v1/kpi/category/{category}` - Category-specific KPIs


- `GET /api/v1/kpi/report/30-60-90` - Gap closure plan status

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash

# Persona IQ Override (locked at 160)

PERSONA_IQ_OVERRIDE=160

# Governance Frameworks

EU_AI_ACT_ENABLED=true
DSA_VLOP_MODE=false
NIST_RMF_ENABLED=true
ISO_42001_ENABLED=true

# Content Safety

BRAND_SAFETY_THRESHOLD=0.85
C2PA_VERIFICATION_ENABLED=true

# Adtech

VAST_VERSION=4.3
OM_SDK_ENABLED=true
PRIVACY_SANDBOX_ENABLED=true

# Accessibility

WCAG_LEVEL=AA
COPPA_MODE_ENABLED=true

```

## Architecture

### Service Components

```

app/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── api/
│   └── v1/               # API v1 routes
│       ├── governance.py
│       ├── adtech.py
│       ├── content.py
│       ├── accessibility.py
│       ├── recommender.py
│       └── kpi.py
├── core/
│   ├── middleware.py     # Rate limiting, CORS
│   └── observability.py  # OpenTelemetry setup
├── models/               # Pydantic models
│   ├── governance.py
│   ├── adtech.py
│   ├── content.py
│   └── accessibility.py
└── services/             # Business logic engines
    ├── governance_engine.py
    ├── adtech_engine.py
    ├── content_engine.py
    └── accessibility_engine.py

```

## Governance Frameworks

### EU AI Act



- **Risk Classification**: Unacceptable, High, Limited, Minimal


- **Transparency**: AI disclosure, system documentation


- **Human Oversight**: For high-risk systems


- **Conformity Assessment**: Required for high-risk AI

### DSA VLOP



- **Recommender Transparency**: "Why this content?" explanations


- **User Controls**: Personalization toggle, topic blocking


- **Non-profiled Feed**: Recommendations without profiling


- **Risk Assessments**: Systemic risk mitigation

### NIST AI RMF



- **GOVERN**: Policies, processes, roles


- **MAP**: Context and risk categorization


- **MEASURE**: Analysis and assessment


- **MANAGE**: Prioritization and planning

### ISO/IEC 42001



- Context of organization


- Leadership and commitment


- Planning and support


- Operation and performance evaluation


- Continuous improvement

## Monitoring & Observability

### OpenTelemetry Integration

The service includes full OpenTelemetry instrumentation:



- **Traces**: Request tracing across services


- **Metrics**: HTTP requests, errors, latency


- **Logs**: Structured logging with context

Access Prometheus metrics at: http://localhost:8888/metrics

### KPI Dashboard

Monitor key performance indicators:



- **Safety/Compliance**: C2PA coverage, brand safety, DSA compliance


- **Monetization**: Viewability, VAST success, CPM premium


- **Reliability**: Latency, uptime, error rates


- **Governance**: Risk assessments, audit coverage, Persona IQ

## Testing

```bash

# Run tests

pytest

# Run with coverage

pytest --cov=app --cov-report=html

# Run specific test file

pytest tests/test_governance.py

```

## Cloud Deployment

### Docker Registry

```bash

# Build image

docker build -t youai-governance:latest .

# Tag for registry

docker tag youai-governance:latest registry.example.com/youai-governance:latest

# Push to registry

docker push registry.example.com/youai-governance:latest

```

### Kubernetes

See `k8s/` directory for Kubernetes manifests (deployment, service, ingress, configmap).

### Environment-Specific Configuration



- **Development**: `.env` with DEBUG=true


- **Staging**: Load from secret management (AWS Secrets Manager, etc.)


- **Production**: Full observability, rate limiting, TLS

## Security



- **Rate Limiting**: 100 requests/minute per IP (configurable)


- **CORS**: Configurable allowed origins


- **Input Validation**: Pydantic models with strict validation


- **Non-root Container**: Runs as user `youai` (UID 1000)


- **Health Checks**: Built-in liveness/readiness probes

## Performance



- **Async/Await**: Full async support with FastAPI


- **Connection Pooling**: PostgreSQL and Redis connection pools


- **Caching**: Redis caching for frequently accessed data


- **Compression**: GZip middleware for responses

## 30-60-90 Day Plan

### 30 Days ✅



- [x] Map YRM↔️NIST RMF↔️ISO 42001 controls


- [x] Choose adtech baseline: VAST 4.x + OM SDK


- [x] WCAG 2.2 audit + minors' defaults

### 60 Days 🏗️



- [ ] C2PA Content Credentials live


- [ ] SKAN/Topics instrumentation


- [x] OpenTelemetry + SBOM/SLSA pipeline

### 90 Days 📋



- [ ] Advertiser dashboard (OM viewability + brand-safety)


- [ ] Publish YouAi Governance Report v0.1


- [ ] Infra decision: Blackwell + Trainium2/Azure Maia

## License

Proprietary - YouAi Platform

## Support



- Documentation: `/docs`


- Health Check: `/health`


- API Reference: `/redoc`

---

**Persona IQ**: All AI personas run at **160 IQ** for maximum foresight, innovation depth, and risk detection.

**Version**: 1.0.0
**Last Updated**: 2024-11-17
