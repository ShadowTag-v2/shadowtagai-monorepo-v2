# Migration Plan: Monorepo-Uphillsnowball → shadowtagai-monorepo-v2

**Goal**: Move from the current workspace (`Monorepo-Uphillsnowball`) into a clean, Google-style monorepo (`shadowtagai-monorepo-v2`) while preserving history where valuable and cleaning up technical debt.

**Source**: [Grok Thread](https://grok.com/share/c2hhcmQtMi1jb3B5_a06c4757-e33e-4879-8703-bdcf8a5e45e8)

---

## Phase 0: Preparation (1–2 days)

1. **Create the new repo** using the `tomsoir/bazel-monorepo` template ✅ DONE
2. **Clone both repos locally**:
   ```bash
   git clone git@github.com:ShadowTag-v2/shadowtagai-monorepo-v2.git
   git clone git@github.com:ShadowTag-v2/Monorepo-Uphillsnowball.git
   ```
3. **Run health check on current repo**:
   ```bash
   cd Monorepo-Uphillsnowball
   python scripts/repo_doctor.py
   ```

---

## Phase 1: Audit & Inventory (1 day)

Run these commands in the **current repo**:

```bash
# Find all key components
find . -name "*.py" -o -name "*.ts" -o -name "Dockerfile" | grep -E "(agent|kovelai|shadowtag|layers|orchestrator)" | head -30

# Check for monoliths
wc -l apps/aiyou_stack/aiyou-fastapi-services/apps/pnkln/governance/judge_architecture/layers.py
wc -l apps/aiyou_stack/aiyou-fastapi-services/apps/pnkln/core/cor_orchestrator.py

# List all nested .git directories (to be cleaned)
find . -name ".git" -type d ! -path "./.git" | grep -v external_repos
```

**Document**:
- Which services should become separate apps in the new repo
- Which libraries should go into `libs/` or `packages/`
- Which infrastructure should move to `infrastructure-catalog-gcp-cloud-run`

---

## Phase 2: Rich Hickey Refactoring (Monolith Breaking)

**Goal**: Break large files into focused, single-responsibility modules.

**Tasks**:

1. **Refactor `layers.py`** (13 classes → 9 files)
   - Split into logical domains: `risk/`, `compliance/`, `governance/`, `orchestration/`

2. **Refactor `cor_orchestrator.py`** (9 classes → 5 files)
   - Extract `KineticActionParser`, `OracleStudio`, `AgentCoordinator`, etc.

3. **Move shared logic** into `libs/` or `packages/`

**Rule**: No file should exceed ~400 lines after refactoring.

---

## Phase 3: Infrastructure Migration (Parallel Workstream)

While refactoring code:

1. **Create the three infrastructure repos** (see `scripts/generate-three-repos.sh`):
   - `infrastructure-catalog-gcp-cloud-run`
   - `infrastructure-live-gcp`
   - `infrastructure-pulumi`

2. **Migrate Cloud Run & related infrastructure**:
   - Move Dockerfiles, `cloudbuild.yaml`, `deploy-cloudrun.sh` into `infrastructure-catalog-gcp-cloud-run`
   - Move Terragrunt stacks into `infrastructure-live-gcp`

3. **Migrate Pulumi components** (if using):
   - Move `CloudRun`, `VpcConnector`, `CloudDeployCanaryPipeline` into `infrastructure-pulumi`

---

## Phase 4: Code Migration Strategy

**Recommended Approach** (Clean Cutover):

1. **Do NOT** copy the entire history (too messy).
2. **Create new clean structure** in `shadowtagai-monorepo-v2`:
   ```
   shadowtagai-monorepo-v2/
   ├── apps/
   │   ├── kovelai/
   │   ├── shadowtag-agent/
   │   └── counselconduit/
   ├── libs/
   ├── packages/
   ├── infra/                    ← Points to the three new repos
   └── tools/
   ```

3. **Copy only clean, refactored code**:
   - Use `git cherry-pick` for important commits only
   - Or simply copy files and create new commits with clear messages

4. **For critical history** (e.g. legal or compliance decisions):
   - Keep the old repo as read-only archive
   - Reference it in `README.md`

---

## Phase 5: Final Cutover & Verification

1. **Freeze development** on the old repo
2. **Run final health check**:
   ```bash
   python scripts/repo_doctor.py
   ```
3. **Push everything** to `shadowtagai-monorepo-v2`
4. **Update all CI/CD** to point to the new repo
5. **Archive the old repo** (make it read-only or move to archive org)

---

## Phase 6: Post-Migration Cleanup

- Delete nested `.git` directories
- Remove duplicate files (`rsta_squadron.py` had duplicates)
- Consolidate CI workflows (target: reduce from 60 → ~15)
- Update all internal links and documentation

---

## Expected Timeline

| Phase | Duration | Owner |
|-------|----------|-------|
| Preparation + Audit | 2 days | Platform Team |
| Rich Hickey Refactoring | 5–7 days | Engineering |
| Infrastructure Migration | 4–5 days | Platform + DevOps |
| Code Migration & Cutover | 3 days | All teams |
| Verification & Cleanup | 2 days | Platform Team |

**Total**: ~3–4 weeks for a clean migration.
