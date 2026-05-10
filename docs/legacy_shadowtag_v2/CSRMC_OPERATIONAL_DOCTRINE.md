# JUDGE 6: CSRMC OPERATIONAL DOCTRINE (v3.0)

**Mandate:** Department of War, Sept 24, 2025
**Philosophy:** "Cyber Survivability > Static Compliance"

## I. THE SHIFT

| Old Way (RMF)                              | New Way (CSRMC)                                 |
| :----------------------------------------- | :---------------------------------------------- |
| **Snapshot:** 3-Year Authorization         | **Continuous:** Real-time ATO                   |
| **Authority:** Certifiers (Paperwork)      | **Authority:** CSSP (Defenders)                 |
| **Action:** "Disconnect on Non-Compliance" | **Action:** "Fight Through" (Mission Dependent) |

## II. THE 5-PHASE KILL CHAIN

1.  **DESIGN:** Embed security (Shift Left).
2.  **BUILD:** Reach IOC (Initial Operating Capability).
3.  **TEST:** Reach FOC (Full Operating Capability).
4.  **ONBOARD:** Connect only after CSSP sign-off.
5.  **OPERATIONS:** ConMon & Active Defense.

## III. SURVIVABILITY LOGIC

- **Scenario:** Critical Vulnerability Detected.
- **If Mission = ROUTINE:** Revoke ATO. Disconnect.
- **If Mission = CRITICAL (Combat):** DO NOT DISCONNECT. Isolate enclave. Fight through.

## IV. DEVSECOPS IMPLEMENTATION (The "Shift Left")

- **Design Phase:** Enforced by `gemini-cli-extensions/security`.
  - _Requirement:_ Zero hardcoded secrets. Zero High-Severity CVEs.

- **Build Phase:** Enforced by `gemini-cli-extensions/code-review`.
  - _Requirement:_ Logic Score > 80%. No debug artifacts.

- **Provenance:** [SUSPENDED] ShadowTag hash requirement is currently paused for velocity.
