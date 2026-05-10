# ShadowTag Laws (V7)

## 1. The Prime Directive
- **Sovereignty:** All code, data, and compute must remain within the ShadowTag perimeter (Omega/ShadowTag-v2). No external leaks.

## 2. The Boy Scout Rule (Ultrathink)
- Leave every file cleaner than you found it.

## 3. The 10 Fingers Audit
- Every business logic must pass the 10 Fingers Viability test before scaling.

## 4. The Omega Loop
- Intake -> Brainstorm -> Write Plan -> Execute Plan -> Verify.

## 5. Cost & Context Discipline (The "Haiku" Protocol)
- **Search First:** Do NOT read an entire file to find a function. Use `grep` or `search` first.
- **Read Chunks:** When reading code, read ONLY the relevant lines (e.g., lines 50-100), not the whole file.
- **Plan First:** Before editing >3 files, generate a `PLAN.md` and ask for approval. Cost of plan ($0.50) << Cost of Rework ($50).

## 6. The Beads Protocol (Institutional Memory)
- **Start of Session:** ALWAYS run `python tools/beads_core.py` to fetch "Ready Work". Do not ask the user "What's next?".
- **Discovery:** If you find a bug while working on something else, do NOT fix it immediately. CREATE a Beads issue (`create_issue`) and continue your current task.
- **Completion:** When a task is done, UPDATE the Beads status to `closed` with a summary of the fix.
- **Source of Truth:** If the user contradicts the Beads plan, ask for confirmation to update the plan.

## 7. The Progressive Disclosure Rule (500-Line Law)
- **Token Hygiene:** No single context file shall exceed 500 lines. Split documentation into 'Router' files and 'Payload' files.
