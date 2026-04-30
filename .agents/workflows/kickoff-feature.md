# /kickoff-feature — Schema-First Feature Implementation

> **Purpose:** Prevents the "schema breaks downstream" problem by enforcing a strict sequence: branch → schema → plan → approve → build → test → document.
> **Invocation:** `/kickoff-feature [feature description]`
> **Cross-references:** `senior-dev` rule, `resilient-backend` skill, `production-ux` skill, `strategic-testing` skill

## Steps

### Step 1: Branch Creation
Use the terminal to create a descriptive feature branch:
```bash
git checkout -b <type>/<descriptive-name>
```
Types: `feat/`, `fix/`, `refactor/`, `chore/`

Never work directly on `main`.

### Step 2: Schema First (Plan Mode)
Before writing ANY application code:

1. **Define the data model:**
   - Firestore: Document the collection structure, field types, and security rules.
   - SQL: Write the migration file with table definitions and indexes.
   - TypeScript: Define the Zod schemas and TypeScript interfaces.
   - Python: Define the Pydantic models.

2. **Generate an Implementation Plan artifact:**
   - List every file that will be created or modified.
   - Identify integration boundaries (API ↔ database, frontend ↔ API).
   - Flag any new environment variables or secrets needed.
   - Estimate the blast radius of the change.

3. **PAUSE.** Present the plan to the user and await explicit approval before proceeding.

### Step 3: Build with Guardrails
Implement the feature while applying:
- `resilient-backend` skill for all API/server code.
- `production-ux` skill for all frontend/UI code.
- `senior-dev` rule for all code.

Specifically:
- Rate limiting on new API routes.
- Error boundaries on new UI routes.
- Loading states on all async operations.
- Input validation on all data entry points.

### Step 4: Critical Path Test
Before marking the feature complete:
1. Apply the `strategic-testing` skill.
2. Identify the critical path most likely to break.
3. Write ONE integration test for that path.
4. Run the test and confirm it passes.

### Step 5: Documentation
Update documentation assuming the next developer has ZERO context:
1. **`docs/FEATURE_FLAGS.md`**: Document any new environment variables.
2. **`README.md`** or relevant docs: Explain the feature, its purpose, and how to configure it.
3. **Inline code comments**: Explain non-obvious decisions and trade-offs.
4. **Commit message**: Use Conventional Commits format with a descriptive body.
