# DOCTRINE ANALYSIS: ATP 5-19 vs. CSRMC
**Date:** 2026-02-16
**Subject:** Selection of Risk Engine for "Constant Mitigation"

## 1. THE USER HYPOTHESIS
> *"Maybe we do want ATP 5-19 only digitized and constantly mitigating down the threats to acceptable levels?"*

**Verdict:** You are describing the **goal** correctly, but **ATP 5-19** is the wrong tool to achieve it.
What you are asking for ("Digitized Constant Mitigation") *is* **CSRMC**.

## 2. THE CHASM: STATIC LABELING vs. DYNAMIC FIGHTING

### OPTION A: Digitized ATP 5-19 (The "Safety Inspector")
*Source Code:* `src/governance/atp_519.py`
*   **Mechanism:** A static lookup table.
*   **Input:** "Probability is Likely, Severity is Critical."
*   **Output:** "Risk is HIGH."
*   **The Flaw:** It stops there. It identifies the risk but does **nothing** to fix it. It is a "Snapshot" tool designed for planning missions (e.g., "Is it too rainy to fly the drone?"), not for fighting cyberwars.
*   **Why it fails Cyber:** Cyber threats change in milliseconds. A static matrix cannot "mitigate down" a polymorphic virus.

### OPTION B: CSRMC (The "Auto-Turret")
*Source Code:* `src/governance/judge_six/csrmc_module.py`
*   **Mechanism:** A dynamic state machine (Green/Yellow/Red).
*   **Input:** Telemetry (`active_threats`, `vuln_score`).
*   **Output:** **ACTION** (`EXECUTE_AUTO_PATCH`, `ISOLATE_ENCLAVE_AND_FIGHT`).
*   **The Advantage:** It doesn't just label the threat; it **attacks** the threat.
    *   *Is the risk too high?* -> **Execute Auto-Patch.** (Mitigates Down).
    *   *Are we under attack?* -> **Isolate Enclave.** (Maintains Survival).

## 3. COMPARISON TABLE

| Feature | ATP 5-19 (Digitized) | CSRMC (DoD Construct) |
| :--- | :--- | :--- |
| **Logic** | `IF (Prob, Sev) THEN Label` | `IF (Threat) THEN Kill` |
| **Timeframe** | Snapshot (Planning Phase) | Continuous (CONMON) |
| **Action** | None (Passive Reporting) | **Patches, Isolates, Fights** |
| **Goal** | Hazard Awareness | **System Survivability** |
| **Best For** | Supply Chain / Logistics | **Cyber / Software / AI** |

## 4. RECOMMENDATION
**Stick to the Split.**
1.  **Keep ATP 5-19 for Supply Chain:** Physical movement of servers/chips is slow. A static matrix is perfect for answering "Should we ship this during a hurricane?"
2.  **Use CSRMC for the Digital OS:** "Constant Mitigation" requires the ability to execute code (patches/bans) in real-time. Only CSRMC allows the system to reach **Green State** automatically.
