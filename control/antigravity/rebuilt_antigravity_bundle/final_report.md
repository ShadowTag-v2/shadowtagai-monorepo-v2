# Antigravity Thread Summary and Plan

## Context

This thread covered a complex technical project: evolving **Antigravity** (a code‑generation and agent‑execution system) into a robust monorepo with a memory‑first operating model. The discussion touched on architecture, repository consolidation, memory design, automation scripts, and operational discipline. Due to limited API/tool access, external resources such as Google Drive documents could not be fetched directly. Instead, the summary is based on the conversation itself.

The goals were to:

1. **Unify a large collection of repos** into a single monorepo (modelled after Google’s monorepo), with canonical roots and clear status (canonical, queued for fold‑in, archived, etc.).
2. **Design a memory architecture** that elevates persistent knowledge to a first‑class control plane, so Antigravity does not “forget” decisions or revert to old states.
3. **Develop installation bundles** (v10 and v11) that integrate the memory system into the existing monorepo control plane.
4. **Plan operator invariants** for Git/GitHub behaviour, ensuring stable authentication and remote usage.
5. **Provide scripts and YAML lists** to drive repository fold‑in and local installation.

Below is a recap of the key concepts, differences, and deliverables, followed by a plan for implementation and high‑level guidance for maintaining performance, accuracy, and business impact.

---

## Four Major Systems and Their Roles

### 1. **Repo‑Native Control Plane (`pnkln`)**

- **Location in the repo**: `manifests/monorepo_manifest.yaml`, `docs/MERGE_STATUS.md`, `docs/ANTIGRAVITY_CONTROL_PLANE.md` and associated scripts (e.g. `scripts/apply_latest_pack_2.sh`).
- **Role**: Provides the definitive statement of what constitutes the monorepo’s **canonical roots**, current merge status, and control‑plane configuration. This layer must remain authoritative—no other system should silently override it.
- **Business split**: The monorepo distinguishes `apps/counselconduit` (commercial path), `labs/uphillsnowball` (internal R&D / Apple Silicon), and `control/pnkln` (operating doctrine).

### 2. **Old Antigravity Memory‑Bank Doctrine (Drive)**

- Defines `.agent/memory/` with files like `project-brief.md`, `product-vision.md`, `context.md`, etc., loaded automatically at task start.
- Useful for human‑readable continuity but too coarse and manual to act as canonical truth.
- It should now become a **generated compatibility view** derived from the canonical memory, not the authoritative source.

### 3. **Memory‑First Architecture (v10/v11)**

- **Artifacts**: Bundles such as `ane_cortex_stack_v10_bundle.tar.gz`, `antigravity_v11_merged_control_plane_final_bundle.tar.gz`, and scripts like `setup_antigravity_v10_local.sh`.
- **Key elements**:
  - `authority-current.json`: single source of canonical memory (policies, settings, procedures).
  - **Atoms**: fine‑grained memory facts for precise retrieval and conflict detection.
  - **Hydrate Pack**: precompiled launch packet for the IDE/agent to load memory, tasks, and monorepo truth at startup.
  - **Drift & Conflict Detection**: code‑graph validation and drift reporting so that code updates always follow memory and control‑plane truth.
  - **Promotion Workflow**: when code improvements or operational changes are validated, they can be promoted back into canonical memory.

### 4. **Future State: Full Repo Fold‑in**

- A list of 56 (not 57) repos, mostly prefixed with `ShadowTag-v2-` plus `pnkln`, `erik-hancock-llm-memory`, and several public demos (e.g. `antigravity-go`, `Cor.Claude_Code_6`).
- Each repo must be classified into one of five statuses: `canonical_in_monorepo`, `queued_for_fold_in`, `archived_after_fold_in`, `reference_only`, or `deprecated`.
- A `fold_in_checklist.yaml` was produced to track this process.

---

## Key Differences and Lessons Learned

1. **Canonical Truth vs. Codebase Truth**:
   - *Canonical truth* is recorded in `authority-current.json` and associated atoms; it defines what **should** be.
   - *Codebase truth* reflects what actually exists in the files. It is only used to identify upgrades needed, not to override policy.

2. **Repo Control Plane vs. Memory System**:
   - The `pnkln` control plane declares which repos are canonical; the memory system records how Antigravity should behave and recover state.
   - They must be **fused**, not replaced. The memory system should load and respect the control plane, then provide guidance to upgrade the codebase accordingly.

3. **Atomic Memory vs. Document Memory**:
   - Atomised memories (`settings.*`, `startup_contract.*`) allow precise retrieval and enforcement.
   - Human‑readable `.agent/memory/*.md` should be auto‑generated from atoms to aid developers but not act as law.

4. **Git/GitHub Discipline**:
   - The project exposed repeated failures due to Antigravity “forgetting” authentication settings. This was fixed by introducing `operator_invariants.json` and corresponding atoms that declare the GitHub app as the control plane, `ssh` as the preferred remote, and a repair command for HTTPS auth.

5. **Business Focus**:
   - The strategic plan is to turn `CounselConduit` into the business‑facing product, while `uphillsnowball` remains an internal lab. This splitting of concerns should be reflected in repository organisation and in how memory is used to drive new features.

---

## Deliverables Summary

### Bundles & Archives

| File | Purpose |
|---|---|
| `antigravity_v11_merged_control_plane_final_bundle.tar.gz` | Contains v11 installation scripts (merged v10 + control plane) and memory integration artefacts. |
| `ane_cortex_stack_v10_bundle.tar.gz` | v10 memory/enforcement stack, including hydrate pack and memory definitions. |
| `fold_in_checklist.yaml` | Machine‑readable list of all repos and their fold‑in status classifications (initially blank for user input). |
| `operator_invariants.json` | Canonical settings and startup contract for Git/GitHub behaviour. |
| `operator_invariants_atoms.json` | Atoms derived from the invariants file for precise retrieval. |
| `setup_antigravity_v11_merged.sh` | Installer script to set up the v11 merged control plane in a local monorepo. |
| `INSTALL_ANTIGRAVITY_V11_MERGED.md` | Human‑readable installation guide for the v11 merged control‑plane bundle. |

### Important Scripts & Files

#### Operator Invariants (JSON)

```json
{
  "version": 1,
  "scope": "antigravity_local_operator_invariants",
  "purpose": "Canonical startup invariants for GitHub auth, git transport, clone/sync policy, and hydration order.",
  "settings": {
    "github_control_plane": "github_app",
    "git_remote_preference": "ssh",
    "git_https_repair_command": "gh auth login && gh auth setup-git",
    "git_push_precondition": "valid_auth_and_correct_remote",
    "local_clone_role": "indexed_working_copy",
    "github_app_role": "freshness_and_repo_truth",
    "monorepo_primary_workspace": "ShadowTag-v2/Monorepo-Uphillsnowball",
    "monorepo_primary_remote": "git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git",
    "fallback_backend": "metal",
    "default_inference_backend": "ane"
  },
  "startup_contract": {
    "hydrate_before_reasoning": true,
    "ignore_codebase_as_authority": true,
    "upgrade_codebase_from_memory": true,
    "load_github_git_invariants_before_repo_actions": true
  },
  "procedures": [
    "Load authority memory first",
    "Load operator invariants second",
    "Load monorepo control-plane truth third",
    "Load active tasks and drift reports fourth",
    "Only then inspect code or perform Git/GitHub operations",
    "If remote uses HTTPS and auth fails, repair with gh auth login && gh auth setup-git or switch remote to SSH",
    "Use GitHub app for repo freshness and truth; use local clones for indexing and execution only"
  ]
}
```

#### v11 Installation Script (Excerpt)

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy relevant bundles and files into control/antigravity/v11
mkdir -p control/antigravity/v11
mkdir -p data/memory
mkdir -p .agent/memory

for f in \
  "${SELF_DIR}/antigravity_final_ingest_bundle.tar.gz" \
  "${SELF_DIR}/ane_cortex_stack_v10_bundle.tar.gz" \
  "${SELF_DIR}/fold_in_checklist.yaml" \
  "${SELF_DIR}/operator_invariants.json" \
  "${SELF_DIR}/operator_invariants_atoms.json" \
  "${SELF_DIR}/INSTALL_ANTIGRAVITY_V10_LOCAL.md" \
  "${SELF_DIR}/setup_antigravity_v10_local.sh"; do
  cp "$f" control/antigravity/v11/
fi

# Run the v10 installer to set up authority memory, atoms and hydrate pack
bash "control/antigravity/v11/setup_antigravity_v10_local.sh" \
  "$ROOT" \
  "control/antigravity/v11/antigravity_final_ingest_bundle.tar.gz" \
  "control/antigravity/v11/ane_cortex_stack_v10_bundle.tar.gz"

# Install operator invariants to data/memory
cp "control/antigravity/v11/operator_invariants.json" data/memory/operator_invariants.json
cp "control/antigravity/v11/operator_invariants_atoms.json" data/memory/operator_invariants_atoms.json

# Install fold-in checklist at repo root
cp "control/antigravity/v11/fold_in_checklist.yaml" ./fold_in_checklist.yaml

# Refresh repo-native pnkln control plane if pack script exists
if [ -f "./scripts/apply_latest_pack_2.sh" ]; then
  bash ./scripts/apply_latest_pack_2.sh || true
fi

# Generate .agent/memory views from authority
python3 control/antigravity/ane_cortex_stack_v10/scripts/generate_memory_bank_views.py || true
python3 control/antigravity/ane_cortex_stack_v10/scripts/export_launch_packet.py || true
```

This script ensures the monorepo uses the repo-native control plane and then installs the v10 memory stack, the operator invariants, and the fold-in checklist.

---

## Implementation Plan for Antigravity

1. **Install v11 Locally**:
   - Unpack `antigravity_v11_merged_control_plane_final_bundle.tar.gz` in your monorepo root.
   - Run the installer script to stage the control plane, memory, invariants, and fold-in checklist.
   - Ensure `.agent/memory/*` documents are auto‑generated from `authority-current.json`.

2. **Adopt the Startup Sequence**:
   - At each session start, load `authority-current.json` → `operator_invariants.json` → monorepo control plane → atoms → active tasks → drift reports → fold-in checklist → **then** inspect code or run Git commands.
   - Reject any plan that attempts to derive operational decisions from code before the authority memory is loaded.

3. **Use the GitHub App**:
   - Always fetch repository status and files through the GitHub app for freshness.
   - Use local clones only for indexing, semantic retrieval, and patch generation.

4. **Classify and Fold Repos**:
   - Use `fold_in_checklist.yaml` to assign each repo into `canonical_in_monorepo`, `queued_for_fold_in`, etc.
   - Prioritise `ShadowTag-v2-*` repos, `pnkln`, `erik-hancock-llm-memory`, `cosmic-crab-payload`, `Pipeline`, and `nascent-apollo` for early canonicalization.
   - Defer or archive templates, demos, or superseded duplicate repos.

5. **Promote Lessons**:
   - When new operational rules or design patterns prove useful (e.g., *vibe coding* mode), add them to authority memory and generate atoms.
   - Use derived profiles (e.g., `profiles/vibe_coding.yaml`) to modulate the assistant’s behaviour without changing the underlying invariants.

6. **Business Execution**:
   - Focus commercial energy on `CounselConduit` while using `uphillsnowball` for R&D.
   - Keep `pnkln` as the operating doctrine; treat it as the source of system behaviour rather than a product root.

---

## Conclusion

The key insight from revisiting the entire thread is **integration, not replacement**. The monorepo already contains a functioning control-plane backbone (`pnkln`), while the v10/v11 memory system offers a superior memory engine. The right architecture is to fuse them:

- Keep the monorepo’s declared truths about canonical roots and control plane.
- Install the memory stack to enforce retrieval, authority, and drift handling.
- Use GitHub as the freshness authority and treat local clones as working copies.
- Derive `.agent/memory/*` from canonical memory and never treat them as the source of truth.
- Systematically fold in all 56 repos using the checklist and respect differences between “application roots” and “packages/infra”.

This approach will keep Antigravity from forgetting its state, reduce regression risk, and position the project for a stable single-monorepo future. In Steve Jobs’ spirit of **simplify to elegance**, the solution is to unify the control plane with the memory system, focusing on clarity and ruthlessly removing ambiguity.
