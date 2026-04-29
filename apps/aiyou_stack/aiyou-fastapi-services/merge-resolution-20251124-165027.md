# Merge Resolution Log

**Date**: Mon Nov 24 16:50:28 PST 2025
**Source**: claude/code-into-c-01M1anzYZdJTDDeZQsiVTkKS
**Target**: claude/integration-main
**Backup**: integration-main-backup-20251124-165027

## Conflict Resolution Decisions

| File | Strategy | Rationale |
|------|----------|-----------|
| .claude/settings.local.json | ours | Config file - keep integration-main version |
| .claude/skills/backend-dev-guidelines/SKILL.md | theirs | Documentation - take source (more current) |
| .claude/skills/skill-rules.json | ours | Config file - keep integration-main version |
| .cursorrules | ours | Project config - keep integration-main |
| .env.example | ours | Project config - keep integration-main |
| .gitignore | ours | Project config - keep integration-main |
| ARCHITECTURE.md | theirs | Documentation - take source (more current) |
| Dockerfile | ours | Project config - keep integration-main |
| README.md | theirs | Documentation - take source (more current) |
| agents/bar_exam_protocol.py | theirs | Source code - take source branch features |
| agents/autoresearch.py | theirs | Source code - take source branch features |
| agents/jura_protocol.py | theirs | Source code - take source branch features |
| agents/legal_whiteboard.py | theirs | Source code - take source branch features |
| agents/pipeline_orchestrator.py | theirs | Source code - take source branch features |
| app/__init__.py | theirs | Source code - take source branch features |
| app/agents/__init__.py | theirs | Source code - take source branch features |
| app/config.py | theirs | Source code - take source branch features |
| app/kernels/Claude_Code_6.py | theirs | Source code - take source branch features |
| app/main.py | theirs | Source code - take source branch features |
| app/main_ecosystem.py | theirs | Source code - take source branch features |
| app/models/__init__.py | theirs | Source code - take source branch features |
| app/monitoring/metrics.py | theirs | Source code - take source branch features |
| app/orchestration/chain.py | theirs | Source code - take source branch features |
| app/validation/jr_engine.py | theirs | Source code - take source branch features |
| coverage.xml | theirs | Coverage file - take source |
