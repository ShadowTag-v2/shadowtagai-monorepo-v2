# UnGPT Deployment Guide

## Quick Start (5 Minutes)

### **Prerequisites**

- Python 3.10+
- Redis (for cost tracking)
- API Keys:
  - Anthropic (Claude)
  - Google (Gemini)
  - OpenAI (optional, for GPT-5)
  - xAI (optional, for Grok)

---

## Step 1: Environment Setup

```bash
# Clone repository (if not already done)
cd /home/user/ShadowTag-v2-fastapi-services

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-ungpt.txt
```

---

## Step 2: Configure Environment Variables

Create `.env` file:

```bash
# .env
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional
XAI_API_KEY=your_xai_key_here         # Optional

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Budget configuration (optional)
MAX_DAILY_SPEND=10.00
MAX_COST_PER_QUERY=0.50
```

**Get API Keys:**

- Anthropic: https://console.anthropic.com/
- Google AI Studio: https://makersuite.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys
- xAI: https://x.ai/api

---

## Step 3: Start Redis (Local Development)

### **Option A: Docker (Recommended)**

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### **Option B: Homebrew (Mac)**

```bash
brew install redis
brew services start redis
```

### **Option C: Skip Redis**

If you don't have Redis, the service will still work but won't track budgets.

---

## Step 4: Run the Service

```bash
# Development mode with auto-reload
uvicorn ungpt_service:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn ungpt_service:app --host 0.0.0.0 --port 8000 --workers 4
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

## Step 5: Test the Service

### **Test 1: Health Check**

```bash
curl http://localhost:8000/v1/ungpt/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "ungpt-consensus",
  "timestamp": "2025-11-08T12:00:00.000000"
}
```

### **Test 2: Simple Query**

```bash
curl -X POST http://localhost:8000/v1/ungpt/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_key_123" \
  -d '{
    "query": "What is edge computing?",
    "user_location": "US",
    "max_cost": 0.50
  }'
```

Expected response:

```json
{
  "final_answer": "Edge computing is...",
  "confidence_score": 0.85,
  "consensus_level": "single_model",
  "execution_time_seconds": 2.3,
  "total_cost": 0.017,
  "models_consulted": ["claude-sonnet-4"],
  "risk_level": "RA-1",
  "query_tier": "simple"
}
```

### **Test 3: Complex Query (Force Full Consensus)**

```bash
curl -X POST http://localhost:8000/v1/ungpt/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_key_123" \
  -d '{
    "query": "Analyze the business viability of deploying GPU compute at cell tower sites, covering technical feasibility, cost structure, partnerships, competitive advantages, and 5-year financial projections",
    "complexity": "complex",
    "user_location": "US",
    "max_cost": 0.50,
    "include_reasoning": true
  }'
```

### **Test 4: Check Budget Status**

```bash
curl http://localhost:8000/v1/ungpt/budget/test_user_123
```

---

## Step 6: Deploy to Vertex AI Workbench

### **Option A: Deploy as Notebook**

1. **Upload files to Workbench:**

```bash
# From your local machine
gsutil -m cp ungpt_service.py gs://your-bucket/ungpt/
gsutil -m cp requirements-ungpt.txt gs://your-bucket/ungpt/
```

2. **In Workbench notebook:**

```python
# Install dependencies
!pip install -r requirements-ungpt.txt

# Set environment variables
import os
os.environ["ANTHROPIC_API_KEY"] = "your_key"
os.environ["GOOGLE_API_KEY"] = "your_key"

# Run service in background
import subprocess
subprocess.Popen([
    "uvicorn", "ungpt_service:app",
    "--host", "0.0.0.0",
    "--port", "8000"
])
```

3. **Access via Workbench proxy:**

```
https://your-workbench-url.notebooks.googleusercontent.com/proxy/8000/
```

---

### **Option B: Deploy to Cloud Run (Recommended for Production)**

1. **Create Dockerfile:**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-ungpt.txt .
RUN pip install --no-cache-dir -r requirements-ungpt.txt

COPY ungpt_service.py .

CMD ["uvicorn", "ungpt_service:app", "--host", "0.0.0.0", "--port", "8080"]
```

2. **Build and deploy:**

```bash
# Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT/ungpt-service

# Deploy to Cloud Run
gcloud run deploy ungpt-service \
  --image gcr.io/YOUR_PROJECT/ungpt-service \
  --platform managed \
  --region us-central1 \
  --set-env-vars ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY \
  --max-instances 10 \
  --memory 2Gi \
  --timeout 300 \
  --allow-unauthenticated
```

3. **Get your service URL:**

```bash
gcloud run services describe ungpt-service --region us-central1 --format 'value(status.url)'
```

---

## Step 7: Voice Client Setup (Optional)

If you want push-to-talk voice interface:

```bash
# Install voice dependencies
pip install pyaudio whisper SpeechRecognition keyboard rich

# Download Whisper model (one-time, ~150MB)
python -c "import whisper; whisper.load_model('base')"

# Run voice client
python ungpt_voice_client.py --mode push-to-talk
```

**Hotkey:** Hold `Ctrl+Shift+Space`, speak, release

---

## Configuration Options

### **Budget Limits (in ungpt_service.py)**

```python
DAILY_BUDGET = {
    "simple_queries": 100,      # Max simple queries per day
    "moderate_queries": 30,     # Max moderate queries per day
    "complex_queries": 15,      # Max complex queries per day
    "max_daily_spend": 10.00    # Hard cap in USD
}

QUERY_LIMITS = {
    "max_cost_per_query": 0.50,       # Per-query limit
    "require_approval_above": 0.30     # Manual approval threshold
}
```

### **Model Configuration**

To add Grok and GPT-5 support, update `execute_complex_path()`:

```python
# Execute Layer 2 in parallel
layer2_tasks = [
    query_gemini(layer1_text, query),
    query_grok(layer1_text, query),      # Add this
    query_gpt5(layer1_text, query)       # Add this
]

results = await asyncio.gather(*layer2_tasks)
```

---

## Monitoring & Observability

### **Cost Tracking**

View daily spend:

```bash
curl http://localhost:8000/v1/ungpt/budget/your_user_id
```

### **Prometheus Metrics (Optional)**

Add to `ungpt_service.py`:

```python
from prometheus_client import Counter, Histogram, generate_latest

query_counter = Counter('ungpt_queries_total', 'Total queries', ['tier'])
query_duration = Histogram('ungpt_query_duration_seconds', 'Query duration', ['tier'])
query_cost = Histogram('ungpt_query_cost_dollars', 'Query cost', ['tier'])

# In each execution path:
query_counter.labels(tier=request.complexity).inc()
query_duration.labels(tier=request.complexity).observe(execution_time)
query_cost.labels(tier=request.complexity).observe(total_cost)

# Add metrics endpoint:
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### **Sentry Error Tracking (Optional)**

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1
)
```

---

## Troubleshooting

### **Issue: "Redis connection refused"**

```
Solution: Start Redis or set REDIS_HOST to your Redis instance
```

### **Issue: "API key not found"**

```
Solution: Ensure .env file is in working directory or set env vars directly:
export ANTHROPIC_API_KEY=your_key
```

### **Issue: "Budget exceeded"**

```
Solution: Check current spend:
curl http://localhost:8000/v1/ungpt/budget/your_user_id

Reset daily limit (increase in code):
DAILY_BUDGET["max_daily_spend"] = 20.00
```

### **Issue: "Query timeout"**

```
Solution: Increase timeout in uvicorn:
uvicorn ungpt_service:app --timeout-keep-alive 300
```

### **Issue: "Whisper model download hangs"**

```
Solution: Download manually:
python -c "import whisper; whisper.load_model('base', download_root='./models')"
```

---

## Security Hardening (Production)

### **1. API Key Authentication**

Replace simple bearer token with JWT:

```python
from jose import JWTError, jwt

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def verify_token(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### **2. Rate Limiting**

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/v1/ungpt/query")
@limiter.limit("10/minute")
async def process_query(...):
    ...
```

### **3. Input Validation**

```python
class UnGPTRequest(BaseModel):
    query: str = Field(..., max_length=10000, description="User query")

    @validator('query')
    def validate_query(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Query too short")
        # Check for injection attempts
        if any(x in v.lower() for x in ['<script>', 'DROP TABLE', 'rm -rf']):
            raise ValueError("Invalid query content")
        return v
```

### **4. HTTPS Only**

In production, always use HTTPS:

```bash
# Cloud Run automatically provides HTTPS
# For custom deployments, use nginx + Let's Encrypt
```

---

## Cost Optimization Tips

1. **Enable caching for common queries:**

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_simple_query(query: str) -> str:
    # Cache simple factual queries
    pass
```

2. **Batch similar queries:**
   Process multiple related queries in one consensus session

3. **Use simple tier by default:**
   Only escalate to complex when user explicitly requests or query classifier has high confidence

4. **Monitor per-user costs:**
   Set per-user daily limits to prevent abuse

---

## Next Steps

1. ✅ Deploy to Vertex AI Workbench or Cloud Run
2. ⏳ Test with 10-20 real queries
3. ⏳ Monitor costs for 7 days
4. ⏳ Adjust budget limits based on usage
5. ⏳ Add voice client if desired
6. ⏳ Integrate with existing PNKLN services

**Support:** Check docs/ folder for additional guides or open an issue.
