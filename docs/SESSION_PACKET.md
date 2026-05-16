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
- `apps/pnkln-stack_stack/pnkln-stack-fastapi-services`
- `apps/pnkln-stack_stack/cosmic-crab-payload`
- `apps/pnkln-stack_stack/Pipeline`
- `apps/pnkln-stack_stack/nascent-apollo`

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
4. `docs/UPDATED_pnkln_PACK.md` = survivorship truth
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

## Source: `docs/UPDATED_pnkln_PACK.md`

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
  pnkln-stack-fastapi-services:
    status: canonical
    canonical_path: apps/pnkln-stack_stack/pnkln-stack-fastapi-services
    notes: Primary live backend root.

  cosmic-crab-payload:
    status: canonical
    canonical_path: apps/pnkln-stack_stack/cosmic-crab-payload
    notes: Canonical payload/runtime support root.

  Pipeline:
    status: canonical
    canonical_path: apps/pnkln-stack_stack/Pipeline
    notes: Live canonical root for Pipeline.

  nascent-apollo:
    status: canonical
    canonical_path: apps/pnkln-stack_stack/nascent-apollo
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

- `.vscode/cline_mcp_settings.json`: `False`

## Model mentions
- `monorepo_manifest.yaml:40` -> `gemini-3.1-flash-lite-preview`
- `monorepo_manifest.yaml:47` -> `gemini-3.1-flash-lite-preview`
- `AGENTS.md:19` -> `gemini-3.1-flash-lite-preview`
- `antigravity-mcp-config.json:75` -> `gemini-3.1-flash-lite-preview`
- `antigravity-mcp-config.json:79` -> `gemini-3.1-flash-lite-preview`
- `.vscode/tasks.json:70` -> `gemini-3.1-flash-lite-preview`
- `.vscode/tasks.json:88` -> `gemini-3.1-flash-lite-preview`
- `.vscode/tasks.json:106` -> `gemini-3.1-flash-lite-preview`
- `.vscode/tasks.json:138` -> `gemini-3.1-flash-lite-preview`
- `.vscode/tasks.json:144` -> `gemini-3.1-flash-lite-preview`
- `.vscode/tasks.json:119` -> `gemini-3.1-pro`
- `.vscode/tasks.json:125` -> `gemini-3.1-pro`
- `.vscode/tasks.json:223` -> `gemini-3.1-pro`
- `docs/SESSION_PACKET.md:33` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:230` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:237` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:331` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:335` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:374` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:375` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:376` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:377` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:378` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:379` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:380` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:381` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:382` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:383` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:387` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:388` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:389` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:390` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:391` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:392` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:393` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:394` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:395` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:396` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:397` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:398` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:399` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:400` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:401` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:402` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:403` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:404` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:405` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:406` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:407` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:408` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:409` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:410` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:411` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:412` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:413` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:414` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:415` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:416` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:417` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:418` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:419` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:420` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:421` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:422` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:423` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:424` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:425` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:426` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:427` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:428` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:429` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:430` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:431` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:432` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:433` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:434` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:435` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:436` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:437` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:438` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:439` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:440` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:441` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:442` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:443` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:444` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:445` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:446` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:447` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:448` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:449` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:450` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:451` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:452` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:453` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:454` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:455` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:456` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:457` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:458` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:459` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:460` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:461` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:462` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:463` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:464` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:465` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:466` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:467` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:468` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:469` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:470` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:471` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:472` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:473` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:474` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:475` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:476` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:477` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:478` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:479` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:480` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:481` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:482` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:483` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:484` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:485` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:486` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:487` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:488` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:489` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:490` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:491` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:492` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:493` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:494` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:495` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:496` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:497` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:498` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:499` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:500` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:501` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:502` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:503` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:504` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:505` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:506` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:507` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:508` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:509` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:510` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:511` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:512` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:513` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:514` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:515` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:516` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:517` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:518` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:519` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:520` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:521` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:522` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:523` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:524` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:525` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:526` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:527` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:528` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:529` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:530` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:531` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:532` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:533` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:534` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:535` -> `gemini-3.1-flash-lite-preview`
- `docs/SESSION_PACKET.md:536` -> `gemini-3.1-flash-li
[truncated]
```
