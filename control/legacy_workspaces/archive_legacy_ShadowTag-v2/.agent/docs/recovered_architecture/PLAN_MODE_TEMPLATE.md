# 🧩 PLAN MODE TEMPLATE v1.0

## Purpose

Ultra-concise, auto-parsable plans for technical execution inside Cursor, Claude, or GPT agents.
Machine-readable, human-scannable, zero-friction syntax.

---

## 🧠 Core Philosophy

**"Sacrifice grammar for concision. Surface decisions last."**



1. **Concision > Grammar**: Every token must carry action, state, or decision


2. **Line = atomic instruction**: One line, one outcome, no conjunctions


3. **All verbs imperative**: "Add param," "Refactor func," "Defer X"


4. **Readable at a glance**: Grasp entire plan <5 seconds


5. **End with blockers**: Questions always surfaced, never buried

---

## 📐 Structure Template

```

<module or package>:


- <action> → <target>


- <action> → <target>


- <comment> // optional brief note

Impl:


- <approach summary>


- <temporary compat plan>


- <phase boundaries>

Unresolved Qs:


- <open decision 1>?


- <open decision 2>?

Options:


1. Proceed + auto-apply edits


2. Proceed + manual approve


3. Hold + continue plan

```

---

## ✍️ Writing Rules

| Rule | Example | Notes |
|------|---------|-------|
| Drop filler words | `change handler → async wrapper` | No "the," "to," or "will" |
| Prefer → over = | `opts.db → opts.adapter` | Direction of change |
| No full stops | `update server params → include adapter` | Ongoing process |
| Capitalize code refs only | `EvaliteAdapter`, `SQLite` | Reduces noise |
| 60 char line width max | `update evalite opts → adapter param` | Narrow pane friendly |

---

## 🧩 Syntax Keys

| Symbol | Meaning |
|--------|---------|
| → | Transformation / migration |
| = | Assignment or decision |
| + | Add / append / include |
| - | Remove / deprecate |
| ? | Question or unresolved |
| // | Optional inline note |
| ⚠️ | Risk or dependency warning |
| Phase 1/2 | Temporal grouping |

---

## 🧮 Example — Applied

```

src/aiyou/services/context_index.py:


- change create_context(opord: Dict) → create_context(opord: OPORD)


- update all opord refs → typed OPORD model


- add Pydantic validation for OPORD schema


- log validation errors → debug flag


- full migration to typed models = Phase 2

Impl:


- create OPORD Pydantic model in models/opord.py


- integrate schema validation in ContextIndexService


- confirm parity w/ existing Dict-based calls


- phase 2: migrate all agents to typed OPORDs

Unresolved Qs:


- backward compat for existing OPORDs in SQLite?


- validation errors fail silently or raise exception?

Options:


1. Proceed + auto-apply (recommended)


2. Proceed + manual review


3. Hold + design schema first

```

---

## 🧭 Cursor Integration

Add to `.cursor/rules.json`:

```json
{
  "plan_mode": {
    "rules": [
      "Sacrifice grammar for concision",
      "One action per line",
      "End with 'Unresolved Qs' section",
      "Include 'Impl' if refactors span >1 module",
      "Output no explanations unless asked"
    ],
    "symbols": {
      "→": "transform/migrate",
      "=": "set/define",
      "+": "add/include",
      "-": "remove/deprecate",
      "?": "question/decision",
      "⚠️": "risk/dependency"
    }
  }
}

```

Command usage:

```bash
/plan phase adapter-extraction

```

---

## 🔄 Optional Extensions

### Phase & Priority Markers

```

Phase 1 ✅ done
Phase 2 🔄 active
Phase 3 ⏳ planned

[P0] integrate adapter logging
[P2] optimize caching layer

```

### Dependencies Linkouts

```

Deps:


- PR #422 adapter-base


- issue #134 SQLite compat


- OPORD 00143 (security audit complete)

```

---

## 📦 Why It Works



- **Machine-parsable**: Programmatic diff/patch possible


- **Human-scannable**: 3-second comprehension


- **Cursor MCP compatible**: Integrates with Claude Plan Mode


- **Military brevity**: OPORD-style concision (no ambiguity)


- **Reduces friction**: Planning → commit → merge in one flow

---

## 🎯 Integration with OPORD System

**Plan Mode = TECHNICAL planning** (code changes, refactors)
**OPORD = OPERATIONAL planning** (agent missions, swarm coordination)

Use Plan Mode for:


- Refactoring modules


- Database migrations


- API changes


- Library upgrades


- Technical debt reduction

Use OPORD for:


- Agent task execution


- Swarm coordination


- Security audits


- Revenue tracking


- Shift handoffs

**Both follow same philosophy**: Maximum clarity, minimum tokens, zero ambiguity.

---

## ⚖️ Governance Note

**Your law school rules control over all else.**
Plan Mode is a syntax layer for technical execution.
Legal/governance frameworks (Judge#6, compliance) take precedence.

When in doubt:


1. Law school rules first


2. OPORD operational format second


3. Plan Mode technical syntax third

---

## 📋 Quick Reference Card

```

PLAN MODE CHECKLIST:
□ Module/package header present
□ All actions imperative verbs
□ Lines <60 chars
□ Symbols used correctly (→, +, -, ?)
□ "Impl:" section for multi-module changes
□ "Unresolved Qs:" always present
□ "Options:" for decision forcing
□ No prose explanations (unless asked)
□ Scannable in <5 seconds

PASS CRITERIA:
✓ Can be parsed programmatically
✓ Human can execute without clarification
✓ Blockers surfaced explicitly
✓ Phase boundaries clear

```

---

**Status**: Ready for Cursor integration + MCP execution
**Version**: 1.0
**Last Updated**: 2025-11-22
