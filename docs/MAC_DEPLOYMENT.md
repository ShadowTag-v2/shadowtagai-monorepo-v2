# Mac Local Deployment Guide

**SHADOWTAGAI Intelligence Pipeline - Complete Platform**
**Date**: 2025-11-18
**Integrations**: MCP Batch API, Nightly Intel Pipeline, LLM Memory System

---

## Overview

This guide walks you through deploying the complete SHADOWTAGAI Intelligence Platform on macOS, including:

- **MCP Gemini Efficiency Patterns** (Batch governance with 90-97% cost savings)
- **Nightly Intel Pipeline** (AI/MLOps intelligence gathering)
- **LLM Memory System** (Persistent memory across Claude Code, Vertex, 4-LLM orchestration)
- **ShadowTag Governance Service** (EU AI Act, DSA, NIST RMF, ISO 42001 compliance)

---

## Prerequisites

### 1. System Requirements

- **macOS**: 12.0 (Monterey) or later
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 10GB free space
- **Python**: 3.11 or later
- **Node.js**: 18.x or later (for LLM Memory scripts)

### 2. Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 3. Install Required Tools

```bash
# Python 3.11
brew install python@3.11

# Node.js 18
brew install node@18

# Git
brew install git

# SQLite (for Nightly Intel)
brew install sqlite3

# Optional: Docker (for containerized deployment)
brew install docker
```

---

## Part 1: ShadowTag Governance Service + MCP Batch API

### 1.1 Clone Repository

```bash
cd ~/Projects
git clone https://github.com/ehanc69/ShadowTag-v2-fastapi-services.git
cd ShadowTag-v2-fastapi-services
git checkout claude/shadowtagai-intelligence-pipeline-01DwB3v8zwZaHZC3HogNeRXt
```

### 1.2 Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

### 1.3 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 1.4 Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

Add your credentials:

```env
# Gemini/Vertex AI
GOOGLE_API_KEY=your_gemini_api_key_here
GCP_PROJECT_ID=your_gcp_project_id
GCP_LOCATION=us-central1

# Anthropic (for Claude)
ANTHROPIC_API_KEY=your_anthropic_key_here

# PostgreSQL (optional for ShadowTag)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ShadowTag_governance
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Redis (optional for ShadowTag)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 1.5 Run Locally

```bash
# Start the FastAPI server
python app/main.py

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 1.6 Test Endpoints

**Health check**:

```bash
curl http://localhost:8000/health
```

**Governance assessment**:

```bash
curl -X POST http://localhost:8000/api/v1/governance/assess \
  -H "Content-Type: application/json" \
  -d '{
    "frameworks": ["eu_ai_act"],
    "is_ai_generated": true,
    "user_age": 25
  }'
```

**Batch assessment (MCP efficiency patterns)**:

```bash
curl -X POST http://localhost:8000/api/v1/governance/assess/batch \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"id": "ad_1", "content": "Buy now!", "type": "advertisement"},
      {"id": "ad_2", "content": "Limited offer", "type": "advertisement"}
    ],
    "frameworks": ["eu_ai_act", "coppa"],
    "top_k_violations": 10
  }'
```

---

## Part 2: Nightly Intel Pipeline

### 2.1 Navigate to Pipeline Directory

```bash
cd nightly_intel_pipeline
```

### 2.2 Setup Environment

```bash
# Copy example config
cp .env.example .env

# Edit with your API keys
nano .env
```

Add:

```env
GITHUB_TOKEN=your_github_personal_access_token
ANTHROPIC_API_KEY=your_anthropic_key
```

### 2.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.4 Run Pipeline Manually

```bash
# Basic run (GitHub + arXiv)
python main.py

# Custom topics
python main.py --topics mlops kubernetes llm

# Look back 30 days
python main.py --days-back 30

# Download PDFs (slower)
python main.py --download-pdfs
```

### 2.5 View Results

```bash
# List briefings
ls -lt data/briefings/

# View latest briefing
cat data/briefings/briefing_$(date +%Y%m%d)*.md | less

# Query database
sqlite3 storage/intel_pipeline.db
> SELECT repo_name, total_score, tier FROM repositories ORDER BY total_score DESC LIMIT 10;
> .quit
```

### 2.6 Schedule Nightly Runs (macOS cron)

```bash
# Edit crontab
crontab -e

# Add nightly run at 2 AM
0 2 * * * cd ~/Projects/ShadowTag-v2-fastapi-services/nightly_intel_pipeline && /usr/bin/python3 main.py >> logs/cron.log 2>&1
```

---

## Part 3: LLM Memory System

### 3.1 Navigate to Memory Directory

```bash
cd ~/Projects/ShadowTag-v2-fastapi-services/erik-hancock-llm-memory
```

### 3.2 Install Dependencies

```bash
npm install  # For sync utilities
pip install google-generativeai  # For Gemini API
```

### 3.3 Extract Conversations

```bash
# Set API key
export GOOGLE_API_KEY=your_gemini_key

# Run extraction (finds Cursor/Claude/Codex databases)
python scripts/extract_and_commit.py
```

This will:

- Find conversation databases in `~/Library/Application Support/Cursor/`, etc.
- Extract conversations
- Generate metadata with Gemini Flash
- Commit to Git with semantic versioning
- Cost: ~$0.45 for 2,121 conversations

### 3.4 Deploy to Claude Code

```bash
# Install memory to ~/.claude-code/
python scripts/claude_code_memory_local.py

# Restart Claude Code
# Memory now auto-loads on startup
```

Test:

```bash
# In Claude Code, ask:
"What is Judge #6?"

# Should respond with:
# "Judge #6 is a hybrid Gemini+PyTorch+Rules validation system with 98% coverage and p99 ≤90ms latency..."
```

### 3.5 4-LLM Orchestration (Optional)

```bash
# Set all API keys
export ANTHROPIC_API_KEY=your_claude_key
export OPENAI_API_KEY=your_openai_key
export GROK_API_KEY=your_grok_key
export PERPLEXITY_API_KEY=your_perplexity_key

# Run orchestration
python scripts/llm_blender_rotation.py

# Input your query when prompted
# System will:
# 1. Grok: Decompose query
# 2. Sonnet 4.5: Assign threads to Gemini/GPT-5/Perplexity
# 3. Round 1: Each LLM answers
# 4. Round 2: Peer review (rotate right)
# 5. Round 3: Second review (rotate right)
# 6. Claude Code: Synthesize final answer
```

### 3.6 Cross-Device Sync

```bash
# Pull latest memory from Git
./scripts/sync_to_devices.sh pull

# Work with updated memory...

# Push your changes
./scripts/sync_to_devices.sh push

# Check sync status
./scripts/sync_to_devices.sh status
```

---

## Part 4: Database Setup (Optional)

### 4.1 PostgreSQL (for ShadowTag Governance)

```bash
# Install
brew install postgresql@15

# Start service
brew services start postgresql@15

# Create database
createdb ShadowTag_governance

# Run migrations (if available)
# alembic upgrade head
```

### 4.2 Redis (for ShadowTag Caching)

```bash
# Install
brew install redis

# Start service
brew services start redis

# Test
redis-cli ping
# Should return: PONG
```

---

## Part 5: Monitoring & Logs

### 5.1 View Application Logs

```bash
# ShadowTag FastAPI
tail -f logs/app.log

# Nightly Intel Pipeline
tail -f nightly_intel_pipeline/logs/pipeline.log

# LLM Memory
tail -f erik-hancock-llm-memory/logs/*.log
```

### 5.2 Monitor Resource Usage

```bash
# CPU & Memory
top

# Disk usage
df -h

# Process monitoring
ps aux | grep python
```

---

## Part 6: Development Workflow

### 6.1 Running Tests

```bash
# Activate venv
source venv/bin/activate

# Run all tests
pytest

# Run specific test
pytest tests/test_governance.py -v

# With coverage
pytest --cov=app tests/
```

### 6.2 Code Quality

```bash
# Format code
black app/ nightly_intel_pipeline/ erik-hancock-llm-memory/

# Lint
flake8 app/
pylint app/

# Type checking
mypy app/
```

### 6.3 Git Workflow

```bash
# Check status
git status

# Create feature branch
git checkout -b feature/my-new-feature

# Commit changes
git add .
git commit -m "Add new feature"

# Push to remote
git push -u origin feature/my-new-feature
```

---

## Part 7: Cost Optimization (Mac Local)

### 7.1 Use Gemini Flash 2.0 (Free Tier)

Edit `app/services/vertex_ai_client.py`:

```python
# Change from
model: str = "gemini-1.5-pro"

# To
model: str = "gemini-2.0-flash"
```

Savings: ~$11/month → $0/month (free tier: 15 RPM, 1M tokens/day)

### 7.2 Reduce Nightly Intel Frequency

Edit `nightly_intel_pipeline/config.py`:

```python
# Change from daily to weekly
PIPELINE_SCHEDULE = {
    "run_hour": 2,
    "enabled": True,
    "frequency": "weekly"  # Instead of "daily"
}
```

Savings: ~$11/month → $3/month (75% reduction)

### 7.3 Limit Batch Sizes

Edit batch configurations:

```python
# Reduce max items per batch
MAX_REPOS_PER_TOPIC = 5  # Instead of 10
MAX_RESULTS_PER_CATEGORY = 25  # Instead of 50
```

---

## Part 8: Troubleshooting

### 8.1 Common Issues

**Issue**: "GITHUB_TOKEN not set"

```bash
# Solution
export GITHUB_TOKEN='ghp_xxxxxxxxxxxxx'
# Or add to .env file
```

**Issue**: "Gemini API rate limit exceeded"

```bash
# Solution: Wait 1 hour or reduce batch size
# In config.py:
RATE_LIMITING = {
    "default_delay": 5.0,  # Increase from 3.0
    "max_concurrent": 1    # Reduce from 3
}
```

**Issue**: "Database locked" (SQLite)

```bash
# Solution: Close any open connections
rm nightly_intel_pipeline/storage/intel_pipeline.db
# Re-run pipeline to recreate
```

**Issue**: "Port 8000 already in use"

```bash
# Solution: Find and kill process
lsof -ti:8000 | xargs kill -9
# Or use different port
uvicorn app.main:app --port 8001
```

### 8.2 Debug Mode

Enable debug logging:

```python
# In app/config.py
DEBUG = True
LOG_LEVEL = "DEBUG"
```

### 8.3 Reset Everything

```bash
# Stop all services
brew services stop postgresql@15
brew services stop redis

# Remove virtual environment
rm -rf venv

# Clean databases
rm nightly_intel_pipeline/storage/*.db
rm erik-hancock-llm-memory/memory/*.json

# Reinstall
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Part 9: Production Deployment (Next Steps)

Once validated locally, deploy to production:

### 9.1 GKE Native (Recommended)

```bash
# See nightly_intel_pipeline/kubernetes/README.md
# Build Docker image
docker build -t gcr.io/PROJECT_ID/shadowtagai-platform:latest .

# Push to GCR
docker push gcr.io/PROJECT_ID/shadowtagai-platform:latest

# Deploy to GKE
kubectl apply -f k8s/
```

### 9.2 Cloud Run (Simpler)

```bash
# Deploy ShadowTag FastAPI
gcloud run deploy ShadowTag-governance \
  --source=. \
  --region=us-central1 \
  --allow-unauthenticated
```

### 9.3 Vertex AI Workbench

See `erik-hancock-llm-memory/configs/vertex_workbench_config.py`

---

## Part 10: Cost Summary (Mac Local)

| Component               | Monthly Cost     | Notes                               |
| ----------------------- | ---------------- | ----------------------------------- |
| **ShadowTag FastAPI**       | $0               | Local, no infrastructure            |
| **Nightly Intel**       | $3-11            | Gemini API only (GitHub/arXiv free) |
| **LLM Memory**          | $0.12            | Incremental extractions             |
| **4-LLM Orchestration** | $0.08-0.12/query | On-demand only                      |
| **PostgreSQL**          | $0               | Local instance                      |
| **Redis**               | $0               | Local instance                      |
| **Total**               | **$3-12/month**  | Pure API costs                      |

**vs. GKE Production**: $77-92/month (includes infrastructure)

**Savings**: 75-90% by running locally on Mac

---

## Part 11: Next Steps

### Immediate (Week 1)

- [ ] Deploy ShadowTag FastAPI locally
- [ ] Test batch governance API
- [ ] Run Nightly Intel manually
- [ ] Extract conversations to LLM Memory

### Short-term (Month 1)

- [ ] Schedule Nightly Intel in cron
- [ ] Integrate memory into Claude Code
- [ ] Setup PostgreSQL + Redis
- [ ] Test 4-LLM orchestration

### Medium-term (Quarter 1)

- [ ] Deploy to GKE for production
- [ ] Setup monitoring (Prometheus + Grafana)
- [ ] Add more intelligence sources (YouTube, News)
- [ ] Fine-tune scoring thresholds

---

## Support

**Documentation**:

- ShadowTag: `docs/ShadowTag-governance-README.md`
- Nightly Intel: `nightly_intel_pipeline/README.md`
- LLM Memory: `erik-hancock-llm-memory/README.md`
- MCP Patterns: `docs/MCP_GEMINI_EFFICIENCY_IMPACT.md`

**Issues**: https://github.com/ehanc69/ShadowTag-v2-fastapi-services/issues

**Cost Analyses**:

- `docs/MCP_GEMINI_EFFICIENCY_IMPACT.md` - 90-97% cost reduction
- `docs/NIGHTLY_INTEL_PIPELINE_FINANCIAL_IMPACT.md` - $146K 3-year NPV
- `erik-hancock-llm-memory/IMPLEMENTATION_SUMMARY.md` - 18,000% ROI

---

**Built for**: ShadowTagAi Corp.
**Platform**: SHADOWTAGAI Intelligence Pipeline
**Deployment Date**: 2025-11-18
**Status**: ✅ Ready for Mac Deployment
