import os
import pathlib

ROOT = pathlib.Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")

files = {}

files["scripts/raw_links.txt"] = """\
https://github.com/lancedb/lancedb
https://github.com/ollama/ollama-python
https://github.com/vinta/awesome-python
https://developers.googleblog.com/introducing-the-developer-knowledge-api-and-mcp-server/
https://developers.google.com/knowledge/mcp
https://stitch.googleapis.com/mcp
https://developers.google.com/knowledge/mcp
https://aiplatform.googleapis.com/v1/publishers/google/models/gemini-3.1-flash-lite-preview:streamGenerateContent
https://github.com/vercel-labs/agent-skills
https://github.com/REPOZY/superpowers-optimized
https://arxiv.org/pdf/2512.14982
"""

files["apps/counselconduit/spec/MVP.md"] = """\
# CounselConduit MVP

CounselConduit is the business-facing MVP.

## Wedge
Stateless legal SaaS workflow with premium pricing and BYOK routing.

## Product principles
- Google-native runtime
- fast onboarding
- premium SaaS economics
- low implementation friction
- high-trust summaries and retrieval

## Internal dependency
pnkln / uphillsnowball powers internal retrieval, eval, and experimentation.
"""

files["apps/counselconduit/spec/PRICING.md"] = """\
# CounselConduit pricing

## Position
Premium SaaS pricing aligned just below enterprise legal pain thresholds.

## Commercial logic
- faster turnaround
- lower internal legal handling time
- clean upgrade path
- BYOK lowers buyer friction

## Next step
Wire pricing assumptions into a live calculator backed by retriever-eval and usage telemetry.
"""

files["apps/counselconduit/spec/VALUATION.md"] = """\
# CounselConduit valuation

## Narrative
CounselConduit is the commercial wedge.
pnkln / uphillsnowball is the internal engine.

## Why this matters
This separation lets the business story stay simple while the technical engine compounds in the background.

## Leverage
- product clarity
- internal tooling leverage
- cheaper experimentation
- stronger defensibility
"""

files["AGENTS.md"] = """\
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
- `apps/aiyou_stack/aiyou-fastapi-services`
- `apps/aiyou_stack/cosmic-crab-payload`
- `apps/aiyou_stack/Pipeline`
- `apps/aiyou_stack/nascent-apollo`

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
"""

files["docs/Cor.Constitution.v3.md"] = """\
# Cor.Constitution.v3

## Core posture

Operate with disciplined, high-signal execution.
Prefer one source of truth per layer.
Prefer canonical roots over copied ambiguity.
Prefer automation over prose where possible.

## Canonical order

1. workspace truth
2. merge truth
3. MCP truth
4. runtime truth
5. product hardening

## Security

- all API tokens live in `.env`
- no secret material in committed JSON
- local adapters may exist, but must not become truth surfaces

## Product split

### counselconduit
Google-native MVP path.
Built for production readiness.

### uphillsnowball
Local Apple Silicon research path.
Used to improve internal methods and experimentation.
Not the product control plane.

## Non-negotiables

- `monorepo_manifest.yaml` is canonical workspace truth
- `antigravity-mcp-config.json` is canonical MCP truth
- all four repos remain live canonical roots
- no unresolved repo root may remain in steady state

## Highest-value missed opportunities

1. Truth surfaces first.
2. Recovered code second.
3. Commercial MVP clarity third.
"""

files[".cursor/rules/cor-vibe-coding.mdc"] = """\
---
description: pnkln canonical workspace and execution rules
globs: ["**/*"]
---

# pnkln rules

- Treat `monorepo_manifest.yaml` as canonical workspace truth.
- Treat `antigravity-mcp-config.json` as canonical MCP truth.
- Never create a second source-of-truth MCP config.
- Keep all four repo roots live and canonical.
- Put all API keys in `.env`, never inline in JSON.
- `counselconduit` is the Google-native MVP product path.
- `uphillsnowball` is the Apple Silicon local lab path.
- Fix truth surfaces before refactors.
- Prefer minimal, reviewable changes.
- Do not revive obsolete thread artifacts once superseded by `docs/UPDATED_PNKLN_PACK.md`.
- Prefer operationalized recovered code over new doctrine prose.
"""

files["ops/audits/third_party_inventory.md"] = """\
# Third-party inventory

## Google-native
- Vertex AI / Gemini
- Firebase MCP
- Developer Knowledge MCP
- Stitch MCP
- Chrome DevTools MCP

## Local lab
- LanceDB
- Python local scripts

## Review targets
- remove stale non-canonical adapters from operational paths
- keep all keys in `.env`
- keep product/runtime split explicit
"""

files["scripts/thread_audit_protocol.txt"] = """\
/thread-recovery-2stage

Stage 1 — Audit and recover only

Re-read the full thread end to end. Build a complete ledger of:
- explicit requests
- implicit requirements
- constraints
- dependencies
- unresolved issues
- abandoned branches
- partially completed deliverables
- implied but unproduced code, analysis, or explanations

Search all available resources for missing context and evidence, including thread history, available artifacts, connected internal sources, Google Drive when available, relevant repos, and web research when useful.

Identify:
- omissions
- contradictions
- changed assumptions
- weak reasoning
- missing code paths
- overlooked implementation details
- performance opportunities
- maintainability improvements
- accuracy improvements
- leverage and monetization opportunities

Then reconcile:
- asked vs answered
- answered vs solved
- assumed vs verified
- explicit vs implied
- mentioned vs operationalized
- drafted vs implemented
- apparently complete vs actually complete
- local optimum vs global optimum
- technically correct vs commercially useful

Stage 1 output only:
A. Recovery findings
B. Complete task ledger
C. Missing or incomplete items
D. Newly recovered material
E. Distinctions and changed assumptions
F. What must be preserved, corrected, expanded, or replaced

Critical rule: do not rewrite answers yet. Do not regenerate code yet.

Stage 2 — Replan and regenerate

Using only the reconciled findings from Stage 1:
- rebuild the plan from first principles
- correct broken assumptions
- incorporate recovered material
- resequence the work for better clarity, implementation quality, and business outcome
- regenerate the answers
- reprint all relevant code in full

Optimize for:
- elegance
- simplicity
- correctness
- performance
- maintainability
- robustness
- accuracy
- clarity
- business leverage
- financial upside

Stage 2 output:
A. Revised plan
B. Regenerated answers
C. Full updated code

Critical rule: prefer truth over continuity, and elegance over thread momentum.
"""

for fname, content in files.items():
    if fname.startswith("/"):
        path = pathlib.Path(fname)
    else:
        path = ROOT / fname
    path.write_text(content, encoding="utf-8")
    if fname.endswith(".sh") or fname.endswith(".py"):
        os.chmod(path, 0o755)
    print(f"Wrote {path}")
