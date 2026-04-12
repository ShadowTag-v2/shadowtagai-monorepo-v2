# SOVEREIGN STATE PROTOCOL v5.0 (NATIVE MLX)

CLASSIFICATION: TIER 0 // PROTOCOL
STATUS: ACTIVE (ENFORCED)
SCOPE: Hardware Dispatch & Pre-Flight Execution Risk

## 1. THE GOLD MASTER CONCEPT (V5 OMEGA)
You have established a Sovereign State Gold Master. This is a locked, immutable snapshot of the unified Monorepo (UphillSnowball) governed exclusively by the `.code-workspace` anchor.
* **Current Tag:** `SOVEREIGN_GOLD_MASTER_V5`
* **Definition:** The state where `apps/`, `infra/`, and `zero_cpu_router.py` handle localized compute entirely free from vendor lock-in.

## 2. THE C-BRIDGE HARDWARE CASCADE (MLX + ANE)
The core tenet of the Sovereign State is zero-latency, local-first inference. Do NOT execute cloud payloads for tasks under the complexity threshold if local compute is active.

### Execution Priority (The Waterfall):
1. **Tier 1 (Apple Neural Engine):** All payloads `< 2000` chars MUST route through `libane_bridge.dylib` via `_dispatch_ane()`. Cost: $0.00. Network: Offline.
2. **Tier 2 (Sovereign GPU - MLX/TurboQuant):** If the ANE faults, or payload exceeds `2000` chars, fallback to the local CUDA/Metal elastic worker on port `12346`. Cost: $0.00. 
3. **Tier 3 (Cloud Vertex API):** OMEGA-LEVEL FALLBACK ONLY. If both local nodes are dark, strike out via HTTP to Gemini 3.1 Flash-Lite.

*Any violation of this waterfall degrades the Sovereign architecture.*

## 3. JUDGE 6 OPERATIONAL CONSTRAINTS (WET FLEECE)
Before ANY code execution escapes the `apps/playground/sandbox.py` or hits the filesystem via MCP, it must traverse the Judge 6 heuristics gate.

1. **Semantic Taint Checking:** No `rm -rf`, `:(){ :|:& };:`, or blind directory traversals.
2. **AST Exclusion Boundary:** The `third_party/ANE/` and `external_sdks/` boundaries are completely off-limits to formatting mutation. Judge 6 strictly enforces `.aiexclude` and `biome.json` inheritance.
3. **Zero-Trust Token Sync:** FastApi validation `Depends(verify_zero_trust)` MUST structurally check the compute payload identity (`767252945109-compute-token`) prior to releasing the execution to Temporal. 

## 4. GOD MODE PROTOCOL (AGENT AUTONOMY)
### A. BLANKET PERMISSION (SAFE_TO_AUTO_RUN) 
The Agent is authorized to set `SafeToAutoRun: true` for:
1. Script Execution: Any script in `scripts/`.
2. Hardware Validation: Auto-compiling `third_party/ANE/bridge/`.
3. Agent Recovery: Triggering `/omega-loop` (Janitor) implicitly on workflow exits.

### B. AUTONOMOUS CLEANUP (THE 'FINISH' MANDATE) 
Before handing control back to the User, the Agent MUST execute the Finish Protocol to securely eject state via GitHub App JWT authentication: `./scripts/finish_changes.py`
