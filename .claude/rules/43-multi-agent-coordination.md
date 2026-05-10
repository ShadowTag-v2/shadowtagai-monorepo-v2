# Rule 43: Multi-Agent Coordination Protocol

> Derived from: repowise-dev/claude-code-prompts (patterns/05, 08), everything-claude-code (common-agents), guanyang/multi-agent-patterns, oh-my-claudecode research

## Delegation Rules

- Delegate only when it improves speed or quality
- Keep one owner (parent agent) responsible for final correctness
- Provide each helper: Goal, Scope boundaries, Required output format, Validation expectations

## Role Assignment

| Role | Purpose | When to Assign |
|------|---------|---------------|
| Planner | Defines scope and task graph | Complex features, refactoring |
| Implementer | Applies code changes | Clear spec, scoped files |
| Reviewer | Checks correctness and maintainability | After code written |
| Verifier | Runs tests/checks and reports evidence | Before claiming done |
| Security Reviewer | Flags auth/injection/secrets | Before commits |

## Handoff Protocol

1. Planner issues scoped tasks with acceptance criteria
2. Implementer returns changed files and decision notes
3. Reviewer flags issues with actionable fixes
4. Verifier confirms behavior with explicit checks
5. Coordinator resolves conflicts and publishes final output

## Conflict Rule

If two outputs disagree, prioritize verified evidence and reroute unresolved items for rework.

## Parallel Execution Mandate

ALWAYS use parallel task execution for independent operations:
- ✅ Launch 3+ agents simultaneously for independent code paths
- ❌ Never run agents sequentially when their work is independent

## Token Economics (from guanyang multi-agent-patterns)

| Architecture | Token Multiplier | Use Case |
|--------------|------------------|----------|
| Single agent chat | 1x baseline | Simple queries |
| Single agent with tools | ~4x baseline | Tool-using tasks |
| Multi-agent system | ~15x baseline | Complex research/coordination |

Budget accordingly. Prioritize model quality upgrades over raw token increases.
