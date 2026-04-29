# Mac Local Deployment Guide

**ShadowTagAi Agent Platform - macOS Setup**

Complete guide for running the ShadowTagAi dual-layer intelligence pipeline locally on macOS (Apple Silicon M1/M2/M3 or Intel).

---

## Table of Contents

1. [Prerequisites](#prerequisites)

2. [Quick Start (5 Minutes)](#quick-start-5-minutes)

3. [Detailed Setup](#detailed-setup)

4. [Configuration](#configuration)

5. [Running the Platform](#running-the-platform)

6. [Testing](#testing)

7. [Troubleshooting](#troubleshooting)

8. [Development Workflow](#development-workflow)

---

## Prerequisites

### System Requirements

- **macOS:** 12.0 (Monterey) or later

- **Processor:** Apple Silicon (M1/M2/M3) or Intel

- **RAM:** 8GB minimum, 16GB recommended

- **Disk Space:** 15GB free (for dependencies and data)

- **Python:** 3.10, 3.11, or 3.12

### Required Tools

#### 1. Homebrew (Package Manager)

```bash

# Install Homebrew if not already installed

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Verify installation

brew --version

```

#### 2. Python 3.10+

```bash

# Install Python via Homebrew

brew install python@3.11

# Verify installation

python3 --version  # Should show 3.10+ or 3.11+

# Create alias (add to ~/.zshrc or ~/.bash_profile)

echo 'alias python=python3' >> ~/.zshrc
echo 'alias pip=pip3' >> ~/.zshrc
source ~/.zshrc

```

#### 3. Git

```bash

# Install Git (likely already installed)

brew install git

# Verify

git --version

```

#### 4. Node.js (Optional - for analysis scripts)

```bash

# Install Node.js via Homebrew

brew install node

# Verify

node --version
npm --version

```

---

## Quick Start (5 Minutes)

**For experienced developers who just want to get running:**

```bash

# 1. Clone repository

git clone https://github.com/ShadowTag-v2/pnkln-stack-fastapi-services.git
cd pnkln-stack-fastapi-services

# 2. Create virtual environment

python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies

pip install --upgrade pip
pip install -r requirements.txt

# 4. Install package in development mode

pip install -e .

# 5. Create .env file (use example or create minimal)

cp .env.example .env  # Or create manually (see Configuration section)

# 6. Run tests to verify installation

pytest

# 7. Run development server (if FastAPI endpoints exist)

# uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

```

**Note:** Some components may not work until you configure API keys (Gemini, etc.). See [Configuration](#configuration) section.

---

## Detailed Setup

### Step 1: Clone Repository

```bash

# Navigate to your projects directory

cd ~/Projects  # Or wherever you keep code

# Clone the repository

git clone https://github.com/ShadowTag-v2/pnkln-stack-fastapi-services.git
cd pnkln-stack-fastapi-services

# Verify you're on the correct branch

git branch

# Should show: claude/shadowtagai-intelligence-pipeline-01DwB3v8zwZaHZC3HogNeRXt

```

### Step 2: Create Virtual Environment

**Why:** Isolates project dependencies from system Python and other projects.

```bash

# Create virtual environment

python3 -m venv venv

# Activate virtual environment

source venv/bin/activate

# You should see (venv) in your prompt:

# (venv) user@macbook pnkln-stack-fastapi-services %

# Verify Python is from venv

which python  # Should show /path/to/pnkln-stack-fastapi-services/venv/bin/python

```

**Tip:** Add this alias to ~/.zshrc for quick activation:

```bash
echo 'alias venv="source venv/bin/activate"' >> ~/.zshrc
source ~/.zshrc

```

### Step 3: Install Dependencies

```bash

# Upgrade pip (important!)

pip install --upgrade pip setuptools wheel

# Install all dependencies

pip install -r requirements.txt

# This may take 5-10 minutes depending on your internet speed

# Large packages: torch (2GB+), transformers, etc.

```

**Apple Silicon (M1/M2/M3) Notes:**

- PyTorch automatically installs ARM64-optimized builds

- If you get errors with `torch`, install explicitly:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
  ```

**Intel Mac Notes:**

- No special configuration needed

- Dependencies install via standard PyPI

### Step 4: Install Package in Development Mode

```bash

# Install shadowtagai_agents as editable package

pip install -e .

# Verify installation

python -c "from shadowtagai_agents import IntelligenceAgent; print('✅ Import successful')"

```

### Step 5: Verify Installation

```bash

# Run tests to verify everything is working

pytest

# Expected output:

# ============================= test session starts ==============================

# collected X items

# tests/... PASSED [ XX%]

# ============================= X passed in X.XXs ================================

```

---

## Configuration

### Environment Variables (.env)

Create `.env` file in project root:

```bash

# Copy example or create from scratch

touch .env
nano .env  # Or use VS Code: code .env

```

**Minimal .env for local development:**

```bash

# Application

APP_ENV=development
APP_DEBUG=true
APP_HOST=127.0.0.1
APP_PORT=8000

# Security

SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# --- API Keys (Optional - only needed for live data) ---

# Gemini API (for enforcement layer)

# Get key: https://makersuite.google.com/app/apikey

# GEMINI_API_KEY=your_gemini_api_key_here

# Anthropic (for future features)

# ANTHROPIC_API_KEY=your_anthropic_key_here

# OpenAI (for embeddings)

# OPENAI_API_KEY=your_openai_key_here

# --- GCP Configuration (Optional - for production ingestion) ---

# Google Cloud Project

# GOOGLE_CLOUD_PROJECT=your-gcp-project-id

# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# --- Data Sources (Optional - for live collection) ---

# Reddit API (for tech news aggregation)

# REDDIT_CLIENT_ID=your_reddit_client_id

# REDDIT_CLIENT_SECRET=your_reddit_secret

# REDDIT_USER_AGENT=SHADOWTAGAIBot/1.0

# YouTube API (for video intelligence)

# YOUTUBE_API_KEY=your_youtube_key

# Twitter API (for social intelligence)

# TWITTER_BEARER_TOKEN=your_twitter_token

# --- Database (Future) ---

# DATABASE_URL=sqlite:///./shadowtagai_agents.db  # Local SQLite for development

# DATABASE_URL=postgresql://user:pass@localhost/shadowtagai_agents  # PostgreSQL

# --- Monitoring (Optional) ---

# SENTRY_DSN=your_sentry_dsn

# PROMETHEUS_PORT=9090

```

**Important Notes:**

- Most features work without API keys in "mock mode"

- For actual intelligence collection, you'll need Gemini API key

- For compliance enforcement testing, Gemini API key is required

### Getting API Keys

#### Gemini API (Required for Enforcement)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)

2. Click "Get API key"

3. Create new project or select existing

4. Copy API key to `.env`:
   ```bash
   GEMINI_API_KEY=AIzaSy...
   ```

**Free Tier:**

- 60 requests/minute

- 1,500 requests/day

- Sufficient for local testing ✅

#### OpenAI API (Optional - for embeddings)

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)

2. Create API key

3. Add to `.env`:
   ```bash
   OPENAI_API_KEY=sk-...
   ```

**Costs:**

- text-embedding-3-small: $0.02/1M tokens (~$0.20 for 10M tokens)

- Budget for testing: $5-10 is plenty

#### Reddit API (Optional - for news collection)

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)

2. Create "script" application

3. Copy credentials to `.env`:
   ```bash
   REDDIT_CLIENT_ID=...
   REDDIT_CLIENT_SECRET=...
   REDDIT_USER_AGENT=SHADOWTAGAIBot/1.0
   ```

**Free:** No cost for API access

---

## Running the Platform

### Option 1: Interactive Python (Recommended for Testing)

```bash

# Activate virtual environment

source venv/bin/activate

# Start Python interpreter

python

# Run example code

>>> from shadowtagai_agents import IntelligenceAgent, IntelligenceTask, DEFAULT_SOURCES
>>>
>>> # Initialize agent
>>> agent = IntelligenceAgent()
>>>
>>> # Register default sources
>>> agent.register_sources(DEFAULT_SOURCES)
>>>
>>> # Collect intelligence (mock mode if no API keys)
>>> result = agent.collect_intelligence(
...     IntelligenceTask(
...         query="AI agent frameworks",
...         target_items=10,
...         customer_id="test_customer",
...         require_briefing=True,
...     )
... )
>>>
>>> # Check results
>>> print(result.status)
>>> print(result.briefing)

```

### Option 2: FastAPI Development Server (Future)

```bash

# Run development server

uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# Access endpoints

# - Health check: http://127.0.0.1:8000/health

# - API docs: http://127.0.0.1:8000/docs

# - Metrics: http://127.0.0.1:8000/metrics

```

**Note:** FastAPI endpoints are placeholders in current version. Main functionality is via Python API.

### Option 3: Run Analysis Scripts

```bash

# Activate virtual environment

source venv/bin/activate

# Run Gemini analysis (requires Gemini API key)

python shadowtagai_intelligence/scripts/run_gemini_analysis.py \
    --project-id your-gcp-project \
    --output docs/analysis/report_$(date +%Y-%m-%d).md

# View analysis results

cat docs/analysis/report_*.md

```

### Option 4: Run Tests

```bash

# All tests

pytest

# With verbose output

pytest -v

# With coverage report

pytest --cov=src/shadowtagai_agents --cov-report=html

# Open coverage report in browser

open htmlcov/index.html

# Specific test file

pytest tests/unit/test_jr_engine.py -v

# Integration tests only

pytest tests/integration/ -v

```

---

## Testing

### Unit Tests

```bash

# Run all unit tests

pytest tests/unit/

# Test specific components

pytest tests/unit/test_jr_engine.py -v
pytest tests/unit/test_Claude_Code_6_lite.py -v
pytest tests/unit/test_gemini_ingestion.py -v

```

### Integration Tests

```bash

# Run all integration tests

pytest tests/integration/

# Test intelligence agent (end-to-end)

pytest tests/integration/test_intelligence_agent.py -v

```

### Example: Manual Testing

```python

# Create test file: test_manual.py

from shadowtagai_agents import ComplianceSDRAgent

# Initialize agent

agent = ComplianceSDRAgent()

# Generate test leads

result = agent.generate_leads(
    query="German fintech CTOs",
    target_count=10,
    customer_id="test_customer",
    context={
        'gdpr_consent': False,
        'allow_personal_emails': False,
    }
)

# Check results

print(f"Status: {result.status.name}")
print(f"Approved: {len(result.output.approved_leads)}")
print(f"Blocked: {len(result.output.blocked_leads)}")
print(f"Cost: ${result.output.total_cost_usd:.2f}")

```

Run:

```bash
python test_manual.py

```

---

## Troubleshooting

### Common Issues

#### 1. `ModuleNotFoundError: No module named 'shadowtagai_agents'`

**Problem:** Package not installed or virtual environment not activated

**Solution:**

```bash

# Activate virtual environment

source venv/bin/activate

# Reinstall package

pip install -e .

# Verify

python -c "from shadowtagai_agents import IntelligenceAgent; print('OK')"

```

#### 2. `ImportError: cannot import name 'IntelligenceAgent'`

**Problem:** Outdated installation or code changes not reflected

**Solution:**

```bash

# Reinstall package in editable mode

pip install -e . --force-reinstall --no-deps

# Or restart Python interpreter

```

#### 3. `torch` Installation Fails (Apple Silicon)

**Problem:** Pre-built wheels not available for ARM64

**Solution:**

```bash

# Install PyTorch explicitly with CPU support

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Or use conda (if you have it)

conda install pytorch torchvision torchaudio -c pytorch

```

#### 4. `google-cloud-*` Dependencies Fail

**Problem:** Missing system dependencies

**Solution:**

```bash

# Install required system libraries

brew install libffi openssl

# Reinstall dependencies

pip install --upgrade google-cloud-storage google-cloud-bigquery google-cloud-aiplatform

```

#### 5. Slow `pip install` (Large Packages)

**Problem:** PyTorch and transformers are 2GB+ each

**Solution:**

```bash

# Use faster mirror (optional)

pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Or install in stages

pip install fastapi uvicorn pydantic  # Small packages first
pip install torch transformers  # Large packages separately
pip install -r requirements.txt  # Remaining packages

```

#### 6. Port 8000 Already in Use

**Problem:** Another service using port 8000

**Solution:**

```bash

# Find process using port 8000

lsof -i :8000

# Kill process (replace PID with actual process ID)

kill -9 <PID>

# Or use different port

uvicorn src.main:app --reload --port 8001

```

---

## Development Workflow

### Recommended Setup

**Terminal 1: Code Editor**

```bash

# Open project in VS Code

code .

# Or use your preferred editor

vim .
nano .

```

**Terminal 2: Python Interpreter (REPL)**

```bash

# Activate venv and start Python

source venv/bin/activate
python

# Quick iteration on code

>>> from shadowtagai_agents import IntelligenceAgent
>>> agent = IntelligenceAgent()
>>> # ... test code ...
>>>
>>> # Reload after code changes
>>> import importlib
>>> import shadowtagai_agents
>>> importlib.reload(shadowtagai_agents)

```

**Terminal 3: Test Watcher (Optional)**

```bash

# Install pytest-watch

pip install pytest-watch

# Run tests automatically on file changes

source venv/bin/activate
ptw tests/

```

### Code Quality Tools

```bash

# Format code with Black

black src/ tests/

# Lint with Ruff

ruff check src/ tests/

# Type check with mypy

mypy src/shadowtagai_agents/

# Run all quality checks

black src/ && ruff check src/ && mypy src/ && pytest

```

### Hot Reload Development

**For FastAPI endpoints:**

```bash

# Run with auto-reload

uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# Any code changes will automatically restart server

```

**For Python API:**

```bash

# Use iPython for better REPL experience

pip install ipython
ipython

# Enable auto-reload

%load_ext autoreload
%autoreload 2

# Now imports will auto-reload on file changes

from shadowtagai_agents import IntelligenceAgent

# ... make code changes ...

# ... re-run code - changes are reflected automatically ...

```

---

## Performance Optimization (Mac-Specific)

### Apple Silicon Acceleration

**Enable Metal Performance Shaders (MPS) for PyTorch:**

```python
import torch

# Check if MPS is available

if torch.backends.mps.is_available():
    device = torch.device("mps")
    print("✅ Using Apple Silicon GPU (MPS)")
else:
    device = torch.device("cpu")
    print("⚠️ Using CPU")

# Use device for tensor operations

# model.to(device)

```

### Memory Management

**Monitor memory usage:**

```bash

# Install memory_profiler

pip install memory_profiler

# Profile memory

python -m memory_profiler your_script.py

# Or use Activity Monitor (GUI)

# Applications > Utilities > Activity Monitor

```

**Reduce memory usage:**

```python

# Use generators instead of lists for large datasets

def process_items():
    for item in large_dataset:
        yield process(item)

# Instead of:

# results = [process(item) for item in large_dataset]

```

---

## Next Steps

### 1. Explore Examples

```bash

# Run example scripts

cd examples/
python compliance_sdr_demo.py
python intelligence_briefing_demo.py

```

### 2. Read Documentation

- **Architecture Decision Records:** `docs/adr/`

- **Cost Analysis:** `docs/COST_REVENUE_ANALYSIS.md`

- **Deployment Guide:** `docs/deployment.md`

### 3. Customize Configuration

- Modify `src/shadowtagai_agents/config/revenue_model.py` for pricing

- Adjust `src/shadowtagai_agents/config/constraints.py` for operational limits

- Update `src/shadowtagai_agents/config/ingestion_config.py` for data sources

### 4. Contribute

- Submit issues: https://github.com/ShadowTag-v2/pnkln-stack-fastapi-services/issues

- Pull requests welcome!

---

## Appendix: Useful Commands

### Virtual Environment Management

```bash

# Activate

source venv/bin/activate

# Deactivate

deactivate

# Recreate (if corrupted)

rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

### Dependency Management

```bash

# List installed packages

pip list

# Show package details

pip show shadowtagai-agents

# Freeze current dependencies

pip freeze > requirements-frozen.txt

# Update single package

pip install --upgrade google-cloud-aiplatform

# Update all packages (careful!)

pip install --upgrade -r requirements.txt

```

### Git Workflow

```bash

# Check current branch

git branch

# Pull latest changes

git pull origin claude/shadowtagai-intelligence-pipeline-01DwB3v8zwZaHZC3HogNeRXt

# Stash changes before pull

git stash
git pull
git stash pop

# View changes

git status
git diff

```

### Debugging

```bash

# Run Python with verbose imports

python -v -c "from shadowtagai_agents import IntelligenceAgent"

# Enable debug logging

export SHADOWTAGAI_DEBUG=true
python your_script.py

# Use pdb (Python debugger)

python -m pdb your_script.py

# Or insert breakpoint in code:

# import pdb; pdb.set_trace()

```

---

## Support

### Local Development Issues

- **Documentation:** Read `README.md` and `docs/` directory

- **Tests:** Run `pytest -v` to verify installation

- **Logs:** Check console output for error messages

### Getting Help

- **GitHub Issues:** https://github.com/ShadowTag-v2/pnkln-stack-fastapi-services/issues

- **Discussions:** https://github.com/ShadowTag-v2/pnkln-stack-fastapi-services/discussions

- **Email:** support@shadowtagai.ai (for enterprise customers)

---

**Last Updated:** 2025-11-16
**Tested On:** macOS 14.0 (Sonoma), Python 3.11.5, Apple Silicon M1
**Estimated Setup Time:** 15-30 minutes (including dependency downloads)

**Happy Coding!** 🚀
