# Deploy Ready Skill

5-prompt workflow to deploy-ready code (Replit-style).

## Pattern

```

IDEA → SCAFFOLD → IMPLEMENT → TEST → DEPLOY

```

## Usage

```python
from atomic_pipeline import DeployReadyOrchestrator

orchestrator = DeployReadyOrchestrator()
result = await orchestrator.run_flow(
    "Build a real-time chat API",
    target="cloud-run"  # cloud-run | gke | vertex | colab | local
)

```

## CLI

```bash
python -m atomic_pipeline.deploy_flow "Your idea here" cloud-run

```

## Stages

| # | Stage | Purpose | Cost |
|---|-------|---------|------|
| 1 | IDEA | Generate design spec (Gemini 3 Pro) | ~$0.087 |
| 2 | SCAFFOLD | Generate project structure | ~$0.02 |
| 3 | IMPLEMENT | Build via atomic pipeline | ~$0.05/atom |
| 4 | TEST | Generate comprehensive tests | ~$0.03 |
| 5 | DEPLOY | Push to production target | - |

## Deployment Targets


- `cloud-run` - Google Cloud Run (default)

- `gke` - Google Kubernetes Engine

- `vertex` - Vertex AI Workbench

- `colab` - Google Colab notebook

- `local` - Local development

## Framework Detection

Automatically detects framework from idea:

- **fastapi**: api, rest, backend, server, endpoint

- **react**: frontend, ui, web, dashboard, component

- **python**: script, tool, automation, data, ml, ai

- **fullstack**: app, application, full, stack

## Output

```python
DeployResult(
    idea="Build a chat API",
    design={...},           # Design spec
    scaffold=ScaffoldResult(...),
    implementation=ImplementationResult(...),
    tests=TestResult(...),
    deployment=DeploymentResult(
        target="cloud-run",
        url="https://chat-api-xyz.run.app",
        status="success"
    ),
    prompts_used=5,
    deploy_ready=True,
    total_duration_seconds=45.2,
    total_cost_usd=0.25
)

```

## Integration

Works with:

- GeminiClient (design leadership)

- AtomicPipelineOrchestrator (implementation)

- n-autoresearch/Kosmos/BioAgents swarm (parallel execution)

## Files


- `atomic_pipeline/deploy_flow.py` - Main orchestrator

- `atomic_pipeline/clients/gemini_client.py` - Gemini 3 Pro client
