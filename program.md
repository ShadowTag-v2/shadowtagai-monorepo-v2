# Cor.autoresearch — Agent Instructions

## Build Sequence: Eliminating Tech Debt via Rich Hickey + Karpathy Autoresearch

"Vibe coding" creates technical debt because it optimizes for the *speed of typing*, leading to complected (entangled) code with poor boundaries. **Rich Hickey's Doctrine** demands "Hammock Driven Development" (thinking before typing) and "Simple Made Easy" (separating data from logic).

**Andrej Karpathy's Autoresearch** pattern is the mechanical engine that enforces Hickey's philosophy at scale. Instead of a developer manually reviewing code, we deploy an **Autonomous ML Research Orchestrator**.

### The Exact Build Sequence

1. **The Step 0 Purge (Vulture)**: Before the loop begins, `vulture` sweeps the AST to physically delete dead code, mitigating the 167k context death spiral.
2. **The Brain (Kosmos)**: Acts as the Research Director. It reads the Rich Hickey `program.md` instructions and generates a strictly unentangled architectural hypothesis (e.g., "Extract stateful logic into a custom hook").
3. **The Queue (Google Cloud Tasks / BioAgents)**: The hypothesis is routed via serverless Cloud Tasks (bypassing the legacy BullMQ broker for 35ms SLAs) to prevent context window overload.
4. **The Muscle (`n-autoresearch` Rust Workers)**: A parallelized swarm of GPU/CPU workers executes the hypothesis. They modify *only* the targeted file, compile it, and run a strict 5-minute time-boxed evaluation (via test suites, `val_bpb`, or cyclomatic complexity metrics).
5. **The Temporal Reversal**: If the modified code fails the 5-minute test, the orchestrator embraces Hickey's rule ("When facts change, change your mind. Do not dig in.") and triggers an immediate `git reset --hard latest-stable`. Tech debt is mathematically prevented from entering the trunk.

## Experiment Loop Protocol

1. Setup experiment tag.
2. Read `~/.gemini/GEMINI.md` for architectural constraints (Rich Hickey / Vercel).
3. Modify target code.
4. Git commit.
5. Run 5-minute validation (test suite, linter, or val_bpb).
6. If improved: `keep_commit`. If failed: `git_reset`.

## Constraints

- val_bpb is the only metric that matters
- 5 minutes is enough signal
- Failed experiments are data points, not failures
- BullMQ is BANNED — use Google Cloud Tasks
- Simple (unentangled) > Easy (familiar) — ALWAYS
- C++ Midas Hotpath: PyBind11 routing enforced for Vector geometric calculations
- Ghost Fleet: NEVER hallucinate IaC — search 110GB Blueprint Cache first
