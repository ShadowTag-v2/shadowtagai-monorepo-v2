# GOVERNANCE: JUDGE 6 (The Enforcer)

## Identity

- **Role**: Policy-as-Code / Risk Engine.
- **Motto**: "Trust but Verify."
- **Stack**: Python (`GideonGuard`), Vertex AI (`UEBA`), BigQuery (`Audit Logs`).

## Core Components

1.  **GideonGuard (`guard.py`)**:
    - **Layer 0**: Secret Sanitization (Redacts API Keys/PII).
    - **Logic Gates**: Enforces hard limits (e.g., `MAX_RISK < 5%`, `MIN_LIQUIDITY > 20%`).
    - **Blocking**: Halts execution if gates are violated.

2.  **API Layer (`routes.py`)**:
    - **Unified Endpoint**: `/judge6/v5/evaluate`.
    - **Domains**: `SAFETY`, `HARM`, `CRIME`, `SHADOW_AI`, `INSIDER_THREAT`.
    - **Agents**:
      - `HarmPreventionAgent`: Checks for violence/bullying.
      - `UEBA`: User Entity Behavior Analytics (Insider Risk).
      - `SupplyChain`: Verifies physical carriers (DOT check).

3.  **Extensions**:
    - `HarmMitigator`: Escalates high-risk anomalies to SCC.
    - `WatermarkService`: Embeds SynthID into generated content.

## Workflow

1.  **Agent Action**: Kosmos/Jetski attempts to `Use Tool`.
2.  **Interception**: `BrowserTool` (or other) calls `Judge`.
3.  **Audit**: Judge checks Payload + Metadata against Policies.
4.  **Verdict**: `ALLOW` or `BLOCK` (with Reason).
