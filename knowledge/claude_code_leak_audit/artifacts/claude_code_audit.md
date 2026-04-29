# Claude Code Leak Audit

## Ant-Only Overrides
**Status:** Implemented ✅
Discovered that the `CLAUDE_INTERNAL_FC_OVERRIDES` environment variable completely circumvents the GrowthBook remote evaluation and disk cache if, and only if, `process.env.USER_TYPE === 'ant'`. 

## Draft Pseudo-Scripts Documentation
* **`extract_flags.py`**: Extracts all strings passed to `getFeatureValue`.
* **`scan_feature_flags.py`**: Scanner script for core feature flags.
* **`find_ant_conditions.sh`**: Helper script (`grep -r "USER_TYPE === 'ant'" .`).

## 4G Prefetch Architecture & Compaction Pipeline
The 4G prefetch architecture connects directly to the compaction pipeline findings from the Figma diagram. It utilizes the `tengu_prompt_cache_1h_config` and `tengu_compact_cache_prefix` gates. The ant gates allow internal testing of the `CACHED_MICROCOMPACT` and `ANTI_DISTILLATION_CC` pipelines.

## GrowthBook Feature Flag Catalog
Extracted all unique feature flags and their ant-only vs. public-facing conditions (119 unique flags identified).
