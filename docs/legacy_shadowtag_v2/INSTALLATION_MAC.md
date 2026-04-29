# pnkln Ultrathink Stack - Mac Installation Guide

**Complete installation instructions for macOS (local and cloud)**

---

## Table of Contents

1. [Prerequisites](#prerequisites)

2. [Local Installation (Mac)](#local-installation-mac)

3. [Cloud Deployment (GCP)](#cloud-deployment-gcp)

4. [Verification](#verification)

5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Mac Requirements

**System:**

- macOS 12.0 (Monterey) or later

- 8GB RAM minimum (16GB recommended)

- 10GB free disk space

**Required Software:**

```bash

# 1. Homebrew (package manager)

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Python 3.11+

brew install python@3.11

# 3. Node.js 18+ and npm

brew install node@18

# 4. Git

brew install git

# 5. Optional: Docker Desktop for Mac

brew install --cask docker

```

**Verify installations:**

```bash
python3 --version   # Should show 3.11+
node --version      # Should show v18+
npm --version       # Should show 9+
git --version       # Should show 2.x+
docker --version    # Optional

```

---

## Local Installation (Mac)

### Step 1: Clone Repository

```bash

# Create workspace

mkdir -p ~/Projects
cd ~/Projects

# Clone repository

git clone https://github.com/YOUR_USERNAME/pnkln-stack-fastapi-services.git
cd pnkln-stack-fastapi-services

# Checkout the integrated branch

git checkout claude/vertex-workbench-code-01MQJ8CfXToph64WHQD2P7Zj

```

---

### Step 2: Python Environment Setup

**Option A: venv (recommended for simplicity)**

```bash

# Create virtual environment

python3 -m venv venv

# Activate (do this every time you open a new terminal)

source venv/bin/activate

# Upgrade pip

pip install --upgrade pip

# Install dependencies

pip install -r requirements.txt

# Install Judge 6 v2.0 dependencies

pip install -r Cor.Claude_Code_6/requirements.txt

```

**Option B: pyenv (recommended for multiple Python versions)**

```bash

# Install pyenv

brew install pyenv

# Add to ~/.zshrc or ~/.bash_profile

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Restart shell

exec "$SHELL"

# Install Python 3.11

pyenv install 3.11.7
pyenv local 3.11.7

# Create virtual environment

python -m venv venv
source venv/bin/activate

# Install dependencies

pip install --upgrade pip
pip install -r requirements.txt
pip install -r Cor.Claude_Code_6/requirements.txt

```

---

### Step 3: Node.js Setup (Universal Copilot)

```bash

# Navigate to Universal Copilot

cd universal-copilot

# Install dependencies

npm install

# Return to root

cd ..

```

---

### Step 4: Configure Environment Variables

```bash

# Copy environment template

cp universal-copilot/.env.example universal-copilot/.env

# Edit with your API keys

nano universal-copilot/.env

```

**Required API keys (choose one or more):**

```bash

# OpenAI (for GPT-4o)

OPENAI_API_KEY=sk-...

# Anthropic (for Claude Sonnet 4)

ANTHROPIC_API_KEY=sk-ant-...

# Google AI (for Gemini)

GOOGLE_API_KEY=...

# Optional: Enable governance

ENABLE_GOVERNANCE=true

# Optional: Cost tracking

ENABLE_COST_TRACKING=true

```

**Get API keys:**

- OpenAI: https://platform.openai.com/api-keys

- Anthropic: https://console.anthropic.com/

- Google AI: https://makersuite.google.com/app/apikey

---

### Step 5: Verify Installation

**Test Judge 6 v2.0:**

```bash

# From repository root

python3 -c "
from Cor.Claude_Code_6 import JudgmentRule, RiskLevel
judge = JudgmentRule(cor_instance_id='local-dev')
print('✅ Judge 6 v2.0 installed successfully')
print(f'Risk levels: {[r.value for r in RiskLevel]}')
"

```

**Test pnkln stack:**

```bash
python3 -c "
from src.pnkln import JudgeSix, RiskLevel, COR53_AXIOMS
judge = JudgeSix(cor_instance_id='local-dev')
print('✅ pnkln stack installed successfully')
print(f'Constitutional axioms: {len(COR53_AXIOMS)} rules')
"

```

**Test Universal Copilot:**

```bash
cd universal-copilot

# Test with mock provider (no API keys needed)

USE_MOCK=1 npm run dev

# Run tests

npm test

# Test with real providers (requires API keys)

npm run dev

```

**Run Stack Verification:**

```bash

# From repository root

python3 scripts/verify_pnkln_stack.py

```

Expected output:

```

======================================================================
pnkln Ultrathink Stack Verification
======================================================================

Layer 0: Memory Persistence
  ✓ Memory persistence directory exists
  ✓ scripts/extract_and_commit.py
  ...

✓ All 6 layers verified successfully!
pnkln Ultrathink Stack is ready for deployment
======================================================================

```

---

### Step 6: Run Daily Health Check

```bash

# Make executable (first time only)

chmod +x scripts/daily_health_check.sh

# Run health check

./scripts/daily_health_check.sh

```

---

## Cloud Deployment (GCP)

### Prerequisites for Cloud

**Install Google Cloud SDK:**

```bash

# Install gcloud CLI

brew install --cask google-cloud-sdk

# Initialize

gcloud init

# Login

gcloud auth login

# Set project

gcloud config set project YOUR_PROJECT_ID

```

**Enable Required APIs:**

```bash
gcloud services enable \
  compute.googleapis.com \
  container.googleapis.com \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  secretmanager.googleapis.com

```

---

### Option 1: Deploy to Vertex AI Workbench

**Best for:** Data science workflows, Jupyter notebooks, experimentation

**1. Create Vertex AI Workbench Instance:**

```bash

# Set variables

PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
INSTANCE_NAME="pnkln-workbench"

# Create instance

gcloud workbench instances create $INSTANCE_NAME \
  --location=$REGION \
  --machine-type=n1-standard-4 \
  --boot-disk-size=100GB \
  --accelerator-type=NVIDIA_TESLA_T4 \
  --accelerator-count=1

```

**2. Configure Memory Persistence:**

```bash

# Create GCS bucket for memory

gsutil mb -l $REGION gs://${PROJECT_ID}-workbench-memory

# Copy memory persistence config

gcloud compute scp erik-hancock-llm-memory/configs/vertex_workbench_config.py \
  $INSTANCE_NAME:/home/jupyter/ \
  --zone=${REGION}-a

```

**3. SSH into instance and install:**

```bash

# SSH to instance

gcloud workbench instances ssh $INSTANCE_NAME --location=$REGION

# Once inside, clone repository

cd /home/jupyter
git clone https://github.com/YOUR_USERNAME/pnkln-stack-fastapi-services.git
cd pnkln-stack-fastapi-services
git checkout claude/vertex-workbench-code-01MQJ8CfXToph64WHQD2P7Zj

# Install Python dependencies

pip install -r requirements.txt
pip install -r Cor.Claude_Code_6/requirements.txt

# Configure IPython startup

mkdir -p ~/.ipython/profile_default/startup
cp erik-hancock-llm-memory/configs/vertex_workbench_config.py \
   ~/.ipython/profile_default/startup/00_pnkln_memory.py

# Verify

python3 scripts/verify_pnkln_stack.py

```

**4. Access JupyterLab:**

```bash

# Get URL

gcloud workbench instances describe $INSTANCE_NAME \
  --location=$REGION \
  --format="value(gceSetup.networkInterfaces[0].accessConfigs[0].natIP)"

# Open in browser: https://[IP]:8080

```

---

### Option 2: Deploy to GKE (Google Kubernetes Engine)

**Best for:** Production deployments, scalability, high availability

**1. Create GKE Cluster:**

```bash
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
CLUSTER_NAME="pnkln-cluster"

# Create cluster with GPU support

gcloud container clusters create $CLUSTER_NAME \
  --region=$REGION \
  --machine-type=n1-standard-4 \
  --num-nodes=3 \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=5 \
  --addons=HorizontalPodAutoscaling,HttpLoadBalancing \
  --enable-stackdriver-kubernetes

# Get credentials

gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

```

**2. Build and Push Docker Image:**

```bash

# Ensure you have deployment infrastructure

# (Note: This is from llm-serving-efficiency-research branch - not integrated yet)

# For now, we'll create a basic Dockerfile

cat > Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements

COPY requirements.txt Cor.Claude_Code_6/requirements.txt ./
COPY Cor.Claude_Code_6/requirements.txt ./Cor.Claude_Code_6_requirements.txt

# Install Python dependencies

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r Cor.Claude_Code_6_requirements.txt

# Copy application code

COPY . .

# Expose ports

EXPOSE 8000 9090

# Run FastAPI server

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Build image

docker build -t gcr.io/${PROJECT_ID}/pnkln-stack:latest .

# Configure Docker for GCR

gcloud auth configure-docker

# Push to Google Container Registry

docker push gcr.io/${PROJECT_ID}/pnkln-stack:latest

```

**3. Create Kubernetes Deployment:**

```bash
cat > k8s-deployment.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pnkln-stack
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pnkln-stack
  template:
    metadata:
      labels:
        app: pnkln-stack
    spec:
      containers:


      - name: pnkln-stack
        image: gcr.io/PROJECT_ID/pnkln-stack:latest
        ports:


        - containerPort: 8000
          name: http


        - containerPort: 9090
          name: metrics
        env:


        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: pnkln-secrets
              key: google-api-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: pnkln-stack
spec:
  type: LoadBalancer
  selector:
    app: pnkln-stack
  ports:


  - name: http
    port: 80
    targetPort: 8000


  - name: metrics
    port: 9090
    targetPort: 9090
EOF

# Replace PROJECT_ID

sed -i '' "s/PROJECT_ID/${PROJECT_ID}/g" k8s-deployment.yaml

# Create secrets

kubectl create secret generic pnkln-secrets \
  --from-literal=google-api-key=YOUR_GOOGLE_API_KEY \
  --from-literal=openai-api-key=YOUR_OPENAI_API_KEY

# Deploy

kubectl apply -f k8s-deployment.yaml

# Check status

kubectl get pods
kubectl get services

```

**4. Access the Service:**

```bash

# Get external IP

kubectl get service pnkln-stack

# Wait for EXTERNAL-IP to appear (may take a few minutes)

# Access at: http://[EXTERNAL-IP]/

# Check logs

kubectl logs -l app=pnkln-stack --tail=100

```

---

### Option 3: Deploy Memory Persistence to GitHub

**Best for:** Cross-device sync, conversation history, collaboration

**1. Configure GitHub Repository:**

```bash

# Create GitHub repository for memory

gh repo create pnkln-memory --private

# Or use existing repo

cd ~/pnkln-memory
git init
git remote add origin https://github.com/YOUR_USERNAME/pnkln-memory.git

```

**2. Set up Automated Extraction:**

```bash

# Copy GitHub Actions workflows

mkdir -p .github/workflows
cp erik-hancock-llm-memory/.github/workflows/daily_sync.yml \
   .github/workflows/

# Configure secrets in GitHub

gh secret set GH_PAT --body "YOUR_GITHUB_PAT"

# Push

git add .
git commit -m "Initial memory persistence setup"
git push -u origin main

```

**3. Install Claude Code Memory (Local Mac):**

```bash

# Run installation script

python3 erik-hancock-llm-memory/scripts/claude_code_memory_local.py --install

# This installs to: ~/.claude-code/memory.md

# Verify

cat ~/.claude-code/memory.md | head -20

```

**4. Configure Cross-Device Sync:**

```bash

# Add sync script to crontab (runs every 6 hours)

crontab -e

# Add this line:

0 */6 * * * cd ~/pnkln-memory && /path/to/erik-hancock-llm-memory/scripts/sync_to_devices.sh --pull

# Manual sync

cd ~/pnkln-memory
./erik-hancock-llm-memory/scripts/sync_to_devices.sh --pull  # Fetch latest
./erik-hancock-llm-memory/scripts/sync_to_devices.sh --push  # Push updates

```

---

## Verification

### Complete System Check

```bash

# 1. Verify all layers

python3 scripts/verify_pnkln_stack.py

# 2. Run health check

./scripts/daily_health_check.sh

# 3. Test Judge 6 v2.0

python3 -c "
from Cor.Claude_Code_6 import JudgmentRule
judge = JudgmentRule(cor_instance_id='verification-test')
decision = judge.evaluate_request(
    user_input='Purpose: System test. Verify Judge 6 is working.',
    declared_purpose='System verification test'
)
print(f'✅ Judge 6 v2.0: {decision.approved}')
print(f'Risk Level: {decision.risk_level.value}')
print(f'Signature: {decision.provenance_stamp.signature[:16]}...')
"

# 4. Test Universal Copilot

cd universal-copilot
USE_MOCK=1 npm test

# 5. Test Gemini Function Calling (requires API key)

python3 -c "
from src.core import GeminiFunctionCaller, FunctionTool

def test_func(x: int) -> int:
    return x * 2

tool = FunctionTool(
    name='double',
    description='Double a number',
    function=test_func,
    parameters={'x': {'type': 'integer'}}
)

# This will fail without API key, but verifies imports work

print('✅ Gemini Function Calling imports OK')
"

```

---

## Troubleshooting

### Python Import Errors

**Problem:** `ModuleNotFoundError: No module named 'Cor.Claude_Code_6'`

**Solution:**

```bash

# Ensure you're in the repository root

cd /path/to/pnkln-stack-fastapi-services

# Ensure virtual environment is activated

source venv/bin/activate

# Verify Python path

python3 -c "import sys; print('\n'.join(sys.path))"

# The current directory should be in the path

# If not, add it:

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or add to your ~/.zshrc:

echo 'export PYTHONPATH="${PYTHONPATH}:/path/to/pnkln-stack-fastapi-services"' >> ~/.zshrc

```

---

### Google API Authentication Errors

**Problem:** `google.auth.exceptions.DefaultCredentialsError`

**Solution:**

```bash

# Option 1: Application Default Credentials (recommended)

gcloud auth application-default login

# Option 2: Service Account Key

gcloud iam service-accounts create pnkln-service-account
gcloud iam service-accounts keys create ~/pnkln-key.json \
  --iam-account=pnkln-service-account@${PROJECT_ID}.iam.gserviceaccount.com

export GOOGLE_APPLICATION_CREDENTIALS=~/pnkln-key.json

# Add to ~/.zshrc:

echo 'export GOOGLE_APPLICATION_CREDENTIALS=~/pnkln-key.json' >> ~/.zshrc

```

---

### Docker Build Errors on Mac M1/M2

**Problem:** Platform compatibility issues

**Solution:**

```bash

# Build for linux/amd64 (GCP)

docker buildx build \
  --platform linux/amd64 \
  -t gcr.io/${PROJECT_ID}/pnkln-stack:latest \
  --push \
  .

```

---

### Port Already in Use

**Problem:** `Address already in use: 8000`

**Solution:**

```bash

# Find process using port

lsof -ti:8000

# Kill process

kill -9 $(lsof -ti:8000)

# Or use different port

uvicorn app.main:app --port 8001

```

---

### npm Install Fails

**Problem:** Node version incompatibility

**Solution:**

```bash

# Install nvm (Node Version Manager)

brew install nvm

# Add to ~/.zshrc

echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.zshrc
echo '[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"' >> ~/.zshrc

# Restart shell

exec "$SHELL"

# Install Node 18

nvm install 18
nvm use 18

# Retry

cd universal-copilot
npm install

```

---

## Quick Start Scripts

### Local Development

```bash
#!/bin/bash

# save as: start-local.sh

# Activate Python environment

source venv/bin/activate

# Start FastAPI backend (terminal 1)

uvicorn app.main:app --reload --port 8000 &

# Start Universal Copilot dev mode (terminal 2)

cd universal-copilot && USE_MOCK=1 npm run dev &

# Run health check

sleep 5
./scripts/daily_health_check.sh

echo "✅ pnkln stack running:"
echo "   API: http://localhost:8000"
echo "   Copilot: Running with mock provider"
echo ""
echo "Press Ctrl+C to stop"
wait

```

---

### Cloud Deployment

```bash
#!/bin/bash

# save as: deploy-gcp.sh

PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"

# Build and push

docker build -t gcr.io/${PROJECT_ID}/pnkln-stack:latest .
docker push gcr.io/${PROJECT_ID}/pnkln-stack:latest

# Deploy to GKE

kubectl set image deployment/pnkln-stack \
  pnkln-stack=gcr.io/${PROJECT_ID}/pnkln-stack:latest

# Wait for rollout

kubectl rollout status deployment/pnkln-stack

# Get external IP

echo "✅ Deployed successfully!"
kubectl get service pnkln-stack

```

---

## Cost Estimates

### Local Mac (Development)

**Hardware:** Your existing Mac
**Cost:** $0/month

**API Usage (light development):**

- OpenAI: ~$10/month

- Anthropic: ~$5/month

- Google AI: Free tier (2M tokens/day)

- **Total: ~$15/month**

---

### GCP Vertex AI Workbench

**Instance:** n1-standard-4 with T4 GPU
**Cost:** ~$400/month

**Storage (GCS):** 100GB
**Cost:** ~$2/month

**API Usage:** Same as local
**Total: ~$417/month**

**When to use:** Data science workflows, experimentation

---

### GCP GKE (Production)

**GKE Cluster:** 3 nodes, n1-standard-4
**Cost:** ~$240/month

**Load Balancer:** External IP
**Cost:** ~$20/month

**Storage & Networking:** ~$30/month

**API Usage:** $870/month (production volume)

**Total: ~$1,160/month**

**When to use:** Production deployments, high availability

---

## Next Steps

### After Installation

1. **Run verification:**

   ```bash
   python3 scripts/verify_pnkln_stack.py
   ./scripts/daily_health_check.sh
   ```

2. **Read documentation:**

   ```bash
   cat INTEGRATION_SUMMARY.md
   cat DOLLAR_VALUE_ANALYSIS.md
   cat MONITORING.md
   ```

3. **Try examples:**

   ```bash
   # Judge 6 v2.0
   python3 Cor.Claude_Code_6/example.py

   # Universal Copilot
   cd universal-copilot
   USE_MOCK=1 npm run dev
   ```

4. **Deploy to production:**
   - Choose deployment option (Vertex AI or GKE)

   - Configure monitoring (Prometheus/Grafana)

   - Set up alerting

   - Enable automated backups

---

## Support

**Documentation:**

- `INTEGRATION_SUMMARY.md` - Complete integration guide

- `MONITORING.md` - Health monitoring

- `DOLLAR_VALUE_ANALYSIS.md` - ROI analysis

- `Cor.Claude_Code_6/README.md` - Judge 6 v2.0 docs

- `universal-copilot/README.md` - Universal Copilot docs

**Verification:**

```bash
python3 scripts/verify_pnkln_stack.py

```

**Health Check:**

```bash
./scripts/daily_health_check.sh

```

---

**Installation complete! You now have the full pnkln Ultrathink Stack ready for development or production.**
