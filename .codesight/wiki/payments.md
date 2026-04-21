# Payments

> **Navigation aid.** Route list and file locations extracted via AST. Read the source files listed below before implementing or modifying this subsystem.

The Payments subsystem handles **7 routes** and touches: auth, payment, email, ai, db, queue.

## Routes

- `POST` `/stripe` [auth, payment]
  `apps/counselconduit/api/stripe_handler.py`
- `POST` `/api/v1/stripe/onboard` → in: MagicLinkRequest, out: dict [auth, email, payment, ai]
  `apps/kovelai/api/main.py`
- `POST` `/api/v1/stripe/webhook` → in: MagicLinkRequest, out: dict [auth, email, payment, ai]
  `apps/kovelai/api/main.py`
- `GET` `/api/v1/stripe/balance/{account_id}` params(account_id) → out: dict [auth, email, payment, ai]
  `apps/kovelai/api/main.py`
- `POST` `/api/v1/stripe/subscribe` → in: MagicLinkRequest, out: dict [auth, email, payment, ai]
  `apps/kovelai/api/main.py`
- `POST` `/api/v1/ingest/webhook` → in: IngestionPayload [auth, db, email, payment]
  `apps/legaltrack/src/legaltrack/main.py`
- `POST` `/webhook/email` → in: EmailWebhookPayload [queue, email, payment]
  `core/lawtrack/services/ingestion.py`

## Middleware

- **corporate_knowledge** (validation) — `apps/aiyou_stack/aiyou-fastapi-services/Doctrine/corporate_knowledge.md`
- **strategic** (validation) — `archive/agent_debris/app/schemas/strategic.py`
- **generate-licenses** (validation) — `control/legacy_workspaces/vercel-skills/scripts/generate-licenses.ts`
- **board_memo_arpa-e_strategy** (validation) — `docs/harvested_from_deleted_user_2/downloads/board_memo_arpa-e_strategy.md`
- **generate_custom_instructions** (validation) — `external_repos/agentsmithy/generate_custom_instructions.py`
- **oss_migrate** (validation) — `external_repos/apps/JamAIBase/scripts/oss_migrate.py`
- **test_generate_docstubs** (validation) — `external_repos/apps/basedpyright/tests/test_generate_docstubs.py`
- **migrate** (validation) — `external_repos/apps/memory-lancedb-pro/src/migrate.ts`
- **guard** (validation) — `external_repos/super-dev/super_dev/guard.py`
- **io-pipeline** (validation) — `reference_architectures/agent-assistant/guardrails/io-pipeline.md`
- **generate-a2a-cards** (validation) — `reference_architectures/agent-assistant/scripts/generate-a2a-cards.js`
- **generate-entry-points** (validation) — `reference_architectures/agent-assistant/scripts/generate-entry-points.js`
- **generate-gallery-data** (validation) — `reference_architectures/agent-assistant/scripts/generate-gallery-data.js`
- **generate-trust-hashes.test** (validation) — `reference_architectures/agent-assistant/scripts/generate-trust-hashes.test.js`
- **generate_hero_videos** (validation) — `scripts/generate_hero_videos.py`
- **validateApiKey** (validation) — `external_repos/apps/Gemini-CLI-UI/server/index.js`

## Source Files

Read these before implementing or modifying this subsystem:
- `apps/counselconduit/api/stripe_handler.py`
- `apps/kovelai/api/main.py`
- `apps/legaltrack/src/legaltrack/main.py`
- `core/lawtrack/services/ingestion.py`

---
_Back to [overview.md](./overview.md)_
