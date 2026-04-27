# Safety Doctrine

## Prohibited
- God Mode inside monorepo
- YOLO mode inside monorepo
- DANGEROUSLY_SKIP_PERMISSIONS
- DISABLE_COMMAND_INJECTION_CHECK
- Unbounded recursive repair loops
- Silent source overwrite
- Direct main pushes without gates
- Inline token minters
- Committed PEM/client_secret paths
- Unmanaged background daemons
- Bulk clone into canonical source
- Treating wiki/vector/SQLite indexes as source truth

## Required
- ToolGateway routing for all mutating actions
- Evidence recording for all significant operations
- Secret scanning before every push
- Bloat gate before every push
- GitHub App token for all automated pushes
