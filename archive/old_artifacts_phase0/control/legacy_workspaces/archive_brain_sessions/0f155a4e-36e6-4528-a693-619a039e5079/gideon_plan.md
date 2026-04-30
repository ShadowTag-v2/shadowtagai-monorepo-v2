# Gideon Sovereign Systems (Gold Master)

## Goal
Implement the 8-Node Sovereign Stack defined in the "Gideon OS" doctrine.

## Structure
-   `/gideon_os`: Root of the Gold Master OS.
-   `/gideon_os/core`: Core logic (Guard/Judge).
-   `/gideon_os/engines`: specialized engines (Bennett, Scholar, Sentinel, Prosecutor).
-   `/gideon_os/main.py`: Master Orchestrator.

## Components
1.  **Judge6 (Core)**: `gideon_os/core/guard.py` - cATO Enforcement.
2.  **Bennett (Shopper)**: `gideon_os/engines/bennett.py` - Solvency & Commerce.
3.  **Scholar (Grounding)**: `gideon_os/engines/scholar.py` - Legal/Medical Verification.
4.  **Sentinel (Safety)**: `gideon_os/engines/sentinel.py` - Duty of Care / Handoff.
5.  **Prosecutor (Vault)**: `gideon_os/engines/prosecutor.py` - WORM Evidence Locking.

## Deployment
-   **Terraform**: `gideon_os/main.tf` for infrastructure.
-   **Execution**: `python gideon_os/main.py`.
