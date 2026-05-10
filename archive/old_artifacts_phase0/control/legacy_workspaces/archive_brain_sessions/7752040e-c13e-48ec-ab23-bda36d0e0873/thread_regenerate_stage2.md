# Sovereign Scale Pivot: Stage 2 Regeneration Plan

## Goal Description
The Sovereign Architecture Pivot successfully drafted the required infrastructural components (LanceDB, Ollama mounts, Judge #6 validation scripts), but failed to wire them into the primary execution path. This plan rectifies the 'value leakage' of Stage 1. We will natively integrate the local LLM stack into the core governance router, activate the cryptographic validation middleware, and expose the commercial value of this pivot by tracking the "Fear & Greed arbitrage" (i.e., the cloud inference costs avoided by processing locally).

## User Review Required
> [!IMPORTANT]
> This plan executes the **Final Mile Wiring** of the Sovereign Engine. It assumes the user has approved the verified findings that `src/main.py` and `PolicyEnforcementAgent` currently bypass the local implementations.

## Proposed Changes

### 1. The Local LLM Engine Wiring
We must sever the hardcoded reliance on `gemini-3.1-flash-lite-preview` in the primary policy agent and route traffic to the zero-cost local Ollama instance, reserving Vertex AI only as a circuit-breaker fallback.

#### [MODIFY] [policy_agent.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services/src/agents/policy_agent.py)
- **Action:** Refactor `PolicyEnforcementAgent.evaluate()` to perform an asynchronous HTTP POST to `http://localhost:11434/api/generate` (the verified Ollama server).
- **Fallback:** If the local request times out or fails (e.g., Ollama is down), catch the exception and fall back to the existing `VertexAI` implementation.

### 2. The Cryptographic Gate (Judge #6) Activation
The `judge6_gating_valve.py` script exists but is orphaned. It must be converted into active FastAPI middleware to protect the primary routes.

#### [MODIFY] [main.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services/src/main.py)
- **Action:** Import `Judge6Gatekeeper` from `tools/judge6_gating_valve.py`.
- **Action:** Add a FastAPI middleware function (`@app.middleware("http")`) that intercepts all `POST`, `PUT`, and `DELETE` requests. The middleware will demand a valid trace graph payload (or a `X-Trace-Graph-Id` header) and invoke `validate_cor30_compliance()` before passing the request to the router.

### 3. The Commercial Arbitrage Metrics
To prove the financial model of the Sovereign Pivot, we must explicitly track the cloud costs we are avoiding.

#### [MODIFY] [base.py](file:///Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services/src/agents/base.py)
- **Action:** Update the `AgentMetrics` dataclass to include a new float field: `local_arbitrage_savings_usd`.
- **Action:** In the `PolicyEnforcementAgent`, when a request is successfully served by Ollama, calculate the hypothetical cost (based on input/output tokens using standard Gemini API rates) and append it to this metric.

## Verification Plan
### Automated Tests
- Send a standard `/v1/governance/evaluate` payload and verify the response `metrics` block contains `local_arbitrage_savings_usd > 0`.
- Shut down the Ollama process (`kill_port(11434)`) and verify the agent gracefully falls back to Gemini, logging the fallback in the reasoning trace.
- Send a simulated `POST` request without a trace graph and verify it receives a `403 Forbidden` from the Judge #6 middleware.
