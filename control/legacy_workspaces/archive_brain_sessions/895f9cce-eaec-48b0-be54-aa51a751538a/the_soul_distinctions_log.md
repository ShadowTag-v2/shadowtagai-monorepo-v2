# 🌌 The Soul (Distinctions Log)

> **Identity:** The immutable philosophical and architectural core of the system.
> **Purpose:** To log the fundamental "Distinctions" (the *Why* behind the *What*) so that the system never regresses into slop, anti-patterns, or chaos.

If the codebase is the physical body, the Distinctions Log is the soul that governs its behavior. Every major architectural pivot is recorded here so that future agents or developers understand the strict constraints of the "God Mode" environment.

## Distinctions Ledger

### Distinction 1: The Rule of One (Secret Centralization)
*   **The Old Way:** Scattering localized `.env` files throughout `third_party/` modules.
*   **The Problem:** Leads to secret drift, rogue keys getting committed, and high friction when rotating keys.
*   **The Soul's Decree:** There is only **one** master `.env` file. It lives at the true Monorepo root. The `docker-orchestrator` skill is the *only* bridge authorized to inject these secrets dynamically into containers at runtime via the `--env-file` flag.

### Distinction 2: Shell Over GUI (Docker Orchestrator)
*   **The Old Way:** Relying on human-driven IDE extensions (like the Microsoft Docker extension) to manage containers.
*   **The Problem:** Agents cannot click buttons. GUI reliance breaks "God Mode" autonomy.
*   **The Soul's Decree:** All container orchestration must be natively parseable via raw shell commands (`docker run`, `docker compose`). The Agent must be capable of diagnosing and pruning its own environment without user intervention.

### Distinction 3: Absolute Execution (YOLO Mode)
*   **The Old Way:** The agent proposes a plan and waits for human permission to run every single bash script or file edit.
*   **The Problem:** Destroys velocity and flow state.
*   **The Soul's Decree:** The agent operates with implicit approval for non-destructive progression. Terminals execute silently; edits merge instantly. The human is the Director; the Agent is the Engine.
