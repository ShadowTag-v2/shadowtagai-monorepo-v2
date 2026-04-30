# ShadowTagAI – Master Handoff Document (2025-11-22)

## Core Truth (non-negotiable)
- **Platform**: ShadowTagAI (formerly pnkln / ShadowTag-v2)
- **Architecture**: **Native Gemini function-calling only** — zero multi-agent frameworks (AutoGen, LangGraph, AG2).
- **Governance Kernel**: ATP_519 → Judge6 → Audit (target p99 ≤ 90 ms, $0.0003/decision).
- **Router**: UNGPT live at `localhost:8787/v1/chat/completions` (Routing: Gemini, Claude, Groq, Ollama, Grok).
- **Cloud**: GCP Project `acquired-jet-478701-b3` | GKE Autopilot Cluster.
- **Privacy**: All PII scrubbed.

## Immediate Next Actions (Priority Order)
1. **Infrastructure**:
   - [x] Create Cloud Build trigger (ShadowTag-v2/n-autoresearch/Kosmos/BioAgentss.cloudbuild.yaml).
   - [x] Trigger first deployment (Flying n-autoresearch/Kosmos/BioAgents & Jetski Active).
2. **Persistent Whiteboard (The Moat)**:
   - [x] Create `agents/legal_whiteboard.py` – GitHub-backed evolving state store.
   - [x] Create `agents/bar_exam_protocol.py` – Qualification + progression gates.
3. **Verification**:
   - [ ] Verify end-to-end latency ≤ 90 ms on `/api/v1/governance/decisions`.

## Architecture Summary
- **Single Gemini Context**: Parallel function sets (COR, JR, NS, JUDGE6, SHADOWTAG).
- **Kernel Chain**: 95% token reduction, $0.0003/decision.
- **Routing Strategy**:
  - *Function Calling*: Gemini (40%)
  - *Deep Reasoning*: Claude (35%)
  - *Bulk/High Volume*: Groq (5%)
  - *Offline/Sensitive*: Ollama
  - *Speed*: Grok (5%)

## Persistent Agent Evolution
**Concept**: GitHub becomes the memory. Every task improves the agent permanently.

**Level Progression**:
0. Task Execution
1. Pattern Recognition
2. Optimization Suggestions
3. Autonomous Self-Improvement
4. Spawns New Agents
5. Swarm Orchestration

## Revenue & Bootstrap Discipline
- **ROI Gate**: ≥3× in 18 months.
- **LTV:CAC Gate**: ≥4:1 in 12 months.
- **Rule**: Every new feature must pass JR Engine (Purpose / Reasons / Brakes).

## One-Line Instruction (Context Propagation)
"Deploy to GKE → ship `legal_whiteboard.py` + `bar_exam_protocol.py` → measure p99 → never mention AutoGen again."
