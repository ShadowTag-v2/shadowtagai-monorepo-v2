# The Simplicity Doctrine

> **"Simplicity is a prerequisite for reliability."** — Edsger W. Dijkstra
>
> **"Simplicity is not an objective in art, but one achieves simplicity despite oneself, as one approaches the real meaning of things."** — Constantin Brancusi
>
> **"Simplicity is the ultimate sophistication."** — Leonardo da Vinci

This document codifies the architectural philosophy of the UphillSnowball monorepo, derived directly from Rich Hickey's body of work: *Simple Made Easy* (2011), *Hammock-Driven Development* (2010), *Effective Programs* (2017), *Clojure Made Simple* (2015), and his 2026 "Thanks AI" perspective.

**Every developer and AI agent working in this monorepo MUST read and internalize this document before making architectural decisions.**

---

## 1. Simple ≠ Easy

This is the foundational distinction. Getting this wrong produces all downstream failures.

| | **Simple** | **Easy** |
|---|---|---|
| **Definition** | One fold/braid. Un-entangled. Objective. | Near, familiar, at-hand. Subjective. |
| **Measure** | How many things are braided together? | How close is it to my current skill set? |
| **Who it serves** | The *artifact* (the running system) | The *programmer* (at the keyboard today) |
| **Temporal cost** | Low maintenance burden over years | High maintenance burden over years |
| **Example** | A pure function that transforms data | A 2000-line class that "does everything" |

### The Cardinal Rule
> **Choose simple over easy. Always.**
>
> "We can be unfamiliar with something and yet it's simple. Hard to learn is NOT the same as complex."

### Applied to This Monorepo
- ❌ **Easy**: One giant `orchestrator.py` that handles routing, business logic, error handling, and database calls.
- ✅ **Simple**: Separate modules — `routes/`, `services/`, `errors/`, `db/` — each handling ONE concern.

---

## 2. Complecting: The Cardinal Sin

**Complect** (v.): To braid together. To interleave orthogonal concerns into a single construct.

> "Every time I encounter a COMPLECTED artifact in this codebase, I know that someone chose EASY over SIMPLE."

### The Complecting Checklist

Before adding code, verify you are NOT braiding together any of these pairs:

| Concern A | Concern B | Complected Pattern | Simple Alternative |
|---|---|---|---|
| State | Identity | Mutable objects | Values + managed references |
| What | How | Implementation in interface | Protocols/interfaces + implementations |
| When | Who | Synchronous coupling | Async messages / queues |
| Data shape | Container name | `class Person { name, email }` | `{:person/name "..." :person/email "..."}` — semantics on attributes |
| Policy | Mechanism | Business rules in route handlers | Service layer + pure functions |
| Value | Time | `user.name = "new"` overwrites | Immutable events; append-only logs |

### Smells of Complecting in Our Codebase
1. **Files importing from >8 modules** → likely braiding multiple concerns
2. **Functions >50 lines** → doing more than one thing
3. **Raw `fetch()` with inline business logic** → complecting HTTP with domain logic
4. **`console.log` scattered through production** → complecting debugging with runtime
5. **Hardcoded `localhost:8080`** → complecting config with code

---

## 3. The Hammock Protocol

> "Most bugs are misconception bugs. You had the wrong idea about how the system should work. No amount of testing catches a wrong idea executed perfectly."

### Before Writing Code: Load → Hammock → Code

1. **State the Problem** (on paper, not in code): What EXACTLY are you trying to accomplish?
2. **Survey the Landscape**: What solutions already exist? What are at least 2 alternative approaches?
3. **Identify the Tradeoffs**: Every design choice eliminates other possibilities. Name what you're giving up.
4. **Sleep On It**: Hickey's "background mind" concept. Load up the problem, step away, let it percolate.
5. **Then Code**: The implementation should feel like transcription, not discovery.

### Applied to This Monorepo
- **Invariant #76 (Pre-Agent Protocol)** already enforces this for tasks >100 LOC.
- This Doctrine extends it: **ALL architectural decisions** must pass through the Hammock Protocol, regardless of LOC count.

---

## 4. Effective Programs: Information Over Logic

> "For me, programming is about making computers effective in the world. Being effective is mostly not about computation, but about generating predictive power from information."

### The Situated Programs Test

Our applications are **situated programs** — they:
- Run continuously (not one-shot lambdas)
- Deal with real-world irregularity ("Two-for-Tuesday" exceptions)
- Interact with people, databases, and other systems
- Must be maintained over years, not days

This means:
1. **Information processing dominates logic.** The fancy algorithm is 10% of the system. The 90% is getting data in, transforming it, and getting results out. Invest accordingly.
2. **Generic data representations win.** Maps, vectors, and plain data structures travel over wires, compose freely, and don't impose "parochial" type systems on every consumer.
3. **Names dominate semantics.** `{person_name: "Erik"}` communicates. `string` does not. Attribute names carry meaning; container names do not.

### What This Means for Our Code
- Prefer JSON/dict structures with meaningful keys over rigid class hierarchies
- When designing APIs: think "what data crosses the wire?" not "what objects do I need?"
- The `libs/core/http.ts` wrapper exists to separate the HOW (fetch mechanics) from the WHAT (domain data)

---

## 5. Puzzles vs. Problems

> "From an endorphin standpoint, solving puzzles and solving problems is the same. But solving puzzles is NOT solving problems."

### The Test
Before any refactoring or new implementation, ask:

1. **Am I solving a PROBLEM** (making the system more effective in the world)?
2. **Or am I solving a PUZZLE** (making the code "elegant" in a way that only pleases me)?

| Puzzle (Reject) | Problem (Pursue) |
|---|---|
| "Let me type-safe this with 12 generics" | "Users are seeing stale data" |
| "I can make this a monad combinator" | "This endpoint takes 4 seconds to load" |
| "Let me refactor to use the visitor pattern" | "New features require changing 15 files" |
| "Let me add another abstraction layer" | "This function has 3 bugs because it does too much" |

---

## 6. AI as Junior Developer (2026 Perspective)

> "If an AI can easily do your work, it is because your work is repetitive and 'what has already been written countless times before'."

### The AI Constraint
- **Treat AI as a junior developer**: pair with it, review its output, maintain responsibility
- **AI excels at**: boilerplate, repetitive patterns, test generation, documentation
- **AI fails at**: novel architecture, domain-specific judgment, "Two-for-Tuesday" exceptions
- **The human role**: Architectural decisions, domain modeling, exception handling, system design

### Applied to This Monorepo
- **Invariant #40 (Senior Dev Override)**: "Ask yourself: What would a senior, perfectionist dev reject?"
- **Invariant #77 (Pilot vs. Passenger)**: The agent is in PILOT mode — it decides WHEN the system is ready.
- **This Doctrine adds**: Before accepting ANY AI-generated architecture, run the Hammock Protocol. AI generates constructs; humans validate simplicity.

---

## 7. Enforcement

This doctrine is NOT aspirational. It is enforced by:

| Mechanism | What It Catches |
|---|---|
| `dead-code-audit.sh` Phase 6e | Files importing from >8 modules (complecting) |
| `dead-code-audit.sh` Phase 6f | Functions >50 LOC (doing too much) |
| `dead-code-audit.sh` Phase 6b | Monolithic files >500 LOC |
| **Invariant #91** | 500 LOC ceiling + service layer extraction |
| **Invariant #90** | 10 Anti-Vibe-Code patterns |
| **Invariant #93** | This doctrine as a mandatory reference |
| **Pre-Action Memory Gate** | Requires LOCKED state before any repo-wide action |
| **NotebookLM Protocol** (`rule-49`) | Session knowledge not archived to Master Brain; DevKnowledge MCP not consulted before planning |
| **ATP 5-19 Process Skeleton** | Risk decisions not scored through the 7-step ATP 5-19 framework (Judge #6's stable substrate) |

---

## 8. The Decision Framework

When making ANY architectural choice, score it against these five questions:

1. **Simple?** — Is this one-fold? Does it have a single purpose? Would removing it break exactly one thing?
2. **Decomplected?** — Is this orthogonal to its neighbors? Can I change this without changing anything else?
3. **Effective?** — Does this make the system more effective in the world for end users?
4. **Information-first?** — Am I working with generic data, or have I created a parochial type?
5. **Problem, not puzzle?** — Am I solving an actual user/system problem, or scratching an intellectual itch?

A "no" to ANY of these is a **design smell**. Stop. Hammock. Reconsider.

---

## References

- [Simple Made Easy](https://github.com/matthiasn/talk-transcripts/blob/master/Hickey_Rich/SimpleMadeEasy.md) — InfoQ 2011
- [Hammock-Driven Development](https://github.com/matthiasn/talk-transcripts/blob/master/Hickey_Rich/HammockDrivenDev.md) — Clojure/Conj 2010
- [Effective Programs](https://github.com/matthiasn/talk-transcripts/blob/master/Hickey_Rich/EffectivePrograms.md) — Clojure/Conj 2017
- [Clojure Made Simple](https://github.com/matthiasn/talk-transcripts/blob/master/Hickey_Rich/ClojureMadeSimple.md) — Java One 2015
- Rich Hickey on AI (2026) — Reddit r/programming
