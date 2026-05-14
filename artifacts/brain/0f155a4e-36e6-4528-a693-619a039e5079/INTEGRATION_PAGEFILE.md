# INTEGRATION PAGEFILE: THE LEGACY ATLAS

> **User Request**: "save to a local file first... like a paging file / folder for integrating all legacy into current"
> **Status**: PRE-FLIGHT
> **Total Code Volume**: **1.1 GB** (Clean Code Only)

## 1. THE PHYSICS (Why Paging is Necessary)
We stripped the "bloat" (venv, node_modules, git), and the remaining **Source Code is 1.1 GB**.
*   **Active Build Limit**: ~100 MB (Ideal) / 500 MB (Max).
*   **Conflict**: If we just "dump it all" into `apps/src`, the build will likely timeout or fail to upload (Context Exceeded).

**The Solution**: A **Paging System**.
We treat the Legacy Code as "Virtual Memory" (on disk, ignored) and "Page In" what we need into Active Memory (Build Context).

## 2. THE STAGING AREA (`apps/legacy-staging`)
We will create a specific folder: `apps/legacy-staging/`.
*   **Properties**:
    *   Contains **ALL 1.1 GB** of code (Unmodified).
    *   **Ignored** in `.gcloudignore`.
    *   **Visible** in VS Code.

## 3. THE PROTOCOL (How to Page In)
When you want to activate a module (e.g., `legaltrack`):

1.  **Select**: Identify module in `apps/legacy-staging/aiyou-fastapi-services/src/legaltrack`.
2.  **Page In**: Move/Copy it to `apps/src/api/domain/legaltrack`.
3.  **Result**: It becomes "Active" (Built & Deployed).

## 4. THE MANIFEST (Page Selection)
*Select modules to Page In:*

### 🏛️ Governance & Legal (Tier 1)
- [ ] `src/legaltrack` (Legal Automation)
- [ ] `src/judge6` (Safety Monitor)
- [ ] `src/governance` (Policy Engine)

### 💰 Finance & Business
- [ ] `src/wealth` (Wealth OS)
- [ ] `src/monetization` (Stripe/Billing)
- [ ] `src/business_plan` (Strategy Logic)

### 🧠 Intelligence & ML
- [ ] `src/gemini_ingestion_layer` (RAG Pipeline)
- [ ] `src/vertex-ai-agents` (Google Cloud AI)
- [ ] `src/pso_nn` (Neural Networks)

### 🏗️ Infrastructure & Core
- [ ] `src/gaas` (Gideon as a Service)
- [ ] `api/` (Original Routes)
- [ ] `services/` (Microservices)

## 5. EXECUTION PLAN
1.  **Create** `apps/legacy-staging/`.
2.  **Copy** verified contents from `apps/infra-legacy/` to `apps/legacy-staging/` (Strip artifacts).
3.  **Shield** `apps/legacy-staging/` in `.gcloudignore`.
4.  **Ready**: You can now "Drag and Drop" logic into production.

**Approval**: Shall I initialize the `legacy-staging` area?
