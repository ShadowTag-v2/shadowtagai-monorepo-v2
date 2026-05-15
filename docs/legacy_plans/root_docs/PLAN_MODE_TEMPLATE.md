# 🧩 PLAN_MODE_TEMPLATE.md

## 🧠 Purpose

A universal schema for concise, auto-parsable plans — built for use in Cursor, Claude MCP, or GPT-driven coding agents.

**Principles:**

- Sacrifice grammar for concision.
- Each line = one executable action.
- End with open questions or blockers.
- Output must be machine- and human-scannable.

---

## 📐 Structure

```
<module or package>:
- <action> → <target>
- <action> → <target>
- <comment if needed> // optional brief note

Impl:
- <short description of method>
- <compat or interim strategy>
- <future phase trigger or boundary>

Unresolved Qs:
- <question 1>?
- <question 2>?
- <decision 3>?

Options:
1. Proceed + auto-accept edits
2. Proceed + manual approve
3. Hold + keep planning
```

---

## ✍️ Style Rules

| Rule                                | Example                               | Rationale                  |
| ----------------------------------- | ------------------------------------- | -------------------------- |
| Drop filler words                   | `change handler → async wrapper`      | More signal per token      |
| Prefer → over =                     | `opts.db → opts.adapter`              | Clear direction of change  |
| No punctuation                      | `update evalite opts → adapter param` | Cleaner diffability        |
| All verbs imperative                | `add, remove, refactor, confirm`      | Unambiguous intent         |
| Keep ≤60 chars per line             | fits Cursor split view                | fast scan + clean wrapping |
| Capitalize only code / proper nouns | e.g. SQLite, EvaliteAdapter           | readability focus          |
| End always with Unresolved Qs:      | surfaces blockers                     | decision forcing           |

---

## 🧩 Symbols

| Symbol    | Meaning                    |
| --------- | -------------------------- |
| →         | transform / migrate        |
| =         | set / define               |
| +         | add / include              |
| -         | remove / deprecate         |
| ?         | question / decision needed |
| ⚠️        | risk / dependency          |
| //        | brief inline note          |
| Phase 1/2 | rollout sequencing         |

---

## ⚙️ Example Plan

```
packages/evalite/src/server.ts:
- change createServer(opts:{db:SQLiteDB}) → {adapter:EvaliteAdapter}
- update all opts.db refs → opts.adapter
- add inline adapter wrapper (backward compat)
- log adapter usage (debug only)
- full SQLite adapter extraction = Phase 2

Impl:
- create adapter iface matching DB ops
- integrate wrapper in runEvalite()
- validate compat w/ legacy calls
- phase 2 = extract adapter module

Unresolved Qs:
- export-static.ts adopt adapter now or later?
- inline logging stay local or reporter?

Options:
1. Proceed + auto-accept edits
2. Proceed + manual approve
3. Keep planning
```

---

## 🧭 Cursor Command Integration

Command prompt header (add to `.cursor/rules.json` or custom prompt):

```
Rules:
- Use PLAN MODE format
- One action per line
- End with 'Unresolved Qs' section
- Use 'Impl:' if >1 module affected
- Output no prose explanations unless asked
```

**Usage Example:**

```
/plan phase adapter-extraction
```

---

## 🔄 Optional Extensions

### Phase & Priority Markers

```
Phase 1 ✅ done
Phase 2 🔄 active
[P0] must-do
[P2] backlog
```

### Dependencies

```
Deps:
- PR #422 adapter-base
- issue #134 SQLite compat
```

---

## 📦 Why This Template Works

- **Machine-parsable** (ideal for AI code review / refactor loops)
- **Human-skim optimized** (readable in 3 seconds flat)
- **Compatible** with Cursor MCP + Claude Plan Mode
- **Reduces friction** between planning → commit → merge

---

## 🧠 Core Philosophy

> "Sacrifice grammar for concision. Surface decisions last."

1. **Concision > Grammar**: Every token must carry an action, state, or decision.
2. **Line = atomic instruction**: One line, one outcome. No conjunctions.
3. **All verbs imperative**: e.g., "Add param," "Refactor func," "Defer X to Phase 2."
4. **Readable at a glance**: You should grasp the entire plan in <5 seconds.
5. **End with open questions or blockers**: They're always surfaced, never buried.

---

## 🎯 Real-World Application

See [GEMINI_INGESTION_ANALYSIS.md](./GEMINI_INGESTION_ANALYSIS.md) for a comprehensive example applying Plan Mode principles to complex system analysis.

**Key Pattern**: Plan Mode scales from micro (code edits) to macro (architecture analysis)

### Applied to System Analysis

```
Judge 6 → Gemini Ingestion Layer:
- swap domain terminology → intelligence collection
- shift p99 ≤90ms → ~45 min/night batch runtime
- replace 98% coverage → multi-gate quality (items, sources, costs, scores)
- flip caller role → foundational callee (4 namespaces)
- add ethical crawling model
- add multi-source coverage tracking
- add tier classification (1/2/3 value distribution)
- lower confidence 70% → 60% (pre-prod, spec-only)

Impl:
- maintain Judge 6 prompt structure
- customize metrics for upstream collection role
- integrate GKE cron architecture analysis
- validate ethical compliance sections

Unresolved Qs:
- test runs calibrated for Gemini 2.0 Pro?
- visualization requests (tables/charts) needed?
- edge case scenarios (outages, cost spikes) included?
- integration analysis with Judge 6 handoffs?

Options:
1. Deploy to pre-prod + run calibration
2. Add visualization enhancement first
3. Create combined Judge 6 ↔ Ingestion prompt
```

**Takeaway**: Same concise format works for code refactors AND architectural migrations.
