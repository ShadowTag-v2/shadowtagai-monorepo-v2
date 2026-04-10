# IMPLEMENTATION PLAN: TRINITY SOVEREIGN OS (SERVERLESS)

## Goal
Deploy the **Trinity Sovereign OS** as a **Serverless FastAPI** application on Google Cloud Run. This replaces the previous "Heavy Lift" VM architecture with a scalable, cost-efficient, and "Grounded" architecture.
Integrated into this OS is the **DoD FULCRUM Engine**, a specialized state machine for processing "Weapon System Profiles" and enforcing cATO (Continuous Authority to Operate).

## User Review Required
> [!IMPORTANT]
> **Paradigm Shift**: This moves from "Infrastructure as Code" (Terraform/VMs) to "Code as Infrastructure" (FastAPI/Cloud Run). We are abandoning the "Sovereign Stack" VM approach.
> **Deployment**: Requires `gcloud run deploy`.

## Proposed Changes

### 1. The Trinity Skeleton (`src/antigravity/`)
New clean module structure.

#### [NEW] `src/antigravity/main.py`
- The `FastAPI` entry point.
- Exposes endpoints:
    - `/api/v1/scholar/ground` (Academic Researcher)
    - `/api/v1/shop/snipe` (Shopper)
    - `/api/v1/defense/fusion` (DoD Fusion)
    - `/api/v1/fulcrum/deploy` (New: FULCRUM Engine Trigger)

#### [NEW] `src/antigravity/core/`
- **`ontology.py`**: Shared DNA (Enums, Pydantic Models).
- **`governor.py`**: Judge #6 (Policy-as-Code).
- **`prosecutor.py`**: Sovereign Vault (WORM Storage).

### 2. The Agents (`src/antigravity/agents/`)
- **`scholar.py`**: The "Academic Researcher" (Vertex AI Grounding).
- **`shopper.py`**: "Bennett" (Automated Purchasing).
- **`sentinel.py`**: Duty of Care (Anti-Suicide).
- **`fraud.py`**: Internal Affairs.
- **`secplus.py`**: Active Defense (Honeynet Steering).

### 3. The FULCRUM Engine (`src/antigravity/engines/fulcrum/`)
Implementing the User's "6 Atomic blocks".
- **`ontology.py`**: FULCRUM specific enums.
- **`phase_1_2_ioc.py`**: Design & Build.
- **`phase_3_foc.py`**: Test & Assess.
- **`phase_4_onboard.py`**: NextGen CSSP.
- **`phase_5_operations.py`**: Watch Officer & Kill-Switch.
- **`main.py`**: Orchestrator (callable from API).

### 4. Integration
- The `DoDFusionCenter` in `src/antigravity/fusion.py` will bridge the specific agents.

## Verification Plan
### Automated Tests
- Run `local_demo.py` to simulate the API calls.
- Verify "Scholar" grounds claims (mocked if no GCP creds).
- Verify "Judge 6" blocks excessive spending.
- Verify "FULCRUM" runs the full RMF cycle.

### Manual Verification
- `gcloud run deploy` (User Action).
