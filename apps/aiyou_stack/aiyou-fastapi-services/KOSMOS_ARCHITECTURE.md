# KOSMOS ON GOOGLE CLOUD: ARCHITECTURE IMPLEMENTATION

## Executive Summary

This document describes the implementation of a **Kosmos-pattern autonomous agent system** on Google Cloud Platform, combining:

- **Kosmos principle**: Long-horizon autonomous workflows with world-model coordination

- **ReAct algorithm**: Reason → Act → Observe → Reason loop for interpretable agent behavior

- **AgentOps infrastructure**: Full observability, tracing, and operational excellence

## Architecture Decision: Option 1 (Production-Grade)

**Stack:**

```

├── GKE Autopilot cluster (GPU-enabled for inference)
├── Vertex AI Gemini 2.5 Pro/Flash (primary LLM brain)
├── Custom ReAct orchestrator (agent coordination)
├── AgentOps SDK (observability layer)
├── Firestore (world model state persistence)
├── Cloud Storage (artifacts, reports, datasets)
└── Cloud Trace + Cloud Logging (OpenTelemetry integration)

```

## Core Components

### 1. World Model (Kosmos-Pattern State Management)

The world model maintains state across multi-cycle autonomous workflows:

```python
class KosmosWorldModel:
    """
    Persistent state tracking across autonomous discovery cycles.
    Implements the 'structured world-model' concept from Kosmos paper.
    """
    hypotheses: List[Hypothesis]           # Generated research hypotheses
    analysis_results: List[AnalysisResult] # Experimental outcomes
    literature_refs: List[LiteratureRef]   # Papers/citations
    knowledge_graph: NetworkX.Graph        # Entity-relationship knowledge
    phase: WorkflowPhase                   # Current cycle phase
    confidence_scores: Dict[str, float]    # Per-hypothesis confidence

```

**Persistence:** Firestore for structured data + Cloud Storage for artifacts (plots, datasets, reports).

### 2. ReAct Loop Orchestrator

Implements the Reason → Act → Observe cycle:

```python
class ReActOrchestrator:
    """
    Core loop: LLM reasons about task → selects tool action →
    observes result → reasons again → repeats until goal.
    """

    def execute_cycle(self, goal: str, max_iterations: int = 50):
        context = []
        for i in range(max_iterations):
            # REASON: LLM generates thought + action
            response = self.llm.generate(
                prompt=self.build_react_prompt(goal, context)
            )
            thought, action, action_input = self.parse_response(response)

            # ACT: Execute tool
            observation = self.execute_tool(action, action_input)

            # OBSERVE: Append to context
            context.append({
                "iteration": i,
                "thought": thought,
                "action": action,
                "observation": observation
            })

            # Check termination
            if self.is_goal_achieved(response):
                return self.extract_final_answer(response)

```

**Termination criteria:**

- Explicit "Final Answer:" in LLM response

- Confidence threshold reached (>0.95)

- Max iterations (safety limit: 50 for fast loops, 500 for long-horizon)

### 3. Specialized Agents (Multi-Agent Workflow)

Following Gemini Enterprise Agent Builder patterns, we decompose into specialized agents:

#### 3.1 Literature Agent

```python
class LiteratureAgent(BaseAgent):
    model = "gemini-2.5-flash"  # Fast + cheap for search
    tools = [google_search, arxiv_search, semantic_scholar]
    instruction = "Search academic literature, extract key findings, maintain citation graph"

```

#### 3.2 Data Analysis Agent

```python
class DataAnalysisAgent(BaseAgent):
    model = "gemini-2.5-pro"  # Deep reasoning for code generation
    tools = [execute_python, plot_generator, statistical_test]
    instruction = "Analyze datasets, generate analysis code, produce visualizations"

```

#### 3.3 Hypothesis Agent

```python
class HypothesisAgent(BaseAgent):
    model = "gemini-2.5-pro"
    tools = [world_model_query, literature_query]
    instruction = "Generate testable hypotheses from literature + data patterns"

```

#### 3.4 Synthesis Agent

```python
class SynthesisAgent(BaseAgent):
    model = "gemini-2.5-pro"
    tools = [report_writer, citation_formatter]
    instruction = "Synthesize findings into structured scientific reports with citations"

```

### 4. Multi-Cycle Workflow (Kosmos-Style Long-Horizon)

Orchestrates agents across phases:

```

PHASE 1: Ingest        → Load datasets, initial literature search
PHASE 2: Explore       → Data exploration, pattern identification
PHASE 3: Hypothesize   → Generate candidate hypotheses
PHASE 4: Test          → Design & execute experiments/analysis
PHASE 5: Validate      → Statistical validation, literature cross-check
PHASE 6: Synthesize    → Write final report with citations

```

Each phase = multiple ReAct cycles. World model persists state between phases.

## Vertex AI Integration

### Model Selection Strategy

| Model | Use Case | Cost (1M tokens) | Latency |
|-------|----------|------------------|---------|
| Gemini 2.5 Flash | Literature search, fast iterations, tool routing | $0.075 input | ~500ms |
| Gemini 2.5 Pro | Deep reasoning, code generation, synthesis | $1.25 input | ~2s |

**Dynamic routing:** Use Flash for <5k context, Pro for >5k or when previous attempt failed.

### API Integration

```python
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.generative_models import Tool, FunctionDeclaration

# Initialize Vertex AI

vertexai.init(project=PROJECT_ID, location="us-central1")

# Create model with function calling

model = GenerativeModel(
    "gemini-2.5-pro",
    tools=[Tool(function_declarations=[
        FunctionDeclaration(name="execute_python", parameters=...),
        FunctionDeclaration(name="search_papers", parameters=...),
    ])]
)

# Generate with streaming for observability

response = model.generate_content(
    prompt,
    stream=True,
    generation_config={"temperature": 0.7, "max_output_tokens": 8192}
)

```

## AgentOps Integration

### Instrumentation Points

```python
import agentops
from opentelemetry import trace

# Initialize AgentOps

agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))

# Decorate agent methods

@agentops.record_action
def execute_cycle(self, goal):
    with agentops.Session(tags=["kosmos", "research"]) as session:
        # ReAct loop
        for iteration in range(max_iterations):
            session.record_event(
                event_type="thought",
                data={"iteration": iteration, "thought": thought}
            )
            session.record_event(
                event_type="action",
                data={"tool": action, "input": action_input}
            )
            session.record_event(
                event_type="observation",
                data={"result": observation, "tokens": token_count}
            )

```

### Observability Dashboards

**Metrics tracked:**

- **Per-session:** Total iterations, tool calls, tokens consumed, cost, duration

- **Per-agent:** Success rate, average cycles to completion, error rate

- **Per-tool:** Invocation count, latency, failure rate

- **Cost tracking:** Token usage by model, daily burn rate, cost per research cycle

**Alerts:**

- Infinite loop detection (>100 iterations without progress)

- Cost threshold exceeded ($200/session warning, $500 hard stop)

- Tool failure rate >10%

- World model state corruption

## OpenTelemetry + Cloud Trace Integration

```python
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure Cloud Trace exporter

trace.set_tracer_provider(TracerProvider())
cloud_trace_exporter = CloudTraceSpanExporter(project_id=PROJECT_ID)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)

tracer = trace.get_tracer(__name__)

# Instrument ReAct loop

with tracer.start_as_current_span("kosmos_cycle") as cycle_span:
    cycle_span.set_attribute("goal", goal)

    with tracer.start_as_current_span("reason") as reason_span:
        thought = self.llm.generate(prompt)
        reason_span.set_attribute("thought", thought)

    with tracer.start_as_current_span("act") as act_span:
        observation = self.execute_tool(action)
        act_span.set_attribute("tool", action)
        act_span.set_attribute("result_length", len(observation))

```

**Result:** Full trace hierarchy visible in Cloud Console → Trace Explorer.

## Cost Management

### Budget Controls

```python
class CostMonitor:
    def __init__(self, daily_budget: float = 2000.0):
        self.daily_budget = daily_budget
        self.current_burn = 0.0

    def check_budget(self, estimated_cost: float) -> bool:
        if self.current_burn + estimated_cost > self.daily_budget:
            raise BudgetExceededError(
                f"Request would exceed daily budget: "
                f"${self.current_burn:.2f} + ${estimated_cost:.2f} > ${self.daily_budget}"
            )
        return True

    def record_usage(self, tokens: int, model: str):
        cost = self.calculate_cost(tokens, model)
        self.current_burn += cost
        self.log_to_bigquery(tokens, model, cost)

```

**Pricing (Gemini 2.5):**

- Flash: $0.075 / 1M input, $0.30 / 1M output

- Pro: $1.25 / 1M input, $5.00 / 1M output

**Estimated cost per 20-cycle Kosmos run:**

- Literature search (Flash): ~500k tokens × $0.075 = $0.04

- Data analysis (Pro): ~2M tokens × $1.25 = $2.50

- Hypothesis generation (Pro): ~1M tokens × $1.25 = $1.25

- Synthesis (Pro): ~1.5M tokens × $1.25 = $1.88

- **Total: ~$5.67 per research cycle** (vs $200 for Edison Scientific Kosmos)

**Monthly capacity at $60k budget:** ~10,600 research cycles

## GKE Deployment

### Infrastructure as Code

```bash

# Create GKE Autopilot cluster with GPU support

gcloud container clusters create-auto kosmos-cluster \
  --location=us-central1 \
  --project=$PROJECT_ID \
  --workload-pool=$PROJECT_ID.svc.id.goog \
  --enable-autoprovisioning \
  --min-nodes=1 \
  --max-nodes=10

# Configure kubectl

gcloud container clusters get-credentials kosmos-cluster \
  --location=us-central1

```

### Kubernetes Manifests

**Deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kosmos-orchestrator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: kosmos
  template:
    metadata:
      labels:
        app: kosmos
    spec:
      serviceAccountName: kosmos-sa
      containers:


      - name: orchestrator
        image: gcr.io/$PROJECT_ID/kosmos-orchestrator:latest
        env:


        - name: GOOGLE_CLOUD_PROJECT
          value: "$PROJECT_ID"


        - name: AGENTOPS_API_KEY
          valueFrom:
            secretKeyRef:
              name: agentops-secret
              key: api-key
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "16Gi"
            cpu: "8"

```

**Service:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: kosmos-service
spec:
  type: LoadBalancer
  selector:
    app: kosmos
  ports:


  - port: 8080
    targetPort: 8080

```

### Workload Identity (Secure GCP Access)

```bash

# Create service account

gcloud iam service-accounts create kosmos-sa \
  --project=$PROJECT_ID

# Grant Vertex AI permissions

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:kosmos-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Bind to Kubernetes service account

gcloud iam service-accounts add-iam-policy-binding \
  kosmos-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:$PROJECT_ID.svc.id.goog[default/kosmos-sa]"

```

## Data Persistence

### Firestore Schema (World Model)

```

/sessions/{session_id}


  - created_at: timestamp


  - goal: string


  - status: "running" | "completed" | "failed"


  - current_phase: WorkflowPhase


  - total_cost: float


  - total_tokens: int

/sessions/{session_id}/hypotheses/{hypothesis_id}


  - text: string


  - confidence: float


  - supporting_evidence: array


  - created_at: timestamp

/sessions/{session_id}/analysis_results/{result_id}


  - code: string


  - outputs: array


  - plots: array (Cloud Storage URLs)


  - statistical_tests: object

/sessions/{session_id}/literature/{paper_id}


  - title: string


  - authors: array


  - abstract: string


  - relevance_score: float


  - citations_extracted: array

```

### Cloud Storage Layout

```

gs://{BUCKET_NAME}/
  sessions/
    {session_id}/
      datasets/
        input_data.csv
      plots/
        analysis_001.png
        analysis_002.png
      reports/
        final_report.pdf
      code/
        analysis_script.py

```

## Validation & Testing

### Unit Tests

- World model state transitions

- ReAct loop termination conditions

- Tool execution error handling

- Cost estimation accuracy

### Integration Tests

- End-to-end single-phase workflow

- Multi-agent coordination

- Firestore persistence/recovery

- Vertex AI API error handling

### Load Tests

- 10 concurrent research cycles

- 100 ReAct iterations (stress test)

- Network partition recovery

- Cost limit enforcement

## Deployment Checklist

- [ ] GCP project created with billing enabled

- [ ] Vertex AI API enabled

- [ ] GKE Autopilot cluster provisioned

- [ ] Workload Identity configured

- [ ] Firestore database created

- [ ] Cloud Storage buckets created

- [ ] AgentOps account + API key

- [ ] OpenTelemetry + Cloud Trace configured

- [ ] Cost monitoring alerts set up

- [ ] Docker image built and pushed to GCR

- [ ] Kubernetes manifests applied

- [ ] Integration tests passing

- [ ] First research cycle executed successfully

## Comparison to Alternatives

| Feature | Option 1 (This) | Option 2 (LangGraph) | Option 3 (Fork Kosmos) |
|---------|----------------|---------------------|----------------------|
| Time to MVP | 2-3 weeks | 3 days | 1 day |
| Production-ready | ✅ Yes | ⚠️ Limited | ❌ No |
| Custom world model | ✅ Full control | ⚠️ Via checkpointing | ✅ Existing implementation |
| Observability | ✅ AgentOps + OTel | ⚠️ Basic | ❌ Manual |
| Scalability | ✅ GKE Autopilot | ✅ Cloud Run | ❌ Single VM |
| Cost/run | ~$5-20 | ~$5-15 | ~$10-30 |
| Vendor lock-in | ⚠️ GCP | ⚠️ GCP | ⚠️ GCP |

## Next Steps

1. **Week 1:** Implement core ReAct orchestrator + world model + Vertex AI integration

2. **Week 2:** Build specialized agents + AgentOps instrumentation + Firestore persistence

3. **Week 3:** GKE deployment + cost monitoring + integration tests

4. **Week 4:** Production hardening + load testing + documentation

## Success Metrics

- ✅ Agent completes 20-cycle research workflow end-to-end

- ✅ AgentOps dashboard shows full trace hierarchy

- ✅ Cost per research cycle <$50 (10x cheaper than Edison Scientific)

- ✅ 95% uptime on GKE cluster

- ✅ P99 latency <5 minutes per ReAct cycle

- ✅ Zero world model state corruption incidents

## References

- Kosmos paper: arxiv.org/abs/2511.02824

- ReAct framework: arxiv.org/abs/2210.03629

- Vertex AI Gemini docs: cloud.google.com/vertex-ai/generative-ai/docs

- AgentOps SDK: docs.agentops.ai

- GKE Autopilot: cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview
