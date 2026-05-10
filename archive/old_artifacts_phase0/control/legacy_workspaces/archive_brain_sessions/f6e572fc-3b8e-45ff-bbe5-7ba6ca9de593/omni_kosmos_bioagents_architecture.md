# Omni-System: Kosmos & BioAgents Scaling Architecture

**Reference Material**:
- *Kosmos* (arXiv:2511.02824): Shared World Model scaling and hypothesis generation.
- *BioAgents* (arXiv:2512.04854): Multi-agent discovery through "Literature / Tool / Synthesis" structures.
- *Aegaeon Slab Context*: VRAM Caching (Gemini 3.1) enabling multi-agent scaling over massive input blocks at ~84% cost reduction.

---

## 1. The Death of Deterministic Voting

Earlier system prototypes hypothesized a "Zero-Cost Deterministic Voting" mechanism, where algorithms simulated swarm choices without querying language models. **This concept is deprecated and fundamentally incompatible with frontier-level reasoning.** Real AI orchestration requires actual inference scaling.

The new architecture relies on **True Inference Scaling**, leveraging `gemini-3.1-flash-lite-preview` for deep reasoning expansion and `gemini-3.1-pro` for synthesis and architectural alignment.

This approach uses **Real Multi-Agent Iteration**, where tokens are spent, latency is incurred, and agents explicitly debate, write code, and critique one another.

---

## 2. BioAgents Duality: Literature & Execution Squadrons

The Omni-System divides agents into specific functional topologies based on the BioAgents methodology.

### 2.1 The Squadrons
*   **The Literature / Intel Squadron (AIR_CAV + CHARLIE):** These agents do not write code or make decisions. They are strictly bound to reading the vast Aegaeon Context Slab (VDRs, JIRA tickets, Slack logs, Doctrinal Manuals). They are researchers.
*   **The Execution / Tool Squadron (ALPHA + BRAVO):** These agents take the summarized briefs from the Literature squadron and attempt to execute tasks—running shell commands, generating code, querying APIs, and pushing state.
*   **The Synthesis Squadron (HHT):** These agents evaluate the results of the execution layer, aggregating findings and formally deciding whether the system advances to the next objective or needs another Kosmos Cycle.

This trio interacts repeatedly over iterations, continuously peer-reviewing their own output and correcting logic faults autonomously.

---

## 3. The Kosmos Recursive Cycle (Up to 20x Iterations)

Rather than generating an answer in a single shot, the Omni-System executes **Kosmos Cycles**. The system tracks state via a shared, structured **World Model** (hosted in Firestore).

### 3.1 The Kosmos Loop
1.  **Read World Model:** Agents load the current objectives and previously discovered facts.
2.  **Parallel Rollout:** Using `asyncio`, the system fires up to 20 parallel *real* API calls to Gemini 3.1 depending on task complexity.
3.  **Synthesis & Scoring:** The HHT Synthesis agents review the rollouts, grading them against the ATP 5-19 Risk Framework. Unsafe or nonsensical responses are immediately discarded.
4.  **Active Mitigation (The Bar Exam & Whiteboard):** If a rollout triggers a violation, it doesn't just fail. The agent swarm enters an Active Mitigation sub-loop:
    *   **Bar Exam "Call of the Question":** Agents draft the precise legal constraints required to answer without violating doctrine before attempting another generation.
    *   **Whiteboard Technique:** Agents maintain a single, mutable point of truth with confirmed deadlines, preventing infinite hallucination spirals during resolution.
    *   **Output:** The swarm either rewrites the AST to be safe, or generates 3 legally compliant alternative prompts for the user with explanations.
5.  **Write World Model:** Verified discoveries, tools used, and updated hypotheses are pushed to the Firestore World Model.
6.  **Hypothesis Generation:** If the objective is unmet, the system loops. The paper demonstrates that scaling up to 20 cycles provides linear improvement on complex scientific and coding benchmarks.

---

## 4. The Engineering Enablers

The primary challenge of True Inference Scaling is **cost** and **context window pollution**.

### 4.1 Aegaeon Slab Context Caching
To execute 20-agent parallel rollouts without bankrupting the system, the Omni-System utilizes Context Caching. The massive baseline logic (codebases, documentation, rules) is uploaded once as an **Aegaeon Slab**. When 20 agents spin up simultaneously, they merely pass a tiny delta query (e.g., "Analyze function X") against the cached slab. This shrinks token consumption dramatically while enabling massive scaling.

### 4.2 Sequential Attention
When evaluating massive documents (e.g., Private Equity VDRs), the system forces the LLMs to read sequentially using the MCP `AtomicThread` integration. The LLM cannot "skim" the whole document in one shot; it is forced to focus on one logical cluster at a time, generating findings linearly.

---

## 5. Security Posture: Brakes and Governance

Despite massive inference scaling, the **Judge #6 Engine** remains the immutable constitutional gatekeeper.
No matter how many Kosmos Cycles run or how deep the BioAgents debate, **no action is committed to the outside world without Judge #6's explicit evaluation.**

*   **p99 ≤90ms SLA:** Judge #6 evaluates the output of the final Synthesis cycle.
*   **ATP 5-19 Matrix:** If the combined agent swarm output breaches the designated risk tolerance, Judge #6 returns an immediate block, overriding all prior reasoning.
*   **Layer 5 Absolute Lock:** For severe or repeated unauthorized behavior, Judge #6 invokes an absolute 5th layer. This instantly disconnects the user's session, suspends the account, and pages management *before* any malicious action leaves the internal network.
*   **RKILL Protocol:** The ultimate fail-safe. If internal telemetry (or Judge #6) suspects the Kosmos swarm itself has been compromised via Prompt Injection (e.g., executing rogue operations), RKILL severs the tenant's KMS encryption keys, instantly rendering the entire cache and world model unreadable and stopping the swarm mid-cycle.
