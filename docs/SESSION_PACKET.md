# Session Packet

Use this packet when context is thin. It summarizes the current control plane from repo truth surfaces.

## Mandatory operating order
1. workspace truth
2. MCP truth
3. behavior truth
4. survivorship truth
5. current audit

## Source: `AGENTS.md`

```text
# AGENTS.md

## Mission

Keep the monorepo structurally truthful, Google-native, and latest-only.

## Repo truth

- `monorepo_manifest.yaml` is the canonical workspace truth.
- `antigravity-mcp-config.json` is the canonical MCP truth.
- Historical adapter files are not sources of truth.

## Product split

### counselconduit
- product path: `apps/counselconduit`
- runtime: Google Cloud
- project: `shadowtag-omega-v4`
- model: `gemini-3.1-flash-lite-preview`

### uphillsnowball
- lab path: `labs/uphillsnowball`
- runtime: local Apple Silicon
- purpose: R&D and local experimentation
- must not redefine counselconduit product truth

## Merge truth

All four repo roots must remain canonical:
- `apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services`
- `apps/ShadowTag-v2_stack/cosmic-crab-payload`
- `apps/ShadowTag-v2_stack/Pipeline`
- `apps/ShadowTag-v2_stack/nascent-apollo`

## Guardrails

- never introduce a second source of truth for MCP
- never commit real secrets
- never mark a live repo archived
- never treat duplicate recovered trees as canonical
- fix root truth first, tooling second, runtime third

## Strategic note

Highest-value sequence:
1. truth surfaces
2. recovered operational code
3. commercial MVP hardening
```

## Source: `docs/MEMORY_LOCK.md`

```text
# Memory Lock

## Purpose
This file is the small, durable control-plane memory for the repo.
When live chat context gets thin, agents must recover from this file and the other canonical truth surfaces instead of guessing.

## Canonical truth order
1. `monorepo_manifest.yaml` = workspace truth
2. `antigravity-mcp-config.json` = MCP truth
3. `AGENTS.md` = agent behavior truth
4. `docs/UPDATED_PNKLN_PACK.md` = survivorship truth
5. `docs/SESSION_PACKET.md` = current compact operating packet

## Product split
- `apps/counselconduit` = Google-native product path
- `labs/uphillsnowball` = local Apple Silicon lab path
- product truth must not be redefined by local-lab experiments

## Recovery rules
- never create a second source of truth
- never inline secrets into tracked config
- prefer latest-only artifacts over historical duplicates
- when uncertain, regenerate `docs/SESSION_PACKET.md` and `docs/RECOVERY_PACKET.md`
- when drift is detected, fix truth surfaces before feature work

## Required startup sequence
1. run `scripts/root_guard.sh`
2. run `scripts/memory_lock_audit.py --repo-root .`
3. run `scripts/rebuild_context_packet.py --repo-root . --write`
4. read `docs/SESSION_PACKET.md`
5. only then begin implementation

## Thin-context fallback
If context is weak or memory appears lost:
- stop drafting new architecture
- regenerate the packets
- compare canonical files against adapters and retired files
- continue only from evidence in repo files or verified external sources
```

## Source: `docs/UPDATED_PNKLN_PACK.md`

```text
# UPDATED_pnkln_PACK.md

## Canonical surviving files

### Control plane
- `monorepo_manifest.yaml`
- `docs/MERGE_STATUS.md`
- `antigravity-mcp-config.json`

### Demoted adapters
- `/Users/pikeymickey/.gemini/antigravity/mcp_config.json`
- `.vscode/cline_mcp_settings.json`

### Product env templates
- `apps/counselconduit/.env.example`
- `labs/uphillsnowball/.env.example`

### Runtime support
- `database_tools.yaml`
- `scripts/verify_mcp.sh`
- `scripts/pnkln_lancedb.py`
- `scripts/pnkln_root_guard.sh`
- `scripts/green_loop.py`
- `scripts/drive_ingest_daemon.py`
- `scripts/retriever_eval.py`
- `scripts/ocr_summary_ingest.py`

### Product and lab support
- `configs/feature_flags.yaml`
- `apps/counselconduit/spec/MVP.md`
- `apps/counselconduit/spec/PRICING.md`
- `apps/counselconduit/spec/VALUATION.md`
- `ops/nginx/csp_collector.conf`
- `ops/audits/third_party_inventory.md`

### Operator guidance
- `AGENTS.md`
- `docs/Cor.Constitution.v3.md`
- `.cursor/rules/cor-vibe-coding.mdc`

## What this pack supersedes

This pack supersedes:
- historical duplicate MCP config surfaces as sources of truth
- unresolved four-repo merge claims
- older partial pnkln pack drafts
- stale cross-thread MCP snippets
- non-canonical repo-root interpretations
- repeated doctrine-only drafts that were not backed by operational files

## Strategic recovery

### Highest-value missed opportunity 1
You already have enough recovered material to make `counselconduit` commercially coherent and `uphillsnowball` technically useful, but the repo still lacked a single truthful backbone. Fixing truth surfaces first unlocks everything else.

### Highest-value missed opportunity 2
Operationalize recovered code instead of redrafting it again:
- green loop
- CSP collector
- retriever eval
- feature flags
- pricing model
- OCR summaries
- Drive-ingest daemon

### Highest-value missed opportunity 3
The recovered CounselConduit blueprint is already stronger than later wandering branches. It should become the business-facing spec while `pnkln/uphillsnowball` remains the internal engine.

## Current truth

- four repos are canonical once the manifest patch lands
- one MCP config is canonical
- all secrets belong in `.env`
- `counselconduit` is the Google-native MVP product path
- `uphillsnowball` is the local Apple Silicon lab path
```

## Source: `monorepo_manifest.yaml`

```text
version: 1

workspace:
  name: Monorepo-Uphillsnowball
  root: /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball
  policy: latest-only
  source_of_truth: monorepo_manifest.yaml

repo_roots:
  ShadowTag-v2-fastapi-services:
    status: canonical
    canonical_path: apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services
    notes: Primary live backend root.

  cosmic-crab-payload:
    status: canonical
    canonical_path: apps/ShadowTag-v2_stack/cosmic-crab-payload
    notes: Canonical payload/runtime support root.

  Pipeline:
    status: canonical
    canonical_path: apps/ShadowTag-v2_stack/Pipeline
    notes: Live canonical root for Pipeline.

  nascent-apollo:
    status: canonical
    canonical_path: apps/ShadowTag-v2_stack/nascent-apollo
    notes: Live canonical root for nascent-apollo.

control_plane:
  canonical_mcp_config: /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity-mcp-config.json
  deprecated_mcp_configs:
    - /Users/pikeymickey/.gemini/antigravity/mcp_config.json
    - /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/.vscode/cline_mcp_settings.json

products:
  counselconduit:
    root: apps/counselconduit
    runtime: google-cloud
    model: gemini-3.1-flash-lite-preview
    project: shadowtag-omega-v4
    business_role: mvp-commercial-wedge

  uphillsnowball:
    root: labs/uphillsnowball
    runtime: local-apple-silicon
    model: gemini-3.1-flash-lite-preview
    project: shadowtag-omega-v4
    business_role: internal-rd-lab

completion_rule:
  canonicalization_complete_when:
    - all_target_repos_have_status_canonical_or_archived
    - no_repo_has_status_unresolved
    - control_plane_has_single_canonical_mcp_config
    - deprecated_mcp_configs_are_demoted

highest_value_opportunities:
  - "Fix truth surfaces first: canonical repo roots and one canonical MCP control plane."
  - "Operationalize recovered code: green loop, CSP collector, retriever eval, feature flags, pricing model, OCR summaries, Drive-ingest daemon."
  - "Make CounselConduit the business-facing MVP spec; keep pnkln/uphillsnowball as the internal engine."
```

## Source: `antigravity-mcp-config.json`

```text
{
  "mcp": {
    "startupTimeoutMs": 60000,
    "toolTimeoutMs": 120000,
    "retryCount": 2
  },
  "mcpServers": {
    "stitch-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://stitch.googleapis.com/mcp",
        "--header",
        "X-Goog-Api-Key: ${STITCH_API_KEY}"
      ]
    },
    "developer-knowledge-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://developers.google.com/knowledge/mcp",
        "--header",
        "X-Goog-Api-Key: ${DEVELOPER_KNOWLEDGE_API_KEY}"
      ]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    },
    "dart-mcp-server": {
      "command": "dart",
      "args": [
        "mcp-server"
      ]
    },
    "mcp-toolbox-for-databases": {
      "command": "npx",
      "args": [
        "-y",
        "@toolbox-sdk/server@0.26.0",
        "--tools-file=/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/database_tools.yaml",
        "--stdio",
        "--user-agent-metadata",
        "antigravity"
      ]
    },
    "firebase-mcp-server": {
      "command": "npx",
      "args": [
        "-y",
        "firebase-tools@latest",
        "experimental:mcp",
        "--project",
        "shadowtag-omega-v4"
      ],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/Users/pikeymickey/.config/gcloud/application_default_credentials.json"
      }
    },
    "chrome-devtools-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest"
      ]
    }
  },
  "commands": {
    "gemini-31-flash-lite-preview-stream": {
      "description": "Direct gemini-3.1-flash-lite-preview streaming test via Google AI Platform API key",
      "command": "bash",
      "args": [
        "-lc",
        "curl \"https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-3.1-flash-lite-preview:streamGenerateContent?key=${API_KEY}\" -X POST -H \"Content-Type: application/json\" -d '{\"contents\":[{\"role\":\"user\",\"parts\":[{\"text\":\"Explain how AI works in a few words\"}]}]}'"
      ]
    },
    "pnkln-lancedb-smoke-test": {
      "description": "Run local LanceDB smoke test on Apple Silicon",
      "command": "bash",
      "args": [
        "-lc",
        "python3 /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/scripts/pnkln_lancedb.py --smoke-test"
      ]
    }
  }
}
```

## Source: `docs/AUDIT_REPORT.md`

```text
# Audit Report

- repo_root: `/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball`

- status: `pass`

- preferred_model_family: `gemini-3.1-family`

## Missing canonical files

None.

## MCP file presence

- `antigravity-mcp-config.json`: `True`

- `mcp_config.json`: `False`

- `.vscode/cline_mcp_settings.json`: `True`

## Model mentions
- `memory_lock.json:5` → `gemini-3.1-family`
- `memory_lock.json:19` → `gemini-3.1-family`
- `CHANGELOG.md:452` → `gemini-2.5`
- `generate_pnkln_pack.sh:143` → `gemini-2.5`
- `monorepo_manifest.yaml:40` → `gemini-3.1-flash-lite-preview`
- `monorepo_manifest.yaml:47` → `gemini-3.1-flash-lite-preview`
- `antigravity-mcp-config.json:75` → `gemini-3.1-flash-lite-preview`
- `antigravity-mcp-config.json:79` → `gemini-3.1-flash-lite-preview`
- `memory_lock.ShadowTag-v2-stack.json:4` → `gemini-3.1-family`
- `AGENTS.md:19` → `gemini-3.1-flash-lite-preview`
- `operator_invariants.json:9` → `gemini-3.1-flash-lite-preview`
- `operator_invariants.json:9` → `gemini-3.1-pro`
- `labs/uphillsnowball/.env.example:5` → `gemini-3.1-flash-lite-preview`
- `labs/uphillsnowball/UPHILL_SNOWBALL_MVP_SPEC.md:8` → `gemini-3.1-flash-lite-preview`
- `labs/uphillsnowball/UPHILL_SNOWBALL_MVP_SPEC.md:42` → `gemini-3.1-flash-lite-preview`
- `drive_knowledge/documents/db11b99e62dae2517e9acfd31d8a1863.txt:17` → `gemini-3.1-family`
- `drive_knowledge/documents/db11b99e62dae2517e9acfd31d8a1863.txt:18` → `gemini-3.1-family`
- `drive_knowledge/documents/Building_Generative_AI_Services_with_FastAPI____Al.txt:12615` → `gemini-3.1-family`
- `drive_knowledge/documents/text_46_txt.txt:48` → `gemini-3.1-family`
- `drive_knowledge/documents/text_47_txt.txt:50` → `gemini-3.1-family`
- `drive_knowledge/documents/pnkln_vertex_rollup_txt.txt:17` → `gemini-3.1-family`
- `drive_knowledge/documents/pnkln_vertex_rollup_txt.txt:18` → `gemini-3.1-family`
- `pnkln/core/judge_six_pipeline.py:100` → `gemini-3.1-flash-lite-preview`
- `pnkln/agents/__init__.py:7` → `gemini-3.1-flash-lite-preview`
- `pnkln/agents/__init__.py:7` → `gemini-3.1-pro`
- `pnkln/agents/orchestrator.py:32` → `gemini-3.1-flash-lite-preview`
- `pnkln/agents/orchestrator.py:462` → `gemini-3.1-flash-lite-preview`
- `pnkln/agents/orchestrator.py:33` → `gemini-3.1-pro`
- `pnkln/agents/orchestrator.py:463` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/Cor.86/Cor.86.txt:13` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/Cor.86/Cor.86.txt:14` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/Cor.86/Cor.86.txt:18` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/Cor.86/Cor.86.txt:155` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/Cor.86/Cor.86.txt:160` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/Cor.86/Cor.86.txt:202` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/“# 📊 COR.100: PNKLN AS AI-NATIVE FAANG/“# 📊 COR.100: PNKLN AS AI-NATIVE FAANG.txt:2801` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/“# 📊 COR.100: PNKLN AS AI-NATIVE FAANG/“# 📊 COR.100: PNKLN AS AI-NATIVE FAANG.txt:2808` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/“# 📊 COR.100: PNKLN AS AI-NATIVE FAANG/“# 📊 COR.100: PNKLN AS AI-NATIVE FAANG.txt:2833` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/stop, drop, then roll all this together in. here.  this is what i…/stop, drop, then roll all this together in. here.  this is what i….txt:1321` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/Cor.95   ⏺ All three tasks complete! Here's the summary:/Cor.95   ⏺ All three tasks complete! Here's the summary:.txt:133` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/Cor.95   ⏺ All three tasks complete! Here's the summary:/Cor.95   ⏺ All three tasks complete! Here's the summary:.txt:160` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/Cor.95   ⏺ All three tasks complete! Here's the summary:/Cor.95   ⏺ All three tasks complete! Here's the summary:.txt:174` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/Cor.95   ⏺ All three tasks complete! Here's the summary:/Cor.95   ⏺ All three tasks complete! Here's the summary:.txt:256` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/Cor.95   ⏺ All three tasks complete! Here's the summary:/Cor.95   ⏺ All three tasks complete! Here's the summary:.txt:270` → `gemini-3.1-pro`
- `artifacts/workspace_archive/icloud_notes/COR 90/COR 90.txt:16` → `gemini-3.1-pro`
- `artifacts/brain/legacy_archive/OMEGA_LATEST_STATE.md:149` → `gemini-2.5`
- `artifacts/brain/legacy_archive/OMEGA_LATEST_STATE.md:397` → `gemini-2.5`
- `artifacts/brain/legacy_archive/OMEGA_LATEST_STATE.md:406` → `gemini-2.5`
- `artifacts/brain/legacy_archive/OMEGA_LATEST_STATE.md:420` → `gemini-2.5`
- `artifacts/brain/legacy_archive/OMEGA_LATEST_STATE.md:521` → `gemini-2.5`
- `artifacts/brain/legacy_archive/OMEGA_LATEST_STATE.md:682` → `gemini-2.5`
- `artifacts/brain/legacy_archive/OMEGA_LATEST_STATE.md:1006` → `gemini-2.5`
- `artifacts/brain/legacy_archive/OMEGA_LATEST_STATE.md:1008` → `gemini-2.5`
- `artifacts/brain/legacy_archive/OMEGA_LATEST_STATE.md:1236` → `gemini-2.5`
- `artifacts/brain/legacy_archive/OMEGA_LATEST_STATE.md:1242` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260324-004727.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260324-201726.md:5` → `gemini-3.1-flash-lite-preview`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-050313.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-194307.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260322-071336.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-053513.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-050449.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260322-080534.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260322-071513.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260322-075620.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260324-003855.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-092348.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-232018.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260324-201428.md:5` → `gemini-3.1-flash-lite-preview`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260324-174013.md:5` → `gemini-3.1-flash-lite-preview`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260322-220406.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260324-173520.md:5` → `gemini-3.1-flash-lite-preview`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260322-080542.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260324-005644.md:5` → `gemini-3.1-flash-lite-preview`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-101144.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-041217.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260322-232703.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-040906.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-052658.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260324-174139.md:5` → `gemini-3.1-flash-lite-preview`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-193411.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-092142.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-041418.md:5` → `gemini-2.5`
- `artifacts/Claude_Code_6-reports/Claude_Code_6-20260323-041838.md:5` → `gemini-2.5`
- `transcripts/antigravity_session_2025-11-29_mcp_integration.md:157` → `gemini-2.5`
- `transcripts/antigravity_session_2025-11-29_mcp_integration.md:192` → `gemini-2.5`
- `transcripts/antigravity_session_2025-11-29_mcp_integration.md:193` → `gemini-2.5`
- `transcripts/antigravity_session_2025-11-29_mcp_integration.md:194` → `gemini-2.5`
- `transcripts/antigravity_session_2025-11-29_mcp_integration.md:195` → `gemini-2.5`
- `tools/external_sdks/generative-ai/.gemini/styleguide.md:127` → `gemini-2.5`
- `tools/external_sdks/generative-ai/.gemini/styleguide.md:128` → `gemini-2.5`
- `tools/external_sdks/generative-ai/.gemini/styleguide.md:137` → `gemini-2.5`
- `tools/external_sdks/generative-ai/.gemini/styleguide.md:137` → `gemini-2.5`
- `tools/external_sdks/generative-ai/.gemini/styleguide.md:126` → `gemini-3.1-pro`
- `tools/external_sdks/generative-ai/tools/llmevalkit/pages/1_Prompt_Management.py:377` → `gemini-2.5`
- `tools/external_sdks/generative-ai/tools/llmevalkit/pages/1_Prompt_Management.py:378` → `gemini-2.5`
- `tools/external_sdks/generative-ai/tools/llmevalkit/pages/3_Evaluation.py:778` → `gemini-2.5`
- `tools/external_sdks/generative-ai/tools/llmevalkit/pages/3_Evaluation.py:779` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/function-calling/sql-talk-app/app.py:11` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/agents/always-on-memory-agent/agent.py:38` → `gemini-3.1-flash-lite-preview`
- `tools/external_sdks/generative-ai/gemini/mcp/mcp_orchestration_app/src/gemini_server.py:326` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/mcp/adk_mcp_app/main.py:39` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/mcp/adk_multiagent_mcp_app/main.py:21` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/use-cases/entity-extraction/config.json:6` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/use-cases/entity-extraction/config.json:18` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/use-cases/entity-extraction/config.json:31` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/use-cases/entity-extraction/README.md:214` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/use-cases/entity-extraction/README.md:237` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-mesop-cloudrun/main.py:56` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-streamlit-cloudrun/app.py:41` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-streamlit-cloudrun/app.py:42` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-streamlit-cloudrun/app.py:43` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-streamlit-cloudrun/app.py:48` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-streamlit-cloudrun/app.py:49` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-streamlit-cloudrun/app.py:50` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-hallcheck/README.md:48` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-hallcheck/README.md:54` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-hallcheck/README.md:90` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-hallcheck/src/gemhall/judge_llm.py:4` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-hallcheck/src/gemhall/runner.py:56` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-hallcheck/src/gemhall/runner.py:121` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-hallcheck/src/gemhall/cli.py:23` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-hallcheck/src/gemhall/cli.py:24` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-hallcheck/src/gemhall/cli.py:24` → `gemini-2.5`
- `tools/external_sdks/generative-ai/gemini/sample-apps/gemini-hallcheck/src/gemhall/eval.py:257` → `gemini-2.5`
- `tools/external_sdks/generative-ai/vision/sample-apps/V-Start/server.js:127` → `gemini-2.5`
- `tools/external_sdks/generative-ai/vision/sample-apps/V-Start/server.js:167` → `gemini-2.5`
- `tools/external_sdks/generative-ai/vision/sample-apps/V-Start/README.md:31` → `gemini-2.5`
- `tools/external_sdks/generative-ai/search/retrieval-augmented-generation/rag_with_dual_llms/src/vertex_rag_demo_dual_llms_with_judge.py:62` → `gemini-2.
[truncated]
```
