# Legacy FlyingMonkeys Archive

**Archived**: 2026-04-24
**Reason**: FlyingMonkeys concept fully retired and replaced by Cor.autoresearch architecture.

## Replacement Architecture

| Legacy Concept | Replacement |
|---|---|
| `FlyingMonkeys` class | `AutoresearchEngine` |
| `flying_monkeys.py` | `cor_autoresearch.py` |
| `flyingmonkeys-server` | `uphillsnowball-engine` |
| 600-agent swarm | Kosmos + BioAgents + n-autoresearch triad |
| monkey watchdog | `runtime_watchdog` / ENDEX / RKILL |
| monkey dashboard | research run console |

## Canonical Doctrine

> **UphillSnowball uses Cor.autoresearch as its engine: Kosmos directs, BioAgents routes,
> n-autoresearch executes, iii tracks state, JudgeSix-Human gates human/server actions,
> JudgeSix-Agent gates every agent output, the whiteboard persists unresolved issues,
> and RKILL terminates unsafe or non-convergent runs.**

## New Paths

```
labs/uphillsnowball/engine/cor_autoresearch.py
labs/uphillsnowball/engine/kosmos_bridge.py
labs/uphillsnowball/engine/bioagents_worker.py
labs/uphillsnowball/engine/n_autoresearch_client.py
labs/uphillsnowball/governance/judge_six_human.py
labs/uphillsnowball/governance/judge_six_agent.py
labs/uphillsnowball/governance/runtime_watchdog.py
labs/uphillsnowball/governance/rkill.py
docs/UPHILLSNOWBALL_ARCHITECTURE.md
docs/COR_AUTORESEARCH.md
```

## Warning

A prior commit attempted to replace FlyingMonkeys with the literal string
`n-autoresearch/Kosmos/BioAgents` inside Python identifiers, class names, and
Cloud Run service names. That was syntactically invalid. The corrected replacement
uses valid identifiers as documented above.

## Files in this archive

These files are preserved for historical reference only. They are NOT active code.
