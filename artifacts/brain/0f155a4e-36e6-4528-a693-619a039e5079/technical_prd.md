# Technical PRD: shadowtagai Execution Fabric (APIs + Schemas + Terraform Layout)

**Doc ID:** Cor.58.2-PRD-TECH
**Version:** 1.0
**Date:** Feb 2, 2026
**Scope:** Pure‑GCP runtime + governance + evidence + billing hooks (Stripe), designed to be production-shippable.

---

## 1) Product definition

### 1.1 What we’re building

A platform that turns each “agent run” into **(1) a billable unit**, **(2) a signed evidence package**, and **(3) a compliance feed**. The system enforces a “Juggernaut ↔ Brake” model:

* **Juggernaut:** high-throughput orchestration + metering + execution
* **Brake:** deterministic policy gates + external verification + immutable audit artifacts

### 1.2 Target users (personas)

* **Developer (Seat):** triggers runs via CLI/API, sees logs + verdict
* **Org Admin:** manages policies, budgets, entitlements, keys
* **Auditor/Assurance Consumer:** reads evidence packages + continuous assurance feed
* **Platform Operator (SRE/SecOps):** monitors, handles incidents, rotates keys

### 1.3 Goals (MVP)

1. **Run API** to create/track/cancel runs with streaming logs.
2. **Judge6 gating** producing deterministic allow/deny + control results.
3. **External verification loop** (Ralph-style truth): verifier stages determine pass/fail.
4. **Evidence package**: hash + KMS signature + WORM storage + index.
5. **Billing hooks**: prepaid credits & idempotent charge events (Stripe secret in Secret Manager).
6. **Terraform module set** to stand up the full stack in staging/prod.

### 1.4 Non-goals (MVP)

* Full IL5/SOC2 certification artifacts (we build foundations + auditability).
* Full “all NIST controls” library (we ship a priority subset + extensible mapping).
* Multi-cloud support.
* Model vendor consensus (pure Vertex AI tiering only).

---

## 2) System architecture (logical)

### 2.1 Services

**Cloud Run**

* `api-judge6` (FastAPI/Go): public API surface, auth, gating, orchestration, log stream
* `worker-exec` (Cloud Run service): handles long-running orchestration steps from Pub/Sub
* `worker-verify` (Cloud Run Jobs or service): runs verifications (lint/test/build/health)
* `ui-cockpit` (Next.js): Bench/Gavel/Metabolism dashboard (optional for MVP)
* `billing-webhook` (Cloud Run service): Stripe webhook receiver (optional MVP)

**Platform**

* **Firestore**: ledger (runs, logs, policy drafts, votes, verdicts, entitlements)
* **Pub/Sub**: run-events bus
* **Cloud Storage (WORM)**: immutable evidence artifacts + log bundles
* **Cloud KMS**: signing keys for evidence package
* **Secret Manager**: Stripe secret + signing config + service credentials
* **Vertex AI**: Gemini Flash = cheap cognition/log steps; Gemini Pro = verdict/fiduciary output
* **BigQuery (optional MVP)**: analytics + searchable run index (can be added in Week 2)

### 2.2 Event-driven run flow (canonical)

1. `POST /v1/runs` → creates `run_id`, writes Firestore `runs/{run_id}`, emits `RunRequested` event
2. `api-judge6` runs **pre-flight Judge6 gates** (fast)
3. `worker-exec` consumes `RunRequested`, generates plan, emits `RunPlanned`
4. `worker-verify` performs external stages, emits `RunVerified`
5. `api-judge6` (or `worker-exec`) generates final verdict using Gemini Pro, emits `VerdictIssued`
6. Evidence bundle is assembled → hashed → KMS-signed → stored in WORM bucket → pointer indexed
7. Billing event emitted (`BillingDebitProposed`) → billing subsystem finalizes

---

## 3) Functional requirements

### 3.1 Run Management

* Create a run with: intent, input payload, risk tier, max budget, optional policy profile.
* Stream logs (server-sent events) and fetch log history.
* Cancel run (best effort).
* Return deterministic state machine status.

### 3.2 Judge6 Gates (Brake)

* Deterministic checks before any expensive execution:

  * Identity & entitlement (seat, org, credits)
  * Budget & exposure ceilings
  * Policy allow/deny list by action type
  * Data sensitivity constraints (PII toggles, export restrictions)
* Output includes:

  * decision (`APPROVED|DENIED|REVIEW_REQUIRED`)
  * control checks array (`control_id`, `pass/fail`, `reason`)
  * risk score (0..1)
  * policy version + config snapshot hash

### 3.3 External Verification (Truth)

* Verification stages are authoritative; model self-assessment is not.
* Stages (MVP example):

  * `lint`
  * `unit_tests`
  * `docker_build`
  * `docker_run`
  * `health_check`
* Each stage emits structured results to Firestore and the event bus.

### 3.4 Evidence Package (Compliance Asset)

* Every run (approved or denied) generates an evidence record.
* Approved runs additionally include verifier stage proofs and artifact URIs.
* Evidence must be:

  * hashed (`sha256`)
  * signed (Cloud KMS asymmetric signing)
  * stored immutably (GCS retention policy / WORM bucket)
  * indexed for retrieval

### 3.5 Billing (Revenue)

* Prepaid credits model:

  * Stripe Checkout → org credit balance updated
  * Each run reserves estimated credits; final debit on completion
* All billing writes must be idempotent.

---

## 4) Non-functional requirements (NFRs)

### 4.1 SLOs

* **Run create latency (P95):** < 500ms (gating only; heavy work async)
* **Log availability:** logs visible in < 1s after emission
* **Evidence availability:** evidence pointer available within 10s of run completion
* **Availability:** 99.9% (MVP), designed for 99.95% later

### 4.2 Security

* No secrets in env vars if avoidable; use Secret Manager at runtime.
* All service-to-service calls use IAM OIDC tokens.
* Firestore rules deny direct client writes to system collections (server-only).
* Evidence bucket uses retention policy + (optional) retention lock once stable.

### 4.3 Observability

* Correlation headers: `X-Request-Id`, `X-Run-Id`
* Structured JSON logs
* OpenTelemetry traces (optional MVP)
* Metrics: runs/min, gate denies, verifier failures, cost/run, queue lag

---

## 5) API Specification (v1)

### 5.1 Conventions

* Base: `/v1`
* Auth: `Authorization: Bearer <OIDC/JWT>` (Google identity or your IdP)
* Idempotency:

  * Header: `Idempotency-Key: <uuid>`
  * Required on all POST endpoints that create state or charge money
* Errors:

  * `{ "error": { "code": "STG_xxx", "message": "...", "details": {...} } }`

---

## 5.2 Run API

### POST `/v1/runs`

Create a new run.

**Request**

```json
{
  "intent": "deploy_patch | research | checkout | policy_evaluate | code_gen",
  "risk_tier": "LOW | MEDIUM | HIGH",
  "budget": { "max_credits": 25 },
  "policy_profile": "default",
  "input": {
    "repo_url": "https://…",
    "task": "…",
    "params": { "key": "value" }
  },
  "client": {
    "source": "cli | cockpit | api",
    "client_version": "0.1.0"
  }
}
```

**Response (201)**

```json
{
  "run_id": "run_20260202_abcd1234",
  "status": "QUEUED",
  "gate": {
    "decision": "APPROVED",
    "risk_score": 0.12,
    "policy_version": "judge6_v1.3.0"
  },
  "links": {
    "self": "/v1/runs/run_20260202_abcd1234",
    "logs": "/v1/runs/run_20260202_abcd1234/logs",
    "events": "/v1/runs/run_20260202_abcd1234/events"
  }
}
```

**Possible statuses**

* `QUEUED → RUNNING → VERIFYING → VERDICTING → COMPLETE`
* terminal: `DENIED | FAILED | CANCELED | COMPLETE`

---

### GET `/v1/runs/{run_id}`

Fetch run metadata.

**Response**

```json
{
  "run_id": "…",
  "status": "VERIFYING",
  "created_at": "2026-02-02T19:22:11Z",
  "updated_at": "…",
  "intent": "deploy_patch",
  "risk_tier": "HIGH",
  "budget": { "max_credits": 25, "reserved_credits": 10, "final_credits": 12 },
  "gate": { "decision": "APPROVED", "risk_score": 0.12 },
  "verifier": {
    "stages": [
      { "name": "lint", "status": "PASS" },
      { "name": "unit_tests", "status": "RUNNING" }
    ]
  },
  "verdict": null,
  "evidence": { "status": "PENDING", "evidence_uri": null }
}
```

---

### POST `/v1/runs/{run_id}/cancel`

Cancel a run.

**Response**

```json
{ "run_id": "…", "status": "CANCELED" }
```

---

### GET `/v1/runs/{run_id}/logs`

Returns recent logs (paged).

Query params:

* `limit` (default 200)
* `before` (cursor)

**Response**

```json
{
  "run_id": "…",
  "items": [
    {
      "ts": "2026-02-02T19:22:15.120Z",
      "level": "INFO",
      "source": "worker-verify",
      "event": "STAGE_STARTED",
      "msg": "unit_tests started",
      "data": { "stage": "unit_tests" }
    }
  ],
  "next": "cursor_…"
}
```

---

### GET `/v1/runs/{run_id}/events` (SSE)

Server-sent events stream.

Event types:

* `RUN_UPDATED`
* `LOG`
* `STAGE`
* `VERDICT`
* `EVIDENCE_READY`

---

### GET `/v1/runs/{run_id}/evidence`

Fetch evidence pointer + signed hash (or full evidence if small).

**Response**

```json
{
  "run_id": "…",
  "evidence_uri": "gs://evidence-vault/runs/run_…/evidence.json",
  "hash_sha256": "…",
  "kms_key": "projects/.../cryptoKeys/evidence-signing",
  "signature_b64": "…"
}
```

---

## 5.3 Policy Governance API (Voting)

### POST `/v1/policies/drafts`

Create policy draft.

**Request**

```json
{
  "base_policy_version": "judge6_v1.3.0",
  "title": "Block external export of evidence bundles",
  "diff": {
    "deny_actions": ["EXPORT_EVIDENCE_EXTERNAL"],
    "allow_actions": []
  },
  "rationale": "Reduce exfil risk",
  "risk_class": "HIGH"
}
```

**Response**

```json
{
  "draft_id": "pd_20260202_xyz",
  "iteration": 1,
  "status": "DRAFT"
}
```

---

### POST `/v1/policies/drafts/{draft_id}/votes`

Cast a vote (agent or human role).

**Request**

```json
{
  "iteration": 1,
  "voter_role": "MONKEY_RISK | MONKEY_AUDIT | HUMAN_ADMIN",
  "approve": true,
  "notes": "OK, add exception for internal auditors"
}
```

---

### POST `/v1/policies/drafts/{draft_id}/judge-reviews`

Judge review with veto.

**Request**

```json
{
  "iteration": 1,
  "controls_failed": [],
  "risk_score": 0.08,
  "veto": false,
  "notes": "Compliant; proceed to iteration 2"
}
```

---

### POST `/v1/policies/drafts/{draft_id}/commit`

Commits final policy after thresholds met.

**Response**

```json
{
  "policy_version": "judge6_v1.4.0",
  "status": "ACTIVE"
}
```

---

## 5.4 Billing API (minimal hooks)

### POST `/v1/billing/checkout-session`

Creates Stripe checkout session for credits.

**Request**

```json
{ "credits_package": "CREDITS_1000", "success_url": "...", "cancel_url": "..." }
```

**Response**

```json
{ "checkout_url": "https://checkout.stripe.com/..." }
```

### POST `/v1/billing/webhook` (Stripe)

Receives Stripe events (verify signature). Updates entitlements.

---

# 6) Data Schemas

## 6.1 Firestore schema (collections)

### `orgs/{org_id}`

```json
{
  "org_id": "org_123",
  "name": "Acme",
  "created_at": "…",
  "billing_plan": "PREPAID",
  "settings": {
    "default_policy_profile": "default",
    "max_concurrent_runs": 25
  }
}
```

### `entitlements/{org_id}`

```json
{
  "org_id": "org_123",
  "credits_balance": 1200,
  "credits_reserved": 50,
  "seat_count": 10,
  "limits": { "runs_per_min": 60 }
}
```

### `runs/{run_id}`

```json
{
  "run_id": "run_…",
  "org_id": "org_123",
  "user_id": "user_456",
  "intent": "deploy_patch",
  "risk_tier": "HIGH",
  "status": "VERIFYING",
  "created_at": "…",
  "updated_at": "…",
  "budget": { "max_credits": 25, "reserved_credits": 10, "final_credits": null },

  "gate": {
    "decision": "APPROVED",
    "risk_score": 0.12,
    "policy_version": "judge6_v1.3.0",
    "control_results": [
      { "control": "AC-2", "result": "PASS", "reason": "" }
    ],
    "gate_hash": "sha256(...)"
  },

  "plan": {
    "status": "READY",
    "model": "gemini-flash",
    "steps": [ { "tool": "verify", "args": {} } ]
  },

  "verifier": {
    "stages": [
      { "name": "lint", "status": "PASS", "started_at": "…", "ended_at": "…" }
    ]
  },

  "verdict": {
    "status": "PENDING|ISSUED",
    "model": "gemini-pro",
    "summary": null,
    "raw_uri": null
  },

  "evidence": {
    "status": "PENDING|READY",
    "evidence_uri": null,
    "hash_sha256": null,
    "signature_b64": null,
    "kms_key": null
  }
}
```

### `runs/{run_id}/logs/{log_id}`

```json
{
  "ts": "…",
  "level": "INFO|WARN|ERROR",
  "source": "api-judge6|worker-exec|worker-verify",
  "event": "STAGE_STARTED",
  "msg": "…",
  "data": { "stage": "unit_tests" }
}
```

### `policy_drafts/{draft_id}`

```json
{
  "draft_id": "pd_…",
  "created_at": "…",
  "created_by": "user_…",
  "base_policy_version": "judge6_v1.3.0",
  "iteration": 1,
  "status": "DRAFT|IN_REVIEW|APPROVED|REJECTED|COMMITTED",
  "diff": { "deny_actions": [], "allow_actions": [] },
  "rationale": "…",
  "risk_class": "HIGH"
}
```

### `policy_drafts/{draft_id}/votes/{vote_id}`

```json
{
  "iteration": 1,
  "voter_role": "MONKEY_RISK",
  "approve": true,
  "notes": "…",
  "ts": "…"
}
```

### `policy_drafts/{draft_id}/judge_reviews/{review_id}`

```json
{
  "iteration": 1,
  "risk_score": 0.08,
  "controls_failed": [],
  "veto": false,
  "notes": "…",
  "ts": "…"
}
```

---

## 6.2 Pub/Sub message schemas (JSON)

Topic: `run-events`

### `RunRequested.v1`

```json
{
  "type": "RunRequested.v1",
  "run_id": "run_…",
  "org_id": "org_…",
  "user_id": "user_…",
  "intent": "deploy_patch",
  "risk_tier": "HIGH",
  "ts": "…"
}
```

### `RunPlanned.v1`

```json
{
  "type": "RunPlanned.v1",
  "run_id": "run_…",
  "plan_ref": "firestore:runs/run_…/plan",
  "ts": "…"
}
```

### `RunVerificationRequested.v1`

```json
{
  "type": "RunVerificationRequested.v1",
  "run_id": "run_…",
  "verifier_profile": "default",
  "ts": "…"
}
```

### `RunVerified.v1`

```json
{
  "type": "RunVerified.v1",
  "run_id": "run_…",
  "result": "PASS|FAIL",
  "stages": [
    { "name": "lint", "result": "PASS" }
  ],
  "ts": "…"
}
```

### `EvidenceReady.v1`

```json
{
  "type": "EvidenceReady.v1",
  "run_id": "run_…",
  "evidence_uri": "gs://…",
  "hash_sha256": "…",
  "ts": "…"
}
```

---

## 6.3 Evidence bundle (canonical JSON)

Stored at: `gs://{evidence_bucket}/runs/{run_id}/evidence.json`

```json
{
  "run_id": "run_…",
  "timestamp_rfc3339": "…",
  "actor": { "org_id": "…", "user_id": "…", "device_posture": "PASS", "ip_risk": "LOW" },
  "request": { "intent": "deploy_patch", "risk_tier": "HIGH", "budget_credits": 25 },

  "judge6": {
    "policy_version": "judge6_v1.3.0",
    "decision": "APPROVED",
    "risk_score": 0.12,
    "controls": [
      { "control": "AC-2", "result": "PASS", "reason": "" }
    ],
    "gate_hash": "sha256(...)"
  },

  "verification": {
    "ralph_loop": true,
    "result": "PASS",
    "stages": [
      { "name": "lint", "result": "PASS", "proof_uri": "gs://…/lint.txt" }
    ]
  },

  "artifacts": {
    "logs_uri": "gs://…/logs.jsonl",
    "bundle_uri": "gs://…/evidence.json",
    "hash_sha256": "…"
  },

  "signature": {
    "kms_key": "projects/.../cryptoKeys/evidence-signing",
    "signature_b64": "…"
  }
}
```

---

# 7) Terraform module layout (production-friendly)

## 7.1 Repo structure

```
infra/
  envs/
    staging/
      main.tf
      variables.tf
      outputs.tf
      terraform.tfvars
    prod/
      main.tf
      variables.tf
      outputs.tf
      terraform.tfvars

  modules/
    project_bootstrap/
    iam/
    firestore/
    pubsub/
    kms/
    secrets/
    storage_worm/
    artifact_registry/
    cloud_run_service/
    cloud_run_job/
    event_routing/
    cloudbuild/
    bigquery/               # optional
```

## 7.2 Module responsibilities

### `project_bootstrap/`

**Creates/enables**

* Required APIs (serviceusage)
* Default labels, org policy baselines (optional)
* Terraform state bucket (optional if not managed elsewhere)

**Variables**

* `project_id`, `region`, `labels`, `enable_apis[]`

**Outputs**

* `project_number`, `enabled_apis`

---

### `iam/`

**Creates**

* Service accounts:

  * `sa-api-judge6`
  * `sa-worker-exec`
  * `sa-worker-verify`
  * `sa-ui-cockpit`
  * `sa-billing-webhook`
* IAM bindings (least privilege)

**Key bindings**

* Firestore: `roles/datastore.user` to server services
* Pub/Sub publisher/subscriber roles
* Secret accessor roles
* KMS signer/verifier roles (signer only where needed)
* Storage object admin limited to evidence paths (prefer uniform bucket + prefix control via separate buckets if needed)

---

### `firestore/`

**Creates**

* Firestore database (Native mode)
* (Optional) composite indexes (if managed)

**Variables**

* `location_id`, `database_name`

---

### `pubsub/`

**Creates**

* topic: `run-events`
* subscriptions:

  * push subscription to `worker-exec` endpoint **or**
  * pull subscription if worker uses pull

**Variables**

* `topic_name`, `subscribers[]`, `dead_letter_topic`

---

### `kms/`

**Creates**

* Key ring `shadowtagai-kr`
* Asymmetric signing key `evidence-signing`

**Outputs**

* `kms_key_resource_id`

---

### `secrets/`

**Creates**

* Secret placeholders:

  * `STRIPE_SECRET_KEY`
  * `STRIPE_WEBHOOK_SECRET`
  * `JUDGE6_CONFIG` (optional)
* IAM: grant access to relevant SAs

---

### `storage_worm/`

**Creates**

* Evidence bucket: `gs://shadowtagai-evidence-{env}`

  * versioning enabled
  * retention policy (e.g., 7 years)
  * **retention lock** optionally controlled via a variable (lock only when ready)

**Variables**

* `retention_period_seconds`
* `lock_retention_policy` (bool)

---

### `artifact_registry/`

**Creates**

* Docker repo `shadowtagai` for built images

---

### `cloud_run_service/`

Reusable module to deploy a Cloud Run service.

**Inputs**

* `service_name`
* `image`
* `service_account_email`
* `env_vars` (non-secret)
* `secret_env_vars` (Secret Manager refs)
* `cpu`, `memory`, `concurrency`, `timeout_seconds`
* `ingress` (`all|internal`)
* `min_instances`, `max_instances`

**Outputs**

* `service_url`, `service_name`

---

### `cloud_run_job/`

Reusable module for verifier jobs.

**Inputs**

* `job_name`, `image`, `service_account_email`
* `env_vars`, `secret_env_vars`
* `cpu`, `memory`, `task_timeout`
* `max_retries`

**Outputs**

* `job_id`

---

### `event_routing/`

**Creates**

* Event routing from Pub/Sub → `worker-exec` Cloud Run service (push)
* Optional DLQ wiring

(If you prefer a simpler MVP: Pub/Sub push subscription directly to Cloud Run service HTTP endpoint.)

---

### `cloudbuild/`

**Creates**

* Cloud Build triggers for:

  * `api-judge6`
  * `worker-exec`
  * `worker-verify`
  * `ui-cockpit`

**Option**

* Deploy on main branch merge; tag-based promotions for prod.

---

### `bigquery/` (optional)

**Creates**

* Dataset `shadowtagai_analytics`
* Tables:

  * `runs_index`
  * `billing_events`
  * `evidence_index`

---

## 7.3 Environment composition (`infra/envs/prod/main.tf`)

Example composition order:

1. `project_bootstrap`
2. `artifact_registry`
3. `kms`
4. `storage_worm`
5. `firestore`
6. `pubsub`
7. `secrets`
8. `iam`
9. `cloud_run_service` (api, worker, cockpit, billing webhook)
10. `event_routing`
11. `cloudbuild`
12. `bigquery` (optional)

---

# 8) IAM & trust boundaries (minimum viable)

### Human roles (suggested)

* `OrgAdmin`: manage policies, billing, secrets (no KMS signing)
* `Developer`: create runs, read logs/evidence
* `Auditor`: read evidence + exports only
* `Operator`: manage infrastructure and incident response

### Service accounts (least privilege)

* `sa-api-judge6`:

  * Firestore read/write (runs/logs/policies)
  * Pub/Sub publish
  * Secret access (Stripe key, config)
  * KMS sign (if api signs evidence) **or** delegate to evidence worker
  * Storage write for artifacts
* `sa-worker-verify`:

  * Firestore update stage status
  * Storage write stage proofs
  * Pub/Sub publish stage results

---

# 9) Acceptance criteria (Definition of Done)

## MVP “Run → Evidence” path

* [ ] `POST /v1/runs` returns `run_id` in < 500ms P95
* [ ] Logs stream via SSE works end-to-end
* [ ] At least 3 verifier stages implemented and recorded
* [ ] Evidence JSON generated, hashed, KMS-signed, stored in WORM bucket
* [ ] `GET /v1/runs/{run_id}/evidence` returns URI + signature
* [ ] Idempotency prevents duplicate runs & billing events
* [ ] Terraform stands up full stack in staging with one command

---

# 10) Deliverables checklist (what engineering builds)

1. **OpenAPI spec** (`openapi.yaml`) covering endpoints above
2. **Firestore schema docs** + index definitions
3. **Pub/Sub schema registry** (even as versioned JSON docs)
4. **Terraform modules** as laid out above
5. **Reference implementations**

   * `api-judge6` skeleton with gate engine + run creation
   * `worker-exec` skeleton consuming Pub/Sub
   * `worker-verify` verifier stage runner
6. **Evidence signer**

   * KMS signing integration + verification tool
