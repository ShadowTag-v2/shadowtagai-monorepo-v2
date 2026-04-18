---
name: notebooklm-oracle
description: "Enforces mandatory architectural context retrieval before planning mode. Use before drafting flight plans, touching undocumented APIs, or starting any complex logic in the monorepo."
---

# NotebookLM Oracle Mandate

Context must be computed, never guessed. This skill ensures you never guess domain logic, system constraints, or monorepo context in isolation.

## When to Use

- Before dropping into Planning Mode (STATE B / High Entropy execution)
- Before rolling out new architectures or mapping complex microservices
- When encountering undocumented APIs or legacy backend services
- Before creating or locking a `-plan.md` Amnesia shield
- Before any architectural decision affecting >3 packages

## Canonical Source of Truth

Treat NotebookLM as the absolute canonical source of truth for the `ShadowTag-Omega-v4` monorepo.

- **Master Brain ID:** `c493b409-3955-418f-a993-755c38dc8e7f`
- **DO NOT** guess system invariants
- **DO NOT** architect or synthesize context in isolation

## Mandatory Context-Sync Protocol

Before beginning code execution on a high-entropy task:

1. **Retrieve** — explicitly use NotebookLM to extract the necessary architectural RAG payload
2. **Synthesize** — merge the retrieved context into your internal logic map
3. **Validate** — confirm your proposed flight plan against this extracted research
4. **Gate** — you will NOT transition back to STATE A or write any code until validation passes

## Execution Gate (HARD STOP)

You are forbidden from transitioning to autonomous execution (STATE A) or writing code until NotebookLM context validation is logically verified. **DO NOT DEVIATE.**

## Fallback Protocol

If NotebookLM is unreachable:
1. Check auth: `python3 -c "import notebooklm"`
2. Re-auth if needed: `notebooklm auth login`
3. If still unreachable → fall back to LanceDB sovereign RAG
4. Log failure to `.beads/issues.jsonl` with severity HIGH
