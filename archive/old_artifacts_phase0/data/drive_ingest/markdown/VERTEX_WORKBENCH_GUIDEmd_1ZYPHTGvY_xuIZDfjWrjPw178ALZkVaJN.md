# pinkln Agent Architecture System - Vertex AI Workbench Deployment Guide

**"Insanely Great AI Systems Through Elegant Orchestration on Google Cloud"**

This guide walks you through deploying the pinkln Agent Architecture System on Google Cloud Vertex AI Workbench.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Configuration](#configuration)
5. [Cost Optimization](#cost-optimization)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Prerequisites

### Google Cloud Requirements

- Google Cloud account with billing enabled
- A Google Cloud project with the following APIs enabled:
  - Vertex AI API
  - Cloud Storage API (optional, for data persistence)
  - Cloud Logging API (for monitoring)

### IAM Permissions

Your user account or service account needs these roles:

```
roles/aiplatform.user
roles/notebooks.admin
roles/serviceusage.serviceUsageConsumer
roles/storage.objectAdmin (if using Cloud Storage)
```

### Local Requirements

- Basic understanding of Python and Jupyter notebooks
- Familiarity with AI/ML concepts
- Access to Claude models in Vertex AI Model Garden

## Quick Start

### Option 1: Create Workbench Instance via Console

1. Go to [Vertex AI Workbench](https://console.cloud.google.com/vertex-ai/workbench) in Google Cloud Console
2. Click **"New Instance"** → **"User-Managed Notebook"**
3. Configure:
   - **Name**: `pinkln-workbench`
   - **Region**: `us-central1` (or your preferred region)
   - **Machine type**: `n1-standard-4` (4 vCPUs, 15 GB RAM)
   - **Disk**: 100 GB
   - **Python version**: Python 3.10
4. Click **"Create"**
5. Wait for instance to start (2-3 minutes)
6. Click **"Open JupyterLab"**

### Option 2: Create via gcloud CLI

```bash
gcloud notebooks instances create pinkln-workbench \
  --location=us-central1-a \
  --machine-type=n1-standard-4 \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=common-cpu-notebooks \
  --disk-size-gb=100 \
  --metadata="proxy-mode=service_account"
```

### Clone the Repository

Once in JupyterLab:

```bash
git clone https://github.com/your-org/ShadowTag-v2-fastapi-services.git
cd ShadowTag-v2-fastapi-services
```

### Run Setup Notebook

1. Open `vertex_workbench_setup.ipynb`
2. Run all cells
3. Verify setup is successful
4. Open `pinkln_vertex_demo.ipynb` to start exploring

## Detailed Setup

### Step 1: Enable Required APIs

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  notebooks.googleapis.com \
  storage.googleapis.com \
  logging.googleapis.com
```

### Step 2: Configure Authentication

The Workbench instance uses Workload Identity by default. To verify:

```python
import google.auth
credentials, project = google.auth.default()
print(f"Project: {project}")
```

### Step 3: Install Dependencies

```bash
pip install -r requirements-vertex.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the repository root:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1

# Claude Configuration
ANTHROPIC_VERTEX_MODEL=gemini-3.1-family-5-sonnet-v2@20241022

# pinkln Configuration
PINKLN_ENV=production
PINKLN_LOG_LEVEL=INFO
```

### Step 5: Verify Claude Access

```python
from anthropic import AnthropicVertex

client = AnthropicVertex(
    region="us-central1",
    project_id="your-project-id"
)

response = client.messages.create(
    model="gemini-3.1-family-5-sonnet-v2@20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello!"}]
)
print(response.content[0].text)
```

## Configuration

### vertex_config.yaml

Customize `vertex_config.yaml` for your needs:

```yaml
google_cloud:
  project_id: "your-project-id"
  location: "us-central1"

claude:
  default_model: "gemini-3.1-family-5-sonnet-v2@20241022"
  max_tokens: 4096
  temperature: 1.0

pinkln:
  reasoning:
    basic_threshold: 0.3
    exploratory_threshold: 0.6
    collaborative_threshold: 0.9

cost_optimization:
  use_preemptible: false
  idle_shutdown_timeout: 120
  enable_semantic_cache: true
```

### Model Selection

Choose the right Claude model for your use case:

| Model | Best For | Input Price | Output Price |
|-------|----------|-------------|--------------|
| Claude 3.5 Sonnet | Complex reasoning, coding | $3/MTok | $15/MTok |
| Claude 3.5 Haiku | Simple tasks, high volume | $0.80/MTok | $4/MTok |
| Claude 3 Opus | Maximum capability | $15/MTok | $75/MTok |

## Cost Optimization

### 1. Right-Size Your Instance

For development:
```yaml
machine_type: n1-standard-2  # 2 vCPUs, 7.5 GB RAM
disk_size_gb: 50
```

For production workloads:
```yaml
machine_type: n1-standard-8  # 8 vCPUs, 30 GB RAM
disk_size_gb: 200
accelerator:
  type: NVIDIA_TESLA_T4  # Optional GPU
  count: 1
```

### 2. Enable Auto-Shutdown

Configure idle timeout to avoid charges when not in use:

```bash
gcloud notebooks instances update pinkln-workbench \
  --location=us-central1-a \
  --metadata="idle-timeout-seconds=7200"  # 2 hours
```

### 3. Use Preemptible Instances

For non-critical workloads, use preemptible instances (60-80% cost savings):

```bash
gcloud notebooks instances create pinkln-workbench-dev \
  --location=us-central1-a \
  --machine-type=n1-standard-4 \
  --vm-image-project=deeplearning-platform-release \
  --vm-image-family=common-cpu-notebooks \
  --metadata="preemptible=true"
```

### 4. Implement Semantic Caching

Reduce token usage by 40-60% with semantic caching:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_agent_call(challenge_hash, role):
    # Implementation in your production code
    pass
```

### 5. Monitor Costs

Set up budget alerts:

```bash
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="pinkln Vertex AI Budget" \
  --budget-amount=500USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Production Deployment

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  User Interface                      │
│              (Jupyter / Web App)                     │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│           Vertex AI Workbench Instance               │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │         pinkln Agent System                 │    │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────┐  │    │
│  │  │  Skills  │  │  Agents  │  │ Reasoning│  │    │
│  │  └──────────┘  └──────────┘  └─────────┘  │    │
│  └────────────────────────────────────────────┘    │
│                      │                              │
└──────────────────────┼──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│              Vertex AI Platform                      │
│                                                      │
│  ┌──────────────┐      ┌──────────────────────┐    │
│  │Claude Models │      │  Model Garden        │    │
│  │(Anthropic)   │◄─────┤  (200+ Models)       │    │
│  └──────────────┘      └──────────────────────┘    │
└─────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│          Supporting Services                         │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │Cloud Storage │  │Cloud Logging │  │Monitoring│  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
```

### Production Checklist

- [ ] **Security**
  - [ ] Enable Workload Identity
  - [ ] Configure VPC Service Controls
  - [ ] Set up private IP for Workbench
  - [ ] Implement IAM least privilege
  - [ ] Enable audit logging

- [ ] **Reliability**
  - [ ] Implement error handling and retries
  - [ ] Set up health checks
  - [ ] Configure backup strategy
  - [ ] Document disaster recovery plan

- [ ] **Monitoring**
  - [ ] Enable Cloud Logging
  - [ ] Set up Cloud Monitoring dashboards
  - [ ] Configure alerts for errors and budget
  - [ ] Track token usage metrics

- [ ] **Cost Management**
  - [ ] Set up budget alerts
  - [ ] Implement semantic caching
  - [ ] Right-size instances
  - [ ] Schedule auto-shutdown

- [ ] **Code Quality**
  - [ ] Version control for prompts
  - [ ] Unit tests for critical paths
  - [ ] Code review process
  - [ ] Documentation

### Sample Production Code

```python
import logging
from typing import Optional
from anthropic import AnthropicVertex
from google.cloud import logging as cloud_logging

class ProductionPnklnAgent:
    """Production-ready pinkln agent with error handling and logging."""

    def __init__(self, project_id: str, location: str):
        # Initialize Cloud Logging
        logging_client = cloud_logging.Client()
        logging_client.setup_logging()
        self.logger = logging.getLogger(__name__)

        # Initialize Vertex AI client
        self.client = AnthropicVertex(region=location, project_id=project_id)
        self.project_id = project_id
        self.location = location

    def execute(
        self,
        challenge: str,
        max_retries: int = 3
    ) -> Optional[dict]:
        """Execute with retry logic and error handling."""
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model="gemini-3.1-family-5-sonnet-v2@20241022",
                    max_tokens=4096,
                    messages=[{"role": "user", "content": challenge}]
                )

                # Log success
                self.logger.info(
                    "Agent execution successful",
                    extra={
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    }
                )

                return {
                    "solution": response.content[0].text,
                    "usage": response.usage.__dict__
                }

            except Exception as e:
                self.logger.error(
                    f"Attempt {attempt + 1} failed: {str(e)}",
                    exc_info=True
                )
                if attempt == max_retries - 1:
                    raise

        return None
```

## Troubleshooting

### Common Issues

#### 1. "Permission denied" errors

**Solution**: Verify IAM permissions

```bash
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:YOUR_EMAIL"
```

#### 2. "Model not found" errors

**Solution**: Ensure Claude models are available in your region

```python
from google.cloud import aiplatform

aiplatform.init(project="YOUR_PROJECT", location="us-central1")
models = aiplatform.Model.list(filter='display_name:"claude"')
for model in models:
    print(f"Available: {model.display_name}")
```

#### 3. High costs

**Solution**:
- Check token usage with `agent.get_usage_summary()`
- Implement caching for repeated queries
- Use Haiku model for simple tasks
- Set appropriate `max_tokens` limits

#### 4. Slow response times

**Solution**:
- Use streaming for long responses
- Reduce `max_tokens` if possible
- Consider using smaller model for less complex tasks
- Check instance size and upgrade if needed

### Getting Help

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Claude on Vertex AI](https://docs.anthropic.com/en/api/claude-on-vertex-ai)
- [pinkln Repository Issues](https://github.com/your-org/ShadowTag-v2-fastapi-services/issues)

## Best Practices

### 1. Prompt Engineering

Follow the pinkln philosophy:
- Question everything - don't accept the first solution
- Obsess over details - be specific in prompts
- Iterate relentlessly - refine prompts based on results

### 2. Error Handling

Always implement retry logic with exponential backoff:

```python
import time
from anthropic import APIError

def execute_with_retry(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except APIError as e:
            if i == max_retries - 1:
                raise
            time.sleep(2 ** i)  # Exponential backoff
```

### 3. Token Management

Monitor and optimize token usage:

```python
def estimate_tokens(text: str) -> int:
    """Rough estimation: 1 token ≈ 4 characters."""
    return len(text) // 4

challenge = "Your challenge here"
estimated = estimate_tokens(challenge)
print(f"Estimated tokens: {estimated}")
```

### 4. Version Control

Keep track of prompt versions:

```python
PROMPT_VERSION = "v1.2.0"
PROMPT_REGISTRY = {
    "revenue_optimizer": {
        "version": "v1.2.0",
        "template": "...",
        "last_updated": "2024-11-15"
    }
}
```

### 5. Testing

Test prompts before production:

```python
def test_agent_response():
    agent = VertexPnklnAgent(PROJECT_ID, LOCATION)

    test_cases = [
        {"input": "Simple test", "expected_strategy": "chain_of_thought"},
        {"input": "Complex multi-part test...", "expected_strategy": "multi_agent_debate"}
    ]

    for case in test_cases:
        result = agent.execute(case["input"])
        assert result["strategy"] == case["expected_strategy"]
```

## Next Steps

1. Complete the setup notebook: `vertex_workbench_setup.ipynb`
2. Explore the demo: `pinkln_vertex_demo.ipynb`
3. Build custom skills in `pinkln/skills/`
4. Implement production monitoring
5. Scale to your use case

## Resources

- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)
- [Claude Model Documentation](https://docs.anthropic.com/en/docs/intro-to-claude)
- [Google Cloud Architecture Center](https://cloud.google.com/architecture)
- [pinkln Documentation](./pinkln/docs/)

---

**"The people who are crazy enough to think they can change the world are the ones who do."** 🚀

Built with craftsmanship. Designed for excellence. Deployed on Google Cloud.
