# knowledge/vault/index.md — Knowledge Vault Index

## Purpose

This vault compiles **research synthesis** — not source truth, not task truth, not operational truth.

The vault is an LLM-compiled wiki. It holds:
- Source material summaries
- Concept pages with backlinks
- Research reports
- Presentation slides
- Visual assets
- Architectural maps

## Directory Structure

| Directory | Purpose |
|-----------|---------|
| `sources/` | Raw source material summaries |
| `concepts/` | Concept pages with cross-references |
| `reports/` | Research reports and analyses |
| `slides/` | Presentation-ready content |
| `visuals/` | Diagrams, architecture maps, screenshots |
| `maps/` | Relationship maps and concept graphs |

## Rules

1. **Synthesis only.** This is a research workbench, not the authority for code, tasks, or execution.
2. **Promote durably.** If a finding becomes operational knowledge, promote it to `.memory/atoms/`.
3. **Create Beads for action.** If research implies work, create a Bead issue.
4. **Manifest raw sources.** Track raw inputs in `knowledge/raw_manifest.yaml`.
5. **Health check.** Run `scripts/wiki-health.sh` after major additions.
