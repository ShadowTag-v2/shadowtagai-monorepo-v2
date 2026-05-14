# AGENTS.md

## Mission

Keep the workspace structurally truthful, migration-safe, and commercially useful.

## Canonical truth surfaces

- Workspace truth: `monorepo_manifest.yaml`
- MCP truth: `antigravity-mcp-config.json`
- Review truth: `REVIEW.md`
- Agent behavior truth: `AGENTS.md`

Do not create a second source of truth.

## Product split

### counselconduit
- business-facing product path
- Google-native runtime
- production-oriented defaults

### uphillsnowball
- Apple Silicon / local R&D path
- experiments, evals, retrieval, hardware-adjacent work
- not the product control plane

## Model policy

Use current supported Google model IDs only.
Preferred defaults:
- `gemini-2.5-pro`
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`

Do not reintroduce deprecated or stale thread-era model names. Gemini Code Assist uses Gemini 2.5 for chat, generation, and transformation.

## Migration policy

Before any destructive move:
1. inventory
2. dry-run plan
3. snapshot / backup
4. execute bounded move
5. verify imports, scripts, Dockerfiles, and build targets
6. present diff summary

Never perform broad migration as an unreviewed one-shot mutation.

## Git policy

- No repo creation.
- No forking.
- Work only in approved repos and approved branches.
- Keep PRs single-purpose and reviewable.

## Refactor policy

- Split by concern, not line-count theater.
- Extract stateful logic into hooks.
- Avoid unrelated churn.
- Preserve behavior unless the task explicitly changes behavior.

## Security policy

- No inline secrets.
- No fake default production secrets.
- Use `.env.example` for shape only.
- Minimize retention.
- Avoid sensitive logs by default.

Gemini Code Assist custom command library

Google documents Gemini Code Assist custom commands in the IDE, including VS Code settings for defining named reusable prompts.

Use these as copy-paste command values.

/plan-refactor

Write a concise implementation plan for the current task.
Rules:
- Preserve behavior unless explicitly told otherwise.
- Prefer small, reviewable diffs.
- Split by concern, not arbitrary line count.
- List files to change, risks, tests, and rollback.
Stop after the plan.

/refactor-monolith

Refactor the current file by natural boundaries only.
Rules:
- Prefer components under 150 lines, but do not split purely to meet a number.
- Extract stateful logic into custom hooks.
- Separate UI from business logic.
- Preserve external behavior and public interfaces unless explicitly told otherwise.
- Do not touch unrelated files.
Return:
1. proposed file tree
2. rationale for each split
3. exact edits

/purge-yolo

Audit the selected files for:
- unused imports
- dead code
- weak typing
- unsafe defaults
- TODO / placeholder logic
Propose the smallest safe cleanup patch.
Do not invent dependencies.
Do not broaden scope.

/migration-dry-run

Plan a migration from the old path layout to the monorepo target layout.
Rules:
- no destructive actions
- produce inventory first
- identify import rewrites, Dockerfile changes, script path changes, build changes
- generate a dry-run mapping and a rollback plan
Stop before execution.

/security-pass

Review the current diff as a security engineer.
Check:
- secrets
- authz/authn assumptions
- CORS
- redirect validation
- webhook verification
- storage access boundaries
- log leakage
- migration/destructive-command safety
Classify findings as:
🔴 Normal
🟡 Nit
🟣 Pre-existing

/accept-ready-stop

Before suggesting large code changes:
- verify the scope
- verify the target files
- verify no second source of truth is being introduced
- prefer one bounded patch
Then stop and present the patch summary first.
