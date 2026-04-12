# Vertex AI Agents - Examples

This directory contains example code demonstrating how to use the Vertex AI Agents in various scenarios.

## Examples Overview

### 1. Basic Usage

**Files:** `basic_usage.py`, `basic_usage.js`

Demonstrates fundamental operations:


- Loading agents from the registry


- Using a single agent with Vertex AI


- Searching for agents by keyword


- Browsing agents by category


- Multi-agent workflows


- Conversation context management

**Run Python example:**

```bash
export VERTEX_AI_PROJECT_ID="your-project-id"
python examples/basic_usage.py

```

**Run JavaScript example:**

```bash
export VERTEX_AI_PROJECT_ID="your-project-id"
node examples/basic_usage.js

```

### 2. FastAPI Integration

**File:** `fastapi_integration.py`

Shows how to build a REST API service using the agents:


- List all agents


- Get agent details


- Search agents


- Chat with agents


- Browse by category

**Run the API:**

```bash
pip install fastapi uvicorn
python examples/fastapi_integration.py

```

**API Endpoints:**


- `GET /` - API information


- `GET /agents` - List all agents


- `GET /agents/{agent_id}` - Get agent details


- `GET /categories/{category_id}` - Get agents by category


- `POST /search` - Search agents


- `POST /chat` - Chat with an agent


- `GET /categories` - List all categories

**Example API usage:**

```bash

# List all agents

curl http://localhost:8000/agents

# Get specific agent

curl http://localhost:8000/agents/system-architect

# Search agents

curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"keyword": "API"}'

# Chat with agent

curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "code-mentor",
    "message": "What are SOLID principles?"
  }'

```

## Prerequisites

### Python

```bash
pip install google-cloud-aiplatform
pip install fastapi uvicorn  # For FastAPI example

```

### JavaScript

```bash
npm install @google-cloud/vertexai

```

### Google Cloud Setup

```bash

# Authenticate

gcloud auth application-default login

# Set project

gcloud config set project YOUR_PROJECT_ID

# Enable Vertex AI API

gcloud services enable aiplatform.googleapis.com

```

## Environment Variables

```bash

# Required

export VERTEX_AI_PROJECT_ID="your-project-id"

# Optional

export VERTEX_AI_LOCATION="us-central1"  # Default location

```

## Common Use Cases

### Use Case 1: Code Review Workflow

```python
from agent_registry import get_agent

# Step 1: Review code

reviewer = get_agent('code-reviewer')

# ... use reviewer to analyze code

# Step 2: Suggest refactorings

refactorer = get_agent('code-refactorer')

# ... use refactorer to improve code

# Step 3: Generate tests

test_gen = get_agent('test-generator')

# ... use test_gen to create tests

# Step 4: Security scan

scanner = get_agent('security-scanner')

# ... use scanner to check for vulnerabilities

```

### Use Case 2: Product Development

```python

# Strategy phase

strategist = get_agent('product-strategist')

# ... plan features

# Design phase

ux_optimizer = get_agent('ux-optimizer')

# ... optimize user flows

# Development phase

api_builder = get_agent('api-builder')

# ... build APIs

# Testing phase

test_gen = get_agent('test-generator')

# ... add tests

# Launch phase

seo_master = get_agent('seo-master')

# ... optimize for search

```

### Use Case 3: Infrastructure Setup

```python

# Design infrastructure

infra_builder = get_agent('infrastructure-builder')

# ... design cloud architecture

# Setup deployment

deployment = get_agent('deployment-wizard')

# ... configure CI/CD

# Add monitoring

monitoring = get_agent('monitoring-expert')

# ... setup observability

# Optimize costs

cost_opt = get_agent('cost-optimizer')

# ... reduce cloud spend

```

## Best Practices



1. **Agent Selection**


   - Use search and category browsing to find the right agent


   - Read agent capabilities and example prompts


   - Choose agents based on specific task requirements



2. **System Prompts**


   - Use the provided system prompts as-is for best results


   - Customize only if you have specific domain requirements


   - Test modifications to ensure quality doesn't degrade



3. **Configuration**


   - Start with default temperature and token settings


   - Adjust based on your needs (lower temp for consistency, higher for creativity)


   - Monitor token usage for cost optimization



4. **Multi-Agent Workflows**


   - Chain agents for complex tasks


   - Pass context between agents when needed


   - Validate outputs at each step



5. **Error Handling**


   - Always handle API errors gracefully


   - Implement retry logic for transient failures


   - Log errors for debugging

## Troubleshooting

**Error: Agent not found**


- Check that agents are loaded: `await loadAgents()` or `load_agents()`


- Verify agent ID is correct


- Check the registry.json file

**Error: Authentication failed**


- Run `gcloud auth application-default login`


- Verify VERTEX_AI_PROJECT_ID is set correctly


- Check that Vertex AI API is enabled

**Error: Rate limit exceeded**


- Implement rate limiting in your application


- Use appropriate retry logic with backoff


- Consider caching responses when possible

## Additional Resources



- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)


- [Generative AI on Vertex AI](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/overview)


- [Agent Registry Documentation](../README.md)

## Contributing Examples

To add new examples:



1. Create a new file in this directory


2. Follow existing example patterns


3. Add documentation in this README


4. Test thoroughly before submitting


5. Include error handling and comments
