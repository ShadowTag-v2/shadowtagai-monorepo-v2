# Atomic Consensus Orchestrator - Quick Start

**Unified system:** Atomic Thread decomposition + Multi-model consensus + Circular peer review

## What It Does

Your message goes through:



1. **JR (Judgment Rule)**: Claude decomposes into atomic threads with Purpose/Reasons/Brakes


2. **NS (Execution)**: Each thread broadcasts to Gemini, Perplexity, SuperGrok


3. **Peer Review**: Circular review (2 rounds) - each model reviews the others


4. **Cor (Synthesis)**: Claude stitches everything into execution-ready output

## Architecture

```

Your Message
    ↓
[Claude: Decompose into Atomic Threads]
    ↓
For Each Thread:
    ↓
[Broadcast to 3 Models]
├─→ Gemini
├─→ Perplexity
└─→ SuperGrok
    ↓
[Circular Review Round 1]
Gemini → Perplexity
Perplexity → SuperGrok
SuperGrok → Gemini
    ↓
[Circular Review Round 2]
Gemini → SuperGrok
Perplexity → Gemini
SuperGrok → Perplexity
    ↓
[Claude: Synthesize Thread Consensus]
    ↓
[Claude: Stitch All Threads Together]
    ↓
Final Execution-Ready Output

```

## Setup (3 Steps)

### 1. Install Dependencies

```bash
cd voice_consensus
source venv/bin/activate  # if not already activated
pip install -r requirements-text-only.txt

```

### 2. Set API Keys

```bash

# Required

export ANTHROPIC_API_KEY='sk-ant-...'

# Optional (add what you have)

export GOOGLE_API_KEY='AIza...'           # Gemini
export PERPLEXITY_API_KEY='pplx-...'      # Perplexity
export XAI_API_KEY='xai-...'              # SuperGrok

```

### 3. Run It

**Interactive mode:**

```bash
python atomic_consensus_orchestrator.py

```

**Command-line:**

```bash
python atomic_consensus_orchestrator.py "Design a scalable edge AI architecture"

```

## Example Output

```

================================================================================
ATOMIC CONSENSUS ORCHESTRATOR
================================================================================

[JR] Decomposing message into atomic threads...
[JR] Created 4 atomic threads

[NS] Executing threads with multi-model consensus...

Thread T001_technical_feasibility:
  → Gemini, Perplexity, SuperGrok responding...
  → Circular peer review (6 reviews)...
  → Consensus synthesized

Thread T002_cost_analysis:
  → Gemini, Perplexity, SuperGrok responding...
  → Circular peer review (6 reviews)...
  → Consensus synthesized

Thread T003_partnership_models:
  → Gemini, Perplexity, SuperGrok responding...
  → Circular peer review (6 reviews)...
  → Consensus synthesized

Thread T004_competitive_positioning:
  → Gemini, Perplexity, SuperGrok responding...
  → Circular peer review (6 reviews)...
  → Consensus synthesized

[NS] Completed 4 threads

[Cor] Stitching results into unified output...
[✓] Complete - ready for execution

================================================================================
FINAL OUTPUT (Execution-Ready)
================================================================================

[Claude's comprehensive synthesized answer incorporating all threads]

================================================================================
EXECUTION SUMMARY
================================================================================
Threads: 4
Success Rate: 100%
Models Consulted: 12
Peer Reviews: 24
Avg Thread Time: 8.5s
================================================================================

```

## What Makes This Powerful

### 1. Atomic Decomposition (AoT)



- Complex queries broken into independent threads


- Each thread has Purpose, Reasons, Brakes (ShadowTag-v2JR doctrine)


- ATP 5-19 risk stratification


- Error isolation (one thread fails ≠ total failure)

### 2. Multi-Model Consensus



- 3 independent AI models analyze each thread


- Catches hallucinations


- Multiple perspectives


- Higher confidence

### 3. Circular Peer Review



- Each model reviews both others (6 reviews per thread)


- Identifies blind spots


- Cross-validation


- Quality assurance

### 4. Claude Synthesis



- Stitches everything together


- Resolves contradictions


- Execution-ready output


- Maintains coherence

## Cost Analysis

**With all models** (Claude + Gemini + Perplexity + SuperGrok):

For a query decomposed into **4 threads**:


- Claude decomposition: 1 call


- Per thread: 3 model responses + 6 peer reviews + 1 synthesis = 10 calls


- Total per thread: 10 calls × 4 threads = 40 calls


- Claude final stitching: 1 call


- **Grand total: 42 API calls**

Estimated cost: **$0.50 - $2.00** depending on thread complexity.

**Cost saving strategies:**



1. **Limit threads:**
   ```bash
   # Modify in code: max_threads=2 instead of 6
   ```



2. **Use fewer models:**


   - Only set `ANTHROPIC_API_KEY` + `GOOGLE_API_KEY`


   - System adapts automatically



3. **Simple queries:**


   - Use `message_consensus.py` for single-thread queries


   - This system is for complex, multi-faceted questions

## When to Use This vs Simple Consensus

**Use Atomic Consensus for:**


- Complex multi-part questions


- Architecture design decisions


- Business analysis with multiple dimensions


- Technical + business + risk analysis


- Queries requiring specialized sub-analyses

**Use Simple Consensus (message_consensus.py) for:**


- Single-focus questions


- Quick validations


- Code review


- Explaining concepts


- Simpler research queries

## Example Queries That Benefit From Atomic Decomposition

```

"Design a complete edge AI infrastructure deployment strategy for cell tower sites,
covering technical architecture, cost modeling, partnership frameworks, competitive
analysis, regulatory compliance, and 5-year financial projections."

```

This would decompose into ~6 threads:


- T001: Technical architecture


- T002: Cost modeling


- T003: Partnership frameworks


- T004: Competitive analysis


- T005: Regulatory compliance


- T006: Financial projections

Each thread gets full consensus + peer review, then Claude stitches into coherent strategy.

## Audit Trail

Every thread maintains full audit trail:


- Thread ID, Purpose, Reasons, Brakes


- Risk level (RA-1 through RA-4)


- Models consulted


- Peer reviews conducted


- Execution time


- Success/failure status


- Timestamp

Access via:

```python
result["threads"]  # List of audit trails

```

## Advanced: Customizing Decomposition

Edit `max_threads` in the message:

```python
result = await orchestrator.process_message(
    "Your complex query here",
    max_threads=8  # Allow up to 8 threads
)

```

More threads = more granular analysis = higher cost but better coverage.

## Troubleshooting

### "No threads created"



- Query might be too simple for decomposition


- Use `message_consensus.py` instead

### "Some threads failed"



- Check API keys are all set correctly


- Check rate limits


- System continues with successful threads

### "Too expensive"



- Reduce `max_threads`


- Use fewer models (only Claude + Gemini)


- Reserve for truly complex queries

## Integration with Your Workflow

**As a pre-processor:**

```bash

# Get consensus on complex design decision

python atomic_consensus_orchestrator.py "Your complex question"

# Then use the output to guide your Claude Code session

```

**For research automation:**


- Save results to files


- Build knowledge base


- Automated analysis pipeline

## Files



- `atomic_consensus_orchestrator.py` - Main unified orchestrator


- `message_consensus.py` - Simpler version (no threading)


- `requirements-text-only.txt` - Dependencies

---

**Ready to test!**

```bash
python atomic_consensus_orchestrator.py "Analyze the tradeoffs between microservices and monolithic architectures for a SaaS platform"

```
