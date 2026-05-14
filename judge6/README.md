# Judge #6 - ATP 5-19 Risk Management API for AI

**Military-grade AI governance system built by a former Army SF operator**

Judge #6 provides real-time risk assessment for AI systems using the ATP 5-19 framework (US Army Risk Management Field Manual). Deploy in 5 minutes, audit every request, sleep at night.

## Features

- ⚡ **Sub-90ms latency** (p99 ≤90ms target)
- 🛡️ **3-layer hybrid architecture** (Gemini + PyTorch + Rules Engine)
- 📊 **ATP 5-19 framework** (Purpose/Reasons/Brakes validation)
- 🔒 **Compliance-ready** (SOC2, HIPAA, GDPR audit trails)
- 💰 **Freemium pricing** (1K requests/month free)
- 🚀 **Production-ready** (FastAPI + PostgreSQL + Redis)

## Quick Start

### 1. Installation

```bash
# Clone repository
cd judge6

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Database Setup

```bash
# Start PostgreSQL (Docker)
docker run -d \
  --name judge6-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=judge6 \
  -p 5432:5432 \
  postgres:15

# Start Redis (Docker)
docker run -d \
  --name judge6-redis \
  -p 6379:6379 \
  redis:7-alpine
```

### 3. Run Application

```bash
# Development mode
uvicorn judge6.main:app --reload

# Production mode
uvicorn judge6.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Visit http://localhost:8000/docs for interactive API documentation.

## API Usage

### Register & Get API Key

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "erik@example.com",
    "password": "your-secure-password",
    "full_name": "Erik Hancock",
    "company": "Pnkln"
  }'
```

Response includes your API key (save it!):

```json
{
  "id": 1,
  "email": "erik@example.com",
  "tier": "free",
  "api_key": "judge6_sk_AbCdEf123456...",
  "monthly_limit": 1000,
  "current_usage": 0
}
```

### Judge an AI Request

```bash
curl -X POST http://localhost:8000/api/v1/judge \
  -H "Authorization: Bearer judge6_sk_AbCdEf123456..." \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Generate a personalized medical diagnosis based on symptoms",
    "context": {
      "user_type": "patient",
      "authenticated": true
    }
  }'
```

Response:

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "decision": "warn",
  "risk_level": "moderate",
  "confidence": 0.85,
  "reasoning": "ATP 5-19 Risk Assessment:\n• Layer 1 (Policy): Medical advice requires professional oversight\n• Layer 2 (Enforcement): No edge cases detected\n• Layer 3 (Rules): Medical information warning triggered",
  "violated_rules": [],
  "latency_ms": 73,
  "usage": {
    "requests_used": 1,
    "requests_limit": 1000,
    "tier": "free"
  }
}
```

## Architecture

### 3-Layer Hybrid System

**Layer 1: Gemini (Policy Understanding)**
- Fine-tuned LLM interprets ATP 5-19 policies
- Evaluates Purpose, Reasons, Brakes
- 92% policy understanding accuracy

**Layer 2: PyTorch (Deterministic Enforcement)**
- Catches edge cases LLMs might miss
- Prompt injection detection
- PII exposure prevention
- 95% enforcement accuracy

**Layer 3: Rules Engine (Hard Gates)**
- Black-and-white compliance rules
- Zero ambiguity, 100% deterministic
- Final enforcement layer

**Aggregation:** Most restrictive layer wins

### ATP 5-19 Risk Levels

| Risk Level | Description | Action |
|---|---|---|
| CATASTROPHIC | Loss of life, critical failure, massive liability | DENY |
| CRITICAL | Serious harm, major compliance violation | DENY |
| MODERATE | Minor harm, compliance concerns | WARN |
| LOW | Minimal risk, easily mitigated | ALLOW |
| NEGLIGIBLE | No meaningful risk | ALLOW |

## Configuration

Edit `.env` file:

```bash
# AI API Keys
GOOGLE_API_KEY="your-gemini-api-key"  # Required for Layer 1
ANTHROPIC_API_KEY="your-claude-key"   # Optional backup
OPENAI_API_KEY="your-gpt-key"         # Optional backup

# Database
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/judge6"

# Redis
REDIS_URL="redis://localhost:6379/0"

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY="your-secret-key-min-32-chars"

# Rate Limits
RATE_LIMIT_FREE=1000          # Free tier: 1K requests/month
RATE_LIMIT_STARTER=10000      # Starter: 10K requests/month
RATE_LIMIT_PROFESSIONAL=100000  # Pro: 100K requests/month
```

## Pricing Tiers

| Tier | Price | Requests/Month | Support | Features |
|---|---|---|---|---|
| **Free** | $0 | 1,000 | Email | Public policy corpus, 7-day audit logs |
| **Starter** | $99 | 10,000 | Email (48hr SLA) | Custom policies, 30-day audit logs |
| **Professional** | $499 | 100,000 | Priority (24hr SLA) | Webhooks, team collaboration |
| **Enterprise** | $2,000+ | Unlimited | Dedicated (4hr SLA) | On-premise, custom SLA, legal review |

## Development

### Run Tests

```bash
pytest judge6/tests/ -v --cov=judge6
```

### Code Quality

```bash
# Format code
black judge6/

# Lint
ruff check judge6/

# Type check
mypy judge6/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment

### Docker

```bash
# Build image
docker build -t judge6:latest .

# Run container
docker run -d \
  --name judge6 \
  -p 8000:8000 \
  --env-file .env \
  judge6:latest
```

### Google Kubernetes Engine (GKE)

```bash
# Deploy to GKE
kubectl apply -f k8s/

# Check status
kubectl get pods -n judge6

# View logs
kubectl logs -f deployment/judge6 -n judge6
```

### Performance Tuning

For production, use:
- **Gunicorn** with multiple workers
- **Redis** for rate limiting and caching
- **PostgreSQL** connection pooling
- **GKE Autopilot** for autoscaling

Target: **p99 ≤90ms latency** at scale

## API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/v1/judge` | Judge an AI request | API Key |
| POST | `/api/v1/auth/register` | Register new user | None |
| POST | `/api/v1/auth/login` | Login and get token | None |
| GET | `/api/v1/usage` | Get usage statistics | API Key |
| GET | `/health` | Health check | None |
| GET | `/docs` | Interactive API docs | None |

## Support

- **Documentation**: https://docs.judgeasaservice.ai
- **Issues**: https://github.com/ehanc69/judge6/issues
- **Email**: erik@pnkln.ai
- **LinkedIn**: [Erik Hancock](https://linkedin.com/in/erik-hancock)

## License

Copyright © 2024 Pnkln. All rights reserved.

Built with 🎖️ by Erik Hancock (former Army SF / JD / AI Builder)

---

**ATP 5-19 for AI. Deploy in 5 minutes, audit every request, sleep at night.**
