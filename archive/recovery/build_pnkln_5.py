import os
import pathlib

ROOT = pathlib.Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")

files = {}

files["scripts/vertex_prompt_templates.txt"] = """\
# pnkln Primer
Operate at pnklnJR(purpose)+Doctrine(reason)+ARM(brakes).
Run all-hands: digest latest -> classify {KEEP|REFERENCE ONLY|DISCARD} -> streamline/optimize -> regenerate roll-up -> post exec summary.
Apply SOPs A-D with Bourne boosts (2x throughput, +90% safety). If conflict/policy risk, voice objections and flag per pnklnJR.

# pnkln Repo Enforcement
Apply pnkln SOPs repo-wide:
1) Upload Triage: classify+score; KEEP->tickets->Active Resources; delta summary.
2) Change & Release: premortem(5), feature-flag, stress drills, promote/rollback, postmortem<24h.
3) Decision Protocol: Decision/Context/Options/Choice(pnklnJR+Doctrine)/Risks(ARM)/Owner+By-When/Metrics.
4) Code Review: minimal diff; tests; security/privacy; observability; rollback plan.
Return plan, diffs/actions, and exec summary.

# pnkln All-Hands Reset
Run all-hands now:
- Sort memory/docs by latest.
- Triage {KEEP|REFERENCE ONLY|DISCARD}.
- Streamline+optimize (pnklnJR+Doctrine+ARM).
- Regenerate comprehensive roll-up.
- Output "pnkln All-Hands Complete" + summary.

# pnkln Valuation Drill
Compute valuation uplift:
Inputs: ARR, OPEX, multiple(10x default).
Assume 15-30% OPEX savings from 2x throughput/decision velocity & +90% safety.
Convert to ARR-equivalent; valuation uplift = ARR-eq x multiple.
Return assumptions, math steps, sensitivity (15, 20, 25, 30%).

# pnkln Rapid Drill
Premortem10|RollbackChecklist|FailureInjection|AuditArtifacts|DebriefTemplate.

# pnkln Investor 2-Slide
Slide1Impact:2xThru,+90Safety,2xDecVel,2.2xEndurance;Slide2Val:$3M/yr->$30M@10x;Mid/Ent+scaling.
"""

files["scripts/counselconduit_blueprint.txt"] = """\
CounselConduit is the business-facing MVP.

Wedge:
- stateless legal SaaS
- premium pricing
- BYOK routing
- fast onboarding
- high-trust retrieval and summaries

Commercial role:
- simplest product story
- shortest path to revenue
- cleaner buyer narrative than sprawling internal platform language

Internal dependency:
- pnkln / uphillsnowball supplies retrieval, eval, experimentation, security hardening, and local lab velocity
"""

files["scripts/uphillsnowball_lab_blueprint.txt"] = """\
uphillsnowball is the internal Apple Silicon lab path.

Purpose:
- local experimentation
- LanceDB / Apple Silicon / ANE-adjacent work
- internal eval harness
- OCR and retrieval experimentation
- operational tooling for pnkln

Non-goal:
- do not let uphillsnowball redefine CounselConduit product truth
"""

files["scripts/final_next_order.txt"] = """\
Best next order to land the current thread pack:

1. patch monorepo_manifest.yaml
2. replace docs/MERGE_STATUS.md
3. install canonical antigravity-mcp-config.json
4. demote adapter MCP files
5. replace verify_mcp.sh
6. add docs/UPDATED_PNKLN_PACK.md
7. add recovered operational scripts
8. add CounselConduit product spec files
9. verify root truth
10. commit only after verification passes
"""

files["scripts/vertex_operator_notes.txt"] = """\
Google-native operator direction:
- one canonical MCP config
- one canonical monorepo manifest
- all secrets in .env
- gemini-3.1-flash-lite-preview everywhere
- counselconduit is the product
- uphillsnowball is the lab
- operationalize recovered code before drafting more doctrine
"""

files["scripts/highest_value_opportunities.txt"] = """\
Highest-value missed opportunity 1:
You already have enough recovered material to make counselconduit commercially coherent and uphillsnowball technically useful, but the repo still lacked a single truthful backbone. Fixing truth surfaces first unlocks everything else.

Highest-value missed opportunity 2:
Operationalize recovered code instead of redrafting it again:
- green loop
- CSP collector
- retriever eval
- feature flags
- pricing model
- OCR summaries
- Drive-ingest daemon

Highest-value missed opportunity 3:
The recovered CounselConduit blueprint is already stronger than later wandering branches. It should become the business-facing spec while pnkln/uphillsnowball remains the internal engine.
"""

files["scripts/recovery_summary.txt"] = """\
Recovered truth:
- product, lab, and control-plane were mixed in thread momentum
- current strongest direction is:
  - counselconduit = business-facing Google-native MVP
  - uphillsnowball = internal Apple Silicon lab
  - pnkln = operating/control doctrine
- canonicalization and control-plane truth must be fixed before more feature drafting
"""

files["scripts/atomic_rollup_manifest.txt"] = """\
This atomic rollup includes current surviving non-script artifacts:
- docs
- prompts
- env examples
- policy/operator notes
- mcp adapter notes
- product/spec artifacts

It excludes:
- stale superseded variants
- earlier contradictory drafts
- obsolete thread momentum claims
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
