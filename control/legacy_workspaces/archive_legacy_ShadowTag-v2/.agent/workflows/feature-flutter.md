---
description: Implements new Flutter features using multi-agent orchestration workflow with enterprise-grade security, performance, and testing
---

# /feature-flutter: Flutter Feature Implementation Protocol

**Trigger:** User request to build a new Flutter feature or screen.
**Context:** This workflow enforces "Antigravity Rule 1: Workflow-First Development" and "Rule 12: Stitch Integration".

## Phase 0: Discovery & Scaffolding (Mandatory)

1.  **Stitch Detection:**
    - Scan for `stitch_*` folders in project root.
    - If found, map to `lib/screens/` destinations.
2.  **Task Initialization:**
    - Create/Update `task.md`.
    - Mark "Phase 0" as In-Progress.
3.  **Agent Handoff:**
    - **INVOKE:** `@grand-architect-flutter`
    - **Instruction:** "Analyze the request and `stitch_*` assets (if any). Generate a detailed `implementation_plan.md` covering: Architecture, State Management, Navigation, and Testing strategy."

## Phase 1: Implementation (The Builder)

1.  **Plan Approval:** Wait for user approval of `implementation_plan.md`.
2.  **Scaffolding:**
    - Create directories: `lib/features/<feature>/data`, `domain`, `presentation`.
3.  **Stitch Conversion (If applicable):**
    - **INVOKE:** `@stitch-converter-flutter`
    - **Instruction:** "Convert `stitch_dashboard/code.html` to a Flutter Widget `lib/features/dashboard/presentation/dashboard_screen.dart` using our Design System tokens."
4.  **Core Logic:**
    - Implement Models, Repositories, Providers.

## Phase 2: Quality Assurance (The Critic)

1.  **Security Audit:**
    - **INVOKE:** `@security-specialist-flutter`
    - **Instruction:** "Audit the new feature for OWASP Mobile Top 10 vulnerabilities (Storage, PiP, Intent Injection)."
2.  **Accessibility Check:**
    - **INVOKE:** `@a11y-enforcer-flutter`
    - **Instruction:** "Verify Semantics, tap targets (48x48), and color contrast."
3.  **Test Generation:**
    - **INVOKE:** `@test-generator-flutter`
    - **Instruction:** "Generate Widget Tests (Goldens) and Unit Tests for the Repository."

## Phase 3: Verification & Closure

1.  **Run Tests:** `flutter test`
2.  **Analyze:** `flutter analyze`
3.  **Commit:** Stage and commit with Conventional Commits.
4.  **Update Task:** Mark all as Complete in `task.md`.
