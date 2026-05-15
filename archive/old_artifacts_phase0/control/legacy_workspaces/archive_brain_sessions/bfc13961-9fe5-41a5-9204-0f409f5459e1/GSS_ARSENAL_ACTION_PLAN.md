# GSS Arsenal Action Plan

**Goal**: Integrate harvested Google Cloud tools into Gideon Sovereign Systems (GSS) architecture to strictly enforce the "Vendor-Agnostic / Sovereign" doctrine.

## 1. Nervous System Expansion (Infrastructure)

### A. Cluster Toolkit (`infra/cluster-toolkit`)
**Role**: Vendor-Agnostic GPU Mesh Orchestrator.
**Action**:
- Use to provision high-performance GPU clusters on GKE.
- Abstracts underlying hardware, enabling the "Vendor Agnostic" pledge (Lambda/Crusoe/AMD).
- **Next Step**: Create a GSS-specific blueprint in `infra/gss/gpu-mesh`.

### B. Magic Modules (`infra/magic-modules`)
**Role**: Custom Sovereign Providers.
**Action**:
- Use to generate custom Terraform providers if standard Google providers lack specific sovereign features.
- Enables "Sovereign Cloud" locking at the API level.

## 2. Serverless Ops Pattern

### PubSub2Inbox (`infra/pubsub2inbox`)
**Role**: Generic sidecar for pushing Pub/Sub messages to any HTTP endpoint (Sovereign Adapter).
**Action**:
- Integrate `serverless-exec-ruby` (`infra/serverless-exec-ruby`) for sidecars.

### serverless-exec-ruby (`infra/serverless-exec-ruby`)
**Role**: Safe Remote Execution.
**Action**:
- **Adopt Pattern**: The repository demonstrates running maintenance tasks (DB migrations, one-off scripts) in serverless containers rather than local workstations.
- **Implementation**: Port the logic to Python/Go for GSS.
- **Use Case**: Running `src/gss/kernel.py` maintenance modes (e.g., `judge.audit("DEEP_CLEAN")`) safely in Cloud Run without exposing production DBs to local machines.

## 3. Code Harvesting & Observability

### ruby-docs-samples, appengine-ruby & getting-started-ruby
**Role**: Pattern Library & Runtime Contracts.
**Action**:
- `ruby-docs-samples`: Scan for `cloud-run`, `pubsub`, and `secret-manager` implementations.
- `appengine-ruby`: Analyze how Google structures secure runtime environments (lifecycle, health checks).
- `getting-started-ruby`: Extract baseline "Hello World" to "Production" migration paths for sovereign services.
- "Transpile" best practices to the GSS Python/Go stack.
- **Immediate Focus**: `pubsub` triggers for the Worker Node.

### opentelemetry-operations-ruby (`infra/opentelemetry-operations-ruby`)
**Role**: Sovereign Observability.
**Action**:
- Analyze Google's specific implementation of OpenTelemetry exporters.
- **Goal**: Implement purely sovereign tracing in `src/gss/kernel.py` (GideonGuard) without vendor lock-in, using the OTel standard but directing telemetry to our Sovereign Vault (GCS) if needed, or Cloud Trace if permitted.

## 4. Edge & Senses Expansion

### mqtt-cloud-pubsub-connector (`infra/mqtt-cloud-pubsub-connector`)
**Role**: Nervous System Edge Interface.
**Action**:
- Deploy as a bridge for "Senses" (Organs that ingest data).
- Allows unauthenticated or lighter-weight devices (IoT, external tickers) to speak MQTT, which this connector translates to authenticated Pub/Sub messages for the Nervous System.
- **Sovereign Capability**: Extending the Nervous System beyond the cloud boundary to the physical edge.

### public-datasets-pipelines (`infra/public-datasets-pipelines`)
**Role**: Ralph Loop (Truth Verification).
**Action**:
- Use these pipelines to ingest "Reference Truth" (e.g., public ledgers, census data, scientific datasets).
- **Mechanism**: DataFlow/Beam pipelines that feed into BigQuery, which "Ralph Scholar" queries to verify citations.
- **Sovereignty**: We own the copy of the public truth, preventing downstream censorship or alteration by third parties.

## 5. Nervous System Canon

### pubsub (`infra/pubsub`)
**Role**: The Law of the Mesh.
**Action**:
- This repository contains the canonical implementation details for Google Pub/Sub.
- **Use Case**: Reference for implementing the "VerifiedMesh" protocol on top of standard Pub/Sub (ordering keys, exactly-once delivery, schema enforcement).
- **Core Doc**: Deep dive into the client library internals to optimize `src/gss/kernel.py` throughput.

## Execution Order
1. **Analyze**: Deep dive into `serverless-exec-ruby` lib folder for the execution wrapper logic.
2. **Port**: Create `src/gss/ops/exec.py` implementing the remote execution pattern.
3. **Deploy**: Update `scripts/deploy_gss_worker.py` to include this ops capability.
