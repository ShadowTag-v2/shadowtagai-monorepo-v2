---
description: Prepare ShadowTagAI Cloud Build/GKE deployment without blind deploys.
---

# /shadowtagai-deploy-preflight

## Goal

Prepare ShadowTagAI Cloud Build or GKE deployment with full verification.
Never blind deploy.

## Steps

1. Load `docs/hand_off/SHADOWTAGAI_CURRENT_STATE.md`
2. Verify project, repo, branch, and `cloudbuild.yaml` exist and are current.
3. Verify no deprecated architecture references are active:
   - No AutoGen / AG2 imports
   - No LangGraph references in production paths
   - No Vertex AI Workbench orchestration
4. Run tests relevant to the deploy target.
5. Measure p99 latency baseline if governance endpoints are involved.
6. If creating a Cloud Build trigger:
   - Use explicit service account (`--service-account`)
   - Require approval for production (`--require-approval`)
   - Include logs with status (`--include-logs-with-status`)
   - Specify branch pattern (`--branch-pattern=^main$`)
   - Reference: `gcloud builds triggers create github`
7. Run `scripts/firebase-ai-logic-preflight.sh` if AI Logic features are touched.
8. Write evidence via `scripts/record-agent-event.sh`.
9. Create Beads update with deploy status.

## Cloud Build Trigger Template

```bash
gcloud builds triggers create github \
  --repo-owner=ShadowTag-v2 \
  --repo-name=Monorepo-Uphillsnowball \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml \
  --service-account="$DEPLOYER_SA" \
  --require-approval \
  --include-logs-with-status \
  --region=us-central1
```

## Rules

- No blind deploys
- No preview models in production without a flag
- Evidence is mandatory
- Rollback plan must exist before production deploy
