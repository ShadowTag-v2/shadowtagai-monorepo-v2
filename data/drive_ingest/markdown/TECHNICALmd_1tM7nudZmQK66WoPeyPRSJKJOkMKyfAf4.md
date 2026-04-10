# Technical Documentation

## UnGPT + AunCRM Integration

This document provides technical details for developers and advanced users.

---

## Architecture Deep Dive

### 1. AunCRM Compliance Framework

#### Purpose-Reasons-Brakes (PRB) Model

Every decision/action in the system must define:

**Purpose**: What problem are we solving?
```python
Purpose(
    description="Deploy feature X to production",
    business_value="Increases revenue by $Y",
    success_criteria=["Metric A improves", "Error rate < Z%"]
)
```

**Reasons**: Why is this approach valid?
```python
Reason(
    justification="Feature tested with 10K users",
    evidence=["A/B test results", "User feedback"],
    assumptions=["Production matches staging"],
    confidence_score=0.85  # 0.0 - 1.0
)
```

**Brakes**: What constraints must be enforced?
```python
Brake(
    constraint="Rollback if error rate > 0.5%",
    threshold=0.005,
    enforcement_method="automated_monitoring",
    violation_action="immediate_rollback",
    roi_threshold=3.0,  # Business gates
    ltv_cac_ratio=4.0,
    time_horizon_months=18
)
```

#### Risk Stratification (ATP 5-19)

```python
class RiskLevel(Enum):
    RA_1 = "routine"      # Normal ops, standard validation
    RA_2 = "low"          # Minor impact, evidence required
    RA_3 = "moderate"     # Significant, needs scenario planning
    RA_4 = "high"         # Mission-critical, explicit approval
```

Validation rules:
- **RA-1**: Standard PRB check
- **RA-2**: + Evidence-based reasoning (confidence ≥ 0.70)
- **RA-3**: + ≥2 reasons, ≥1 brake, Monte Carlo simulation recommended
- **RA-4**: + ≥3 reasons, ≥2 brakes, explicit approval required

#### Business Judgment Rule Gates

```python
def _apply_business_judgment_gates(context: ComplianceContext):
    # Gate 1: Evidence threshold
    avg_confidence = mean(r.confidence_score for r in context.reasons)
    if avg_confidence < 0.70:
        FAIL("Insufficient evidence")

    # Gate 2: Risk-adjusted approval
    if context.risk_level == RA_4 and not context.approved:
        FAIL("RA-4 requires explicit approval")

    # Gate 3: Brake enforcement
    if not context.brakes:
        FAIL("No brake mechanisms defined")
```

---

### 2. Atomic Thread Orchestrator

#### Decomposition Phase (JR - Judgment Rule)

Query → Atomic Threads with PRB

```python
decomposition_prompt = f"""
Decompose query into atomic threads.
Each thread needs:
- PURPOSE: Specific sub-problem
- REASONS: Why this decomposition?
- BRAKES: What constraints?
- RISK_LEVEL: RA-1 through RA-4
- DEPENDENCIES: Which threads must complete first?
"""
```

Example decomposition:

**Query**: "Analyze edge AI compute market"

**Threads**:
1. `T001_market_size`
   - Purpose: Calculate TAM/SAM/SOM
   - Reasons: ["Independent analysis", "Public data available"]
   - Brakes: ["Must cite sources", "No speculation"]
   - Risk: RA-2
   - Dependencies: []

2. `T002_competitive_landscape`
   - Purpose: Identify competitors and positioning
   - Reasons: ["Can run in parallel", "Publicly available data"]
   - Brakes: ["No insider information", "Verify all claims"]
   - Risk: RA-2
   - Dependencies: []

3. `T003_financial_model`
   - Purpose: Build revenue projections
   - Reasons: ["Needs market size from T001"]
   - Brakes: ["Use conservative assumptions", "Show confidence intervals"]
   - Risk: RA-3
   - Dependencies: ["T001_market_size"]

#### Execution Phase (NS - Neural Swarm)

Topological sort → Parallel execution

```python
async def execute_threads_concurrent(threads):
    executed = set()
    results = []

    while len(executed) < len(threads):
        # Find threads with dependencies met
        ready = [
            t for t in threads
            if t.thread_id not in executed
            and all(dep in executed for dep in t.dependencies)
        ]

        # Execute ready threads in parallel
        batch = await asyncio.gather(*[execute_thread(t) for t in ready])

        for result in batch:
            executed.add(result.thread_id)
            results.append(result)

    return results
```

**Error Isolation**: Exceptions in one thread don't propagate

```python
try:
    thread.result = await call_llm(thread.prompt)
except Exception as e:
    thread.error = e  # Contained!
    # Other threads continue executing
```

#### Synthesis Phase (Cor - Unified Brain)

Stitch results → Coherent output

```python
stitching_prompt = f"""
You received {len(successful)} thread results.
Synthesize into coherent response:

THREAD RESULTS:
{thread_results_text}

FAILED THREADS:
{failed_threads}  # Handle gracefully

Requirements:
1. Logical flow
2. Resolve contradictions
3. Note gaps from failures
4. Executive summary
"""
```

---

### 3. Multi-LLM Consensus System

#### Layer 1: Initial Reasoning (Claude)

```python
async def layer1_initial_reasoning(query):
    prompt = f"""
    You are Layer 1 in consensus system.
    Analyze: {query}

    Your response goes to Grok, Gemini, GPT for review.
    Be thorough and show reasoning.
    """

    response = anthropic.messages.create(...)
    return ModelResponse(model=CLAUDE, content=response.text, ...)
```

#### Layer 2: Parallel Analysis (Grok, Gemini, GPT)

```python
async def layer2_parallel_analysis(claude_response, query):
    prompt = f"""
    ORIGINAL: {query}
    CLAUDE'S ANALYSIS: {claude_response}

    Your task:
    1. Independently analyze query
    2. Evaluate Claude's reasoning
    3. Provide your own response
    4. Rate confidence (0.0-1.0)
    """

    # Execute concurrently
    grok, gemini, gpt = await asyncio.gather(
        query_grok(prompt),
        query_gemini(prompt),
        query_gpt(prompt)
    )

    return [grok, gemini, gpt]
```

#### Layer 2.5: Cross-Validation (Peer Review)

```python
async def layer2_5_cross_validation(responses):
    reviews = {}

    for target in responses:
        peer_reviews = []

        for reviewer in responses:
            if reviewer == target:
                continue  # Don't review yourself

            review = await get_peer_review(reviewer, target)
            peer_reviews.append(review)

        reviews[target.model] = peer_reviews

    return reviews
```

Peer review prompt:

```python
review_prompt = f"""
Peer-review this model's response:

MODEL: {target.model}
RESPONSE: {target.content}

Provide:
1. What they got right
2. Concerns/errors
3. Suggestions
4. Agreement score (0.0-1.0)

Return JSON:
{{
  "agreement_score": 0.85,
  "strengths": [...],
  "concerns": [...],
  "suggestions": [...],
  "critique": "..."
}}
"""
```

#### Layer 3: Final Synthesis (Claude)

```python
async def layer3_final_synthesis(query, layer1, layer2, reviews):
    prompt = f"""
    ORIGINAL: {query}
    YOUR INITIAL: {layer1.content}

    INDEPENDENT ANALYSES:
    - Grok: {layer2[0].content}
    - Gemini: {layer2[1].content}
    - GPT: {layer2[2].content}

    PEER REVIEWS:
    {format_reviews(reviews)}

    Your task (Layer 3):
    1. Identify consensus
    2. Evaluate disagreements
    3. Integrate peer feedback
    4. Synthesize final answer
    5. Flag uncertainties

    Provide:
    - Executive summary
    - Final answer
    - Confidence assessment
    - Dissenting views (if any)
    - Recommended actions
    """

    return anthropic.messages.create(...)
```

---

### 4. Voice Interface

#### Whisper Local Transcription

```python
def _transcribe_whisper_local(audio: sr.AudioData):
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        f.write(audio.get_wav_data())
        temp_path = f.name

    # Transcribe
    result = whisper_model.transcribe(temp_path, language="en")

    # Cleanup
    Path(temp_path).unlink()

    return result["text"].strip()
```

**Model Sizes**:
- `tiny`: 39M params, 32MB, ~1s transcription, lowest accuracy
- `base`: 74M params, 142MB, ~2s, good accuracy (recommended)
- `small`: 244M params, 466MB, ~5s, better accuracy
- `medium`: 769M params, 1.5GB, ~15s, high accuracy
- `large`: 1550M params, 2.9GB, ~30s, highest accuracy

#### Push-to-Talk Mode (planned)

```python
# Requires keyboard library
def run_push_to_talk(hotkey="ctrl+shift+space"):
    while True:
        keyboard.wait(hotkey)
        # Record while key held
        audio = record_until_release(hotkey)
        transcript = transcribe(audio)
        result = orchestrator.process_query(transcript)
        display_result(result)
```

**Note**: `keyboard` library may require admin/sudo permissions

#### Continuous Listening Mode

```python
def run_continuous(wake_word="hey ungpt"):
    while True:
        transcript = capture_audio(timeout=10)

        if wake_word.lower() in transcript.lower():
            query = transcript.replace(wake_word, "").strip()
            result = orchestrator.process_query(query)
            display_result(result)
```

---

## Data Flow

### Single-Model Atomic Flow

```
User Query
  ↓
[AunCRM Validation]
  ↓ ✓ Approved
[JR Decomposition]
  → Thread T1 (RA-2)
  → Thread T2 (RA-2)
  → Thread T3 (RA-3, depends on T1)
  ↓
[NS Execution]
  Batch 1: T1, T2 (parallel)
  ↓
  Batch 2: T3 (after T1)
  ↓
[Cor Synthesis]
  ↓
[Audit Trail + Output]
```

### Multi-LLM Consensus Flow

```
User Query
  ↓
[Layer 1: Claude]
  → Initial reasoning
  ↓
[Layer 2: Broadcast]
  ├→ Grok analysis
  ├→ Gemini analysis
  └→ GPT analysis
  ↓
[Layer 2.5: Cross-Validation]
  • Grok reviews Gemini & GPT
  • Gemini reviews Grok & GPT
  • GPT reviews Grok & Gemini
  ↓
[Layer 3: Claude Synthesis]
  → Consensus + peer feedback
  ↓
[Final Output + Meta-Analysis]
```

---

## Performance Optimization

### Reduce Latency

1. **Parallel execution**: `MAX_CONCURRENT_THREADS=10`
2. **Smaller models**: Use `gemini-3.1-flash-exp` not `gemini-3.1-pro`
3. **Fewer threads**: Limit `max_threads=4` in decomposition
4. **Skip consensus**: Use single-model for simple queries

### Reduce Cost

1. **Cost gates**: `MAX_COST_PER_QUERY=0.50`
2. **Single-model mode**: Skip consensus for routine queries
3. **Token limits**: `max_tokens=2000` instead of 4000
4. **Caching**: Implement response cache for repeated queries

### Tiered Routing

```python
def route_query(query, complexity_score):
    if complexity_score < 0.3:
        # Simple query → Claude only
        return single_model_orchestrator.process(query)

    elif complexity_score < 0.7:
        # Moderate → Atomic threads
        return atomic_orchestrator.process(query)

    else:
        # Complex → Full consensus
        return consensus_orchestrator.execute(query)
```

Complexity scoring:

```python
def score_complexity(query):
    factors = {
        "length": len(query.split()) / 100,  # Longer = more complex
        "questions": query.count("?") * 0.1,
        "sub_topics": count_conjunctions(query) * 0.15,
        "uncertainty": count_uncertainty_words(query) * 0.2
    }
    return min(sum(factors.values()), 1.0)
```

---

## Error Handling

### Thread Execution Errors

```python
try:
    thread.result = await execute_thread(thread)
except asyncio.TimeoutError:
    thread.error = Exception(f"Timeout after 60s")
    # Other threads continue!
except APIError as e:
    thread.error = e
    # Logged and contained
finally:
    thread.execution_time = time.time() - start
    # Always tracked
```

### Consensus Layer Failures

```python
# Layer 2: Parallel execution
responses = await asyncio.gather(
    query_grok(prompt),
    query_gemini(prompt),
    query_gpt(prompt),
    return_exceptions=True  # Don't fail entire layer
)

# Filter out exceptions
valid = [r for r in responses if not isinstance(r, Exception)]

# Proceed with valid responses
if len(valid) >= 2:
    # Continue with consensus
else:
    # Fallback to single-model
```

---

## Testing

### Unit Tests

```python
# tests/test_aunccrm.py

def test_purpose_validation():
    purpose = Purpose(
        description="Too short",
        business_value="Value",
        success_criteria=[]  # Invalid: empty
    )
    assert not purpose.validate()

def test_compliance_context_ra4_requirements():
    context = ComplianceContext(
        purpose=valid_purpose,
        reasons=[single_reason],  # Invalid: RA-4 needs ≥3
        brakes=[single_brake],    # Invalid: RA-4 needs ≥2
        risk_level=RiskLevel.RA_4
    )

    is_valid, violations = context.validate_all()
    assert not is_valid
    assert any("RA-4" in v for v in violations)
```

### Integration Tests

```python
# tests/test_orchestrator.py

@pytest.mark.asyncio
async def test_thread_error_isolation():
    threads = [
        create_thread("T001", will_succeed=True),
        create_thread("T002", will_fail=True),
        create_thread("T003", will_succeed=True)
    ]

    results = await orchestrator.execute_threads_concurrent(threads)

    # T001 and T003 should succeed despite T002 failure
    assert results[0].error is None
    assert results[1].error is not None
    assert results[2].error is None
```

### Load Tests

```bash
# Generate 100 queries
python tests/load_test.py --queries 100 --concurrent 10

# Expected output:
# Total time: 45.2s
# Avg latency: 4.1s
# Success rate: 98%
# Total cost: $12.50
```

---

## Deployment

### Local Development

```bash
python example_usage.py
```

### Production Considerations

1. **API key rotation**: Store in secret manager (AWS Secrets, GCP Secret Manager)
2. **Rate limiting**: Implement exponential backoff
3. **Monitoring**: Log all audit trails to centralized system
4. **Alerting**: Alert on compliance violations (RA-4 failures)
5. **Cost tracking**: Monitor token usage and costs

### Cloud Deployment Options

**Option A: Container (Docker)**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "example_usage.py"]
```

**Option B: Serverless (AWS Lambda)**

```python
# lambda_handler.py

import json
from example_usage import AnthropicOrchestrator

def lambda_handler(event, context):
    query = event['query']

    orchestrator = AnthropicOrchestrator(
        api_key=os.environ['ANTHROPIC_API_KEY']
    )

    result = asyncio.run(orchestrator.process_query(query))

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

**Option C: GCP Cloud Run**

```yaml
# cloudbuild.yaml

steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ungpt', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ungpt']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    args:
      - 'run'
      - 'deploy'
      - 'ungpt'
      - '--image=gcr.io/$PROJECT_ID/ungpt'
      - '--platform=managed'
      - '--region=us-central1'
```

---

## Extending the System

### Add New Risk Level

```python
# aunccrm/core.py

class RiskLevel(Enum):
    RA_1 = "routine"
    RA_2 = "low"
    RA_3 = "moderate"
    RA_4 = "high"
    RA_5 = "catastrophic"  # NEW

# Update validation logic
if context.risk_level == RiskLevel.RA_5:
    if len(context.reasons) < 5:
        violations.append("RA-5 requires ≥5 independent reasons")
    if len(context.brakes) < 3:
        violations.append("RA-5 requires ≥3 brake mechanisms")
    if not context.approved:
        violations.append("RA-5 requires board-level approval")
```

### Add New LLM to Consensus

```python
# ungpt/consensus.py

class ModelType(Enum):
    CLAUDE = "claude-sonnet-4-20250514"
    GROK = "grok-2-latest"
    GEMINI = "gemini-3.1-flash-exp"
    GPT5 = "gemini-3.1-family-turbo-preview"
    LLAMA = "llama-3.1-405b"  # NEW

async def _query_llama(self, prompt):
    # Implement Llama API call
    response = await self.llama_client.generate(prompt)
    return ModelResponse(
        model=ModelType.LLAMA,
        content=response.text,
        ...
    )

# Update layer2_parallel_analysis
tasks = [
    self._query_grok(prompt),
    self._query_gemini(prompt),
    self._query_gpt5(prompt),
    self._query_llama(prompt)  # NEW
]
```

### Add Custom Brake Enforcement

```python
# aunccrm/core.py

class Brake:
    # ... existing fields ...

    custom_enforcer: Optional[Callable] = None

    def enforce(self, context: Any) -> bool:
        if self.custom_enforcer:
            return self.custom_enforcer(context, self)

        # Default enforcement
        if self.enforcement_method == "automated_monitoring":
            return self._automated_monitor(context)
        ...

# Usage
def custom_revenue_check(context, brake):
    actual_revenue = get_current_revenue()
    return actual_revenue >= brake.threshold

brake = Brake(
    constraint="Revenue must exceed $1M",
    threshold=1_000_000,
    custom_enforcer=custom_revenue_check
)
```

---

## Debugging

### Enable Verbose Logging

```python
# config.py

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('ungpt')
```

### Inspect Audit Trails

```python
# After execution
result = await orchestrator.process_query(query)

# Save audit trail
with open("audit_trails/query_001.json", "w") as f:
    json.dump(result["audit_trail"], f, indent=2)

# Inspect thread details
for thread in result["audit_trail"]["thread_details"]:
    print(f"Thread: {thread['thread_id']}")
    print(f"  Success: {thread['success']}")
    print(f"  Execution time: {thread['execution_time']}s")
    if thread['error']:
        print(f"  Error: {thread['error']}")
```

### Mock LLM Responses (Testing)

```python
class MockOrchestrator(PNKLNAtomicOrchestrator):
    async def _call_model(self, prompt):
        # Return canned response
        return "Mock response for testing"

# Use in tests
orchestrator = MockOrchestrator(api_key="test")
result = await orchestrator.process_query("test query")
```

---

## FAQ

**Q: Can I use this without voice interface?**
A: Yes, just use `example_usage.py` or call orchestrator directly.

**Q: Do I need all 4 API keys?**
A: No. Minimum: Anthropic (Claude). Others only for consensus mode.

**Q: How do I customize risk levels?**
A: Edit `aunccrm/core.py` and add validation logic.

**Q: Can I add my own LLM?**
A: Yes. Extend `ModelType` enum and implement `_query_*` method.

**Q: What if a thread fails?**
A: Other threads continue. Synthesis layer handles gaps gracefully.

**Q: How accurate is cost estimation?**
A: Conservative estimates. Actual costs typically 10-20% lower.

**Q: Can I run this offline?**
A: Voice transcription (Whisper) yes. LLM inference no (requires API).

**Q: Is this HIPAA/SOC2 compliant?**
A: Framework supports compliance. You must configure brakes and audit trails appropriately.

---

## Performance Benchmarks

**Hardware**: M1 MacBook Pro, 16GB RAM

### Voice Transcription

| Model | File Size | Transcription Time | Accuracy |
|-------|-----------|-------------------|----------|
| tiny  | 39MB      | 0.8s              | Good     |
| base  | 142MB     | 1.5s              | Better   |
| small | 466MB     | 3.2s              | High     |

### Query Processing (Single-Model)

| Complexity | Threads | Execution Time | Cost |
|------------|---------|----------------|------|
| Simple     | 2       | 3.5s           | $0.08|
| Moderate   | 4       | 6.2s           | $0.15|
| Complex    | 8       | 12.8s          | $0.32|

### Consensus Mode

| Models | Execution Time | Cost  |
|--------|----------------|-------|
| 2      | 8.5s           | $0.40 |
| 3      | 11.2s          | $0.75 |
| 4      | 14.6s          | $1.20 |

---

**Built for personal research automation. Obsess over details. Iterate relentlessly.**