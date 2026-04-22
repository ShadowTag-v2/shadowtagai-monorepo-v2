# FastAPI Governance Engine

**Sub-90ms p99 latency | 100% security gate**

## Quick Start

```bash

# Install dependencies

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server

uvicorn main:app --reload --port 8000

# Run tests

pytest tests/ --cov=. --cov-report=html

# Format code

black main.py
ruff check main.py

```

## API Endpoints

### `GET /health`

Health check for GKE probes.

**Response**:

```json
{
  "status": "healthy",
  "service": "pnkln-governance-api",
  "version": "0.1.0"
}

```

### `POST /decide`

AI governance decision endpoint.

**Headers**:


- `X-API-Key`: Required (set via `PNKLN_API_KEY` env var)

**Request**:

```json
{
  "context": "User uploaded file with PII: names, SSNs, addresses",
  "risk_tolerance": "low",
  "require_rationale": true
}

```

**Response**:

```json
{
  "decision": "reject",
  "confidence": 0.92,
  "rationale": "Context contains high-risk PII without encryption",
  "processing_time_ms": 45.3,
  "timestamp": "2025-11-16T12:34:56.789Z"
}

```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PNKLN_API_KEY` | Yes | `dev-key-insecure` | API key for endpoint authentication |

## Docker Build

```bash

# Build image

docker build -t pnkln-fastapi:latest .

# Run container

docker run -p 8000:8000 -e PNKLN_API_KEY=your-key pnkln-fastapi:latest

# Test health endpoint

curl http://localhost:8000/health

```

## SLA Targets

| Metric | Target | Current |
|--------|--------|---------|
| p99 latency | <90ms | TBD |
| p95 latency | <50ms | TBD |
| Uptime | 99.9% | TBD |
| Error rate | <0.1% | TBD |

## Next Steps



- [ ] Integrate Judge 6 AI engine for real decision logic


- [ ] Add pytest test suite (target: 85%+ coverage)


- [ ] Implement rate limiting (100 req/min per API key)


- [ ] Add structured logging (JSON format for GCP Cloud Logging)


- [ ] Performance benchmarking with locust/k6
