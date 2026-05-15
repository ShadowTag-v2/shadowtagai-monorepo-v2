# Aerial Scaffolding & Cor.Self Analysis

## 1. The Vision: "Cor.Self" Recursive Loop
The user has defined a specific "Self-Prompting Loop" managed by Gemini Code Assist (GCA) acting as "Aerial Scaffolding".

### The Cycle (The "Judge's Turbine")
1.  **Intake**: GCA uses "Smart Actions" to refine User Prompt -> "Call of the Question".
2.  **The Swarm (Flying n-autoresearch/Kosmos/BioAgents)**:
    *   n-autoresearch/Kosmos/BioAgents vote/discuss the prompt on the "Whiteboard".
    *   n-autoresearch/Kosmos/BioAgents use **Jetski** to research (Internet/Docs).
3.  **The Filter (Judge 6 - CSRMC)**:
    *   Proposed approaches are vetted for Security/Legal violations.
    *   Output: "Mitigated/Approved" Prompt.
4.  **The Recursion (Aerial Scaffolding)**:
    *   GCA observes the result and generates **2 "Suggested Prompts"**.
    *   **Loop**: These new prompts go back to Step 2 (The Swarm).
    *   **Iterations**: Minimum **4 Loops**.
5.  **Final Output**:
    *   Once fully vetted (`x4`), GCA "punches the code" (writes final artifacts).
    *   Antigravity does *not* write; GCA does.

## 2. Gap Analysis (Current Implementation)

| Component | Status | Implementation |
| :--- | :--- | :--- |
| **Judge 6** | ✅ Active | `apps/tribunal`, `libs/pnkln/judge6` |
| **Flying n-autoresearch/Kosmos/BioAgents** | ✅ Active | `apps/n-autoresearch/Kosmos/BioAgentss-server` |
| **Jetski** | ✅ Active | `tools/jetski`, `jetski-sidecar` |
| **Aerial Scaffolding** | ⚠️ Partial | `libs/ShadowTag-v2/bridge_client.py` exists but logic is manual. |
| **Cor.Self Loop** | ❌ Missing | No automated "4-loop" orchestrator exists in `libs/ShadowTag-v2`. |

## 3. Implementation Plan
We need to create `libs/ShadowTag-v2/recursive_intelligence.py` to strictly enforce this loop:

```python
class CorSelfLoop:
    def __init__(self, iterations=4):
        self.iterations = iterations
        self.judge = JudgeSixClient()
        self.swarm = n-autoresearch/Kosmos/BioAgentssClient()

    def execute(self, user_prompt):
        current_context = user_prompt
        for i in range(self.iterations):
            # 1. Swarm Research
            research = self.swarm.dispatch(current_context)
            # 2. Judge Vetting
            verdict = self.judge.evaluate(research)
            if not verdict.approved:
                 current_context = self._mitigate(verdict)
                 continue
            # 3. GCA "Suggested Prompts" (Simulated/API)
            current_context = self._generate_suggested_prompts(verdict)
```
