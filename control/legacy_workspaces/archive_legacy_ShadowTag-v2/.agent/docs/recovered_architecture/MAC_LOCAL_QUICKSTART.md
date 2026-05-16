# Mac Local Deployment - Quick Start Guide

**Platform**: SHADOWTAGAI Intelligence Pipeline v0.2.0
**Last Updated**: 2025-11-18
**Model**: Gemini 2.0 Flash Experimental (15-20% cost reduction)
**Time to Deploy**: 30 minutes

---

## Prerequisites Checklist

Before starting, ensure you have:



- [ ] macOS 12+ (Monterey or later)


- [ ] Homebrew installed


- [ ] Google Cloud account with billing enabled


- [ ] GitHub account


- [ ] 10GB free disk space


- [ ] Internet connection

---

## Part 1: Install Development Tools (10 minutes)

### Step 1: Install Homebrew (if not installed)

```bash

# Check if Homebrew is installed

brew --version

# If not installed, install it:

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Follow the post-installation instructions to add Homebrew to PATH

```

### Step 2: Install Python 3.11

```bash

# Install Python 3.11

brew install python@3.11

# Verify installation

python3.11 --version

# Expected: Python 3.11.x

# Create alias (add to ~/.zshrc or ~/.bashrc)

echo 'alias python=python3.11' >> ~/.zshrc
echo 'alias pip=pip3.11' >> ~/.zshrc
source ~/.zshrc

```

### Step 3: Install Node.js 20+

```bash

# Install Node.js

brew install node@20

# Verify installation

node --version  # Expected: v20.x.x
npm --version   # Expected: 10.x.x

```

### Step 4: Install PostgreSQL and Redis

```bash

# Install PostgreSQL

brew install postgresql@15
brew services start postgresql@15

# Install Redis

brew install redis
brew services start redis

# Verify services are running

brew services list

# Expected: postgresql@15 and redis both "started"

```

### Step 5: Install Google Cloud SDK

```bash

# Install gcloud CLI

brew install --cask google-cloud-sdk

# Initialize gcloud

gcloud init

# Follow prompts:

# 1. Login with your Google account

# 2. Select or create a GCP project

# 3. Set default region to us-central1

# Verify installation

gcloud --version

```

---

## Part 2: Clone and Setup Repository (5 minutes)

### Step 1: Clone Repository

```bash

# Clone the repository

git clone https://github.com/ShadowTag-v2/aiyou-fastapi-services.git
cd aiyou-fastapi-services

# Check current branch

git branch

# Should show: claude/shadowtagai-intelligence-pipeline-01DwB3v8zwZaHZC3HogNeRXt

```

### Step 2: Create Python Virtual Environment

```bash

# Create virtual environment

python3.11 -m venv venv

# Activate virtual environment

source venv/bin/activate

# Upgrade pip

pip install --upgrade pip setuptools wheel

# Verify virtual environment

which python

# Expected: /Users/yourname/aiyou-fastapi-services/venv/bin/python

```

### Step 3: Install Python Dependencies

```bash

# Install all Python dependencies

pip install -r requirements.txt

# This will install:

# - FastAPI, Uvicorn (web framework)

# - Google Cloud libraries (aiplatform, storage, bigquery)

# - Vertex AI SDK

# - SQLAlchemy, asyncpg (database)

# - Redis client

# - And more...

# Expected time: 2-3 minutes

```

### Step 4: Install TypeScript Dependencies

```bash

# Install Node.js packages

npm install

# Build TypeScript agents

npm run build

# Verify build

ls -la dist/

# Should show compiled JavaScript files

```

---

## Part 3: Configure Environment (5 minutes)

### Step 1: Create .env File

```bash

# Copy example environment file

cp .env.example .env

# Open in your favorite editor

nano .env  # or: code .env, vim .env, etc.

```

### Step 2: Configure Required Variables

**Minimum configuration for local development:**

```bash

# ============================================================================

# GCP Settings (REQUIRED)

# ============================================================================

GCP_PROJECT_ID=your-gcp-project-id  # Get from: gcloud config get-value project
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GCP_LOCATION=us-central1
GCP_REGION=us-central1

# GCS Bucket (create one or use existing)

GCP_GCS_BUCKET_RAW=your-project-id-raw-data
GCP_GCS_BUCKET_PROCESSED=your-project-id-processed-data
STORAGE_BUCKET=your-project-id-kosmos-artifacts

# ============================================================================

# Gemini 2.0 Flash Configuration (REQUIRED)

# ============================================================================

DEFAULT_MODEL=gemini-3.1-flash-exp
GEMINI_PRO_MODEL=gemini-1.5-pro
GEMINI_FLASH_MODEL=gemini-3.1-flash-exp

# ============================================================================

# Database Configuration (Local PostgreSQL)

# ============================================================================

DATABASE_URL=postgresql+asyncpg://youai:youai_password@localhost:5432/youai_governance
REDIS_URL=redis://localhost:6379/0

# ============================================================================

# Service Configuration

# ============================================================================

ENVIRONMENT=development
DEBUG=true
SERVICE_NAME=youai-governance-service
API_HOST=0.0.0.0
API_PORT=8000

# ============================================================================

# Security (Generate a secure key)

# ============================================================================

SECRET_KEY=$(openssl rand -hex 32)  # Run this in terminal, paste result
API_KEY_HEADER=X-API-Key
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# ============================================================================

# Logging

# ============================================================================

LOG_LEVEL=INFO
ENABLE_TELEMETRY=false  # Set to false for local development

# ============================================================================

# Budget Controls (IMPORTANT for cost management)

# ============================================================================

DAILY_BUDGET=10.0  # $10/day limit for local dev
MONTHLY_BUDGET=300.0  # $300/month limit
SESSION_BUDGET=5.0  # $5 per session
ALERT_THRESHOLD=0.8  # Alert at 80% of budget

```

### Step 3: Generate Secret Key

```bash

# Generate a secure secret key

openssl rand -hex 32

# Copy the output and paste into .env as SECRET_KEY value

```

### Step 4: Setup GCP Authentication

```bash

# Login to Google Cloud

gcloud auth login

# Set application default credentials

gcloud auth application-default login

# Set your project

gcloud config set project YOUR_PROJECT_ID

# Enable required APIs

gcloud services enable aiplatform.googleapis.com
gcloud services enable storage-component.googleapis.com
gcloud services enable bigquery.googleapis.com

```

### Step 5: Create GCS Buckets

```bash

# Set your project ID

export PROJECT_ID=$(gcloud config get-value project)

# Create buckets for data storage

gsutil mb -l us-central1 gs://${PROJECT_ID}-raw-data
gsutil mb -l us-central1 gs://${PROJECT_ID}-processed-data
gsutil mb -l us-central1 gs://${PROJECT_ID}-kosmos-artifacts

# Verify buckets created

gsutil ls

```

---

## Part 4: Setup Databases (5 minutes)

### Step 1: Create PostgreSQL Database

```bash

# Create database and user

psql postgres << EOF
CREATE DATABASE youai_governance;
CREATE USER youai WITH PASSWORD 'youai_password';
GRANT ALL PRIVILEGES ON DATABASE youai_governance TO youai;
\q
EOF

# Verify database created

psql -U youai -d youai_governance -c "SELECT version();"

```

### Step 2: Run Database Migrations

```bash

# Activate virtual environment if not already active

source venv/bin/activate

# Run migrations (if using Alembic)

# If migrations exist:

cd app
alembic upgrade head
cd ..

# Or initialize tables directly with Python

python << EOF
from app.database import engine, Base
from app.models import *
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully")
EOF

```

### Step 3: Verify Redis

```bash

# Test Redis connection

redis-cli ping

# Expected: PONG

# Check Redis status

brew services list | grep redis

# Expected: redis started

```

---

## Part 5: Test the Platform (5 minutes)

### Test 1: Start YouAi Governance Service

```bash

# Activate virtual environment

source venv/bin/activate

# Start FastAPI server

cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# You should see:

# INFO:     Uvicorn running on http://0.0.0.0:8000

# INFO:     Application startup complete

```

**In a new terminal tab**, test the API:

```bash

# Test health endpoint

curl http://localhost:8000/health

# Expected response:

# {"status":"healthy","timestamp":"2025-11-18T..."}

# Test Gemini 2.0 Flash integration

curl -X POST http://localhost:8000/api/v1/governance/assess \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a test content",
    "framework": "EU_AI_ACT"
  }'

# Expected: JSON response with governance assessment

```

### Test 2: Run Nightly Intel Pipeline

```bash

# In a new terminal, activate environment

cd /Users/yourname/aiyou-fastapi-services
source venv/bin/activate

# Run intelligence pipeline

cd nightly_intel_pipeline
python main.py \
  --topics mlops kubernetes \
  --days-back 7 \
  --download-pdfs

# Expected output:

# ✓ Fetching GitHub repositories for: mlops, kubernetes

# ✓ Searching arXiv papers (last 7 days)

# ✓ Scraping YouTube videos

# ✓ Analyzing with Gemini 2.0 Flash

# ✓ Generating executive briefing

#

# Briefing saved to: data/briefings/briefing_20251118.md

```

### Test 3: Test TypeScript Agent System

```bash

# Test agent registry

node -e "
const { getAllAgents } = require('./dist/index.js');
console.log(JSON.stringify(getAllAgents(), null, 2));
"

# Expected: JSON array of 53 agents

# Test specific agent

node -e "
const { getAgent } = require('./dist/index.js');
const agent = getAgent('product-strategist');
console.log('Agent:', agent.metadata.name);
console.log('Category:', agent.metadata.category);
console.log('Version:', agent.metadata.version);
"

# Expected:

# Agent: Product Strategist

# Category: product-strategy

# Version: 1.0.0

```

### Test 4: Test LLM Memory System

```bash

# Navigate to LLM memory directory

cd erik-hancock-llm-memory

# Run memory extraction (dry-run)

python scripts/extract_and_commit.py --dry-run

# Expected output:

# ✓ Found Cursor databases

# ✓ Extracting conversations (last 7 days)

# ✓ Generating metadata with Gemini 2.0 Flash

#

# DRY RUN - Would commit:

# - 15 new conversations

# - Estimated cost: $0.03

# - Memory version: v1.2.0

# If satisfied, run actual extraction:

python scripts/extract_and_commit.py

# Install memory to Claude Code

python scripts/claude_code_memory_local.py --install

# Memory installed to: ~/.claude-code/memory.md

```

---

## Part 6: Cost Optimization for Local Dev (Important!)

### Monitor Costs

```bash

# Check current month's costs

gcloud billing accounts list
gcloud billing projects link YOUR_PROJECT_ID --billing-account=BILLING_ACCOUNT_ID

# Set up budget alerts (HIGHLY RECOMMENDED)

gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="SHADOWTAGAI Local Dev Budget" \
  --budget-amount=300USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=80 \
  --threshold-rule=percent=100

# Monitor usage

gcloud billing accounts describe BILLING_ACCOUNT_ID

```

### Cost Saving Tips for Mac Local Dev



1. **Use Gemini 2.0 Flash** (already configured)


   - Cost: $0.075/1M input tokens (vs $1.25 for Pro)


   - Savings: 94% cheaper for most tasks



2. **Limit API calls during development**
   ```bash
   # In .env, set conservative budgets:
   DAILY_BUDGET=5.0
   SESSION_BUDGET=1.0
   ```



3. **Run services only when needed**
   ```bash
   # Stop PostgreSQL when not in use
   brew services stop postgresql@15

   # Stop Redis when not in use
   brew services stop redis

   # Restart when needed
   brew services start postgresql@15
   brew services start redis
   ```



4. **Use local caching aggressively**
   ```bash
   # Redis cache reduces Gemini API calls
   # Check cache hit rate:
   redis-cli INFO stats | grep keyspace_hits
   ```

### Expected Monthly Costs (Local Mac)

| Service | Cost | Notes |
|---------|------|-------|
| Gemini 2.0 Flash API | $3-8 | For development/testing |
| GCS Storage | $0.50 | ~10GB data |
| BigQuery | $0.50 | Minimal queries |
| **Total** | **$4-9/month** | vs $77-92 on GCP |

---

## Part 7: Development Workflow

### Daily Workflow

```bash

# 1. Start your day

cd /Users/yourname/aiyou-fastapi-services
source venv/bin/activate

# 2. Start databases

brew services start postgresql@15
brew services start redis

# 3. Start FastAPI server (terminal 1)

cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 4. Run Nightly Intel Pipeline (terminal 2 - optional)

cd nightly_intel_pipeline
python main.py --topics mlops ai --days-back 1

# 5. Develop and test

# - Make code changes

# - FastAPI auto-reloads

# - Test at http://localhost:8000

# 6. End your day

# Stop services to save battery

brew services stop postgresql@15
brew services stop redis

```

### Testing Workflow

```bash

# Run Python tests

pytest app/tests/ -v

# Run TypeScript tests

npm test

# Check code quality

# Python

pylint app/
black app/ --check

# TypeScript

npm run lint
npm run format

```

### Git Workflow

```bash

# Create feature branch

git checkout -b feature/your-feature-name

# Make changes

# ... edit files ...

# Stage and commit

git add .
git commit -m "feat: Add your feature description"

# Push to remote

git push -u origin feature/your-feature-name

# Create PR on GitHub

gh pr create --title "Your Feature" --body "Description"

```

---

## Part 8: Troubleshooting

### Problem: PostgreSQL won't start

```bash

# Check PostgreSQL status

brew services list | grep postgresql

# Check logs

tail -f /opt/homebrew/var/log/postgresql@15.log

# Common fix: Remove lock file

rm /opt/homebrew/var/postgresql@15/postmaster.pid
brew services restart postgresql@15

```

### Problem: "Module not found" errors

```bash

# Ensure virtual environment is activated

which python

# Should point to venv/bin/python

# If not activated:

source venv/bin/activate

# Reinstall dependencies

pip install -r requirements.txt

```

### Problem: Gemini API authentication errors

```bash

# Re-authenticate with gcloud

gcloud auth application-default login

# Verify credentials exist

ls -la ~/.config/gcloud/application_default_credentials.json

# Test authentication

python -c "
from google.cloud import aiplatform
aiplatform.init(project='YOUR_PROJECT_ID', location='us-central1')
print('✅ Authentication successful')
"

```

### Problem: Port 8000 already in use

```bash

# Find process using port 8000

lsof -i :8000

# Kill the process

kill -9 PID

# Or use a different port

uvicorn main:app --reload --port 8001

```

### Problem: GCS bucket access denied

```bash

# Check your project ID

gcloud config get-value project

# Verify bucket exists

gsutil ls

# Check bucket permissions

gsutil iam get gs://your-bucket-name

# Grant yourself permissions

gsutil iam ch user:your-email@gmail.com:roles/storage.admin gs://your-bucket-name

```

### Problem: High Gemini API costs

```bash

# Check current usage

gcloud monitoring time-series list \
  --project=YOUR_PROJECT_ID \
  --filter='metric.type="aiplatform.googleapis.com/prediction/online/prediction_count"'

# Review budget alerts

gcloud billing budgets list --billing-account=BILLING_ACCOUNT_ID

# Reduce costs:

# 1. Lower DAILY_BUDGET in .env

# 2. Use Redis caching more aggressively

# 3. Reduce --days-back in nightly pipeline

# 4. Test with smaller datasets

```

---

## Part 9: Next Steps

### Week 1: Get Comfortable



- [ ] Run Nightly Intel Pipeline daily


- [ ] Test different governance frameworks


- [ ] Explore TypeScript agents


- [ ] Monitor costs (should be <$10)

### Week 2: Integrate MCP (Optional)



- [ ] Review: `mcp-validation/IMMEDIATE_NEXT_STEPS.md`


- [ ] Deploy MCP server to GKE


- [ ] Run 72-hour validation sprint


- [ ] Decision: GO/NO-GO on MCP integration

### Week 3: Build Custom Agents



- [ ] Create your first custom TypeScript agent


- [ ] Add to agent registry


- [ ] Test via FastAPI endpoint


- [ ] Share with team

### Month 2: Advanced Features



- [ ] Implement A2A protocol for multi-agent coordination


- [ ] Deploy Google Agent Starter Pack templates


- [ ] Setup ADK Visual Builder


- [ ] Integrate MCP Agent Mail

---

## Part 10: Quick Reference

### Useful Commands

```bash

# Start services

brew services start postgresql@15 redis

# Stop services

brew services stop postgresql@15 redis

# Restart services

brew services restart postgresql@15 redis

# Activate Python environment

source venv/bin/activate

# Start FastAPI server

uvicorn app.main:app --reload

# Run Nightly Intel Pipeline

python nightly_intel_pipeline/main.py --topics mlops --days-back 7

# Build TypeScript agents

npm run build

# Run tests

pytest app/tests/ -v
npm test

# Check costs

gcloud billing accounts describe BILLING_ACCOUNT_ID

# View logs

tail -f logs/app.log
tail -f /opt/homebrew/var/log/postgresql@15.log

```

### Important URLs



- **FastAPI Docs**: http://localhost:8000/docs


- **Health Check**: http://localhost:8000/health


- **Agent Registry**: http://localhost:8000/api/v1/agents/list


- **PostgreSQL**: localhost:5432


- **Redis**: localhost:6379

### Important Files



- **Environment Config**: `.env`


- **Python Dependencies**: `requirements.txt`


- **TypeScript Config**: `package.json`


- **Agent Manifests**: `agents/*/manifest.json`


- **FastAPI Main**: `app/main.py`


- **Intel Pipeline**: `nightly_intel_pipeline/main.py`

### Directory Structure

```

aiyou-fastapi-services/
├── app/                          # FastAPI YouAi Governance Service
│   ├── api/v1/                   # API endpoints
│   ├── services/                 # Business logic
│   │   └── vertex_ai_client.py   # Gemini 2.0 Flash client
│   ├── models/                   # Database models
│   └── main.py                   # FastAPI entry point
├── nightly_intel_pipeline/       # Intelligence gathering
│   ├── main.py                   # CLI entry point
│   ├── engines/                  # JR Engine, scoring
│   ├── scrapers/                 # GitHub, arXiv, YouTube
│   └── storage/                  # Briefing generation
├── erik-hancock-llm-memory/      # LLM Memory System
│   ├── scripts/                  # Extraction, sync
│   └── memory/                   # Conversation storage
├── src/agents/                   # TypeScript agents (53+)
│   ├── product-strategy/
│   ├── development/
│   ├── design-ux/
│   ├── quality-testing/
│   ├── operations/
│   ├── business-analytics/
│   └── ai-innovation/
├── marketplace/                  # Agent marketplace
│   └── marketplace.json
├── mcp-validation/              # MCP validation framework
│   ├── mcp_server.py
│   ├── architecture/
│   └── security/
├── docs/                        # Documentation
│   ├── MAC_LOCAL_QUICKSTART.md  # This file
│   ├── LATEST_TECH_INTEGRATION_RECOMMENDATIONS.md
│   └── SESSION_SUMMARY_2025-11-18.md
└── .env                         # Your configuration (git-ignored)

```

---

## Success Checklist

After completing this guide, you should be able to:



- [x] Run FastAPI server locally on Mac


- [x] Execute Nightly Intel Pipeline


- [x] Test Gemini 2.0 Flash integration


- [x] Query TypeScript agents via API


- [x] Extract and install LLM memory


- [x] Monitor costs (<$10/month)


- [x] Develop new features locally


- [x] Run tests and CI checks


- [x] Push changes to GitHub

**Total Setup Time**: ~30 minutes
**Monthly Cost**: $4-9 (vs $77-92 on GCP)
**Status**: ✅ Ready for local development

---

## Support

**Documentation**:


- Main Guide: `docs/MAC_DEPLOYMENT.md`


- Integration Guide: `docs/LATEST_TECH_INTEGRATION_RECOMMENDATIONS.md`


- Session Summary: `docs/SESSION_SUMMARY_2025-11-18.md`

**Issues**:


- GitHub: https://github.com/ShadowTag-v2/aiyou-fastapi-services/issues


- Check existing issues before creating new ones

**Community**:


- Review `CONTRIBUTING.md` for contribution guidelines


- Check `CHANGELOG.md` for recent updates

---

**Last Updated**: 2025-11-18
**Platform Version**: SHADOWTAGAI Intelligence Pipeline v0.2.0
**Model**: Gemini 2.0 Flash Experimental
**Status**: ✅ Production Ready for Local Development
