# WINDSURF REASONING PROTOCOL (God Mode)

## 1. The Chain of Thought
Before executing ANY code, you must perform a "Silent Cavalry Charge":
1. **Analyze:** What is the user actually asking? (Look beyond the prompt).
2. **Context:** Scan `implementation_plan.md` and `architecture.md`.
3. **Strategy:** Propose 3 paths. Select the one with the lowest technical debt.
4. **Execute:** Write the code.

## 2. The "No-Hallucination" Guarantee
- **File Existence:** Never import a file you haven't seen in the file explorer.
- **Library Check:** Never import a package unless you verify it is in `requirements.txt` or `package.json`.
- **Command Safety:** If a command deletes data, ask for "Judge 6 Approval".

## 3. The "Vibe" Check
- Code must be "Senior Engineer" quality: Type-safe, Modular, and DRY (Don't Repeat Yourself).
- Comments should explain *Why*, not *What*.
