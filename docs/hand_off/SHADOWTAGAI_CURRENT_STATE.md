# ShadowTagAI — Current State Handoff

> **Status:** Active Development | **Last Updated:** 2026-04-27
> **Project:** `shadowtag-omega-v4` | **Runtime:** Google Cloud

---

## Identity

- **Product Name:** ShadowTagAI (renamed from ShadowTag)
- **PII Status:** Fully sanitized — no personal identifiers in codebase
- **Repo:** `git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git`
- **Branch:** `main`

## Architecture

| Layer              | Technology                                      | Status       |
|--------------------|--------------------------------------------------|--------------|
| Orchestration      | Native Gemini function calling (NOT AutoGen/AG2) | **CANONICAL** |
| Compute            | Cloud Run (current), GKE Autopilot (next)        | LIVE / PLANNED |
| Database           | Firestore                                        | LIVE         |
| Queue              | Google Cloud Tasks                               | LIVE         |
| Auth               | Firebase Auth                                    | LIVE         |
| Hosting            | Firebase Hosting (kovelai, shadowtagai)           | LIVE         |
| CI/CD              | Cloud Build (next)                               | PLANNED      |
| Observability      | Cloud Monitoring, OTel                           | ACTIVE       |

## Deprecated Frameworks

The following are **explicitly deprecated** for ShadowTagAI production orchestration.
A future ADR may reverse any of these, but until then they are not authorized:

- AutoGen / AG2
- LangGraph
- Vertex AI Workbench (for orchestration; Vertex AI API for model calls is fine)
- Any multi-agent framework that wraps Gemini instead of using native function calling

## Production Services

| Service            | URL / Identifier                                              |
|--------------------|--------------------------------------------------------------|
| CounselConduit API | `https://counselconduit-767252945109.us-central1.run.app`    |
| Cloud Run Revision | `counselconduit-00045-kjp`                                   |
| Service Account    | `$COUNSELCONDUIT_SA` (resolved via `scripts/load_mcp_secrets.sh`) |
| KovelAI Site       | `kovelai.web.app`                                            |
| ShadowTagAI Site   | `shadowtagai.web.app`                                        |

## Next Steps (Tracked in Beads)

1. **Cloud Build Trigger:** Create GitHub-connected Cloud Build trigger for ShadowTagAI
   - Use `gcloud builds triggers create github` with:
     - `--repo-owner=ShadowTag-v2`
     - `--repo-name=Monorepo-Uphillsnowball`
     - `--branch-pattern=^main$`
     - `--build-config=cloudbuild.yaml`
     - `--service-account=<deployer-sa>`
     - `--require-approval`
     - `--include-logs-with-status`
   - Reference: [Cloud Build Triggers](https://docs.cloud.google.com/build/docs/triggers)

2. **GKE Autopilot Migration:** Prepare CounselConduit for GKE Autopilot deployment
   - Current: Cloud Run (single container)
   - Target: GKE Autopilot (multi-service, auto-scaling)

3. **Persistent Whiteboard:** Implement agent state tracking via Memory atoms
   - NOT a single JSON silo — fold into `.memory/atoms/` + `.beads/issues.jsonl`

4. **p99 Latency Measurement:** Establish baseline for `/api/v1/governance/decisions`
   - Target: sub-500ms p99

## Preflight Flow

Before any ShadowTagAI work, agents MUST run:

```bash
scripts/antigravity-preflight.sh
scripts/beads-sync.sh
scripts/repo-oracle "ShadowTagAI deploy or governance task"
cat docs/hand_off/SHADOWTAGAI_CURRENT_STATE.md
```

## Function Calling Doctrine

The model proposes structured function calls (name + arguments).
Application code executes only approved functions through ToolGateway.
The model NEVER executes shell commands directly.
All function declarations must be registered and schema-validated.
Evidence is recorded for every function call execution.

See: `tool_contracts/gemini.function_call.yaml`
