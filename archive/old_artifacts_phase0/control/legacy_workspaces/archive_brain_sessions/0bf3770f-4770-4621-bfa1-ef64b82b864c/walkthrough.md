# TRINITY SOVEREIGN OS (SERVERLESS) - DEPLOYMENT WALKTHROUGH

## 1. The Pivot: "Grounded Reality"
We have successfully pivoted from a "Heavy Lift" VM-based architecture to a **Serverless FastAPI** architecture (`src/antigravity/`). This aligns with the "Omnibus v8.0" goal of infinite scale with zero idle cost.

### Key Changes
- **No Terraform/VMs**: Replaced by Google Cloud Run.
- **Unified API**: Single entry point `src/antigravity/main.py`.
- **DoD Doctrine**: The **FULCRUM Engine** is now a Python class library, not just a document.

## 2. The Architecture

### A. The Core (`src/antigravity/core/`)
- **`ontology.py`**: The DNA. Strict Pydantic models and proper secret management (`os.getenv`).
- **`governor.py`** (**Judge #6**): Policy-as-Code. Prevents financial suicide and enforces "Lindy" rules on tech adoption.
- **`prosecutor.py`**: The **Sovereign Vault**. WORM storage and the "LEO Toggle" for cryptographic evidence handling.

### B. The Agents (`src/antigravity/agents/`)
- **Scholar**: Connects to Vertex AI Grounding to kill hallucinations.
- **Shopper (Bennett)**: Automated purchasing with Judge 6 oversight.
- **Sentinel**: Duty of Care (Anti-Suicide intent detection).
- **Fraud**: Internal Affairs (Behavioral analysis).
- **Sec+**: Active Defense (Honeynet VLAN steering).
- **Legal**: Automates Corp Code (DE/CA), IP checks, and M&A logic.
- **Finance (CFO)**: Audits Tax (409A/QSBS), Valuation, and GAAP revenue.
- **Product (CPO)**: Enforces Positioning (Dunford) and Growth Loops (Reforge).

### C. The FULCRUM Engine (`src/antigravity/engines/fulcrum/`)
The DoD Risk Management Framework (RMF) implemented as a state machine.
- **Phases 1-5**: Design, Build, Test, Onboard, Operations.
- **Capabilities**: Automated cATO, Continuous Monitoring (CONMON), and the "Watch Officer Kill-Switch".

### D. The Interface (`trinity/apps/cockpit/app/page.tsx`)
- **Visuals**: Rebranded from "Sci-Fi" to "Defense-Grade Governance".
- **Copy**: Highlights Judge 6, Scholar, and Vault.
- **Architecture**: Explicitly lists "Serverless (Cloud Run)" and "DoD FULCRUM".

## 3. Deployment Instructions

To deploy the Sovereign OS to Google Cloud Run:

```bash
gcloud run deploy trinity-os \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT_ID=trinity-omega-v2,CEO_SOVEREIGN_KEY=YOUR_SECRET_KEY"
```

## 4. Verification
Once deployed, you can interact with the Swagger UI at `https://[YOUR-CLOUD-RUN-URL]/docs`.

### Test Endpoints:
- `POST /api/v1/scholar/ground`: Verify a claim.
- `POST /api/v1/defense/fusion`: Generate a "Warfighter Scorecard".
- `POST /api/v1/fulcrum/deploy`: Run the full DoD RMF simulation.
