# ═══════════════════════════════════════════════════════════
# skills.md — Ruler SkillOps Policy
# Version: 1.0.0
# Distributed by: ruler apply
# ═══════════════════════════════════════════════════════════

## SkillOps Policy

### Skill Lifecycle
1. **Create**: New skills MUST have SKILL.md with YAML frontmatter (name, description, version).
2. **Update**: Skill updates MUST run `scripts/skills-registry.py --refresh` after modification.
3. **Archive**: Skills are NEVER deleted. Archive to `_archive_redundant_<date>/` directory.
4. **Dedup**: Duplicate stubs go to `_dedup_stubs_<date>/` with redirect SKILL.md.

### Naming
- Directory: kebab-case, max 40 characters
- SKILL.md: required in every skill root
- Version: semver in frontmatter

### Overlap Resolution
- Workspace skills override global skills of the same name
- Only ONE instance may be active at a time
- Run `bash scripts/skills-audit.sh --check-overlap` to detect

### External Skills
- External skills MUST be listed in `external_repos/upstream_manifest.yaml`
- Install via `npx skills add <org>/<repo>` or manual copy from external_repos/
- Never blindly install skills from untrusted sources (Epistemic Airgap applies)

### Registry Contract
- Tool contract: `tool_contracts/skills.update.yaml`
- Workflow: `.agent/workflows/skills-refresh.md`
- Audit: `scripts/skills-audit.sh`
- Registry: `scripts/skills-registry.py`
