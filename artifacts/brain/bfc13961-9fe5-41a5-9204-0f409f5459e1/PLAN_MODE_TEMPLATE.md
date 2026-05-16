# PLAN MODE STYLE GUIDE (v1.0)

**Purpose**: A universal schema for concise, auto-parsable plans.
**Principles**: Sacrifice grammar for concision. One line = one action. Surface blockers last.

---

## 📐 Structure Template

```markdown
<package or module>:
- <action> → <target>
- <next action> → <target>
- <decision> // brief note

Impl:
- <approach summary>
- <interim strategy>
- <phase boundary>

Unresolved Qs:
- <question 1>?
- <decision 2>?

Options:
1. Proceed + auto-apply
2. Proceed + manual approve
3. Hold + plan
```

---

## ✍️ Style Rules

| Rule | Example | Rationale |
| :--- | :--- | :--- |
| **Drop filler words** | `change handler → async wrapper` | High signal/token ratio |
| **Prefer `→` over `=`** | `opts.db → opts.adapter` | Clear directionality |
| **No punctuation** | `update params → include adapter` | Cleaner diffs |
| **Imperative Intention** | `add`, `remove`, `refactor` | Unambiguous |
| **<60 chars/line** | Fits split views | Fast scanning |

---

## 🧩 Syntax Keys

*   `→` : Transform / Migrate
*   `=` : Set / Define
*   `+` : Add / Include
*   `-` : Remove / Deprecate
*   `?` : Unresolved / Decision needed
*   `//`: Inline note
*   `⚠️`: Risk / Dependency

---

## 🧭 Cursor Command Integration

Add this to your System Prompt or `.cursor/rules.json`:

```text
Rules:
- Use PLAN MODE format
- One action per line
- End with 'Unresolved Qs'
- Use 'Impl:' if >1 module affected
- No prose explanations unless asked
```
