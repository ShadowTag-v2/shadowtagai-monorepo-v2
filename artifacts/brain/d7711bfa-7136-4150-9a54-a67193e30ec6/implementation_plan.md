# Sovereign Stack Implementation Plan (Active)

## Vision
Deploy a "Sovereign AI" architecture consisting of a secure "Glass House" backend (Judge 6) and a "Tinted Void" frontend (ShadowTag Web), connected via the AG-UI protocol.

## Phase 1: The Factory (Frontend)
- **Status:** ✅ Core Implemented
- **Tech:** Next.js, Tailwind ("Tinted Void"), CopilotKit.
- **Component:** `ReactorCore.tsx` (Payment Interface).
- **Bridge:** `api/copilotkit/route.ts` (AG-UI Adapter).

## Phase 2: Judge 6 Sentinel (Backend)
- **Status:** ✅ Core Logic Implemented
- **Tech:** Python (Flask), Gemini 3.0 Flash, Google Maps.
- **Role:** "The Automated Authorizing Official" (Blocking Middleware).
- **Security:**
    - **Strict Act-As:** Service Account identity enforcement (Dataform pattern).
    - **Physical Grounding:** Maps API verification of vendors.
    - **Shadow AI Block:** Regex filtering of non-Sovereign keys.

## Phase 3: The Nervous System (Integration)
- **Protocol:** AG-UI (Agent-User Interaction) + A2UI (Agent-to-UI).
- **Architecture:**
    1.  **User** interacts with `ShadowTag Web`.
    2.  `CopilotKit` sends event to `api/copilotkit`.
    3.  Next.js proxies request to `Judge Sentinel` (Cloud Run).
    4.  Judge adjudicates (Pass/Block).
    5.  Result streams back to UI.

## Phase 4: Ignition (Deployment)
- **Target:** Google Cloud Run (Serverless).
- **Command:** `uv run adk deploy cloud_run`.
- **Infrastructure:**
    - Artifact Registry (Immutable Vault).
    - Secret Manager (Stripe Keys).

## Tech Radar (Research Decisions)
| Tech | Status | Reasoning |
| :--- | :--- | :--- |
| **Gemini CLI Hooks** | **ADOPT** | Use for "Zero Entropy" Git safety. |
| **GenAI Toolbox** | **ADOPT** | Use for AlloyDB MCP connection. |
| **Strict Act-As** | **ADOPT** | Security model for Cloud Run. |
| **Pickle Rick** | *Reference* | Inspiration for "Ruthless" persona/hooks. |
| **Datadog** | *Reject* | Avoid vendor lock-in; use Cloud Logging. |
| **GDC Edge** | *Reject* | Overkill; Cloud Run is sufficient. |
