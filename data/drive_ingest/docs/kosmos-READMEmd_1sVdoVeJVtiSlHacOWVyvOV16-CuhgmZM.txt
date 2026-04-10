# Kosmos on Google Cloud Platform

**Production-grade autonomous agent system implementing the Kosmos pattern on GCP infrastructure**

Combines:
- **Kosmos principle**: Long-horizon autonomous workflows with world-model coordination (inspired by arxiv 2511.02824)
- **ReAct algorithm**: Reason → Act → Observe loop for interpretable agent behavior (arxiv 2210.03629)
- **AgentOps**: Full observability, tracing, and operational excellence

Built for Vertex AI, GKE, and Gemini 2.5 Pro/Flash models.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GKE Autopilot Cluster                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Kosmos Orchestrator Pods                  │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │ │
│  │  │  Literature │  │ Data        │  │ Hypothesis  │   │ │
│  │  │  Agent      │  │ Analysis    │  │ Agent       │   │ │
│  │  │             │  │ Agent       │  │             │   │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘   │ │
│  │                                                        │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │          ReAct Orchestrator                     │  │ │
│  │  │  (Reason → Act → Observe → Reason loop)        │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    ┌──────────────┐   ┌────────────────┐   ┌──────────────┐
    │  Vertex AI   │   │   Firestore    │   │Cloud Storage │
    │ Gemini 2.5   │   │  (World Model) │   │ (Artifacts)  │
    │  Pro/Flash   │   │                │   │              │
    └──────────────┘   └────────────────┘   └──────────────┘
           │
           ▼
    ┌──────────────┐   ┌────────────────┐   ┌──────────────┐
    │  AgentOps    │   │  Cloud Trace   │   │ Cost Monitor │
    │ (Observ.)    │   │ (OpenTelemetry)│   │              │
    └──────────────┘   └────────────────┘   └──────────────┘
```

## Key Features

### Autonomous Research Workflows
- Multi-phase workflow orchestration (Ingest → Explore → Hypothesize → Test → Validate → Synthesize)
- Long-horizon task execution (20+ cycle autonomous runs)
- World model state management across phases

### Specialized Agents
- **Literature Agent** (Gemini Flash): Academic paper search, citation extraction
- **Data Analysis Agent** (Gemini Pro): Code generation, statistical testing, visualization
- **Hypothesis Agent** (Gemini Pro): Hypothesis generation, evaluation, refinement
- **Synthesis Agent** (Gemini Pro): Scientific report writing, citation formatting

### Production-Grade Infrastructure
- **GKE Autopilot**: Serverless Kubernetes with auto-scaling
- **Vertex AI**: Gemini 2.5 Pro ($1.25/1M tokens) and Flash ($0.075/1M tokens)
- **Firestore**: Persistent world model state
- **Cloud Storage**: Large artifact storage (datasets, plots, reports)

### Observability & Cost Control
- **AgentOps SDK**: Session tracking, event recording, dashboards
- **OpenTelemetry**: Cloud Trace integration with full trace hierarchy
- **Cost Monitor**: Budget enforcement, real-time burn tracking, alerts
- **Estimated cost**: ~$5-20 per 20-cycle research run (vs $200 for comparable systems)

---

## Quick Start

### Prerequisites

1. GCP project with billing enabled
2. APIs enabled: Vertex AI, Firestore, Cloud Storage, Cloud Trace
3. `gcloud` CLI installed and authenticated
4. Docker installed
5. kubectl configured

### Installation

```bash
# Clone repository
git clone https://github.com/ehanc69/aiyou-fastapi-services.git
cd aiyou-fastapi-services

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GCP_REGION="us-central1"
export STORAGE_BUCKET="${GOOGLE_CLOUD_PROJECT}-kosmos-artifacts"
export AGENTOPS_API_KEY="your-agentops-key"  # Optional
```

### Local Development

```bash
# Run example research cycle
python examples/simple_research_cycle.py
```

### Deploy to GKE

```bash
# Deploy using automated script
cd deployment
./scripts/deploy.sh

# Or manually:
# 1. Build and push Docker image
docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/kosmos-orchestrator:latest -f deployment/Dockerfile .
docker push gcr.io/$GOOGLE_CLOUD_PROJECT/kosmos-orchestrator:latest

# 2. Create GKE cluster
gcloud container clusters create-auto kosmos-cluster \
  --location=us-central1 \
  --project=$GOOGLE_CLOUD_PROJECT

# 3. Deploy to Kubernetes
kubectl apply -f deployment/kubernetes/deployment.yaml

# 4. Create AgentOps secret
kubectl create secret generic kosmos-secrets \
  --from-literal=agentops-api-key=$AGENTOPS_API_KEY
```

---

## Usage Examples

### Basic Research Cycle

```python
from kosmos.core.world_model import KosmosWorldModel
from kosmos.core.vertex_client import VertexAIClient, GeminiModel
from kosmos.agents.literature import LiteratureAgent
from kosmos.observability.cost_monitor import CostMonitor

# Initialize infrastructure
project_id = "your-project-id"
cost_monitor = CostMonitor(daily_budget=100.0)
vertex_client = VertexAIClient(project_id, cost_tracker=cost_monitor)

# Create world model
world_model = KosmosWorldModel(
    session_id="research_001",
    goal="Analyze correlation between variables in dataset"
)

# Create agent
tool_registry = {"google_search": google_search, ...}
lit_agent = LiteratureAgent(
    config=LiteratureAgent.DEFAULT_CONFIG,
    vertex_client=vertex_client,
    world_model=world_model,
    tool_registry=tool_registry,
)

# Execute task
result = lit_agent.search_papers(
    query="correlation analysis methods",
    limit=10
)

# Access results
print(f"Found {len(world_model.literature_refs)} papers")
print(f"Cost: ${cost_monitor.get_daily_burn():.2f}")
```

### Multi-Agent Workflow

```python
# Phase 1: Literature search
lit_result = literature_agent.search_papers("machine learning autonomous agents")

# Phase 2: Data analysis
analysis_result = data_analysis_agent.explore_dataset("data.csv")

# Phase 3: Hypothesis generation
hyp_result = hypothesis_agent.generate_hypotheses(num_hypotheses=5)

# Phase 4: Test top hypothesis
top_hyp = world_model.get_top_hypotheses(1)[0]
test_result = data_analysis_agent.test_hypothesis(top_hyp.id, "data.csv")

# Phase 5: Synthesize report
report = synthesis_agent.write_full_report()
```

### Custom Agent

```python
from kosmos.agents.base import BaseAgent, AgentConfig
from kosmos.core.vertex_client import GeminiModel

class CustomAgent(BaseAgent):
    DEFAULT_CONFIG = AgentConfig(
        name="custom_agent",
        model=GeminiModel.PRO,
        instruction="Your specialized instruction here...",
        tools=["tool1", "tool2"],
        temperature=0.7,
        max_iterations=20,
    )

    def execute_task(self, task, context=None):
        goal = self._build_goal_with_instruction(task)
        result = self.orchestrator.execute_cycle(goal)
        # Custom post-processing
        return result
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | Required |
| `GCP_LOCATION` | GCP region | `us-central1` |
| `FIRESTORE_DATABASE` | Firestore database name | `(default)` |
| `STORAGE_BUCKET` | Cloud Storage bucket | `{project}-kosmos-artifacts` |
| `AGENTOPS_API_KEY` | AgentOps API key | Optional |
| `DAILY_BUDGET` | Daily cost budget (USD) | `2000.0` |
| `MONTHLY_BUDGET` | Monthly cost budget (USD) | `60000.0` |
| `ENABLE_TELEMETRY` | Enable OpenTelemetry | `true` |

### Model Selection

```python
from kosmos.core.vertex_client import GeminiModel

# Use Flash for fast, cheap operations
vertex_client = VertexAIClient(
    project_id=PROJECT_ID,
    default_model=GeminiModel.FLASH,  # $0.075/1M input tokens
)

# Use Pro for deep reasoning
vertex_client = VertexAIClient(
    project_id=PROJECT_ID,
    default_model=GeminiModel.PRO,  # $1.25/1M input tokens
)

# Auto-routing based on context length and complexity
result = vertex_client.generate_with_auto_routing(
    prompt=long_prompt,
    complexity="high",  # Will use Pro
)
```

---

## Cost Optimization

### Estimated Costs

| Task | Model | Tokens | Cost |
|------|-------|--------|------|
| Literature search (10 papers) | Flash | 500k | $0.04 |
| Data analysis (1 dataset) | Pro | 2M | $2.50 |
| Hypothesis generation (5 hypotheses) | Pro | 1M | $1.25 |
| Report synthesis | Pro | 1.5M | $1.88 |
| **Total 20-cycle research run** | Mixed | ~5M | **$5-20** |

### Budget Controls

```python
from kosmos.observability.cost_monitor import CostMonitor, BudgetExceededError

cost_monitor = CostMonitor(
    daily_budget=100.0,
    monthly_budget=2000.0,
    session_budget=50.0,
    alert_threshold=0.8,  # Alert at 80%
)

try:
    # Check before execution
    cost_monitor.check_budget(estimated_cost=5.0)

    # Execute operation
    result = agent.execute_task(task)

    # Record actual usage
    cost_monitor.record_usage(
        tokens=result.tokens,
        model="gemini-3.1-family-pro",
        cost=result.cost,
    )

except BudgetExceededError as e:
    print(f"Budget exceeded: {e}")
```

---

## Observability

### AgentOps Dashboard

```python
from kosmos.observability.agentops_integration import AgentOpsTracker

tracker = AgentOpsTracker(api_key="your-key")

# Start session
tracker.start_session(
    goal="Research task",
    agent_name="literature_agent",
)

# Record events
tracker.record_thought(iteration=1, thought="I should search papers...")
tracker.record_action(iteration=1, action="google_search", action_input={"query": "..."})
tracker.record_observation(iteration=1, observation="Found 10 papers...")

# End session
tracker.end_session(result="success")
```

**Dashboard metrics:**
- Session success rate
- Average iterations per task
- Tool usage frequency
- Cost per session
- Token consumption trends

### Cloud Trace Integration

```python
from kosmos.observability.telemetry import setup_telemetry, TracedOperation

# Set up tracing
tracer = setup_telemetry(project_id=PROJECT_ID)

# Trace operations
with TracedOperation("agent_execution", agent="literature", goal="search"):
    result = agent.execute_task("search papers")
```

View traces in Cloud Console → Trace Explorer:
- Full hierarchy of agent → ReAct loop → tool calls
- Latency breakdown
- Error attribution
- Cross-service tracing

---

## Persistence

### World Model State

```python
from kosmos.persistence.firestore_backend import FirestoreBackend

firestore = FirestoreBackend(project_id=PROJECT_ID)

# Save
firestore.save_world_model(world_model)

# Load
world_model = firestore.load_world_model(session_id="research_001")

# Query
hypotheses = firestore.query_hypotheses(
    session_id="research_001",
    min_confidence=0.8,
    tested=False,
)
```

### Artifacts Storage

```python
from kosmos.persistence.storage_backend import CloudStorageBackend

storage = CloudStorageBackend(
    project_id=PROJECT_ID,
    bucket_name="my-kosmos-bucket",
)

# Upload
url = storage.upload_file(
    session_id="research_001",
    file_path="analysis.py",
    artifact_type="code",
)

# Download
storage.download_file(
    session_id="research_001",
    filename="analysis.py",
    artifact_type="code",
)

# Get shareable URL
public_url = storage.get_public_url(
    session_id="research_001",
    filename="plot.png",
    artifact_type="plots",
    expiration_hours=24,
)
```

---

## Production Deployment

### GKE Best Practices

1. **Autoscaling**: GKE Autopilot handles pod scaling automatically
2. **Resource limits**: Set appropriate memory/CPU limits in `deployment.yaml`
3. **Workload Identity**: Use for secure GCP service access
4. **Health checks**: Implement `/health` and `/ready` endpoints
5. **Monitoring**: Enable Cloud Monitoring and Logging

### Security

```bash
# Use Workload Identity (no service account keys)
gcloud iam service-accounts create kosmos-sa

# Grant minimal permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:kosmos-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Bind to K8s service account
gcloud iam service-accounts add-iam-policy-binding \
  kosmos-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[default/kosmos-sa]"
```

### Scaling Considerations

- **Concurrent sessions**: 3-10 pods handle ~50 concurrent research cycles
- **Cost scaling**: Linear with usage (~$5-20 per cycle)
- **Firestore limits**: 10K writes/sec (sufficient for 100+ agents)
- **Vertex AI quotas**: Monitor token/min quotas per model

---

## Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Load tests
pytest tests/load/ --workers=10
```

---

## Troubleshooting

### Common Issues

**Issue**: `BudgetExceededError`
**Solution**: Increase budget limits or optimize prompts to reduce token usage

**Issue**: Vertex AI quota exceeded
**Solution**: Request quota increase in Cloud Console or use rate limiting

**Issue**: Firestore permission denied
**Solution**: Verify service account has `roles/datastore.user`

**Issue**: GKE pods crashing (OOM)
**Solution**: Increase memory limits in `deployment.yaml`

### Debugging

```bash
# View pod logs
kubectl logs -f -l app=kosmos

# Check resource usage
kubectl top pods -l app=kosmos

# Describe pod issues
kubectl describe pod <pod-name>

# View Cloud Trace
# Navigate to: Cloud Console → Trace → Trace Explorer
```

---

## Contributing

See [KOSMOS_ARCHITECTURE.md](KOSMOS_ARCHITECTURE.md) for detailed architecture documentation.

---

## License

MIT License - See LICENSE file

---

## References

- Kosmos paper: [arxiv.org/abs/2511.02824](https://arxiv.org/abs/2511.02824)
- ReAct framework: [arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)
- Vertex AI Gemini: [cloud.google.com/vertex-ai/generative-ai](https://cloud.google.com/vertex-ai/generative-ai/docs)
- AgentOps: [docs.agentops.ai](https://docs.agentops.ai)
- GKE Autopilot: [cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)

---

**Built with ❤️ for autonomous research on Google Cloud Platform**
