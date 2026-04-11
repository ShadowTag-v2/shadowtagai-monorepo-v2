import os
import pathlib

ROOT = pathlib.Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")

dirs_to_create = [
    "docs",
    ".vscode",
    ".cursor/rules",
    "apps/counselconduit/spec",
    "labs/uphillsnowball",
    "configs",
    "ops/nginx",
    "ops/audits",
    "scripts"
]

for d in dirs_to_create:
    (ROOT / d).mkdir(parents=True, exist_ok=True)

files = {}

files["monorepo_manifest.yaml"] = """\
version: 1

workspace:
  name: Monorepo-Uphillsnowball
  root: /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball
  policy: latest-only
  source_of_truth: monorepo_manifest.yaml

repo_roots:
  aiyou-fastapi-services:
    status: canonical
    canonical_path: apps/aiyou_stack/aiyou-fastapi-services
    notes: Primary live backend root.

  cosmic-crab-payload:
    status: canonical
    canonical_path: apps/aiyou_stack/cosmic-crab-payload
    notes: Canonical payload/runtime support root.

  Pipeline:
    status: canonical
    canonical_path: apps/aiyou_stack/Pipeline
    notes: Live canonical root for Pipeline.

  nascent-apollo:
    status: canonical
    canonical_path: apps/aiyou_stack/nascent-apollo
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
"""

files["docs/MERGE_STATUS.md"] = """\
# MERGE_STATUS.md

## Status

The four-repo merge is complete at the canonical-root layer once this manifest lands.

### Canonical
- `aiyou-fastapi-services` -> `apps/aiyou_stack/aiyou-fastapi-services`
- `cosmic-crab-payload` -> `apps/aiyou_stack/cosmic-crab-payload`
- `Pipeline` -> `apps/aiyou_stack/Pipeline`
- `nascent-apollo` -> `apps/aiyou_stack/nascent-apollo`

## Meaning

All four shared repos have one declared live canonical root.
There are no unresolved repos remaining in `monorepo_manifest.yaml`.

## Completion rule

A repo counts as fully merged only when:

1. it has exactly one declared canonical live root
2. it is no longer unresolved in `monorepo_manifest.yaml`
3. active tooling points to that canonical root
4. duplicate live roots, backup trees, recovered trees, legacy mirrors, and raw-ingest debris are excluded from live code paths

## Remaining work

Canonicalization of repo roots is complete after the manifest patch lands.

Structural hardening may still remain:
- denied-zone cleanup in live trees
- build / CI hardening
- CODEOWNERS and protected-main enforcement
- shared contracts and `third_party` centralization
- repo-wide refactorability proof

## Strategic note

The highest-value unlock was not more drafting. It was making the monorepo truthful enough that product work, lab work, and agent work stop drifting apart.

- `CounselConduit` is the MVP commercial path.
- `uphillsnowball` is the internal R&D / Apple Silicon path.
- `pnkln` is the operating/control doctrine around them.

## Summary

- 4 canonical
- 0 unresolved
- merge canonicalization complete
"""

files["antigravity-mcp-config.json"] = """\
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
        "curl \\"https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-3.1-flash-lite-preview:streamGenerateContent?key=${API_KEY}\\" -X POST -H \\"Content-Type: application/json\\" -d '{\\"contents\\":[{\\"role\\":\\"user\\",\\"parts\\":[{\\"text\\":\\"Explain how AI works in a few words\\"}]}]}'"
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
"""

files["/Users/pikeymickey/.gemini/antigravity/mcp_config.json"] = """\
{
  "note": "RETIRED. Canonical MCP truth lives in /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity-mcp-config.json. Do not edit this file as a primary config surface."
}
"""

files[".vscode/cline_mcp_settings.json"] = """\
{
  "note": "ADAPTER ONLY. Canonical MCP truth lives in /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/antigravity-mcp-config.json. Mirror from canonical if required by client."
}
"""

files["docs/UPDATED_PNKLN_PACK.md"] = """\
# UPDATED_PNKLN_PACK.md

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
"""

for fname, content in files.items():
    if fname.startswith("/"):
        path = pathlib.Path(fname)
    else:
        path = ROOT / fname
    path.write_text(content, encoding="utf-8")
    print(f"Wrote {path}")
