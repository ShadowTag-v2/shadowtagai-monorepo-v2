# Cloud Run Deployment Guide (Local & Architecture)

## 1. The "Design Session" Architecture

_Reference: Dina Graves Portman & Martin Omander_

**Goal:** Secure, Serverless Internal App (Port Management & Auditing).

- **Users:** Developer (Request), Admin (Approve), Auditor (View Logs).
- **Access Control:** `IAP` (Identity Aware Proxy) + `App Engine` frontend.
- **Database:** `Firestore` (NoSQL) for Requests/Approvals.
- **Audit Loop (Nightly):**
  1.  **Trigger:** `Cloud Scheduler` (Cron).
  2.  **Orchestrator:** Function 1 (Get all IPs).
  3.  **Fan Out:** `Pub/Sub` (1 message per server).
  4.  **Worker:** Function 2 (Port Scan Single Server).
  5.  **Reporting:**
      - **Alerts:** Filtered `Pub/Sub` -> Admin Email.
      - **Analysis:** All Logs -> `BigQuery` -> `Looker Studio` (Data Studio).

## 2. Local Development with VS Code (Cloud Code)

### Prerequisites

- **Cloud Code Extension:** Installed in VS Code.
- **Docker:** Installed and running locally.
- **GCP Project:** Active project with Cloud Run API enabled.

### Steps to Deploy Locally (Emulator)

1.  **Create App:**
    - Cloud Code Status Bar -> `New Application` -> `Cloud Run Application` -> `Node.js` (or Python).
2.  **Run Emulator:**
    - Cloud Code Status Bar -> `Run on Cloud Run Emulator`.
    - _Tip:_ Use **Buildpacks** (not Dockerfile) for faster updates.
    - _Tip:_ Set CPU to 1 vCPU in advanced settings.
3.  **Debug:**
    - Set Breakpoints in VS Code.
    - Cloud Code Status Bar -> `Debug on Cloud Run Emulator`.
    - Select `Debug: Toggle Auto Attach` -> `Smart`.
4.  **Hot Reload:**
    - Edit code -> Save -> Emulator rebuilds automatically.

### Deploy to Production

1.  **Command:** Cloud Code Status Bar -> `Deploy to Cloud Run`.
2.  **Region:** Select your target region.
3.  **Log:** View URL and verify.

## 3. Managing Secrets & Configs

- Use **Secret Manager** integrated with Cloud Run.
- **NEVER** hardcode credentials in the local emulator `env` files if possible; use `gcloud auth` application-default credentials.
