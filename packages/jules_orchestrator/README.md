# Jules Orchestrator SDK

The Jules Orchestrator SDK provides a robust Python client and session management system for integrating with Jules AI. This package communicates with the `jules_mcp_server` to provide autonomous and interactive AI agent capabilities.

## Installation

This package is part of the `ShadowTag-v2` Monorepo.

```bash
cd packages/jules_orchestrator
pip install -e .
```

## Overview

The SDK is composed of two main layers:

1. **`JulesClient`**: A low-level HTTP client wrapper that handles authentication, API headers, and direct calls to the Jules API endpoints.
2. **`JulesSession`**: A high-level state machine and session orchestrator. It manages the lifecycle of an AI task from initialization to completion, providing methods for polling, interactive approval, and automated workflow execution.

## Usage

### 1. Client Initialization

Initialize the `JulesClient` using an API key (typically fetched from GCP Secret Manager in this environment):

```python
import os
from jules_orchestrator.client import JulesClient

# The API key must be provided; typically via JULES_API_KEY env var.
client = JulesClient(
    api_key=os.environ.get("JULES_API_KEY", "your-api-key"),
    base_url="https://api.jules.ai/v1" # Defaults to standard URL
)
```

### 2. Starting a Session

A `JulesSession` represents a distinct task or continuous interaction context with the AI.

```python
from jules_orchestrator.session import JulesSession

session = JulesSession(
    client=client,
    source_name="example_repository",
    automation_mode="AUTO_CREATE_PR",
    task_description="Implement a new login component."
)

# Starts the session via the Jules API.
session_data = session.start()
print(f"Session started: {session.session_name}")
```

### 3. Workflow Management

You can poll the session status or run it as an automated workflow until completion:

```python
# Runs a blocking polling loop that automatically approves the plan
# and waits for the session to reach COMPLETED or FAILED state.
final_state = session.run_auto_pr_workflow(
    timeout=600,  # 10 minutes timeout
    interval=10   # poll every 10 seconds
)

print(f"Workflow finished with state: {final_state['state']}")
```

### 4. Interactive Mode

You can also interact directly with an active session using the `interact` tool. This requires the session to be in a valid interactive state.

```python
response = session.interact(text="Please refine the implementation of the login button.")
print(f"Current State: {response['state']}")
```

## Testing

The SDK comes with a comprehensive, deterministic test suite using `pytest` and `hypothesis`. The tests simulate network faults, `401 Unauthorized` errors, timeouts, and state transitions without making real network requests.

Run tests via:

```bash
pytest packages/jules_orchestrator/test_session.py
```
