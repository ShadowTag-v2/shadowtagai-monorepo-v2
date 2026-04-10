# Atomic Chat Integration Example - Autoresearch + SwarmOrchestrator

This document demonstrates how to use the Atomic Chat API pipeline
with the Autoresearch swarm and SwarmOrchestrator.

## Workflow: New Security Audit Task

### Step 1: Agent Receives Task via Broadcast

```python
from agents.autoresearch import Autoresearch

fm = Autoresearch(num_agents=600)

# Broadcast OPORD to Shift 0
result = fm.broadcast_task(
    task="Comprehensive security audit of ShadowTagAccount.sol",
    shift=0
)

# Returns:
# {
#   "task": "Comprehensive security audit...",
#   "agents_notified": 200,
#   "opord_number": 143,
#   "consensus_required": True
# }
```

Behind the scenes, `broadcast_task` creates OPORD 00143 with:
- **Situation**: Blockchain security risks, available agents
- **Mission**: WHO (Shift 0), WHAT (audit), WHEN (24h), WHERE (contracts/), WHY ($100M milestone)
- **Execution**: 4 phases, squad assignments, phase lines
- **Service Support**: Slither, Mythril, Foundry
- **Command & Signal**: SwarmOrchestrator, Context Index logging

### Step 2: Agent Searches Scholarly PDFs for Research

```python
import requests

# Agent searches for academic papers on smart contract security
response = requests.post(
    "http://localhost:8000/api/v1/atomic-chat/scholarly-pdfs/search",
    json={
        "query": "reentrancy attacks Ethereum smart contracts",
        "topics": ["blockchain", "security"],
        "year_range": [2020, 2025],
        "limit": 10
    }
)

papers = response.json()
# Returns ranked papers with excerpts:
# [
#   {
#     "title": "Analyzing and Preventing Reentrancy Attacks",
#     "authors": ["Researcher A", "Researcher B"],
#     "year": 2023,
#     "score": 12.5,
#     "excerpts": [
#       "...reentrancy attacks exploit callback mechanisms...",
#       "...CEI pattern (Checks-Effects-Interactions) mitigates..."
#     ]
#   },
#   ...
# ]
```

**HOW SCHOLARLY PDF SEARCH WORKS:**

1. **PDF Upload** (one-time setup):
   ```bash
   curl -X POST http://localhost:8000/api/v1/atomic-chat/scholarly-pdfs/upload \
     -F "file=@apertus-indexing-paper.pdf" \
     -F "title=Apertus LLM Training Data Indexing" \
     -F "authors=Researcher A,Researcher B" \
     -F "year=2024" \
     -F "topics=elasticsearch,llm,indexing"
   ```

2. **Text Extraction** (PyPDF2):
   - Extracts text from each page
   - Normalizes: lowercase, ASCII folding, tokenization
   - Similar to Apertus `web_content_analyzer`

3. **Elasticsearch Indexing**:
   - Custom analyzer: `scholarly_analyzer`
   - Filters: lowercase, asciifolding, stop words
   - Index size ≈ 1.3× raw PDF (Apertus ratio)

4. **Full-Text Search**:
   - `match_phrase` query with `slop=2` (2-word gaps allowed)
   - Excerpt highlighting (150-char fragments)
   - Ranked by relevance score

5. **Agent Uses Results**:
   - Reads excerpts to understand reentrancy attacks
   - References papers in audit report
   - Logs citations to OPORD 00143 for audit trail

### Step 3: Agent Executes Audit

```python
# Agent uses blockchain-security-auditor skill (auto-activated)
# Runs Slither, Mythril, manual review
# Finds 2 critical issues, 3 high, 5 medium

# Creates audit report in OPORD context
```

### Step 4: SwarmOrchestrator Logs Decision

```python
from src.ShadowTag-v2.orchestrator.swarm_orchestrator import SwarmOrchestrator
from src.ShadowTag-v2.services.context_index import ContextIndexService

orchestrator = SwarmOrchestrator(bar_exam_protocol=...)
context_service = ContextIndexService()

# Route task to best child agent based on audit results
decision = orchestrator.route_task_to_best_child({
    "type": "fix_security_issues",
    "priority": "CRITICAL",
    "deadline": "2025-11-23"
})

# Log routing decision to Context Index
context_service.create_context(
    task_title=f"Fix Security Issues from OPORD 00143",
    agent_id=decision["assigned_agent"],
    shift_number=0,
    mission={
        "who": decision["assigned_agent"],
        "what": "Fix 2 critical reentrancy vulnerabilities",
        "when": "Within 24 hours",
        "where": "contracts/tba/ShadowTagAccount.sol",
        "why": "Block mainnet deployment until fixed"
    },
    tags=["security", "critical", "derivative-of-143"]
)
```

### Step 5: Revenue Distribution

```python
# After fixes are deployed and generate revenue
revenue_event = {
    "source": "ShadowTagAccount deployment fees",
    "amount": 5000.00,  # $5k
    "generation": 1,  # First-generation child
    "parent_id": "agent_042"
}

# Distribute using RoyaltyMath.sol pattern
distribution = orchestrator.distribute_revenue(
    child_id="agent_143",
    amount=5000.00,
    generation=1
)

# Returns:
# {
#   "child": 4100.00,    # 82% (5000 - 18%)
#   "parent": 900.00,    # 18%
#   "grandparent": 0,    # N/A (generation < 2)
#   "great_grandparent": 0  # N/A (generation < 3)
# }

# Log to Context Index
context_service.log_revenue_event(
    opord_number=143,
    amount=5000.00,
    source="deployment_fees",
    generation=1
)
```

### Step 6: Judge#6 Governance Check

```python
# Check if deployment meets governance standards
judge6_decision = {
    "opord_number": 143,
    "policy_violated": "security_audit_required",
    "severity": "PASSED",
    "action_taken": "Approved for mainnet deployment",
    "reasoning": "All critical vulnerabilities fixed, tests passing"
}

# Log to Context Index
context_service.log_judge6_decision(**judge6_decision)
```

### Step 7: Complete OPORD

```python
# Mark OPORD as completed
context_service.update_context(
    opord_number=143,
    summary="Security audit completed. Found 10 issues (2 critical, 3 high, 5 medium). All critical issues fixed and verified. Approved for mainnet deployment.",
    decisions=[
        "Used CEI pattern to fix reentrancy",
        "Added nonReentrant modifier via OpenZeppelin",
        "Increased test coverage to 95%",
        "Referenced 3 academic papers on smart contract security"
    ],
    status="completed"
)
```

## Atomic Chat Workflow JSON Example

```json
{
  "block_name": "New Security Audit",
  "description": "Create OPORD for smart contract security audit",
  "actions": [
    {
      "type": "AskForInput",
      "title": "Contract Name",
      "prompt": "Which contract should be audited?"
    },
    {
      "type": "AskForInput",
      "title": "Shift Number",
      "prompt": "Which shift should execute? (0, 1, or 2)"
    },
    {
      "type": "GetDate",
      "format": "YYYY-MM-DD HH:mm"
    },
    {
      "type": "CreateNote",
      "folder": "Notes",
      "noteTitle": "Security Audit - {{Contract Name}}",
      "content": "Issue: Security audit for {{Contract Name}}\nDate: {{Date}}\nBrief: Comprehensive security audit using Slither, Mythril, and manual review\nTags: security, audit, blockchain"
    }
  ]
}
```

Execute via API:

```bash
curl -X POST http://localhost:8000/api/v1/atomic-chat/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": {...},
    "inputs": {
      "Contract Name": "ShadowTagAccount.sol",
      "Shift Number": "0"
    }
  }'
```

Returns:

```json
{
  "block_name": "New Security Audit",
  "started_at": "2025-11-22T22:30:00Z",
  "actions_executed": [
    {"type": "AskForInput", "result": "ShadowTagAccount.sol"},
    {"type": "AskForInput", "result": "0"},
    {"type": "GetDate", "result": "2025-11-22 22:30"},
    {"type": "CreateNote", "result": {"opord_number": 144}}
  ],
  "opord_number": 144,
  "status": "completed",
  "completed_at": "2025-11-22T22:30:01Z"
}
```

## Scholarly PDF Search - Enabling "Sauron's Panorama"

The key innovation: **Elasticsearch infrastructure scales from OPORDs to PDFs**

### Architecture (Inspired by Apertus 8.6T Token Indexing)

```
┌─────────────────────────────────────────────────┐
│     Elasticsearch 8.x on GKE Autopilot          │
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │ opord_contexts│  │ scholarly_pdfs          │ │
│  │  (60k docs)   │  │  (1000s of papers)      │ │
│  └──────────────┘  └──────────────────────────┘ │
│                                                  │
│  Custom Analyzer: scholarly_analyzer             │
│  - Tokenization: standard                        │
│  - Filters: lowercase, asciifolding, stop       │
│                                                  │
│  Query: match_phrase with slop=2                │
│  - "smart contract security" matches             │
│    "smart contracts and security"               │
└─────────────────────────────────────────────────┘
```

### Performance (Apertus Benchmarks Applied)

| Metric | Apertus (8.6T tokens) | Our Scale (1k PDFs) |
|--------|------------------------|---------------------|
| Indexing Speed | ~10k docs/sec | ~100 PDFs/min |
| Query Latency | <100ms p99 | <50ms p99 |
| Index Size | 1.3× raw data | 1.3× PDF size |
| Storage Cost | ~$200/month (60k OPORDs) | ~$50/month (1k PDFs) |

### Revenue Opportunity: "Sauron's Panorama" Enterprise Tier

**Pricing**:
- **Basic**: 100 PDFs indexed (included)
- **Standard**: 1,000 PDFs (+$200/month)
- **Enterprise**: Unlimited PDFs + custom taxonomies (+$1,000/month)

**Target Customers**:
- **Law Firms**: Index case law, legal precedents
- **Research Teams**: Index academic papers, patents
- **Compliance Departments**: Index regulations, standards
- **Defense Contractors**: Index technical specs, manuals

**Value Prop**: "Your AI agents autonomously research like PhD-level humans"

## Summary: Complete Pipeline

1. **Workflow Trigger** → JSON action blocks define task
2. **OPORD Creation** → Context Index stores structured task
3. **Agent Research** → Searches scholarly PDFs via Elasticsearch
4. **Task Execution** → Agent completes work with full context
5. **Decision Logging** → SwarmOrchestrator logs routing/revenue
6. **Governance Check** → Judge#6 validates compliance
7. **OPORD Completion** → Summary and decisions logged
8. **Audit Trail** → Full history searchable via Context Index

**Result**: Military-grade precision + academic-level research + production-ready automation