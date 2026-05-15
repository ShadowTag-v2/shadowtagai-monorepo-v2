# KI Artifacts & Codebase Audit Status Report

## 4. GrowthBook Tengu Flag Inventory
The `tengu_*` flags are scattered across `analytics/growthbook.ts` and UI commands. Many map to UI/UX friction logs (`tengu_ultraplan_failed`, etc) and AST parser fallbacks.

## 5. ccleaks Taxonomy Dictionary
Flags mapped in `knowledge/claude-code-audit/codename_flags_crossref.md`:
- `tengu_*`: AST parsing, Security, Telemetry
- `cedar_*`: Context compaction
- `oak_*`: VCR replay mechanisms

## 7. Remaining Pseudo-scripts Audit
Pending full extraction. Key scripts identified include `tengu_malort_pedway` cache overrides and `tengu_frond_boric` sink killswitches.

## 12. bashPermissions.ts Safe Wrapper
Analyzed bash command evaluation gating via AST checks in `packages/agnt_classifier/`.

## 13. BUSINESS_CONTEXT_LOCKED.md
CounselConduit is positioned as an "emotional arbitrage engine" utilizing a Safety-Empathy-Utility (S.E.U.) framework. Enterprise tiers run on isolated GCP sidecars.

## 14. 17 Hidden Features Table
Located in `knowledge/claude-code-audit/services_gate_inventory.md`. Details shadow capabilities and routing heuristics.

## 15. multi-clauding detection in insights.ts
Heuristics use a sliding window via the `willow_multi_clauding_detection` flag to prevent concurrent session state corruption.

## 18. Epistemic Airgapping DLP
Implemented via `ANT_ONLY_SAFE_ENV_VARS` overrides and telemetry sinks, isolating environment variable leaks.

## 19. Remaining Codebase Feature Gates (172+)
Partially documented in the new growthbook_cache layer.

## 21. Current KI Artifacts Status
Artifacts successfully aggregated in `knowledge/claude-code-audit/`.
