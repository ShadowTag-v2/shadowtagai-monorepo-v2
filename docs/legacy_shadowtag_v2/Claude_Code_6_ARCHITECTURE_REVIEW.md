# JUDGE 6: OMEGA ARCHITECTURE REVIEW (V2.0.0)

**Status:** CRITICAL REVISION REQUIRED
**Date:** 2026-01-28
**Source:** Judge 6 Sentinel

## 🔴 CRITICAL ISSUES IDENTIFIED

### 1. ARCHITECTURAL MISMATCH

- **Problem:** Previous plan used `google-cloud-notebooks` (VMs).
- **Doctrine:** Cloud Run ONLY. No VMs, no GKE.
- **Fix:** Deploy to Cloud Run managed platform.

### 2. DEPENDENCY BLOAT

- **Problem:** Installed `google-cloud-notebooks`, `psutil`.
- **Fix:** Stick to minimal `mcp`, `google-cloud-aiplatform`, `google-cloud-firestore`.

### 3. SPM ENGINE SIMULATION TRAP

- **Problem:** `Jetski` and `GCA_Core` were mocks.
- **Fix:** Use `subprocess` for real shell execution and `vertexai` for real Gemini calls.

### 4. RKILL DAEMON INCOMPATIBILITY

- **Problem:** `psutil` daemon usage in stateless container.
- **Fix:** Use Cloud Run `timeoutSeconds` (hard limit) and Cloud Monitoring.

### 5. DRIVE ACCESS & AUTH

- **Problem:** Default credentials don't access User Drive.
- **Fix:** Explicit OAuth scopes or Service Account delegation (if applicable) or switch to Google Drive API with stored refresh token (Project Omega requirement). _Note: For Cloud Run, we use Service Identity._

### 6. MEMORY BANK PERSISTENCE

- **Problem:** `learned_rules.json` is ephemeral in Cloud Run.
- **Fix:** Use Firestore (`shadowtag-omega-v2`).

---

## 🔧 REVISED ARCHITECTURE

### TIER 1: FOUNDATION

#### 1.1 Cloud Run Deploy Script

`scripts/deploy_omega_cloudrun.py` (Source-based deploy).

#### 1.2 Firestore Memory Bank

`src/governance/memory/memory_bank.py` using `google.cloud.firestore`.

### TIER 2: SPM ENGINE (REALITY)

#### 2.1 Jetski (Real Bash)

Uses `subprocess` with timeouts.

#### 2.2 GCA Core (Real Vertex AI)

Uses `gemini-3.1-flash-001`.

### TIER 3: MCP SERVER

#### 3.1 Health Check & Port

Expose port 8080/$PORT.

---

## 🎯 EXECUTION PLAN

### Phase 1: Infrastructure Lock

1.  Config project `shadowtag-omega-v2`.
2.  Enable APIs (Run, Firestore, AI Platform).
3.  Init Firestore.
4.  Deploy MCP.

### Phase 2: Constitution Install

1.  Docs & Src structure.
2.  Copy revised code.

### Phase 3: Validation

1.  Test Judge 6 Locally.
2.  Test Firestore.
3.  Cloud Run Health Check.
