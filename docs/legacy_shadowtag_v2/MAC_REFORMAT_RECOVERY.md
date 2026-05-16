# Mac Reformat Recovery Guide

## Quick Start After Reformat

```bash

# 1. Install Homebrew

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install essentials

brew install git gh node python@3.11

# 3. Clone the repo

git clone https://github.com/ShadowTag-v2/pnkln-stack-fastapi-services.git ~/pnkln-stack-fastapi-services
cd ~/pnkln-stack-fastapi-services

# 4. Auth GitHub

gh auth login

# 5. Install Claude Code

npm install -g @anthropic-ai/claude-code

```

---

## Sovereign Infrastructure Recovery

### 1. Self-Hosted GitHub Runner

```bash

# Create runner directory

mkdir ~/actions-runner && cd ~/actions-runner

# Download latest runner

curl -o actions-runner-osx-x64.tar.gz -L https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-osx-x64-2.329.0.tar.gz
tar xzf ./actions-runner-osx-x64.tar.gz

# Get registration token

RUNNER_TOKEN=$(gh api -X POST repos/ShadowTag-v2/pnkln-stack-fastapi-services/actions/runners/registration-token --jq '.token')

# Configure

./config.sh --url https://github.com/ShadowTag-v2/pnkln-stack-fastapi-services --token $RUNNER_TOKEN --name sovereign --labels self-hosted,macOS,X64 --unattended

# Start (background)

nohup ./run.sh > runner.log 2>&1 &

# Verify

gh api repos/ShadowTag-v2/pnkln-stack-fastapi-services/actions/runners --jq '.runners[]'

```

### 2. Google Cloud SDK

```bash

# Install

curl https://sdk.cloud.google.com | bash

# Init

~/google-cloud-sdk/bin/gcloud init

# Set project

gcloud config set project acquired-jet-478701-b3

# Auth

gcloud auth login
gcloud auth application-default login

```

### 3. Flying Monkeys (Cloud Run)

Already deployed at:


- **URL**: `https://https://github.com/karpathy/autoresearchs-server-215390634092.us-central1.run.app`


- **Image**: `us-central1-docker.pkg.dev/acquired-jet-478701-b3/https://github.com/karpathy/autoresearchs/server:gemini25flash`

```bash

# Health check

curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://https://github.com/karpathy/autoresearchs-server-215390634092.us-central1.run.app/health

```

---

## Key Credentials (Store in 1Password/Keychain)

| Service | Location |
|---------|----------|
| GitHub Token | `gh auth login` |
| GCP Service Account | `~/Downloads/client_secret_*.json` |
| GEMINI_API_KEY | Environment variable |
| Anthropic API Key | Claude Code auth |

---

## Environment Variables (.zshrc)

```bash
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
export GOOGLE_CLOUD_PROJECT="acquired-jet-478701-b3"
export GEMINI_API_KEY="your-key-here"

```

---

## Project Locations

| Project | Path |
|---------|------|
| Main Repo | `~/pnkln-stack-fastapi-services` |
| Actions Runner | `~/actions-runner` |
| GCloud SDK | `~/google-cloud-sdk` |

---

## Verification Checklist



- [ ] Git configured (`git config --global user.name/email`)


- [ ] GitHub CLI authenticated (`gh auth status`)


- [ ] GCloud authenticated (`gcloud auth list`)


- [ ] Runner online (`gh api .../actions/runners`)


- [ ] Claude Code installed (`claude --version`)


- [ ] Python 3.11+ (`python3 --version`)


- [ ] Node 18+ (`node --version`)

---

## Cloud Resources (No Local State Needed)

| Resource | Location | Status |
|----------|----------|--------|
| GKE Autopilot | us-central1 | Active |
| Cloud Run (FM) | us-central1 | Active |
| Artifact Registry | us-central1 | Active |
| Cloud SQL | us-central1 | Provisioned |

---

*Last updated: 2025-11-30*
