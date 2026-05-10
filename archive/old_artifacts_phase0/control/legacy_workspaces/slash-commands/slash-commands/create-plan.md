---
description: Create a comprehensive task plan with context, success criteria, approach, and risks
argument-hint: TASK=<task-description-or-goal>
---

<task>
$TASK
</task>

# Create Plan (slash command)

Goal: draft a full task plan in `docs/tasks/todo/<XX>-<name>.md`.

Always do this first:
- Read AGENTS.md and follow all rules/constraints.

Plan requirements (keep concise, but complete):
- Context: 2–3 bullet recap of the problem/goal.
- Success criteria / acceptance: bullet list with measurable checks.
- Deliverables: code/docs/tests to produce.
- Approach: ordered steps (no workarounds; sustainable, clean implementation).
- Risks / unknowns: note dependencies, edge cases, perf/security concerns.
- Testing & validation: what to run (unit/integration/e2e), data sets, platforms.
- Rollback / escape hatches: brief note if applicable.
- Owner / date: stamp with today’s date.

After writing the plan:
- Save at path `docs/tasks/todo/<XX>-<name>.md`.
- Ask the user: “What are the most important questions to confirm before implementation?” and list your top 3–5 clarifying questions.

Suggested prompt body:
```
Context
- ...
- ...

Success criteria
- ...

Deliverables
- ...

Approach
1) ...
2) ...
3) ...

Risks / unknowns
- ...

Testing & validation
- ...

Rollback / escape hatch
- ...

Owner/Date
- <you> / <YYYY-MM-DD>
```

Reminder:
- No workarounds or half measures; design for long-term maintainability.
- If info is missing, include assumptions and surface them in the questions you ask the user at the end.
