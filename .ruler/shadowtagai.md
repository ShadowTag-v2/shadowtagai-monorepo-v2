# ShadowTagAI — Ruler Agent Rule

## Architecture Lock

- **Orchestration:** Native Gemini function calling ONLY
- **Deprecated:** AutoGen, AG2, LangGraph, Vertex AI Workbench (for orchestration)
- **Database:** Firestore
- **Queue:** Google Cloud Tasks
- **CI/CD:** Cloud Build (planned)
- **Compute:** Cloud Run → GKE Autopilot (migration planned)

## Handoff

Before any ShadowTagAI work, load:

```
docs/hand_off/SHADOWTAGAI_CURRENT_STATE.md
```

## Function Calling Doctrine

The model proposes structured function calls. Application code executes approved
functions through ToolGateway. The model never executes shell commands directly.

- All function declarations must be registered and schema-validated
- Active tool bundle should stay under 10, review threshold at 20
- Temperature 0.0 for deterministic tool selection
- Consequential actions require user confirmation
- Evidence is recorded for every function call execution

See: `tool_contracts/gemini.function_call.yaml`
See: `tool_contracts/firebase.function_bridge.yaml`

## Deploy Workflow

Use `/shadowtagai-deploy-preflight` — never blind deploy.

## Client-Side AI

Firebase AI Logic function calling uses the same safety physics:

```
function declaration → schema validation → risk classification
→ confirmation if consequential → execution → evidence → response
```

See: `tool_contracts/firebase.ai_logic_launch.yaml`
