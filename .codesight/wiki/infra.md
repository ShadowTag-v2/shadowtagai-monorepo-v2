# Infra

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Infra subsystem handles **16 routes** and touches: auth, db, payment, queue, cache, ai.

## Routes

- `GET` `/health` [auth]
  `apps/aiyou-fastapi-services/main.py`
- `GET` `/` [auth]
  `apps/aiyou_stack/aiyou-fastapi-services/ag_ui_server.py`
- `GET` `/metrics` → out: ComplianceCertificate [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/api/enterprise_compliance_api.py`
- `GET` `/status` → in: dic, out: SwarmVoteResponse [payment]
  `apps/aiyou_stack/aiyou-fastapi-services/api/swarm_endpoint.py`
- `POST` `/` → in: FixRequest, out: FixResponse
  `apps/aiyou_stack/aiyou-fastapi-services/fixer-agent/main.py`
- `GET` `/ready` → out: CodeExecutionResponse [auth, db, queue]
  `apps/aiyou_stack/aiyou-fastapi-services/mcp-validation/mcp_server.py`
- `GET` `/status/{account_id}` params(account_id) → out: ConnectOnboardResponse [auth, payment]
  `apps/counselconduit/api/stripe_connect.py`
- `GET` `/health/ready` → out: DecisionResult [auth, cache]
  `archive/agent_debris/app/main.py`
- `GET` `/status/{job_id}` params(job_id) → out: JobResponse [auth, db, queue, ai]
  `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `POST` `/ping` → in: HelpRequest [auth, queue]
  `core/lawtrack/services/help_on_demand.py`
- `ALL` `/`
  `apps/aiyou_stack/aiyou-fastapi-services/cloud-run-go/main.go`
- `ALL` `/health`
  `apps/aiyou_stack/shield/shield.go`
- `ALL` `/healthz`
  `apps/bennett/edge/main.go`
- `ALL` `/metrics` [auth, payment]
  `external_repos/flagger/pkg/loadtester/server.go`
- `GET` `/sse` [auth, db, cache, queue]
  `external_repos/mcp-toolbox/internal/server/mcp.go`
- `DELETE` `/` [auth, db, cache, queue]
  `external_repos/mcp-toolbox/internal/server/mcp.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou-fastapi-services/main.py`
- `apps/aiyou_stack/aiyou-fastapi-services/ag_ui_server.py`
- `apps/aiyou_stack/aiyou-fastapi-services/api/enterprise_compliance_api.py`
- `apps/aiyou_stack/aiyou-fastapi-services/api/swarm_endpoint.py`
- `apps/aiyou_stack/aiyou-fastapi-services/fixer-agent/main.py`
- `apps/aiyou_stack/aiyou-fastapi-services/mcp-validation/mcp_server.py`
- `apps/counselconduit/api/stripe_connect.py`
- `archive/agent_debris/app/main.py`
- `control/legacy_workspaces/archive_swarm/api_flyingmonkeys_api.py`
- `core/lawtrack/services/help_on_demand.py`
- `apps/aiyou_stack/aiyou-fastapi-services/cloud-run-go/main.go`
- `apps/aiyou_stack/shield/shield.go`
- `apps/bennett/edge/main.go`
- `external_repos/flagger/pkg/loadtester/server.go`
- `external_repos/mcp-toolbox/internal/server/mcp.go`

---
_Back to [overview.md](./overview.md)_
