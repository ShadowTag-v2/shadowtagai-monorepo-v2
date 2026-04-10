# Stage 3 Canonicalization & Repo-Drift Audit Implementation Plan

## Goal Description
Ingest all provided v10/v11 control plane bundles, operator invariant atoms, rules packs, and reference repositories to establish the strict "One workspace truth, one MCP truth" canonical state. This includes wiring ANE (Apple Neural Engine) as an experimental sidecar and ensuring the monorepo root is the singular source of truth while referencing multiple community AI systems for procedural extraction.

## Proposed Changes

1. **Ingest Downloads Bundles**
   - Extract `pnkln_master_rules_pack_v2.zip` over the root to enforce governance.
   - Extract `merged_master_rules_pack.zip` to overlay operations, control-plane, and ShadowTag files.
   - Extract `antigravity_rebuilt_bundle_2026_03_18.zip`.
   - Extract `antigravity_v11_merged_control_plane_final_bundle.tar.gz` and `ane_cortex_stack_v9_bundle.tar.gz`.

2. **Copy Control Files**
   - Copy `operator_invariants(1).json` to `data/memory/operator_invariants.json` (and `control/antigravity/v11/`).
   - Copy `operator_invariants_atoms(1).json` to `data/memory/operator_invariants_atoms.json`.
   - Copy `setup_antigravity_v10_local(1).sh` and `INSTALL_ANTIGRAVITY_V10_LOCAL(1).md` to `control/antigravity/v11/`.
   - Copy `fold_in_checklist(2).yaml` to repo root as `fold_in_checklist.yaml`.

3. **Install the v11 Merged Control System**
   - Write `scripts/v11_merged_installer_explicit.sh` as provided in the instructions.
   - Execute the installer to lock the memory loop, generating the `.agent/memory` compatibility views if possible.

4. **Clone Reference Repositories**
   The prompt defined several repositories to clone. We will place these under a `reference/external_upstreams` or `reference/public-demos` folder so they are visible but not live application code.
   - Repos include: CortexLTM, CortexUI, prettier-vscode, beads, pgvector, postgres, grafana, payload, essentials-claude-code, grepai-beads-helpers, Threadwork, beads-templates, vllm, OpenViking, memory-lancedb-pro, Agentic-AI-Pipeline, claude-skills-automation.

5. **Clone Skill References**
   The prompt highlighted an arXiv paper on skills extraction and listed several skill repositories:
   - superpowers-optimized, agent-skills, agentskills, notebooklm-skill, stitch-skills, gemini-skills, skills (rodydavis), google_style_guide_agent_skills, coderabbitai/skills, payload, antigravity-skills.
   - We will clone these into `reference/skills_extraction_sources`.

6. **Create the Concrete Skills Manifest**
   - Based on the East China Normal University paper synthesis, write `.agent/skills/skills-manifest.yaml` (or `reference/skills-manifest.yaml`) to formally adopt the "verification-before-completion", "storyboard-code-consistency-check", "visual-theorem-walkthrough", etc., and formally reject direct public community skill execution without the four-stage gate.

## Verification Plan

### Automated Tests
- Run `bash scripts/v11_merged_installer_explicit.sh` and verify it exits 0 and logs `[done] Antigravity v11 merged control-plane install staged`.
- Run `git status` to observe the massive influx of reference material and ensure it is isolated to `reference/` and `control/` apart from root governance files.

### Manual Verification
- Review `data/memory/operator_invariants.json` to ensure the Apple Silicon "metal" and "ane" backend split is correctly represented.
- Validate that the monorepo root hasn't been polluted with stray `.git` submodules by stripping `.git` from the cloned reference repositories to maintain a flat monorepo integration.
