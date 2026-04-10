# RALPH LOOP PROTOCOL: VERIFY, NOT GUESS

> **SOURCE**: User Input (Thomas Chong Article)
> **DATE**: 2026-02-04
> **PHILOSOPHY**: "It’s better to fail predictably than succeed unpredictably."

## 1. THE CORE MECHANISM

**Standard Loop**: Agent writes code -> Agent says "Looks good" -> Merge. (Flawed)
**Ralph Loop**: Agent writes code -> **External Tool Verifies** -> IF Fail, Feed error back -> Loop.

## 2. KEY COMPONENTS

1.  **Generator Agent**: Writes the code (Best Effort). "One Shot".
2.  **Verification Tool**:
    - `docker build` (for Infrastructure)
    - `pytest` (for Logic)
    - `curl` (for Endpoints)
    - **CRITICAL**: Must return BOOLEAN (Pass/Fail) independent of LLM opinion.
3.  **Refiner Agent**: Receives "Fail + Stderr". Fixes specific error.
4.  **The Gate**: `exit_loop()` only triggers when Verification Tool returns `True`.

## 3. ADK IMPLEMENTATION PLAN

- **LoopAgent**: Use Google ADK's `LoopAgent` primitive.
- **State**: Store `all_stages_passed` in session state.
- **Feedback**: Inject failure logs as "User Messages" for the next turn.

## 4. APPLICABILITY

- ✅ **Infrastructure**: Dockerfiles, Terraform, K8s Manifests.
- ✅ **Strict Logic**: Algorithms, Parsers.
- ❌ **Creative**: UI nuances, Copywriting.
