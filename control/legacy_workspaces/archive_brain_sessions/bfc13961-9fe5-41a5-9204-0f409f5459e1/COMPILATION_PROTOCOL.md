# IMPL PLAN: THE COMPILATION PHASE (V6 Deploy)

**Objective**: Actualize the "Ghost Code" and physically instantiate the Dual-OS Architecture.

## 1. MERGE GHOST CODE (The Engine)
*Unlock the "Sovereign Stack v5" capabilities.*

*   **Source**: `claude/gptram-integration-01`
    *   **Action**: Extract `gptram_core.py` -> `libs/ShadowTag-v2/memory/`
*   **Source**: `claude/lawtrack-ultrathink-transfer`
    *   **Action**: Extract `ultrathink_prompts.yaml` -> `libs/ShadowTag-v2/prompts/`
*   **Source**: `claude/pnkln-vertex-ai-rollup`
    *   **Action**: Verify integration with `src/financial/monte_carlo.py`

## 2. SCAFFOLD GENESIS SPV (The Sky)
*Physically segregate the Moonshot assets.*

*   **Create**: `apps/genesis/`
*   **Create**: `apps/genesis/bio_sim/` (Placeholder for Chaos-Bio)
*   **Create**: `apps/genesis/failure_library/` (Data Asset)
*   **Constraint**: `Judge 6` must BLOCK direct import of `genesis` code into `core` apps.

## 3. DEPLOYMENT (The Release)
*   **Target**: Google Cloud Run (ShadowTag Omega)
*   **Command**: `python3 scripts/deploy_omega_cloudrun.py`
*   **Validation**: Verify `/risk` endpoint returns ATP score.

## 4. VERIFICATION
*   [ ] `libs/ShadowTag-v2` contains GPTRAM logic.
*   [ ] `apps/genesis` exists.
*   [ ] Cloud Run Service `n-autoresearch/Kosmos/BioAgentss-server` is Green.
