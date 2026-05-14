# ATOMIC THREAD TEMPLATE — OPORD FORMAT

## Thread Metadata

```yaml
thread_id: ATOMIC-XXX
tier: FREE | FLASH | PRO
created: YYYY-MM-DD HH:MM UTC
status: ACTIVE | COMPLETE | BLOCKED
parent: null | ATOMIC-XXX
insert_type: PROMPT | BUGFIX | OPTIMIZE | GENERAL

```

---

## 1. SITUATION (Context)

### a. Environment


- **Codebase State**: [Current branch, recent commits, test status]

- **Dependencies**: [Relevant files, modules, external services]

- **Constraints**: [Time, resources, technical limitations]

### b. Problem Statement

[One paragraph: What is broken/missing/needed? Be specific.]

### c. Prior Work


- **Related Threads**: [List ATOMIC-XXX references]

- **Relevant Docs**: [Links to specs, PRs, issues]

---

## 2. MISSION (Purpose)

### a. Task

[One sentence: Action verb + object + outcome]
> Example: "Fix the Redis connection timeout causing 502 errors in production."

### b. Purpose

[Why this matters to the larger system]

### c. End State


- **Success Criteria**: [Measurable outcomes]

- **Acceptance Tests**: [Specific checks to verify completion]

### d. Brakes (Kill Conditions)


- [ ] If [condition], STOP and escalate

- [ ] If [condition], STOP and escalate

- [ ] p99 latency exceeds [X]ms for [Y] consecutive calls

---

## 3. EXECUTION (Plan)

### a. Concept of Operation

[High-level approach in 2-3 sentences]

### b. Tasks

| Step | Action | File(s) | Verification |
|------|--------|---------|--------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### c. Coordinating Instructions


- **Sequence**: [Dependencies between steps]

- **Timing**: [Any ordering constraints]

- **Boundaries**: [What NOT to touch]

---

## 4. SERVICE & SUPPORT (Resources)

### a. Tools Required


- [ ] Gemini tier: FREE / FLASH / PRO

- [ ] Redis cache: Yes / No

- [ ] External APIs: [List]

### b. Reference Materials


- **Code**: [File paths with line numbers]

- **Docs**: [URLs, local paths]

- **Examples**: [Similar implementations]

### c. Budget


- **Max API calls**: [Number]

- **Max tokens**: [Number]

- **Time limit**: [Minutes]

---

## 5. COMMAND & SIGNAL (Control)

### a. Reporting


- **Checkpoints**: [When to report progress]

- **Format**: [What to include in updates]

### b. Escalation Path


1. **YELLOW**: [Condition] → [Action]

2. **RED**: [Condition] → [Action]

3. **BLACK**: [Condition] → ABORT

### c. Handoff Protocol

```json
{
  "summary": "[One paragraph outcome]",
  "files_changed": [],
  "tests_passed": true | false,
  "follow_up": "[Next ATOMIC-XXX or null]"
}

```

---

## INSERT SECTION

<!-- Include appropriate insert based on insert_type -->
<!-- See: docs/templates/inserts/ -->

---

## Execution Log

### TLP (Troop Leading Procedures) Checklist


- [ ] 1. Receive the mission

- [ ] 2. Issue warning order

- [ ] 3. Make tentative plan

- [ ] 4. Initiate movement

- [ ] 5. Conduct reconnaissance

- [ ] 6. Complete the plan

- [ ] 7. Issue order

- [ ] 8. Supervise and refine

### Activity

| Timestamp | Action | Result |
|-----------|--------|--------|
| | | |

---

## Completion

**Status**: [ ] COMPLETE  [ ] BLOCKED  [ ] ESCALATED

**Handoff JSON**:

```json
{
  "thread_id": "ATOMIC-XXX",
  "outcome": "",
  "files_changed": [],
  "tests": { "passed": 0, "failed": 0 },
  "next_action": ""
}

```
