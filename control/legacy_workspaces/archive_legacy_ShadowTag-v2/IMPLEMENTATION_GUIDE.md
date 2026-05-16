# Implementation Guide: DeepAgent → AiYou on Vertex AI

## Overview

This guide provides detailed instructions for implementing and deploying the AiYou system across the 8-week timeline, culminating in full deployment to ActiveShield's production environment.

## Table of Contents

1. [Week 1-2: Foundation](#week-1-2-foundation-completed)
2. [Week 3-4: ToolPO Training](#week-3-4-toolpo-training)
3. [Week 5-6: LangGraph Enhancement](#week-5-6-langgraph-enhancement)
4. [Week 7-8: ActiveShield Testing](#week-7-8-activeshield-testing)
5. [Month 3: Production Deployment](#month-3-production-deployment)

---

## Week 1-2: Foundation (✅ COMPLETED)

### Objectives
- [x] Implement tool discovery with dense retrieval
- [x] Build transparent memory management system
- [x] Create ActiveShield tool definitions
- [x] Set up Vertex AI Workbench notebooks

### What Was Delivered

#### 1. Tool Discovery Engine (`src/aiyou/tool_discovery.py`)
- Dense retrieval using Vertex AI text embeddings
- Support for 16k+ tools via vector search
- OpenAI function format compatibility
- Export/import functionality

**Usage:**
```python
from aiyou import ToolDiscoveryEngine

engine = ToolDiscoveryEngine(
    project="pnkln-activeshield",
    embedding_model="text-embedding-004"
)
engine.index_tools(activeshield_tools)
results = engine.search_tools("detect network threats", top_k=5)
```

#### 2. Transparent Memory Management (`src/aiyou/memory.py`)
- Episodic, working, and tool memory types
- User-controlled checkpoints (NOT autonomous)
- Full transparency with compression metrics
- Gemini-powered summarization

**Usage:**
```python
from aiyou import TransparentMemoryManager

memory = TransparentMemoryManager(
    project="pnkln-activeshield",
    model_name="gemini-3.1-flash-thinking-exp"
)
checkpoint = memory.create_checkpoint(
    interaction_history,
    reason="USER_REQUESTED_AT_MILESTONE"
)
print(f"Compression ratio: {checkpoint['metadata']['compression_ratio']:.2f}x")
```

#### 3. ToolPO Judge #6 (`src/aiyou/toolpo.py`)
- Fine-grained advantage attribution
- Token-level credit assignment
- Group-relative advantage computation
- Policy gradient data formatting

**Usage:**
```python
from aiyou import ToolCallAdvantageAttribution

judge = ToolCallAdvantageAttribution()
advantages = judge.compute_advantages(trajectories, task_rewards)
pg_data = judge.get_policy_gradient_data(advantages)
```

#### 4. LangGraph Reasoning (`src/aiyou/reasoning.py`)
- Multi-turn agentic reasoning
- State management with LangGraph
- Tool discovery integration
- Error recovery

**Usage:**
```python
from aiyou.reasoning import build_reasoning_graph, create_initial_state

graph, engine = build_reasoning_graph(tool_engine, memory_manager)
state = create_initial_state("Analyze network threats")
final_state = graph.invoke(state)
```

#### 5. Cor Unified Brain (`src/aiyou/cor.py`)
- Integrates all components
- Unified interface for task execution
- Full transparency and statistics
- ActiveShield-specific configuration

**Usage:**
```python
from aiyou.cor import create_activeshield_cor

cor = create_activeshield_cor(
    project="pnkln-activeshield",
    tools=activeshield_tools
)
result = cor.execute_task("Detect threats from IP 192.168.1.50")
```

#### 6. ActiveShield Tools (`src/aiyou/activeshield/`)
- 24 tools across 5 verticals
- Real-time threat detection (5 tools)
- Incident response (5 tools)
- Threat intelligence (5 tools)
- Vulnerability management (4 tools)
- Security monitoring (5 tools)

### Testing
All components have unit tests in `tests/`:
```bash
pytest tests/ -v
```

---

## Week 3-4: ToolPO Training

### Objectives
- [ ] Integrate ToolPO with Gemini training loop
- [ ] Implement K=8 rollout generation
- [ ] Set up advantage computation pipeline
- [ ] Configure Gemini API quota

### Implementation Steps

#### Step 1: Rollout Generation

Create `src/aiyou/training/rollout_generator.py`:

```python
from typing import List, Dict
from aiyou.cor import CorExecutionBrain
import asyncio

class RolloutGenerator:
    """Generate K rollouts for ToolPO training"""

    def __init__(self, cor_brain: CorExecutionBrain, K: int = 8):
        self.cor = cor_brain
        self.K = K

    async def generate_rollouts(self, task: str) -> List[Dict]:
        """Generate K diverse rollouts for a task"""
        rollouts = []

        for k in range(self.K):
            # Introduce randomness via temperature
            result = await self.cor.execute_task_async(
                task,
                temperature=0.7 + (k * 0.1),  # Vary temperature
                enable_memory=True
            )
            rollouts.append(result)

        return rollouts
```

#### Step 2: Training Loop

Create `src/aiyou/training/toolpo_trainer.py`:

```python
from vertexai.preview.generative_models import GenerativeModel
import vertexai

class ToolPOTrainer:
    """ToolPO training loop for Judge #6"""

    def __init__(self, project: str, model: str = "gemini-3.1-flash-thinking-exp"):
        vertexai.init(project=project)
        self.model = GenerativeModel(model)
        self.rollout_gen = RolloutGenerator(cor_brain)

    def train_epoch(self, tasks: List[str]):
        """Train for one epoch on a batch of tasks"""
        for task in tasks:
            # Generate rollouts
            rollouts = await self.rollout_gen.generate_rollouts(task)

            # Compute task rewards
            rewards = [self.evaluate_task(r) for r in rollouts]

            # Compute advantages
            advantages = self.judge.compute_advantages(
                [r['trajectory'] for r in rollouts],
                rewards
            )

            # Update policy (via Gemini fine-tuning API)
            self.update_policy(advantages)
```

#### Step 3: Gemini API Configuration

1. Request increased quota:
   ```bash
   # Submit quota increase request for:
   # - gemini-3.1-flash-thinking-exp: 10M tokens/day
   # - text-embedding-004: 5M tokens/day
   ```

2. Configure API keys:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
   export GCP_PROJECT="pnkln-activeshield"
   ```

### Testing
```bash
# Test rollout generation
python -m aiyou.training.test_rollouts

# Test advantage computation
python -m aiyou.training.test_advantages
```

### Deliverables
- Rollout generation system
- ToolPO training loop
- Gemini API integration
- Training metrics dashboard

---

## Week 5-6: LangGraph Enhancement

### Objectives
- [ ] Advanced reasoning patterns
- [ ] Error recovery mechanisms
- [ ] Multi-agent coordination
- [ ] Checkpoint optimization

### Implementation Steps

#### Step 1: Advanced Reasoning Patterns

Enhance `src/aiyou/reasoning.py`:

```python
def reflection_node(state: AgentState) -> AgentState:
    """Reflect on actions and adjust strategy"""
    if state['error_count'] > 2:
        # Analyze failures
        reflection = model.generate_content(f"""
        Previous actions failed. Analyze what went wrong:
        {state['tool_results'][-3:]}

        Suggest alternative approach.
        """)
        state['reasoning_chain'].append(f"REFLECTION: {reflection.text}")
    return state

# Add to workflow
workflow.add_node("reflection", reflection_node)
workflow.add_edge("tool_execution", "reflection")
```

#### Step 2: Error Recovery

```python
def error_recovery_node(state: AgentState) -> AgentState:
    """Attempt recovery from errors"""
    if state['error_count'] > 0:
        last_error = state['tool_results'][-1].get('error')

        # Analyze error and retry with different approach
        recovery_plan = model.generate_content(f"""
        Error occurred: {last_error}
        Current state: {state['working_memory']}

        Suggest recovery action.
        """)

        state['messages'].append(f"RECOVERY: {recovery_plan.text}")
    return state
```

#### Step 3: Multi-Agent Coordination

Create `src/aiyou/multi_agent/coordinator.py`:

```python
class AgentCoordinator:
    """Coordinate multiple specialized agents"""

    def __init__(self):
        self.agents = {
            'detector': create_detector_agent(),
            'responder': create_responder_agent(),
            'analyst': create_analyst_agent(),
        }

    def coordinate(self, task: str):
        """Coordinate agents for complex task"""
        # Decompose task
        subtasks = self.decompose_task(task)

        # Assign to specialists
        results = []
        for subtask in subtasks:
            agent = self.select_agent(subtask)
            result = agent.execute(subtask)
            results.append(result)

        # Synthesize results
        return self.synthesize(results)
```

### Deliverables
- Enhanced reasoning patterns
- Robust error recovery
- Multi-agent coordination
- Performance benchmarks

---

## Week 7-8: ActiveShield Testing

### Objectives
- [ ] Real-time threat detection integration
- [ ] Performance benchmarking
- [ ] Security validation
- [ ] Production readiness

### Implementation Steps

#### Step 1: Real Tool Integration

Replace mock executors in `src/aiyou/activeshield/executors.py`:

```python
import requests
from activeshield_sdk import Client

class ActiveShieldExecutors:
    """Real ActiveShield tool executors"""

    def __init__(self, api_key: str, base_url: str):
        self.client = Client(api_key, base_url)

    def analyze_network_traffic(self, params: Dict) -> Dict:
        """Real network traffic analysis"""
        return self.client.threat_detection.analyze_traffic(
            packet_data=params['packet_data'],
            threshold=params.get('threshold', 0.7)
        )

    def isolate_endpoint(self, params: Dict) -> Dict:
        """Real endpoint isolation"""
        return self.client.incident_response.isolate(
            endpoint_id=params['endpoint_id'],
            isolation_type=params.get('isolation_type', 'full')
        )
```

#### Step 2: Performance Benchmarking

Create `tests/benchmarks/test_performance.py`:

```python
import pytest
import time

def test_tool_discovery_performance():
    """Benchmark tool discovery latency"""
    engine = ToolDiscoveryEngine()
    engine.index_tools(get_all_activeshield_tools())

    start = time.time()
    results = engine.search_tools("detect threats", top_k=10)
    latency = time.time() - start

    assert latency < 0.5, "Tool discovery too slow"

def test_end_to_end_latency():
    """Benchmark full task execution"""
    cor = create_activeshield_cor()

    start = time.time()
    result = cor.execute_task("Analyze network threats")
    latency = time.time() - start

    assert latency < 10.0, "Task execution too slow"
```

#### Step 3: Security Validation

Create `tests/security/test_security.py`:

```python
def test_no_code_injection():
    """Ensure no code injection in tool parameters"""
    malicious_params = {
        "packet_data": "'; DROP TABLE users; --"
    }

    # Should sanitize and reject
    with pytest.raises(ValueError):
        executor.analyze_network_traffic(malicious_params)

def test_authentication_required():
    """Ensure all tools require authentication"""
    cor = CorExecutionBrain()  # No credentials

    with pytest.raises(AuthenticationError):
        cor.execute_task("Isolate endpoint")
```

### Deliverables
- Real ActiveShield integration
- Performance benchmarks
- Security validation report
- Production deployment plan

---

## Month 3: Production Deployment

### Objectives
- [ ] Deploy to all 5 ActiveShield verticals
- [ ] Scale to 16k+ tools
- [ ] Production monitoring
- [ ] User training

### Implementation Steps

#### Step 1: Vertex AI Matching Engine Setup

```bash
# Create vector index for 16k tools
gcloud ai index-endpoints create \
  --display-name="activeshield-tools" \
  --region=us-central1

gcloud ai indexes create \
  --display-name="tool-embeddings" \
  --metadata-file=index_metadata.json \
  --region=us-central1
```

#### Step 2: Production Configuration

Create `config/production.yaml`:

```yaml
vertex_ai:
  project: pnkln-activeshield
  location: us-central1
  embedding_model: text-embedding-004
  reasoning_model: gemini-3.1-flash-thinking-exp

cor:
  max_steps: 100
  enable_toolpo: true
  memory_checkpoints: true

activeshield:
  api_url: https://api.activeshield.ai
  timeout: 30
  retry_attempts: 3
```

#### Step 3: Monitoring Setup

Create `monitoring/dashboards.py`:

```python
from google.cloud import monitoring_v3

def create_cor_dashboard():
    """Create Cloud Monitoring dashboard"""
    client = monitoring_v3.DashboardsServiceClient()

    dashboard = {
        'display_name': 'Cor Execution Brain',
        'widgets': [
            # Task success rate
            {'title': 'Task Success Rate', 'metric': 'cor/task_success_rate'},
            # Average latency
            {'title': 'Avg Latency', 'metric': 'cor/latency_seconds'},
            # Tool usage
            {'title': 'Tool Calls', 'metric': 'cor/tool_calls_count'},
        ]
    }

    client.create_dashboard(dashboard)
```

#### Step 4: Deployment

```bash
# Deploy to Cloud Run
gcloud run deploy cor-brain \
  --image=gcr.io/pnkln-activeshield/cor:latest \
  --region=us-central1 \
  --memory=8Gi \
  --cpu=4 \
  --timeout=3600

# Deploy to GKE (for high scale)
kubectl apply -f k8s/cor-deployment.yaml
```

### Deliverables
- Production deployment across 5 verticals
- Vertex AI Matching Engine for 16k tools
- Monitoring and alerting
- User documentation and training

---

## Resource Requirements

### Compute
- **Vertex AI Workbench**: n1-standard-8 (8 vCPU, 30GB RAM)
- **Cloud Run**: 4 vCPU, 8GB RAM per instance
- **GKE** (optional): n1-standard-4 nodes, 3-10 nodes

### API Quotas
- **Gemini API**: 10M tokens/day
- **Embeddings API**: 5M tokens/day
- **Vertex AI Matching Engine**: 100k queries/day

### Storage
- **Cloud Storage**: 100GB for checkpoints and logs
- **BigQuery**: For training data and metrics

### Estimated Costs
- Vertex AI: ~$500/month
- Cloud Run: ~$200/month
- Storage: ~$50/month
- **Total**: ~$750/month

---

## Success Metrics

### Week 3-4
- [ ] ToolPO training loop operational
- [ ] K=8 rollouts generating successfully
- [ ] Advantage computation accuracy > 95%

### Week 5-6
- [ ] Error recovery rate > 80%
- [ ] Multi-agent coordination working
- [ ] Reasoning quality improvement > 20%

### Week 7-8
- [ ] Tool discovery latency < 500ms
- [ ] Task execution latency < 10s
- [ ] Security validation passing 100%

### Month 3
- [ ] All 5 verticals deployed
- [ ] 16k tools indexed
- [ ] Uptime > 99.9%
- [ ] User satisfaction > 90%

---

## Next Actions

1. **Immediate** (This Week):
   - Review Week 1-2 implementation
   - Begin ToolPO training loop development
   - Request Gemini API quota increase

2. **Short Term** (Next 2 Weeks):
   - Complete ToolPO integration
   - Test with ActiveShield sandbox
   - Prepare LangGraph enhancements

3. **Medium Term** (Month 2):
   - ActiveShield production integration
   - Performance optimization
   - Security hardening

4. **Long Term** (Month 3):
   - Full production deployment
   - Scale to all verticals
   - Continuous improvement

---

## Support and Documentation

- **Technical Docs**: `/docs`
- **API Reference**: `/docs/api.md`
- **Jupyter Notebooks**: `/notebooks`
- **Tests**: `/tests`

For questions or issues, contact the AiYou team.
