# ANTIGRAVITY OPERATING DOCTRINE (AOD-2025)

## "HOW WE TALK TO THE MACHINE"

**CLASSIFICATION:** PROPRIETARY // pnkln CORP
**DATE:** 01 DEC 2025
**SYSTEM:** ANTIGRAVITY (UNGPT v2.0)

---

### 1. THE INTERFACE (THE "TALK")

We do not "prompt" the machine; we **brief** it. The interaction model is military command-and-control, not chat.

**1.1 The Input Vector**

- **Primary Node:** Antigravity IDE (Local Mac).

- **Intake Model:** Gemini 3 Pro (Web/Voice).

- **Modality:** Text or Whisper Voice (for rapid "Field Grade" commands).

- **The Command:** "Briefing" style. High-context, intent-focused.
  - _Example:_ "Situation: Auth service is flaky. Mission: Refactor to OAuth2. Execution: Use the Courtroom pattern. Sustainment: 500k tokens."

**1.2 The "Ungpt" Flow (What happens next)**

1. **Intake (Gemini 3 Pro)**:
   - Receives the brief.

   - **Searches ALL Sources**: Pipeline, Drive, Memory, and Web.

   - **Atomizes**: Breaks the mission into atomic chat threads.

2. **Reasoning Handoff (The Chain)**:
   - **Gemini** explains reasoning to **Perplexity**.

   - **Perplexity** researches (Web/Deep Search) and explains reasoning to **SuperGrok**.

   - **SuperGrok** applies business acumen/code expertise and routes to **Cloud Code**.

   - _Crucial:_ Each handoff includes the _entire_ prior reasoning chain.

---

### 2. THE GOVERNANCE (THE "SWARM")

We do not rely on single agents. We deploy a **https://github.com/karpathy/autoresearchs Swarm** governed by **Advanced Agentic Control (AAC-2025)**.

**2.1 Control Paradigm (The "Brakes")**

- **Circuit-Breaking Architecture:** We moved beyond prompt-based refusals. We use **Representation Circuit Breakers** to intercept and modify harmful model representations _before_ execution.

- **VeriGuard (Correctness-by-Construction):** Every action generates a formal verification specification.
  - _Zero Trust:_ 0% attack success rate target.

  - _Protocol:_ If verification fails, the swarm re-plans; it does not just block.

**2.2 Bounded Autonomy (The "Scopes")**

Aligned with AWS Agentic Security Scoping Matrix:

- **Scope 1 (Prescribed):** Read-only, zero modification. (Junior Agents)

- **Scope 2 (HITL):** Human-in-the-loop approval workflows. (Standard Ops)

- **Scope 3 (Supervised):** Autonomous execution with mid-trajectory guidance. (Senior Agents)

- **Scope 4 (Full Agency):** Self-directed with continuous behavioral validation. (Commanders only)

**2.3 Force Structure (Hierarchical Cognitive Architecture)**

- **Meta-Cognitive Layer (Strategy):** Long-horizon planning, policy selection. (Commanders)

- **Deliberative Layer (Tactics):** Mid-horizon planning (Judge #6), MPC. (Squad Leaders)

- **Reactive Layer (Reflex):** <90ms safety shutdowns and collision avoidance. (Line Agents)

**2.4 Coordination (A2A Protocol)**

- **Identity:** Cryptographically verified agent identity (prevent spoofing).

- **Discovery:** Dynamic discovery of specialist agents without centralized bottlenecks.

- **Attenuated Delegation:** Human -> Platform -> Agent -> Sub-agent chains with full traceability.

**2.5 Discipline (UCMJ & Endex)**

- **The Clock:** Every mission has a "Drag Race" light bar visualizing timeout.

- **Endex:** If timeout is reached, the mission aborts.

- **UCMJ:** Team Leaders _scream_ at line agents. Infractions (Art 92, Art 134) are logged.
  - _Visual:_ "YOU ARE IN VIOLATION OF ARTICLE 92! GET YOUR ACT TOGETHER!"

---

### 3. THE QUALITY ASSURANCE (THE "COURTROOM")

We do not "check" code; we **put it on trial**.

**3.1 The 3-Tier Funnel**

- **Tier 0: The Draft (Cheap/Fast)**
  - **Models:** Qwen, GLM, DeepSeek (Local/HF).

  - **Role:** Generate initial code/text.

  - **Cost:** Near zero.

- **Tier 1: Explain-to-Peer (E2P)**
  - **Pattern:** Model A proposes -> Model B interrogates -> Model A repairs.

  - **Requirement:** Must show "Receipts" (Tool outputs, tests, hashes).

- **Tier 2: The High Court (Arbiter)**
  - **Prosecutor (GPT-5 A):** Argues _against_ the code (Security, Specs).

  - **Defense (GPT-5 B):** Defends the code (Context, Necessity).

  - **Judge (Arbiter):** Decides based on **Verdict.yaml** laws.

  - **Hard Rails:** Bugbot (Tests), Policy Gates (Safety).

**3.2 The Verdict**

- **Merge:** Score > 0.92 (Auto-merge).

- **Human Review:** Score 0.75 - 0.92 (RHR - Real Human Review).

- **Reject:** Score < 0.75 (Loop back to Tier 0).

---

### 4. THE INFRASTRUCTURE (THE "STACK")

**4.1 Cloud Run Architecture**

- **Orchestrator:** FastAPI + LangGraph on Cloud Run.

- **Draft Tier:** vLLM/TGI on Cloud Run GPUs (hosting open models).

- **Review Tier:** HTTP Clients to OpenAI/Anthropic (GPT-5/Claude).

- **State:** Postgres/Supabase (Case Files & Traces).

**4.2 Integration Points**

- **Antigravity IDE:** Connects via "Google Colab" extension to Vertex AI / Cloud Run.

- **GitHub:** All chats/traces saved to repo. Code pushed via PRs.

- **Nowgrep:** High-speed repo search for context grounding.

---

### 5. EXECUTION COMMANDS

**5.1 Initialize the Court**

```bash

# Deploy the Orchestrator

./scripts/deploy_courtroom.sh

# Run a Mission (The "Brief")

./bin/ungpt "Mission: Implement OAuth2. Constraints: No external auth providers."

```

**5.2 The "Dual-Chain" Review**

- **Command:** `agent:dual-chain-review`

- **Action:** Spawns two parallel 6-stage chains. Cross-examines packets. Arbiter merges.

**5.3 Emergency Override**

- **Command:** `agent:fire-alarm`

- **Action:** Immediate memory vacuum. Container kill. Reset to base state.

---

**END OF DOCTRINE**
