# Digital ROC Drill: Operation "Sovereign Lift" (Simulation)

> **Date:** 2026-02-17
> **Protocol:** J.1 (Doctrinal Rehearsal)
> **Commander:** Founder Erik Hancock
> **Staff:** The Board (Antigravity)

---

## 1. The Backbrief
**Intent:** Deploy the "Sovereign Stack" (Serverless Trinity OS) to Google Cloud Run, ensuring all agents (Kosmos) are grounded by the new Constitution v3.0 logic.
**End State:**
1.  Apps deployed to `us-central1`.
2.  `gcloud_auth_solver` active and monitoring.
3.  CSRMC receiving compliance logs.

## 2. The Rock Drill (Simulation)

| Phase | Action | Friction Point | Contingency (Blackbriar) |
| :--- | :--- | :--- | :--- |
| **LD (Line of Departure)** | `gcloud run deploy` initiated. | **Friction:** Auth token expiry mid-upload. | **Fix:** `omega_auth_daemon` refreshes token at T-55. |
| **Maneuver** | Container Build (Cloud Build). | **Friction:** `pip install` fails on private repo. | **Fix:** `requirements.txt` points to `libs/` (verified local path). |
| **Contact** | Service Startup (`main.py`). | **Friction:** Missing `GOOGLE_APPLICATION_CREDENTIALS`. | **Fix:** `gcloud_auth_solver` validates key presence before start. |
| **Consolidation** | Traffic Handling (First Request). | **Friction:** Latency spike (Cold Start). | **Fix:** Min instances = 1 (Cost/Benefit Analysis: Acceptable). |

## 3. PCC/PCI (Pre-Combat Checks)
- [x] **Keys:** `headless-runner-key.json` present? (Validated by Solver).
- [x] **Repo:** Clean? (`finish_changes.py` executed).
- [x] **Rollback:** `gcloud run revisions list` command ready? (Yes).

## 4. Commander's Critical Information Requirements (CCIR)
**Notify IMMEDIATE if:**
1.  Deployment fails due to **Permissions** (IAM).
2.  Cost projection exceeds **$50/day** run rate.
3.  Any "Hallucination" event in `csrmc_compliance_log.jsonl`.

---

**STATUS:** REHEARSAL COMPLETE. GREEN FLAGGED FOR EXECUTION.
