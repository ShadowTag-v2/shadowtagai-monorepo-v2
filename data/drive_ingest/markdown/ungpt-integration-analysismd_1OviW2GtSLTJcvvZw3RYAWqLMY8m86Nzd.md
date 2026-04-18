# UnGPT Multi-LLM Consensus System - Integration Analysis

## Executive Summary

**What UnGPT Does:**
Automates your current manual process of:

1. Ask Claude Sonnet 4.5 (initial reasoning)
2. Broadcast response to Grok, Gemini Pro, GPT-5 (parallel analysis)
3. Cross-validate horizontally (each model reviews others)
4. Return to Claude Sonnet 4.5 (final synthesis & execution)

**Key Innovation:** Voice-activated, multi-model consensus with ATP 5-19 risk stratification

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER VOICE INPUT                            │
│                  (Push-to-Talk / Wake Word)                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               LOCAL WHISPER TRANSCRIPTION                        │
│                    (Mac/PC Desktop App)                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY COMPLEXITY ROUTER                       │
│   Simple (RA-1): Claude only    Complex (RA-3/4): Full consensus│
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
    ┌─────────────────┐     ┌──────────────────────────┐
    │  FAST PATH      │     │  CONSENSUS PATH          │
    │  Claude Solo    │     │  (Your Innovation)       │
    │  $0.01/query    │     │  $2-4/query             │
    └─────────────────┘     └──────────┬───────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
        ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
        │  Layer 1        │ │  Layer 2        │ │  Layer 2.5      │
        │  Claude Initial │ │  Parallel       │ │  Cross-Validate │
        │  Reasoning      │ │  Grok/Gemini/   │ │  Peer Review    │
        │                 │ │  GPT-5 Analysis │ │  Matrix         │
        └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
                 │                   │                   │
                 │      Broadcast    │    Reviews        │
                 └───────────────────┼───────────────────┘
                                     │
                                     ▼
                         ┌──────────────────────┐
                         │  Layer 3             │
                         │  Claude Synthesis    │
                         │  Final Answer        │
                         └──────────┬───────────┘
                                     │
                                     ▼
                         ┌──────────────────────┐
                         │  AUDIO RESPONSE      │
                         │  (TTS - Optional)    │
                         └──────────────────────┘
```

---

## System Components

### **Component 1: Atomic Thread Orchestrator**

**Purpose:** Decomposes complex queries into parallelizable sub-questions

**Example:**

- Query: "Analyze edge AI compute viability at cell towers"
- Threads:
  - T001: Market size analysis (RA-2)
  - T002: Technical feasibility (RA-3)
  - T003: Partnership models (RA-2)
  - T004: Financial projections (RA-3)
  - T005: Regulatory landscape (RA-4)
  - T006: Competitive positioning (RA-2)

**Value:**

- Executes 6 analyses concurrently (6x faster than sequential)
- Error isolation (T005 failure doesn't break T001-T004)
- Risk-stratified per ATP 5-19

---

### **Component 2: Multi-LLM Consensus Layer**

**Layer 1: Claude Initial Reasoning**

- Input: Voice query
- Output: Structured reasoning framework
- Cost: ~$0.015/query (1500 tokens)

**Layer 2: Parallel Analysis**

- Input: Claude's reasoning + original query
- Output: 3 independent analyses
- Models: Grok, Gemini 2.0 Pro, GPT-5
- Cost: ~$0.60/query (3 x $0.20)

**Layer 2.5: Cross-Validation Matrix**

```
         Reviewer →
Reviewed  │  Grok  │ Gemini │  GPT-5
─────────┼────────┼────────┼────────
Grok     │   --   │   ✓    │   ✓
Gemini   │   ✓    │   --   │   ✓
GPT-5    │   ✓    │   ✓    │   --
```

Each model reviews the other two (6 peer reviews total)

**Layer 3: Claude Final Synthesis**

- Input: All analyses + peer reviews
- Output: Consensus answer with confidence score
- Cost: ~$0.025/query (2500 tokens)

**Total Cost: ~$0.70-$1.20 per consensus query**

---

### **Component 3: Voice Interface**

**Local Desktop App (Mac/PC)**

**Technology Stack:**

- `pyaudio`: Microphone capture
- `whisper`: Local transcription (offline, private)
- `keyboard`: Hotkey detection (Ctrl+Shift+Space)
- `rich`: Beautiful terminal UI

**Modes:**

1. **Push-to-Talk** (Recommended): Hold hotkey, speak, release
2. **Wake Word**: Say "Hey Atomic" + query
3. **Single Query**: One-shot for testing

**Why Local Voice?**

- Privacy (audio never leaves your Mac)
- Latency (no network round-trip for transcription)
- Works offline
- No browser permissions needed

---

## Integration with Your FastAPI Stack

### **Architecture: Desktop App + Vertex AI Backend**

```python
# ungpt_service.py
# FastAPI endpoint for UnGPT consensus queries

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
from enum import Enum

app = FastAPI(title="UnGPT Consensus Service")

class QueryComplexity(Enum):
    """Route queries based on complexity."""
    SIMPLE = "simple"      # Claude only (RA-1)
    MODERATE = "moderate"  # Claude + 1 model (RA-2)
    COMPLEX = "complex"    # Full consensus (RA-3/4)

class UnGPTQuery(BaseModel):
    query: str
    user_location: str
    complexity: Optional[QueryComplexity] = None  # Auto-detect if None
    max_cost: float = 2.0  # Dollar limit
    include_audio_response: bool = False

class UnGPTResponse(BaseModel):
    final_answer: str
    confidence_score: float
    consensus_level: str  # "unanimous", "majority", "split"
    execution_time_seconds: float
    total_cost: float
    models_consulted: List[str]
    risk_level: str
    audit_trail_uri: str

@app.post("/v1/ungpt/query", response_model=UnGPTResponse)
async def process_ungpt_query(request: UnGPTQuery):
    """
    Main UnGPT endpoint.

    Auto-routes based on complexity:
    - Simple: Claude only
    - Moderate: Claude + Gemini
    - Complex: Full 4-model consensus
    """

    # 1. Detect complexity if not specified
    if request.complexity is None:
        request.complexity = await detect_complexity(request.query)

    # 2. Route based on complexity
    if request.complexity == QueryComplexity.SIMPLE:
        result = await execute_simple_path(request.query)
    elif request.complexity == QueryComplexity.MODERATE:
        result = await execute_moderate_path(request.query)
    else:
        result = await execute_full_consensus(request.query)

    # 3. Check cost gate
    if result["total_cost"] > request.max_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Query cost ${result['total_cost']:.2f} exceeds limit ${request.max_cost}"
        )

    # 4. Store encrypted audit log (multi-region)
    audit_uri = await store_audit_log(result, request.user_location)

    # 5. Generate audio response if requested
    if request.include_audio_response:
        audio_url = await generate_tts(result["final_answer"])
        result["audio_url"] = audio_url

    return UnGPTResponse(
        final_answer=result["final_answer"],
        confidence_score=result["confidence"],
        consensus_level=result["consensus_level"],
        execution_time_seconds=result["execution_time"],
        total_cost=result["total_cost"],
        models_consulted=result["models"],
        risk_level=result["risk_level"],
        audit_trail_uri=audit_uri
    )

async def detect_complexity(query: str) -> QueryComplexity:
    """
    Use Claude to assess query complexity.

    Simple: Factual questions, definitions, single-step reasoning
    Moderate: Comparisons, multi-step analysis
    Complex: Strategic decisions, financial projections, multi-domain analysis
    """

    classification_prompt = f\"\"\"Classify this query's complexity:

QUERY: {query}

Return JSON:
{{
  "complexity": "simple" | "moderate" | "complex",
  "reasoning": "Why this classification?",
  "recommended_models": ["claude"] | ["claude", "gemini"] | ["claude", "grok", "gemini", "gpt5"]
}}

Criteria:
- Simple: Single fact, definition, straightforward question
- Moderate: Comparison, 2-3 step reasoning, analysis with clear scope
- Complex: Strategic, financial, multi-domain, high-stakes decision
\"\"\"

    # Call Claude for classification (cheap, ~500 tokens)
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": classification_prompt}]
    )

    classification = json.loads(response.content[0].text)
    return QueryComplexity(classification["complexity"])

async def execute_simple_path(query: str) -> Dict[str, Any]:
    """Claude only - fast and cheap."""

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": query}]
    )

    return {
        "final_answer": response.content[0].text,
        "confidence": 0.85,
        "consensus_level": "single_model",
        "execution_time": 2.5,
        "total_cost": 0.015,
        "models": ["claude-sonnet-4"],
        "risk_level": "RA-1"
    }

async def execute_full_consensus(query: str) -> Dict[str, Any]:
    """
    Full 3-layer consensus with peer review.
    """

    orchestrator = ConsensusOrchestrator(
        anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
        google_api_key=os.environ["GOOGLE_API_KEY"],
        openai_api_key=os.environ["OPENAI_API_KEY"],
        xai_api_key=os.environ["XAI_API_KEY"]
    )

    result = await orchestrator.execute_full_consensus(query)

    # Calculate consensus level
    peer_reviews = result["peer_reviews"]
    avg_agreement = calculate_average_agreement(peer_reviews)

    if avg_agreement >= 0.9:
        consensus_level = "unanimous"
    elif avg_agreement >= 0.7:
        consensus_level = "majority"
    else:
        consensus_level = "split"

    return {
        "final_answer": result["final_synthesis"],
        "confidence": avg_agreement,
        "consensus_level": consensus_level,
        "execution_time": sum(r.latency for r in result["layer2_responses"]) + 5,
        "total_cost": calculate_total_cost(result["token_usage"]),
        "models": ["claude-sonnet-4", "grok-2", "gemini-2-flash", "gpt-5"],
        "risk_level": assess_risk_from_consensus(result)
    }

def calculate_average_agreement(peer_reviews: Dict) -> float:
    """Calculate average agreement score across all peer reviews."""
    all_scores = []
    for model, reviews in peer_reviews.items():
        for review in reviews:
            all_scores.append(review.agreement_score)
    return sum(all_scores) / len(all_scores) if all_scores else 0.0

def calculate_total_cost(token_usage: Dict) -> float:
    """
    Calculate cost based on actual token usage.

    Pricing (as of 2025):
    - Claude Sonnet 4: $3/$15 per 1M tokens (in/out)
    - Grok: $2/$10 per 1M tokens
    - Gemini 2.0: $0.075/$0.30 per 1M tokens
    - GPT-5: $10/$30 per 1M tokens (estimated)
    """

    cost = 0.0

    # Layer 1: Claude
    cost += (token_usage["layer1"]["input"] / 1_000_000 * 3)
    cost += (token_usage["layer1"]["output"] / 1_000_000 * 15)

    # Layer 2: All models
    for model_usage in token_usage["layer2"]:
        # Simplified - use average pricing
        cost += (model_usage.get("input", 0) / 1_000_000 * 4)
        cost += (model_usage.get("output", 0) / 1_000_000 * 15)

    # Layer 3: Claude synthesis
    cost += (token_usage["layer3"]["input"] / 1_000_000 * 3)
    cost += (token_usage["layer3"]["output"] / 1_000_000 * 15)

    return round(cost, 4)

async def store_audit_log(result: Dict, user_location: str) -> str:
    """Store encrypted audit log in compliant region."""

    from aunccrm_violations_fixed import MultiRegionAuditLog

    audit_logger = MultiRegionAuditLog(project_id="ShadowTag-v2-services")

    audit_data = {
        "query": result.get("query", ""),
        "models_consulted": result["models"],
        "consensus_level": result["consensus_level"],
        "confidence": result["confidence"],
        "cost": result["total_cost"],
        "timestamp": datetime.utcnow().isoformat()
    }

    return audit_logger.store_audit_log_regional(
        audit_data=audit_data,
        user_location=user_location,
        data_classification="research"
    )
```

---

## Desktop Voice Client Configuration

```python
# ungpt_voice_client.py
# Mac/PC voice client that connects to your Vertex AI backend

from voice_client import VoiceCapture, VoiceAtomicClient
import aiohttp
import asyncio
from rich.console import Console

console = Console()

class UnGPTVoiceClient(VoiceAtomicClient):
    """
    Voice client for UnGPT with tiered routing.
    """

    def __init__(
        self,
        voice_capture: VoiceCapture,
        backend_url: str,
        api_key: str,
        max_cost_per_query: float = 2.0
    ):
        self.voice = voice_capture
        self.backend_url = backend_url
        self.api_key = api_key
        self.max_cost = max_cost_per_query

    async def send_to_orchestrator(self, query: str) -> dict:
        """Send query to UnGPT backend."""

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.backend_url}/v1/ungpt/query",
                json={
                    "query": query,
                    "user_location": "US",  # Or detect from system
                    "max_cost": self.max_cost,
                    "include_audio_response": False
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                if response.status == 402:
                    console.print("[red]Query too expensive - simplify or increase budget[/red]")
                    return None

                return await response.json()

    def _display_result(self, result: dict):
        """Enhanced display with consensus info."""

        if not result:
            return

        console.print(f"\n[bold cyan]Consensus Level:[/bold cyan] {result['consensus_level']}")
        console.print(f"[bold cyan]Confidence:[/bold cyan] {result['confidence_score']*100:.0f}%")
        console.print(f"[bold cyan]Models:[/bold cyan] {', '.join(result['models_consulted'])}")
        console.print(f"[dim]Cost: ${result['total_cost']:.4f} | Time: {result['execution_time_seconds']:.1f}s[/dim]\n")

        console.print(Panel.fit(
            result["final_answer"],
            title="[bold green]UnGPT Consensus Answer[/bold green]",
            border_style="green"
        ))

# Usage
if __name__ == "__main__":
    import os

    voice = VoiceCapture(transcription_engine="whisper_local", model_size="base")

    client = UnGPTVoiceClient(
        voice_capture=voice,
        backend_url="https://your-vertex-ai-endpoint.com",  # Or "http://localhost:8000" for local
        api_key=os.environ["UNGPT_API_KEY"],
        max_cost_per_query=2.0
    )

    client.run_push_to_talk()
```

---

## Cost Analysis: Your Query Volume

**Your Past 72 Hours:**

- 80-120 queries
- 20 distinct threads
- Average: 40 queries/day

**Cost Projections:**

### **Scenario 1: All Queries Use Full Consensus**

- Cost/query: $1.20
- Daily cost: 40 × $1.20 = **$48/day**
- Monthly: **~$1,440**

### **Scenario 2: Tiered Routing (Recommended)**

- Simple (70%): 28 queries × $0.015 = $0.42
- Moderate (20%): 8 queries × $0.30 = $2.40
- Complex (10%): 4 queries × $1.20 = $4.80
- Daily total: **$7.62/day**
- Monthly: **~$230**

### **Scenario 3: ShadowTag MVP Focus Only**

- Complex queries (10 per day): 10 × $1.20 = $12/day
- Monthly: **~$360**

**ROI Check:**

- Your time: $200/hr (conservative for co-founder)
- Consensus saves: 15 min/complex query (no manual model switching)
- Value: 10 queries/day × 0.25 hr × $200 = **$500/day saved**
- Net benefit: $500 - $12 = **$488/day**

**Decision:** Even full consensus ($48/day) is profitable at your volume.

---

## Recommended Deployment: Hybrid Approach

```
┌─────────────────────────────────────────────────┐
│  YOUR MAC (Desktop Voice Client)               │
│  - Whisper transcription (local)               │
│  - Push-to-talk interface                      │
│  - Query routing logic                         │
└──────────────────┬──────────────────────────────┘
                   │ HTTPS
                   ▼
┌─────────────────────────────────────────────────┐
│  VERTEX AI WORKBENCH (Backend)                 │
│  - FastAPI service (ungpt_service.py)          │
│  - Consensus orchestrator                      │
│  - Multi-region audit logs                     │
│  - Cost gates + monitoring                     │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   [Claude]   [Gemini]   [External APIs]
                            (Grok, GPT-5)
```

**Benefits:**

- Voice stays local (privacy)
- Compute scales in cloud
- Easy to add new models
- Audit logs compliant
- Cost monitoring built-in

---

## Implementation Checklist

### **Phase 1: Backend (Vertex AI Workbench)**

- [ ] Deploy `ungpt_service.py` to Workbench
- [ ] Configure API keys (Anthropic, OpenAI, xAI) in Secret Manager
- [ ] Set up multi-region audit log buckets
- [ ] Implement cost gates ($2/query max)
- [ ] Test with curl/Postman

### **Phase 2: Desktop Client (Your Mac)**

- [ ] Install dependencies: `pip install pyaudio whisper SpeechRecognition keyboard rich`
- [ ] Test microphone: `python voice_client.py --list-mics`
- [ ] Configure backend URL in client
- [ ] Test push-to-talk mode
- [ ] Add keyboard shortcut to macOS

### **Phase 3: Integration Testing**

- [ ] Simple query: "What is edge computing?"
- [ ] Complex query: "Analyze ShadowTag MVP financial projections"
- [ ] Validate consensus output quality
- [ ] Check cost tracking accuracy
- [ ] Verify audit logs stored correctly

### **Phase 4: Production Hardening**

- [ ] Add authentication (API key rotation)
- [ ] Implement rate limiting (protect from runaway costs)
- [ ] Add monitoring/alerting (daily cost threshold)
- [ ] Create kill switch (disable consensus if budget exceeded)
- [ ] Document for team use

---

## Next Steps

**Decision Point: Where to start?**

**Option A: MVP Testing (1 day)**

- Deploy backend to Vertex AI
- Test via curl (skip voice for now)
- Validate consensus quality with 10 queries
- Measure cost vs. value

**Option B: Full Voice Integration (3 days)**

- Build desktop client first
- Connect to local FastAPI (localhost)
- Add voice once working
- Deploy to Vertex AI later

**Option C: ShadowTag-Specific (2 days)**

- Build only for watermark detection queries
- Skip general-purpose routing
- Optimize for ACM paper implementation
- Voice optional

**Recommendation:** Start with **Option A** to validate consensus value before investing in voice UX.

What's your call?
