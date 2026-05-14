# 🧩 PLAN MODE STYLE GUIDE v1.0

## 🧠 Purpose

A universal schema for concise, auto-parsable plans — built for use in Cursor, Claude MCP, or GPT-driven coding agents.

**Principles:**
- Sacrifice grammar for concision.
- Each line = one executable action.
- End with open questions or blockers.
- Output must be machine- and human-scannable.

---

## 🧠 Core Philosophy

**"Sacrifice grammar for concision. Surface decisions last."**

1. **Concision > Grammar**: Every token must carry an action, state, or decision.
2. **Line = atomic instruction**: One line, one outcome. No conjunctions.
3. **All verbs imperative**: e.g., "Add param," "Refactor func," "Defer X to Phase 2."
4. **Readable at a glance**: You should grasp the entire plan in <5 seconds.
5. **End with open questions or blockers**: They're always surfaced, never buried.

---

## 📐 Structure Template

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

## ✍️ Writing Rules

| Rule | Example | Rationale |
|------|---------|-----------|
| Drop filler words | `change handler → async wrapper` | More signal per token |
| Prefer → over = | `opts.db → opts.adapter` | Clear direction of change |
| No punctuation | `update evalite opts → adapter param` | Cleaner diffability |
| All verbs imperative | `add, remove, refactor, confirm` | Unambiguous intent |
| Keep ≤60 chars per line | fits Cursor split view | fast scan + clean wrapping |
| Capitalize only code / proper nouns | e.g. SQLite, EvaliteAdapter | readability focus |
| End always with Unresolved Qs: | surfaces blockers | decision forcing |

---

## 🧩 Syntax Keys

| Symbol | Meaning |
|--------|---------|
| → | transform / migrate |
| = | set / define |
| + | add / include |
| - | remove / deprecate |
| ? | question / decision needed |
| ⚠️ | risk / dependency |
| // | brief inline note |
| Phase 1/2 | rollout sequencing |

---

## 🧮 Example — Applied

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

## 🧩 Optional Extensions

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
- **Compatible with Cursor MCP + Claude Plan Mode**
- **Reduces friction** between planning → commit → merge

---

## 🔄 Advanced Usage

### Annotated Execution States

```
Phase 1 ✅ done
Phase 2 🔄 active
Phase 3 ⏳ planned
```

### Priority Tags

```
- [P0] integrate adapter logging
- [P2] optimize caching layer
```

### Dependency Linkouts

```
Deps:
- PR #422 adapter-base
- issue #134 SQLite compat
```

---

**This template is optimized for:**
- Cursor AI
- Claude Code
- GPT-based development loops
- MCP (Model Context Protocol) agents
- Any AI-assisted planning workflow
