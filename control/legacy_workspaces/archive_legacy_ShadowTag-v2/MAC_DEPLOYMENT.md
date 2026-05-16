# Mac Local Deployment Guide

**Deploy AIYOU FastAPI Services as a running platform on your MacBook**

## 🎯 Overview

This guide shows you how to **deploy and run** the complete AIYOU platform locally, not just test individual components. You'll have:

- 🚀 FastAPI server running on http://localhost:8000
- 🤖 Multi-LLM consensus endpoints
- 🔐 Judge #6 validation layer
- 📊 Monitoring dashboard
- 🗄️ Local database for persistence
- 📥 Ingestion pipeline (optional scheduled job)

---

## ⚡ Quick Deploy (15 Minutes)

### Prerequisites

```bash
# Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11

# Verify
python3.11 --version
```

### Step 1: Environment Setup

```bash
# Navigate to project
cd ~/Projects/aiyou-fastapi-services

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install uvicorn[standard] fastapi python-multipart
```

### Step 2: Configuration

```bash
# Create production .env file
cat > .env << 'EOF'
# Environment
ENV=local
DEBUG=True

# Server
HOST=127.0.0.1
PORT=8000

# API Keys
GOOGLE_API_KEY=your-gemini-api-key-here
ANTHROPIC_API_KEY=your-claude-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
XAI_API_KEY=your-grok-api-key-here

# Database
DATABASE_URL=sqlite:///./data/aiyou.db

# Consensus Settings
CONSENSUS_ENABLED=true
JUDGE6_ENABLED=true
PNKLN_ENABLED=true

# Model Allocation
GEMINI_ALLOCATION=0.40
CLAUDE_ALLOCATION=0.35
GPT_ALLOCATION=0.15
PERPLEXITY_ALLOCATION=0.05
GROK_ALLOCATION=0.05

# Performance
MAX_WORKERS=4
TIMEOUT_SECONDS=60
P99_LATENCY_TARGET_MS=90

# Monitoring
PROMETHEUS_ENABLED=false
METRICS_PORT=9090
EOF

# Edit with your actual API keys
nano .env
```

**Get API Keys**:
- Gemini: https://aistudio.google.com/app/apikey (FREE tier: 1M tokens/day)
- Claude: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/api-keys (optional)
- Grok/X.AI: https://console.x.ai/ (optional)

### Step 3: Create Main Application

```bash
# Create main FastAPI app
cat > main.py << 'EOF'
"""
AIYOU FastAPI Services - Main Application
Local deployment configuration
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

# Import our components
from voice_consensus.consensus_with_posture import run_consensus_with_posture
from voice_consensus.consensus_ultrathink import run_ultrathink_consensus

# Initialize FastAPI
app = FastAPI(
    title="AIYOU FastAPI Services",
    description="Multi-LLM consensus with PNKLN validation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ConsensusRequest(BaseModel):
    query: str
    mode: Optional[str] = "standard"  # standard, ultrathink, wealth

class ConsensusResponse(BaseModel):
    query: str
    final_synthesis: str
    models_consulted: List[str]
    execution_time_seconds: float
    validation: dict
    metadata: dict

# Health check
@app.get("/")
async def root():
    return {
        "service": "AIYOU FastAPI Services",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "consensus": "/api/v1/consensus",
            "ultrathink": "/api/v1/ultrathink",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "consensus": "operational",
            "judge6": "operational",
            "pnkln": "operational"
        }
    }

@app.post("/api/v1/consensus", response_model=ConsensusResponse)
async def consensus_endpoint(request: ConsensusRequest):
    """
    Multi-LLM consensus with Judge #6 validation

    Example:
        POST /api/v1/consensus
        {
            "query": "What is quantum computing?",
            "mode": "standard"
        }
    """
    try:
        # Run consensus
        if request.mode == "ultrathink":
            result = await run_ultrathink_consensus(
                request.query,
                mode="ultrathink",
                evolution_enabled=True
            )
        elif request.mode == "wealth":
            result = await run_ultrathink_consensus(
                request.query,
                mode="wealth",
                evolution_enabled=False
            )
        else:
            result = await run_consensus_with_posture(request.query)

        return ConsensusResponse(
            query=request.query,
            final_synthesis=result.get("final_synthesis", ""),
            models_consulted=result.get("models_consulted", []),
            execution_time_seconds=result.get("execution_time_seconds", 0),
            validation=result.get("validation", {}),
            metadata=result.get("metadata", {})
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ultrathink")
async def ultrathink_endpoint(request: ConsensusRequest):
    """
    Jobs-inspired ultrathink mode with DTE evolution

    Example:
        POST /api/v1/ultrathink
        {
            "query": "Design a scalable API architecture",
            "mode": "ultrathink"
        }
    """
    try:
        result = await run_ultrathink_consensus(
            request.query,
            mode="ultrathink",
            evolution_enabled=True
        )

        return {
            "query": request.query,
            "synthesis": result.get("final_synthesis"),
            "glicko_ratings": result.get("glicko_ratings", {}),
            "evolution_score": result.get("evolution_score", 0),
            "metadata": result.get("metadata", {})
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run server
if __name__ == "__main__":
    # Create data directory
    Path("./data").mkdir(exist_ok=True)

    # Load environment
    from dotenv import load_dotenv
    load_dotenv()

    # Run server
    uvicorn.run(
        app,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "False").lower() == "true",
        log_level="info"
    )
EOF
```

### Step 4: Create Startup Script

```bash
cat > start.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting AIYOU FastAPI Services"
echo "==================================="
echo ""

# Activate virtual environment
source venv/bin/activate

# Check API keys
if ! grep -q "GOOGLE_API_KEY=.*[a-zA-Z0-9]" .env; then
    echo "❌ Error: GOOGLE_API_KEY not set in .env"
    echo "   Get your key from: https://aistudio.google.com/app/apikey"
    exit 1
fi

if ! grep -q "ANTHROPIC_API_KEY=.*[a-zA-Z0-9]" .env; then
    echo "❌ Error: ANTHROPIC_API_KEY not set in .env"
    echo "   Get your key from: https://console.anthropic.com/"
    exit 1
fi

echo "✓ API keys configured"
echo "✓ Virtual environment activated"
echo ""

# Create necessary directories
mkdir -p data
mkdir -p logs

# Start server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python main.py
EOF

chmod +x start.sh
```

### Step 5: Deploy!

```bash
# Start the server
./start.sh
```

**Expected output**:
```
🚀 Starting AIYOU FastAPI Services
===================================

✓ API keys configured
✓ Virtual environment activated

🌐 Starting FastAPI server on http://localhost:8000
📖 API docs available at http://localhost:8000/docs

Press Ctrl+C to stop

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 🧪 Test Your Deployment

### Option 1: Browser (Interactive API Docs)

Open in your browser:
```
http://localhost:8000/docs
```

You'll see interactive API documentation where you can test endpoints directly!

### Option 2: Command Line (curl)

```bash
# Health check
curl http://localhost:8000/health

# Simple consensus query
curl -X POST http://localhost:8000/api/v1/consensus \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is quantum computing?",
    "mode": "standard"
  }'

# Ultrathink mode
curl -X POST http://localhost:8000/api/v1/ultrathink \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Design a REST API for a social network",
    "mode": "ultrathink"
  }'
```

### Option 3: Python Client

```python
# test_client.py
import requests

base_url = "http://localhost:8000"

# Health check
response = requests.get(f"{base_url}/health")
print("Health:", response.json())

# Consensus query
response = requests.post(
    f"{base_url}/api/v1/consensus",
    json={
        "query": "Explain machine learning in simple terms",
        "mode": "standard"
    }
)
result = response.json()
print("\nConsensus Result:")
print(f"Query: {result['query']}")
print(f"Models: {result['models_consulted']}")
print(f"Time: {result['execution_time_seconds']:.2f}s")
print(f"\nSynthesis:\n{result['final_synthesis']}")
```

Run it:
```bash
python test_client.py
```

---

## 📊 Monitoring Your Deployment

### View Logs

```bash
# Watch server logs in real-time
tail -f logs/aiyou.log

# View last 50 lines
tail -50 logs/aiyou.log
```

### Check Performance

```bash
# Create performance monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash

echo "📊 AIYOU Performance Monitor"
echo "=============================="
echo ""

while true; do
    # Health check
    health=$(curl -s http://localhost:8000/health | jq -r '.status')

    # Get timestamp
    timestamp=$(date "+%Y-%m-%d %H:%M:%S")

    echo "[$timestamp] Status: $health"

    # Wait 5 seconds
    sleep 5
done
EOF

chmod +x monitor.sh
./monitor.sh
```

### View Metrics

```bash
# Check database size
du -h data/aiyou.db

# Count archived queries
sqlite3 data/aiyou.db "SELECT COUNT(*) FROM transcripts;"

# Recent queries
sqlite3 data/aiyou.db "SELECT timestamp, user_query FROM transcripts ORDER BY timestamp DESC LIMIT 5;"
```

---

## 🔄 Background Services (Optional)

### Run as Background Service

```bash
# Start in background
nohup ./start.sh > logs/server.log 2>&1 &

# Get process ID
ps aux | grep "python main.py"

# Stop server
pkill -f "python main.py"
```

### Use Screen (Recommended)

```bash
# Install screen
brew install screen

# Start in screen session
screen -S aiyou
./start.sh

# Detach: Press Ctrl+A, then D
# Reattach: screen -r aiyou
# Kill session: screen -X -S aiyou quit
```

### Use LaunchAgent (macOS Native)

```bash
# Create LaunchAgent
mkdir -p ~/Library/LaunchAgents

cat > ~/Library/LaunchAgents/com.aiyou.fastapi.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aiyou.fastapi</string>
    <key>ProgramArguments</key>
    <array>
        <string>$HOME/Projects/aiyou-fastapi-services/start.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$HOME/Projects/aiyou-fastapi-services</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/Projects/aiyou-fastapi-services/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Projects/aiyou-fastapi-services/logs/stderr.log</string>
</dict>
</plist>
EOF

# Load service
launchctl load ~/Library/LaunchAgents/com.aiyou.fastapi.plist

# Check status
launchctl list | grep aiyou

# Unload service
launchctl unload ~/Library/LaunchAgents/com.aiyou.fastapi.plist
```

---

## 🎛️ Advanced Configuration

### Enable All Features

Edit `.env`:
```bash
# Enable full PNKLN stack
PNKLN_ENABLED=true
JUDGE6_ENABLED=true
SHADOWTAG_ENABLED=true
SEMANTIC_MEMORY_ENABLED=true

# Enable GPU pooling (if available)
GPU_POOLING_ENABLED=true
MAX_MODELS_PER_GPU=7

# Enable ingestion pipeline
INGESTION_ENABLED=true
INGESTION_SCHEDULE="0 2 * * *"  # Daily at 2 AM

# Enable monitoring
PROMETHEUS_ENABLED=true
METRICS_PORT=9090
```

### Add More Endpoints

Edit `main.py` and add:

```python
@app.post("/api/v1/judge6/validate")
async def judge6_validate(request: dict):
    """Validate a decision with Judge #6"""
    from src.pnkln.judge_six import JudgeSix
    # ... implementation

@app.post("/api/v1/memory/extract")
async def memory_extract():
    """Extract conversation patterns"""
    from erik_hancock_llm_memory.scripts.extract_local import main
    # ... implementation

@app.get("/api/v1/models/pool")
async def model_pool_status():
    """Get GPU pool status"""
    from src.models.pool import GPUPool
    # ... implementation
```

---

## 🐛 Troubleshooting

### Server won't start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill process using port
kill -9 <PID>

# Or use a different port
export PORT=8001
./start.sh
```

### API key errors

```bash
# Verify .env is loaded
source venv/bin/activate
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GOOGLE_API_KEY'))"

# Should print your API key
```

### Import errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check installed packages
pip list | grep -E "(fastapi|uvicorn|anthropic|google-generativeai)"
```

### Slow responses

```bash
# Check which model is being used
# Gemini 2.0 Flash is fastest
# Edit voice_consensus/*.py to ensure model_name="gemini-3.1-flash-exp"

# Reduce concurrency
export MAX_WORKERS=2
```

---

## 📈 Performance Tuning

### Optimize for Speed

```python
# In main.py, add caching
from functools import lru_cache

@lru_cache(maxsize=100)
def get_consensus_cached(query: str):
    # Cached consensus for repeated queries
    pass
```

### Database Optimization

```bash
# Enable WAL mode for better concurrency
sqlite3 data/aiyou.db "PRAGMA journal_mode=WAL;"

# Vacuum database periodically
sqlite3 data/aiyou.db "VACUUM;"
```

### Add Redis Caching (Optional)

```bash
# Install Redis
brew install redis

# Start Redis
redis-server &

# Add to requirements.txt
echo "redis>=4.5.0" >> requirements.txt
pip install redis

# Use in main.py
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
```

---

## 🚀 Production Checklist

Before deploying to production:

- [ ] Set `DEBUG=False` in `.env`
- [ ] Use strong secrets for any auth
- [ ] Enable HTTPS (use reverse proxy like nginx)
- [ ] Set up proper logging (structured logs)
- [ ] Configure rate limiting
- [ ] Add authentication/authorization
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure backups for database
- [ ] Set up alerting (PagerDuty, etc.)
- [ ] Load test with expected traffic
- [ ] Document API endpoints
- [ ] Set up CI/CD pipeline

---

## 📚 Next Steps

1. **Explore API docs**: http://localhost:8000/docs
2. **Run performance tests**: `cd load_testing && python validate_judge6_latency.py`
3. **Set up monitoring**: Enable Prometheus + Grafana
4. **Add authentication**: Implement API key validation
5. **Deploy to cloud**: Use deployment configs in `deployment/`

---

## 🎯 You're Deployed!

Your AIYOU FastAPI Services platform is now running at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

**Test it**:
```bash
curl http://localhost:8000/api/v1/consensus \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AI?", "mode": "standard"}'
```

**Happy deploying!** 🚀
