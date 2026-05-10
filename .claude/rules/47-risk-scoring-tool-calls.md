# Rule 47: Risk Scoring for Tool Calls

> Derived from: oh-my-claudecode/ecc2 research (observability/), everything-claude-code common-performance

## 4-Axis Risk Analysis

Every destructive tool call should be scored on:

| Axis | Score 0.0-1.0 | Description |
|------|--------------|-------------|
| Base tool risk | Tool-inherent danger (write=0.3, delete=0.8, shell=0.9) |
| File sensitivity | Target file criticality (.env=1.0, test=0.1, config=0.7) |
| Blast radius | Number of downstream files affected (1=0.1, 10+=0.8) |
| Irreversibility | Can this be undone? (yes=0.1, partially=0.5, no=0.9) |

## Composite Score → Action

| Composite Score | Suggested Action |
|----------------|------------------|
| 0.0 - 0.25 | Allow |
| 0.25 - 0.50 | Review |
| 0.50 - 0.75 | RequireConfirmation |
| 0.75 - 1.0 | Block |

## Model Selection Strategy (from everything-CC)

| Model Tier | Usage | When |
|------------|-------|------|
| Flash/Haiku | 90% of Sonnet capability, 3x savings | Lightweight agents, pair programming |
| Gemini 3.1 Flash Lite / Sonnet | Best coding model | Main development work |
| Pro/Opus | Deepest reasoning | Architecture decisions, complex analysis |

## Context Window Management

- Avoid last 20% of context window for large-scale work
- Lower context sensitivity tasks (single-file edits, docs) can use end-of-window
- Monitor for context degradation signals (referencing nonexistent variables, forgetting file structures)
