---
name: Tool Gateway
description: BANS unrestricted mutating shell commands. All destructive OS/Network ops route through packages/tool_gateway.
---

# Tool Gateway

## Prohibition

**Unrestricted mutating shell commands are BANNED.** The following operations MUST NOT be executed directly:

- `rm`, `rm -rf`, `unlink` — Use archive (`mv` to `_archive_*`) per Rule 00
- `sudo` anything — Physically excluded from toolset
- `curl -X POST/PUT/DELETE` to production endpoints — Must route through gateway
- `docker rm`, `docker rmi` — Must use evidence logging
- Raw database mutations without schema verification — Must query schema first

## Mandatory Execution Path

All destructive or mutating operations MUST route through the ToolGateway contract system:

```python
from packages.tool_gateway.gateway import ToolGateway
from packages.tool_gateway.contracts import ToolContract

# Every mutating operation requires a contract
contract = ToolContract(
    tool_name="file_delete",
    risk_level="HIGH",
    requires_evidence=True,
    rollback_path="archive"
)

gateway = ToolGateway()
gateway.execute(contract, target="/path/to/file")
```

### Contract Registry

Located at `packages/tool_gateway/contracts.py`. Contains 39 enforced contracts covering:

- File system mutations (create, delete, move, overwrite)
- Network egress (API calls, webhook triggers, deployments)
- Database operations (schema changes, data mutations)
- Infrastructure changes (Cloud Run deploys, DNS updates)

### Evidence Logging

All gateway executions are logged to `packages/tool_gateway/evidence.py`:

- Timestamp, contract name, target, result, rollback path
- Exported to `.beads/issues.jsonl` for audit trail

## Allowed Direct Operations

The following are SAFE and do NOT require gateway routing:

- `cat`, `ls`, `find`, `grep`, `head`, `tail` — Read-only
- `git status`, `git log`, `git diff` — Read-only git
- `ruff check`, `biome check`, `dart analyze` — Lint/analysis
- `python -m pytest` — Test execution
- `npm run dev`, `npm run build` — Dev/build (non-destructive)

## Detection Pattern

If any agent executes `rm`, `unlink`, `sudo`, or raw production API mutations without ToolGateway, flag as `GATEWAY_BYPASS_VIOLATION` in `.beads/issues.jsonl`.

## Cross-References

- `packages/tool_gateway/gateway.py` — Gateway implementation
- `packages/tool_gateway/contracts.py` — Contract definitions
- `packages/tool_gateway/evidence.py` — Evidence logger
- `.agents/RULE_00_IMMUTABLE_INFRASTRUCTURE.md` — Non-destruction law
- `GEMINI.md` → Tool and Telemetry Posture
