# Auth

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Auth subsystem handles **19 routes** and touches: auth, db, email, cache, queue, payment.

## Routes

- `POST` `/verify/{item_id}` params(item_id) → in: FeedRequest, out: FeedResponse [auth, upload]
  `apps/aiyou_stack/aiyou-fastapi-services/aiyou/api.py`
- `POST` `/verify/{certificate_id}` params(certificate_id) → in: ComplianceCertificateRequest, out: ComplianceCertificate [auth, db]
  `apps/aiyou_stack/aiyou-fastapi-services/api/enterprise_compliance_api.py`
- `POST` `/verify` → in: UploadFile, out: AuthenticationResponse [auth, upload]
  `apps/aiyou_stack/aiyou-fastapi-services/shadowtag/api.py`
- `POST` `/endpoint` → in: dic [auth]
  `apps/counselconduit/api/auth.py`
- `GET` `/verify/{token}` params(token) → out: MagicLinkResponse [auth, email]
  `apps/counselconduit/api/magic_link.py`
- `ALL` `/auth/login` [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/auth/verify` [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/auth/recovery` [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/auth/logout` [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/auth/oidc/{provider}/login` params(provider) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/auth/oidc/{provider}/redirect` params(provider) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/auth/oidc/{provider}/redirect/{redirect_path:.*}` params(provider) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/tasks/{task_id}/confirm` params(task_id) [auth, cache, queue, payment]
  `external_repos/semaphore/api/router.go`
- `ALL` `/{user}/{repo}/locks/verify` params(user, repo) [auth, db, upload]
  `libs/cyberpunk_stack/lfs-test-server/server.go`
- `ALL` `/verify/{oid}` params(oid) [auth, db, upload]
  `libs/cyberpunk_stack/lfs-test-server/server.go`
- `GET` `failed to redirect request` [auth, db, upload]
  `libs/cyberpunk_stack/git-lfs/lfsapi/auth.go`
- `GET` `credentials` [auth, db, upload]
  `libs/cyberpunk_stack/git-lfs/lfsapi/auth.go`
- `GET` `token` [auth, db, upload]
  `libs/cyberpunk_stack/git-lfs/lfsapi/auth.go`
- `GET` `warning: current Git remote contains credentials` [auth, db, upload]
  `libs/cyberpunk_stack/git-lfs/lfsapi/auth.go`

## Middleware

- **auth** (auth) — `apps/aiyou-fastapi-services/routers/auth.py`
- **generate_final_report** (auth) — `apps/aiyou_stack/aiyou-fastapi-services/scripts/generate_final_report.py`
- **auth** (auth) — `apps/counselconduit/api/auth.py`
- **attorney_rate_limit** (auth) — `apps/counselconduit/api/middleware/attorney_rate_limit.py`
- **rate_limiter** (auth) — `apps/counselconduit/api/middleware/rate_limiter.py`
- **generate_memory_bank_views** (auth) — `archive/agent_debris/ane_cortex_stack_v9/scripts/generate_memory_bank_views.py`
- **profiling** (auth) — `archive/agent_debris/app/middleware/profiling.py`
- **auth** (auth) — `archive/broken/aiyou_fastapi_src/auth.py`
- **migrateAutoUpdatesToSettings** (auth) — `archive/claude-code-src-leak/src/migrations/migrateAutoUpdatesToSettings.ts`
- **migrateSonnet45ToSonnet46** (auth) — `archive/claude-code-src-leak/src/migrations/migrateSonnet45ToSonnet46.ts`
- **rateLimitMessages** (auth) — `archive/claude-code-src-leak/src/services/rateLimitMessages.ts`
- **auth** (auth) — `archive/claude-code-src-leak/src/utils/auth.ts`
- **authFileDescriptor** (auth) — `archive/claude-code-src-leak/src/utils/authFileDescriptor.ts`
- **authPortable** (auth) — `archive/claude-code-src-leak/src/utils/authPortable.ts`
- **generate_memory_bank_views** (auth) — `control/antigravity/ane_cortex_stack_v10/scripts/generate_memory_bank_views.py`
- **generate_memory_bank_views** (auth) — `control/antigravity/ane_cortex_stack_v9/scripts/generate_memory_bank_views.py`
- **auth_and_build_report** (auth) — `control/legacy_workspaces/archive_brain_sessions/895f9cce-eaec-48b0-be54-aa51a751538a/auth_and_build_report.md`
- **authentication** (auth) — `control/legacy_workspaces/codex/docs/authentication.md`
- **generate-changelog** (auth) — `control/legacy_workspaces/prettier/scripts/generate-changelog.js`
- **Corporate_CLA** (auth) — `control/legacy_workspaces/vexa/CLA/Corporate_CLA.md`
- **strategic-business-integrationmd_1WUns9x_SRl8tnfrNbvg7TZsVHMYhydTI** (auth) — `data/drive_ingest/markdown/strategic-business-integrationmd_1WUns9x_SRl8tnfrNbvg7TZsVHMYhydTI.md`
- **strategic-business-integrationmd_1hnLU6F27939iAGYHkhPfW3G4cpldzxVZ** (auth) — `data/drive_ingest/markdown/strategic-business-integrationmd_1hnLU6F27939iAGYHkhPfW3G4cpldzxVZ.md`
- **[CORE_L2] Watermark_thread__Persisting_Strategic_Vision___PQ** (auth) — `docs/legacy_shadowtag_v2/Strategic_Intelligence/[CORE_L2] Watermark_thread__Persisting_Strategic_Vision___PQ.md`
- **enumerated-tickling-feather** (auth) — `docs/recovered-plans/enumerated-tickling-feather.md`
- **strategic-business-integration** (auth) — `docs/research/strategic-business-integration.md`
- **auth** (auth) — `external_repos/BioAgents/src/middleware/auth.ts`
- **authResolver** (auth) — `external_repos/BioAgents/src/middleware/authResolver.ts`
- **rateLimiter** (auth) — `external_repos/BioAgents/src/middleware/rateLimiter.ts`
- **auth** (auth) — `external_repos/BioAgents/src/routes/auth.ts`
- **auth** (auth) — `external_repos/BioAgents/src/types/auth.ts`
- **authenticated-pages** (auth) — `external_repos/GoogleChrome/lighthouse/docs/authenticated-pages.md`
- **generate_minimatch_dep** (auth) — `external_repos/apps/deno/tools/generate_minimatch_dep.js`
- **generate_types_deno** (auth) — `external_repos/apps/deno/tools/generate_types_deno.ts`
- **generate_metric_compare_strings** (auth) — `external_repos/apps/devtools-frontend/scripts/generate_metric_compare_strings.js`
- **scamguard-malwarebytes_20250608** (auth) — `external_repos/apps/leaked-system-prompts/scamguard-malwarebytes_20250608.md`
- **config-session-strategy-migration.test** (auth) — `external_repos/apps/memory-lancedb-pro/test/config-session-strategy-migration.test.mjs`
- **auth_manager** (auth) — `external_repos/apps/notebooklm-skill/scripts/auth_manager.py`
- **generateDatabaseAdapter** (auth) — `external_repos/apps/payload/test/generateDatabaseAdapter.ts`
- **generate-changelog** (auth) — `external_repos/apps/prettier/scripts/generate-changelog.js`
- **auth_2fa** (auth) — `external_repos/apps/rustdesk/src/auth_2fa.rs`
- **authentication** (auth) — `external_repos/apps/starlette/docs/authentication.md`
- **authentication** (auth) — `external_repos/apps/starlette/starlette/authentication.py`
- **auth** (auth) — `external_repos/cli/lib/utils/auth.js`
- **auth** (auth) — `external_repos/cloud-run-mcp/lib/cloud-api/auth.js`
- **oauth** (auth) — `external_repos/cloud-run-mcp/lib/middleware/oauth.js`
- **auth.spec** (auth) — `external_repos/firebase-tools/src/auth.spec.ts`
- **auth** (auth) — `external_repos/firebase-tools/src/auth.ts`
- **auth-export** (auth) — `external_repos/firebase-tools/src/commands/auth-export.ts`
- **auth-import** (auth) — `external_repos/firebase-tools/src/commands/auth-import.ts`
- **dataconnect-sdk-generate** (auth) — `external_repos/firebase-tools/src/commands/dataconnect-sdk-generate.ts`
- **dataconnect-sql-migrate** (auth) — `external_repos/firebase-tools/src/commands/dataconnect-sql-migrate.ts`
- **auth.spec** (auth) — `external_repos/firebase-tools/src/gcp/auth.spec.ts`
- **auth** (auth) — `external_repos/firebase-tools/src/gcp/auth.ts`
- **authorizer** (auth) — `external_repos/flagger/pkg/loadtester/authorizer.go`
- **auth** (auth) — `external_repos/gcsfuse/internal/auth/auth.go`
- **auth_test** (auth) — `external_repos/gcsfuse/internal/auth/auth_test.go`
- **auth.test** (auth) — `external_repos/google-api-nodejs-client/system-test/auth.test.ts`
- **auth** (auth) — `external_repos/google-api-php-client/docs/auth.md`
- **authenticated-pages** (auth) — `external_repos/lighthouse/docs/authenticated-pages.md`
- **auth** (auth) — `external_repos/mcp-toolbox/internal/auth/auth.go`
- **auth_integration_test** (auth) — `external_repos/mcp-toolbox/tests/auth/auth_integration_test.go`
- **auth** (auth) — `external_repos/mcp-toolbox/tests/auth.go`
- **generate_config_gypi** (auth) — `external_repos/node/tools/generate_config_gypi.py`
- **generate_config_gypi** (auth) — `external_repos/npm/node/tools/generate_config_gypi.py`
- **meta_backend_migrate** (auth) — `external_repos/opentofu/internal/command/meta_backend_migrate.go`
- **meta_backend_migrate_test** (auth) — `external_repos/opentofu/internal/command/meta_backend_migrate_test.go`
- **generate_config** (auth) — `external_repos/opentofu/internal/genconfig/generate_config.go`
- **generate_config_test** (auth) — `external_repos/opentofu/internal/genconfig/generate_config_test.go`
- **generate_config_write** (auth) — `external_repos/opentofu/internal/genconfig/generate_config_write.go`
- **tofumigrate** (auth) — `external_repos/opentofu/internal/tofumigrate/tofumigrate.go`
- **tofumigrate_test** (auth) — `external_repos/opentofu/internal/tofumigrate/tofumigrate_test.go`
- **auth** (auth) — `external_repos/semaphore/api/auth.go`
- **auth_verify** (auth) — `external_repos/semaphore/pro/api/auth_verify.go`
- **auth** (auth) — `external_repos/semaphore/util/mailer/auth.go`
- **auth** (auth) — `libs/cyberpunk_stack/git-lfs/lfsapi/auth.go`
- **auth_test** (auth) — `libs/cyberpunk_stack/git-lfs/lfsapi/auth_test.go`
- **auth-patterns** (auth) — `reference_architectures/agent-assistant/guardrails/auth-patterns.md`
- **injection-defense** (auth) — `reference_architectures/agent-assistant/guardrails/injection-defense.md`
- **auth** (auth) — `reference_architectures/agent-assistant/skills/api-patterns/auth.md`
- **rate-limiting** (auth) — `reference_architectures/agent-assistant/skills/api-patterns/rate-limiting.md`
- **SKILL** (auth) — `reference_architectures/agent-assistant/skills/context-guardian/SKILL.md`
- **SKILL** (auth) — `reference_architectures/agent-assistant/skills/secure-code-guardian/SKILL.md`
- **SKILL** (auth) — `reference_architectures/agent-assistant/skills/tool-use-guardian/SKILL.md`
- **authenticated-pages** (auth) — `reference_architectures/lighthouse/docs/authenticated-pages.md`
- **auth_github_app** (auth) — `scripts/auth_github_app.py`
- **auth_monorepo_push** (auth) — `scripts/auth_monorepo_push.py`
- **auth_setup** (auth) — `scripts/auth_setup.py`
- **generate_ab_variants** (auth) — `scripts/generate_ab_variants.py`
- **generate_assimilation_inventory** (auth) — `scripts/generate_assimilation_inventory.py`
- **generate_memory_bank_views** (auth) — `scripts/generate_memory_bank_views.py`
- **auth** (auth) — `tools/firebase-quickstart-js/auth/exampletokengenerator/auth.ts`
- **auth-state-persistence** (auth) — `tools/firebase-snippets-web/auth/auth-state-persistence.js`
- **auth-state-persistence** (auth) — `tools/firebase-snippets-web/auth-next/auth-state-persistence.js`
- **auth** (auth) — `tools/mcp-toolbox/internal/auth/auth.go`
- **auth_integration_test** (auth) — `tools/mcp-toolbox/tests/auth/auth_integration_test.go`
- **auth** (auth) — `tools/mcp-toolbox/tests/auth.go`
- **generate_token** (auth) — `tools/scripts/generate_token.py`
- **authRoute** (auth) — `external_repos/BioAgents/src/index.ts`
- **authRoutes** (auth) — `external_repos/apps/Gemini-CLI-UI/server/index.js`
- **authenticateToken** (auth) — `external_repos/apps/Gemini-CLI-UI/server/index.js`
- **oauthMiddleware** (auth) — `external_repos/cloud-run-mcp/mcp-server.js`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/aiyou_stack/aiyou-fastapi-services/aiyou/api.py`
- `apps/aiyou_stack/aiyou-fastapi-services/api/enterprise_compliance_api.py`
- `apps/aiyou_stack/aiyou-fastapi-services/shadowtag/api.py`
- `apps/counselconduit/api/auth.py`
- `apps/counselconduit/api/magic_link.py`
- `external_repos/semaphore/api/router.go`
- `libs/cyberpunk_stack/lfs-test-server/server.go`
- `libs/cyberpunk_stack/git-lfs/lfsapi/auth.go`

---
_Back to [overview.md](./overview.md)_
