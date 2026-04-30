# 02_merge_plan.md — ehanc69 Sub-Repository Merge Plan

> Generated: 2026-04-30 | Workflow: `/merge-56-four-file-proof`

## Summary

| Disposition | Count |
|------------|-------|
| canonical_in_monorepo | 4 |
| queued_for_fold_in | 43 |
| reference_only | 6 |
| archived_after_fold_in | 3 |
| **Total** | **56** |

## Already Canonical (4 repos — No Action)

| Repo | Destination | Notes |
|------|------------|-------|
| shadowtag-omega-v4-fastapi-services | apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services | Primary API. Duplicate family: fastapi-services |
| ehanc69-counselconduit-api | apps/counselconduit | Live Cloud Run service |
| ehanc69-kovelai-frontend | apps/kovelai | Firebase Hosting live |
| ehanc69-shadowtag-agents | apps/aiyou_stack | Agent orchestration |

## Queued for Fold-In (43 repos — Code-Only Import)

These repos are staged for import via `/merge-56-code-only-no-history`. Git history is NOT preserved. Priority ordering: safest first, blocked last.

### Tier 1: Static/Config (safest, no dependencies)

| Repo | Destination | Rationale | Risk |
|------|-----------|-----------|------|
| shadowtag-omega-v4jr-template-2 | apps/templates/ | Static template | None |
| shadowtag-omega-v4-objections-decisions | governance/ | Governance docs | None |
| ehanc69-landing-page-templates | apps/templates/ | Marketing assets | None |
| ehanc69-pitch-deck | docs/pitch/ | Sales docs | None |
| ehanc69-brand-guidelines | docs/brand/ | Brand assets | None |

### Tier 2: Library/Module Code (moderate, needs build check)

All remaining 38 repos follow the same pattern:
- **Next action**: `git clone --depth 1 <repo> && cp -r <src> <dest> && rm -rf <repo>`
- **Duplicate paths to demote**: Any existing code at `<dest>` is renamed to `<dest>.pre-foldin`
- **Rollback**: `git checkout -- <dest>` to restore pre-fold state
- **Risk**: Build breakage if repo has unresolvable dependencies

## Reference-Only (6 repos — No Fold-In)

These repos are kept as external references only.

| Repo | Rationale |
|------|-----------|
| ehanc69-terraform-examples | Reference IaC patterns |
| ehanc69-gcp-samples | GCP SDK examples |
| ehanc69-ml-notebooks | R&D notebooks |
| ehanc69-archived-v3 | Legacy v3 code |
| ehanc69-interview-prep | Non-product |
| ehanc69-personal-site | Non-product |

## Archived After Fold-In (3 repos)

These repos have been folded in and their original GitHub repos should be archived.

| Repo | Folded Into |
|------|------------|
| ehanc69-legal-prompts | apps/counselconduit/prompts/ |
| ehanc69-firestore-rules | config/firestore/ |
| ehanc69-stripe-config | config/stripe/ |

## Blocked Repos

None currently blocked. All 56 repos have assigned destinations.
