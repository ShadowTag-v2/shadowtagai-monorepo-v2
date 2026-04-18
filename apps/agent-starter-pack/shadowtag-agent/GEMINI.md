# ShadowTag Agent — Coding Guide

> **Project**: `shadowtag-omega-v4`
> **Authorized Runtime Model**: `gemini-3.1-flash-lite-preview-thinking`
> **Agent Framework**: Google ADK
> **Queue Broker**: Google Cloud Tasks (BullMQ BANNED)

---

## Canonical Truth Hierarchy

1. `AGENTS.md` — Constitutional contract (monorepo root)
2. `GEMINI.md` — This file; agent-local operational guide
3. `monorepo_manifest.yaml` — Workspace truth
4. `BUSINESS_CONTEXT_LOCKED.md` — Pricing and architecture truth
5. `RISK_REGISTER.md` — Operational risk truth

---

## Reference Documentation

If ADK skills are available, use those instead of fetching URLs.

- **ADK Cheatsheet**: https://raw.githubusercontent.com/GoogleCloudPlatform/agent-starter-pack/refs/heads/main/agent_starter_pack/resources/docs/adk-cheatsheet.md
- **Evaluation Guide**: https://raw.githubusercontent.com/GoogleCloudPlatform/agent-starter-pack/refs/heads/main/agent_starter_pack/resources/docs/adk-eval-guide.md
- **Deployment Guide**: https://raw.githubusercontent.com/GoogleCloudPlatform/agent-starter-pack/refs/heads/main/agent_starter_pack/resources/docs/adk-deploy-guide.md
- **ADK Docs**: https://google.github.io/adk-docs/llms.txt

---

## Development Phases

### Phase 1: Understand Requirements
Before writing any code, understand the project's requirements, constraints, and success criteria. Use `uphillsnowball_*` tool naming convention for all legal domain tools.

### Phase 2: Build and Implement
Implement agent logic in `app/`. Use `make playground` for interactive testing. All tools must follow the privilege-shield doctrine.

### Phase 3: The Evaluation Loop
Start with 1-2 eval cases, run `make eval`, iterate. Expect 5-10+ iterations.

### Phase 4: Pre-Deployment Tests
Run `make test`. Fix issues until all tests pass.

### Phase 5: Deploy to Dev
**Requires explicit human approval.** Run `make deploy` only after user confirms.

### Phase 6: Production Deployment
Ask user: Option A (single-project) or Option B (full CI/CD with `uvx agent-starter-pack setup-cicd`).

---

## Development Commands

| Command | Purpose |
|---------|---------|
| `make playground` | Interactive local testing |
| `make test` | Run unit and integration tests |
| `make eval` | Run evaluation against evalsets |
| `make eval-all` | Run all evalsets |
| `make lint` | Check code quality |
| `make setup-dev-env` | Set up dev infrastructure (Terraform) |
| `make deploy` | Deploy to dev |

---

## Operational Guardrails

- **Code preservation**: Only modify code directly targeted by the request.
- **NEVER change the model** unless explicitly asked. Use `gemini-3-flash-preview` for agent runtime.
- **Model 404 errors**: Fix `GOOGLE_CLOUD_LOCATION` (use `global`), not the model name.
- **ADK tool imports**: Import the tool instance, not the module.
- **Run Python with `uv`**: `uv run python script.py`. Run `make install` first.
- **Stop on repeated errors**: If the same error appears 3+ times, fix the root cause.
- **Terraform conflicts** (Error 409): Use `terraform import` instead of retrying creation.

---

## ShadowTag-Specific Doctrine

### Tool Naming Convention
All legal domain tools MUST use the `uphillsnowball_` prefix:
- `uphillsnowball_case_intake`
- `uphillsnowball_sanctions_check`
- `uphillsnowball_document_analysis`
- `uphillsnowball_billing_tracker`

### Privilege Shield
All agent interactions are protected under attorney-client privilege. Never log raw client descriptions to unencrypted stores.

### Firestore Integration
Agent state persistence targets the `shadowtag-engine` Firestore database. Use the `google-cloud-firestore` SDK for document operations.

### Deployment Target
- **Cloud Run** on `shadowtag-omega-v4`
- **Region**: `us-central1`
- **Auth**: Workload Identity Federation (WIF) for GitHub Actions CI/CD

### GitHub Doctrine
- SSH is the mandatory transport for push/pull.
- GitHub App JWT is for API operations (PRs, issues, releases) ONLY.
- Repository: `ShadowTag-v2/Monorepo-Uphillsnowball`
