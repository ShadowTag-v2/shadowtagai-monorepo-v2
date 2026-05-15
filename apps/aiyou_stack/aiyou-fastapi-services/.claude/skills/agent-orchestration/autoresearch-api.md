# n-autoresearch/Kosmos/BioAgents Server API Reference

**Version**: 1.0
**Last Updated**: 2025-11-26
**Scope**: External API interaction with the n-autoresearch/Kosmos/BioAgents Swarm Server

## Overview

The n-autoresearch/Kosmos/BioAgents Server exposes a REST API for submitting tasks to the agent swarm. It implements the **JURA Protocol** for cost-aware routing (Free/Flash/Pro tiers).

## Connection Details


- **Base URL**: `http://localhost:8600`

- **Port**: 8600

- **Protocol**: HTTP/1.1

- **Content-Type**: `application/json`

## Endpoints

### 1. Health Check

Verify server status and agent count.

```bash
GET /health

```

**Response**:

```json
{
  "status": "ok",
  "agents": 600,
  "tiers": {
    "bulk": { "model": "gemini-2.0-flash", "agents": 570 },
    "governance": { "model": "gemini-2.0-pro", "agents": 30 }
  },
  "uptime_seconds": 123.45
}

```

### 2. Submit Task

Submit a task for execution. The JURA protocol automatically routes to the optimal tier (Free/Flash/Pro) unless overridden.

```bash
POST /task

```

**Request Body**:

```json
{
  "prompt": "Analyze this python file for security vulnerabilities",
  "agents": 5,           // Optional: Requested agent count (default: 5)
  "timeout_ms": 500,     // Optional: Timeout in ms
  "governance": false,   // Optional: Force governance tier (Pro)
  "cost_tier": "auto",   // Optional: "auto", "free", "flash", "pro"
  "context_size": 1000   // Optional: Estimated token count
}

```

**Response**:

```json
{
  "success": true,
  "result": {
    "prompt": "...",
    "agents_assigned": ["exec_security_001", ...],
    "jura_tier": "flash",
    "model": "gemini-2.0-flash",
    "status": "executed"
  },
  "tier": "flash",
  "model": "gemini-2.0-flash",
  "agents_used": 3,
  "latency_ms": 15.2,
  "cost_usd": 0.0002
}

```

### 3. Governance Task

Submit a high-priority governance task (always uses Pro tier).

```bash
POST /governance

```

**Request Body**:

```json
{
  "prompt": "Review architectural compliance",
  "agents": 5
}

```

### 4. JURA Stats

Get cost tracking statistics.

```bash
GET /jura/stats

```

## Usage Patterns

### Python Client Example

```python
import requests

def run_swarm_task(prompt, tier="auto"):
    url = "http://localhost:8600/task"
    payload = {
        "prompt": prompt,
        "cost_tier": tier
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Swarm Error: {e}")
        return None

# Usage

result = run_swarm_task("Refactor this function")
print(f"Agents used: {result['agents_used']}")

```

### CLI Usage

Use the provided workflow:
`python3 bin/n-autoresearch/Kosmos/BioAgents-server`

## Troubleshooting


- **Connection Refused**: Server not running. Run `python3 bin/n-autoresearch/Kosmos/BioAgents-server`.

- **422 Validation Error**: Check request body format. Ensure `"prompt"` key is used, not `"task"`.

- **503 Service Unavailable**: Swarm initializing. Wait 5-10 seconds.
