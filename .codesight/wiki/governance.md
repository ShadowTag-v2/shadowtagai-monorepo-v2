# Governance

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Governance subsystem handles **14 routes** and touches: auth, db, queue, ai.

## Routes

- `POST` `/assess` → in: GovernanceAssessmentRequest, out: GovernanceAssessmentResponse [auth]
  `app/api/v1/governance.py`
- `POST` `/eu-ai-act/assess` → in: GovernanceAssessmentRequest, out: GovernanceAssessmentResponse [auth]
  `app/api/v1/governance.py`
- `POST` `/nist-rmf/assess` → in: GovernanceAssessmentRequest, out: GovernanceAssessmentResponse [auth]
  `app/api/v1/governance.py`
- `POST` `/iso-42001/assess` → in: GovernanceAssessmentRequest, out: GovernanceAssessmentResponse [auth]
  `app/api/v1/governance.py`
- `GET` `/frameworks` → out: GovernanceAssessmentResponse [auth]
  `app/api/v1/governance.py`
- `GET` `/risk-levels` → out: GovernanceAssessmentResponse [auth]
  `app/api/v1/governance.py`
- `POST` `/assess/batch` → in: GovernanceAssessmentRequest, out: GovernanceAssessmentResponse [auth]
  `app/api/v1/governance.py`
- `POST` `/v1/governance/evaluate` → in: MissionRequest, out: GovernanceResponse [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/src/main.py`
- `GET` `/api/governance/workflow-harness` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/api/governance/harnesses` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/api/governance/operational-harness` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/api/governance/timeline` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/api/governance/framework-harness` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`
- `GET` `/api/governance/hook-harness` → out: PipelinePolicyResponse [auth, db, queue, ai]
  `external_repos/super-dev/super_dev/web/api.py`

## Source Files

Read these before implementing or modifying this subsystem:
- `app/api/v1/governance.py`
- `apps/aiyou_stack/aiyou-fastapi-services/src/main.py`
- `external_repos/super-dev/super_dev/web/api.py`

---
_Back to [overview.md](./overview.md)_