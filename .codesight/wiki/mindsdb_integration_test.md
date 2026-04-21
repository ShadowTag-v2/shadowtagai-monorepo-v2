# Mindsdb_integration_test

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Mindsdb_integration_test subsystem handles **2 routes** and touches: auth, db.

## Routes

- `POST` `http://127.0.0.1:5000/api/tool/my-exec-sql-tool/invoke` params(5000) [auth, db]
  `external_repos/mcp-toolbox/tests/mindsdb/mindsdb_integration_test.go`
- `POST` `http://127.0.0.1:5000/api/tool/my-auth-exec-sql-tool/invoke` params(5000) [auth, db]
  `external_repos/mcp-toolbox/tests/mindsdb/mindsdb_integration_test.go`

## Source Files

Read these before implementing or modifying this subsystem:
- `external_repos/mcp-toolbox/tests/mindsdb/mindsdb_integration_test.go`

---
_Back to [overview.md](./overview.md)_