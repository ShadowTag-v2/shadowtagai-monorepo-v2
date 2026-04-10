# Ultrathink Setup Guide

Complete setup guide for integrating Anthropic Claude API and deploying the Ultrathink framework.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Anthropic API Integration](#anthropic-api-integration)
4. [Running the Application](#running-the-application)
5. [Testing the Integration](#testing-the-integration)
6. [Deployment to Google Cloud](#deployment-to-google-cloud)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **Python 3.11+**
- **pip** or **Poetry** (package manager)
- **Git**
- **Anthropic API Key** (from [console.anthropic.com](https://console.anthropic.com))

### Optional (for production)

- **Google Cloud Account** (for Vertex AI / GKE deployment)
- **Docker** (for containerized deployment)

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ehanc69/pnkln-stack-fastapi-services
cd pnkln-stack-fastapi-services
```

### 2. Create Virtual Environment

```bash
# Using venv
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using Poetry
poetry install
poetry shell
```

### 3. Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# Or using Poetry
poetry install
```

---

## Anthropic API Integration

### 1. Get Your API Key

1. Visit [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to **API Keys**
4. Create a new API key
5. **Copy the key** (you won't see it again!)

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```bash
# Anthropic Claude API
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_MAX_TOKENS=4096
ANTHROPIC_TEMPERATURE=0.7

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Revenue & Monitoring
ENABLE_REVENUE_TRACKING=true
ENABLE_COST_MONITORING=true
```

### 3. Verify Configuration

```python
from ultrathink.config import settings

print(f"API Key configured: {bool(settings.anthropic_api_key)}")
print(f"Model: {settings.anthropic_model}")
print(f"Environment: {settings.environment}")
```

---

## Running the Application

### 1. Start the FastAPI Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. Access the API Documentation

Open your browser and visit:

- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/

---

## Testing the Integration

### 1. Test Simple Prompting

```bash
curl -X POST "http://localhost:8000/prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "technique": "RTF",
    "user_input": "Analyze the SaaS market for 2025",
    "params": {
      "role": "market analyst",
      "task": "identify top 3 trends",
      "format": "bullet points"
    }
  }'
```

Expected response:

```json
{
  "technique": "RTF",
  "formatted_prompt": "You are a market analyst...",
  "result": {
    "response": "Based on analysis of 2025 SaaS trends...",
    "metadata": {
      "model": "claude-sonnet-4-5-20250929",
      "tokens_input": 45,
      "tokens_output": 312,
      "cost_usd": 0.00486,
      "latency_ms": 1247
    }
  }
}
```

### 2. Test Chain-of-Thought Reasoning

```bash
curl -X POST "http://localhost:8000/reason" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "CoT",
    "problem": "If a SaaS has $10k MRR and 5% monthly churn, what is the customer lifetime value?",
    "params": {
      "steps": 5,
      "verify": true
    }
  }'
```

### 3. Test Multi-Agent Debate

```bash
curl -X POST "http://localhost:8000/multi-agent" \
  -H "Content-Type: application/json" \
  -d '{
    "system": "MAD",
    "task": "Should we build microservices or stick with a monolith for a new SaaS product?",
    "agents": 3,
    "rounds": 3
  }'
```

### 4. Test BugBot Triage

```bash
curl -X POST "http://localhost:8000/bugbot/triage" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "API returns 500 error on /users endpoint",
    "body": "When calling GET /api/users, the server returns 500. Logs show KeyError for database_url in config.",
    "labels": ["api", "backend"],
    "author": "user123"
  }'
```

Expected response:

```json
{
  "triage": {
    "severity": "high",
    "category": "bug",
    "priority_score": 8,
    "estimated_hours": 4.0,
    "suggested_labels": ["high", "bug"],
    "auto_fix_possible": false,
    "reasoning": "This is a high-severity production bug affecting API availability..."
  },
  "time_saved_usd": 18.75
}
```

---

## Deployment to Google Cloud

### Vertex AI Workbench (Development/Staging)

```bash
# 1. Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# 2. Initialize and authenticate
gcloud init
gcloud auth application-default login

# 3. Set project
gcloud config set project YOUR_PROJECT_ID

# 4. Create .env with production settings
ENVIRONMENT=production
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_PROJECT_ID=your-project-id

# 5. Run the application
uvicorn main:app --host 0.0.0.0 --port 8080
```

### GKE Native (Production)

#### 1. Build Docker Image

```bash
docker build -t gcr.io/YOUR_PROJECT_ID/ultrathink:v1.0 .
docker push gcr.io/YOUR_PROJECT_ID/ultrathink:v1.0
```

#### 2. Create GKE Cluster

```bash
gcloud container clusters create ultrathink-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 20
```

#### 3. Create Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ultrathink
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ultrathink
  template:
    metadata:
      labels:
        app: ultrathink
    spec:
      containers:
        - name: ultrathink
          image: gcr.io/YOUR_PROJECT_ID/ultrathink:v1.0
          ports:
            - containerPort: 8000
          env:
            - name: ANTHROPIC_API_KEY
              valueFrom:
                secretKeyRef:
                  name: ultrathink-secrets
                  key: anthropic-api-key
```

#### 4. Deploy

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

---

## Troubleshooting

### Issue: "API key required in production mode"

**Solution**: Ensure `.env` file has `ANTHROPIC_API_KEY` set.

```bash
# Check if .env exists
ls -la .env

# Verify content
cat .env | grep ANTHROPIC_API_KEY
```

### Issue: "Invalid Anthropic API key format"

**Solution**: API key must start with `sk-ant-`.

```bash
# Correct format
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Incorrect
ANTHROPIC_API_KEY=xxxxx  # Missing prefix
```

### Issue: "ModuleNotFoundError: No module named 'anthropic'"

**Solution**: Install dependencies.

```bash
pip install -r requirements.txt
```

### Issue: High latency on first request

**Expected behavior**: First request initializes Anthropic client (~1-2 seconds).
Subsequent requests are much faster.

### Issue: "429 Rate Limit Error"

**Solution**: Anthropic free tier has rate limits. Upgrade plan or add retry logic (already included in `LLMExecutor`).

### Issue: Costs tracking shows $0 despite API calls

**Solution**: Ensure `ENABLE_COST_MONITORING=true` in `.env`.

---

## Next Steps

1. **Run examples**: `python examples/quickstart.py`
2. **Test BugBot**: `python bugbot.py`
3. **Explore API docs**: http://localhost:8000/docs
4. **Check revenue metrics**: http://localhost:8000/analytics/revenue
5. **Deploy to production**: Follow GKE Native guide above

---

## Support

- **Documentation**: [README.md](../README.md)
- **Quickstart**: [QUICKSTART.md](../QUICKSTART.md)
- **Issues**: https://github.com/ehanc69/pnkln-stack-fastapi-services/issues

---

**Built with obsession. Deployed with precision. Optimized for revenue.**
