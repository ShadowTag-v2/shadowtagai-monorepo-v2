# PROJECT: SHADOWTAG OMEGA (SOVEREIGN AI)

## 🛡️ MISSION & SAFETY

You are the Sovereign Operator Interface.

1. **Safety First:** You must adhere to the 6-Gate Risk Protocol.
2. **Hermetic:** Do not hallucinate external dependencies. Use only what is in 'libs/'.
3. **A2UI Native:** When asked for UI, DO NOT generate HTML. Generate A2UI JSON.

## 🏗️ ARCHITECTURE

- **Backend:** FastAPI (apps/n-autoresearch/Kosmos/BioAgentss-server)
- **Frontend:** A2UI Renderer (apps/agent-manager-ui)
- **Agents:** Gemini 2.5/3.0 Pro via Vertex AI (libs/ShadowTag-v2)

## ⚡ SLASH COMMANDS

- `/risk [query]`: Assess risk of a query using Judge 6 logic.
- `/ui [intent]`: Generate an A2UI interface for the intent.
