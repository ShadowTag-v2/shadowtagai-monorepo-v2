# Antigravity Constitution
<!-- Based on github/spec-kit constitution-template.md -->

## Core Principles

### I. Memory-First Authority
Memory decides what is true. The codebase is what must change.
Load order at every session: authority-current.json → operator_invariants.json → operator_invariants_atoms.json → monorepo_manifest.yaml → fold_in_checklist.yaml. Only then inspect code or run git/GitHub operations.

### II. Zero-CPU Compute
ML/tensor compute routes exclusively to ANE → Metal → Colab. Never local CPU.
M1 Max L2 SRAM budget: 12,582,912 bytes. All ML code must enforce this constraint.

### III. Security-First (NON-NEGOTIABLE)
Every feature ships with the 14-point Security Definition of Done checked.
No custom production auth. No secrets in code, logs, or commits. Validate all inputs at every boundary. Authorization enforced server-side only.

### IV. GitHub App as Control-Plane Truth
GitHub App (ID 3018200, ShadowTag-v2) is the authority for repo freshness and truth.
Local clones are indexed working copies only. SSH is preferred remote. HTTPS repair: `gh auth login && gh auth setup-git`.

### V. Cor.Rules Coding Standards
All code follows `docs/governance/Cor.Rules.md`. Functions ≤50 lines. Components ≤150 lines (mandatory refactor review >300). Atomic Design for design-system layer only. If a rule is broken: `SEC-DEBT: <reason>` comment required.

### VI. Spec-Driven Development
Features start as specs in `.specify/`. Workflow: Constitution → Specify → Plan → Tasks → Implement.
No freelance implementation. No "vibe coding" without a spec.

### VII. Fold-In Discipline
All 56 repos in `fold_in_checklist.yaml` must reach `canonical_in_monorepo` or explicit `reference_only`/`archived_after_fold_in` status. Each fold-in completes all 11 checklist gates before final stamp.

## Compute & Inference Stack

- **ANE**: Stories110M, MIL kernels, primary inference
- **Metal**: fallback for ANE-incompatible shapes
- **Colab**: overflow / large-batch jobs
- **Hydrate-pack API**: `control/antigravity/ane_cortex_stack_v10`, port 8090

## Development Workflow

1. Check `fold_in_checklist.yaml` and active tasks before starting any feature
2. Write spec in `.specify/` using `templates/spec-template.md`
3. Generate plan using `templates/plan-template.md`
4. Break plan into tasks using `templates/tasks-template.md`
5. Implement against the spec; red-team before output
6. Run pre-commit: ruff, eslint, detect-secrets, typecheck, tests
7. PR must pass pnkln-governance CI and Security Definition of Done

## Governance

This Constitution supersedes all other practices.
Amendments require: documentation update + update to `data/memory/operator_invariants.json`.
All PRs must verify compliance with this Constitution.
`docs/governance/Cor.Rules.md` is the operational implementation of this Constitution.

**Version**: 1.0.0 | **Ratified**: 2026-03-21 | **Last Amended**: 2026-03-21
