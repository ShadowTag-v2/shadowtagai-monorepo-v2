# INTERNAL TOOLING (FACTORY) ROADMAP

## 1. THE FACTORY: UPHILLSNOWBALL SOVEREIGN
**Role**: The "Builder" of the Commercial MVP.
**Located at**: `/Users/pikeymickey/aiyou-stack/ShadowTag-v2/uphillsnowball_sovereign/` (Proposed)

### Core Components needed for MVP Generation:
1.  **Orchestrator (`main_factory.py`)**:
    *   Accepts high-level product specs (e.g., "Build Judge#6 API with ATP 5-19 gates").
    *   Dispatches tasks to FlyingMonkeys.
2.  **Swarm (`flying_monkeys7.py`)**:
    *   **BRAVO Troop**: Writes the FastAPI code.
    *   **CHARLIE Troop**: Writes the Tests (PyTest).
    *   **CODEPMCS**: Scans for vulnerabilities.
3.  **Knowledge Base (`whiteboard/`)**:
    *   Contains the "Self-Prompting Loop" patterns.
    *   Contains the "ATP 5-19" requirements.

## 2. THE PIPELINE: FACTORY -> PRODUCT

### Step 1: Definition (The Spec)
*   **Input**: `HANSEN_HOLDINGS_CHARTER.md` + `ATP_5_19_REQUIREMENTS.md` (to be created).
*   **Action**: `Uphillsnowball` parses requirements into a JSON task list.

### Step 2: Fabrication (The Coding)
*   **Action**: FlyingMonkeys agents generate:
    *   `deploy/main.py` (The Commercial API).
    *   `deploy/Dockerfile` (The Commercial Container).
    *   `deploy/cloudbuild.yaml` (The Commercial Pipeline).
*   **Constraint**: Use "Pure Serverless" patterns (Cloud Run, no GKE).

### Step 3: Verification (The Audit)
*   **Action**: Judge#6 (Internal Instance) validates the *generated code* against the ATP 5-19 rules.
*   **Output**: `GENERATION_AUDIT_LOG.json`.

### Step 4: Ejection (The Handoff)
*   **Action**: Validated code is moved to `shadowtag-commercial` directory for deployment.

---

## 3. IMMEDIATE TASKS (MVP GENERATION)

1.  [x] **Initialize Factory**: Verified `uphillsnowball_sovereign` exists and has `flying_monkeys7.py` (as `flying_monkeys_factory.py`).
2.  [x] **Define Commercial Spec**: Implemented in `generate_mvp.py`.
3.  [x] **Run The Factory**: Executed `generate_mvp.py` to generate commercial codebase in `../shadowtag-commercial`.
4.  [ ] **Deploy**: `gcloud run deploy shadowtag-commercial ...`

## 4. VALUE PROPOSITION
*   The "Product" (ShadowTagAi) is disposable. We can regenerate it from the Factory at any time.
*   The "Factory" (Family Holdings) is the asset. It contains the intelligence to build the product.
