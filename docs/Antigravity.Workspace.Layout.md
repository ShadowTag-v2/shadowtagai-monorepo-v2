# pnkln Antigravity Workspace Layout

This is the missing structural layer Antigravity expects: a concrete workspace map, agent lanes, artifact locations, PR batching boundaries, and file ownership zones.

## 1. Canonical top-level layout

```text
pnkln/
├── AGENTS.md
├── README.md
├── package.json
├── pyproject.toml
├── turbo.json
├── pnpm-workspace.yaml
├── tsconfig.base.json
├── .editorconfig
├── .gitignore
├── .gitattributes
├── .cursor/
│   ├── rules/
│   │   └── cor-vibe-coding.mdc
│   └── prompts/
│       ├── all-hands.md
│       ├── security-review.md
│       ├── adversarial-review.md
│       └── reduce-entropy.md
├── .github/
│   ├── pull_request_template.md
│   └── workflows/
│       ├── ci.yml
│       ├── bazel-build.yml
│       └── bazel-test.yml
├── docs/
│   ├── Cor.Constitution.v3.md
│   ├── Antigravity.Workspace.Layout.md
│   ├── Architecture-Map.md
│   ├── Security-Definition-of-Done.md
│   ├── Architecture-Definition-of-Done.md
│   ├── PR-Checklist.md
│   ├── Product/
│   │   ├── Positioning.md
│   │   ├── Strategy.md
│   │   ├── Product-Spec.md
│   │   └── Roadmap.md
│   └── Ops/
│       ├── Decision-Log.md
│       ├── Postmortems/
│       ├── Premortems/
│       └── Release-Runbooks/
├── artifacts/
│   ├── plans/
│   ├── audits/
│   ├── screenshots/
│   ├── repros/
│   ├── perf/
│   └── valuations/
├── manifests/
│   ├── monorepo_manifest.yaml
│   ├── ownership.yaml
│   ├── denied_zones.yaml
│   └── toolchain.yaml
├── apps/
│   ├── web/
│   │   ├── app/
│   │   ├── features/
│   │   ├── components/
│   │   │   ├── atoms/
│   │   │   ├── molecules/
│   │   │   └── organisms/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── policies/
│   │   ├── validation/
│   │   ├── styles/
│   │   └── tests/
│   ├── api/
│   │   ├── src/
│   │   │   ├── routes/
│   │   │   ├── services/
│   │   │   ├── policies/
│   │   │   ├── jobs/
│   │   │   ├── telemetry/
│   │   │   └── security/
│   │   └── tests/
│   ├── worker/
│   │   ├── src/
│   │   └── tests/
│   └── console/
│       ├── src/
│       └── tests/
├── packages/
│   ├── ui/
│   ├── config/
│   ├── sdk/
│   ├── schemas/
│   ├── prompts/
│   ├── telemetry/
│   ├── security/
│   ├── policy-engine/
│   ├── objection-engine/
│   ├── rag/
│   ├── evals/
│   └── shared/
├── services/
│   ├── ingestion/
│   ├── retrieval/
│   ├── classification/
│   ├── routing/
│   └── billing/
├── infra/
│   ├── bazel/
│   ├── terraform/
│   ├── cloud-run/
│   ├── scripts/
│   └── policies/
├── scripts/
│   ├── startup_self_check.sh
│   ├── workspace_guard.py
│   ├── all_hands.py
│   ├── valuation_drill.py
│   ├── rapid_drill.py
│   ├── security_review.py
│   └── reduce_entropy.py
├── data/
│   ├── fixtures/
│   ├── samples/
│   └── eval_sets/
└── tests/
    ├── integration/
    ├── e2e/
    └── smoke/
```

## 2. Antigravity agent lanes

### Lane A — Thread mining and planning

Writes only to:

- `artifacts/plans/`
- `docs/Ops/Decision-Log.md`
- `docs/Architecture-Map.md`

### Lane B — Product and UX

Writes only to:

- `apps/web/`
- `packages/ui/`
- `docs/Product/`

### Lane C — API and jobs

Writes only to:

- `apps/api/`
- `apps/worker/`
- `packages/security/`
- `packages/policy-engine/`

### Lane D — Retrieval, prompts, and evals

Writes only to:

- `packages/rag/`
- `packages/prompts/`
- `packages/evals/`
- `services/ingestion/`
- `services/retrieval/`

### Lane E — Infra and release

Writes only to:

- `infra/`
- `.github/`
- `manifests/`
- `scripts/startup_self_check.sh`

## 3. Required artifacts for major Antigravity runs

Every major run should produce these, with timestamps in filenames when useful:

- `artifacts/plans/current-plan.md`
- `artifacts/audits/security-audit.md`
- `artifacts/audits/architecture-audit.md`
- `artifacts/perf/perf-summary.md`
- `artifacts/valuations/value-impact.md`
- `artifacts/repros/blockers.md`

## 4. Default PR batch order

1. workspace guardrails
2. toolchain and CI
3. prompt registry and doctrine files
4. security and policy engine
5. retrieval and ingestion
6. app shell and shared UI primitives
7. web features
8. worker jobs and telemetry
9. evals and perf tuning
10. docs and release runbooks

## 5. Immediate file set Antigravity can create first

```text
AGENTS.md
.cursor/rules/cor-vibe-coding.mdc
docs/Cor.Constitution.v3.md
docs/Antigravity.Workspace.Layout.md
docs/Architecture-Map.md
docs/Security-Definition-of-Done.md
docs/Architecture-Definition-of-Done.md
docs/PR-Checklist.md
manifests/monorepo_manifest.yaml
manifests/ownership.yaml
manifests/denied_zones.yaml
scripts/startup_self_check.sh
scripts/workspace_guard.py
.github/pull_request_template.md
.github/workflows/ci.yml
```

## 6. Monorepo manifest stub

```yaml
repo_name: pnkln
canonical_root: .
workspace_mode: strict
allow_non_workspace_access: false
allowed_roots:
  - apps
  - packages
  - services
  - infra
  - scripts
  - docs
  - manifests
  - artifacts

denied_zones:
  - archive
  - tools/legacy
  - docs/legacy
  - tmp
  - backups
  - external_clones

entrypoints:
  web: apps/web
  api: apps/api
  worker: apps/worker

quality_gates:
  - lint
  - typecheck
  - unit_tests
  - security_scan
  - secret_scan
```

## 7. Antigravity mission prompt drop-in

```text
MISSION: pnkln workspace sweep
MODE: strict workspace
ROOT: canonical repo only
OBJECTIVE:
- plan small PR batches
- create required artifacts
- obey ownership lanes
- refuse nested repos or off-root edits
- raise objections on security or rollback risk
DELIVERABLES:
- current-plan.md
- security-audit.md
- architecture-audit.md
- blockers.md
```

## 8. Approximate 300-file-equivalent architecture, grouped

This layout is intentionally sparse at the top level and dense in module expansion. Antigravity can fan this out into roughly 300 implementation files across:

- 40–60 web feature files
- 30–50 API/service files
- 20–30 worker and job files
- 25–40 shared package files
- 15–25 infra and CI files
- 20–30 tests and eval files
- 20–30 docs and artifact templates
- 10–20 policy/security files

That is enough structure for immediate PR slicing without creating empty-file theater.
