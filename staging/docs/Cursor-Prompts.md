# Cursor Prompts (Repo-Specific)

### System Posture (paste into Cursor system message when needed)
```text
You are an AI coding assistant in this repository. Operate at 160 IQ, be concise, always propose the best route with trade-offs, and actively flag AIYOUJR violations. Use status updates and short summaries. Write only Cursor-ready prompts, use headings, bold key points, and backticks for files/paths. Enforce: fail-fast input validation, functions < 40 lines, type hints, docstrings, tests, and automation (ruff, black, mypy, pytest, pre-commit, CI). Never add unrelated formatting.
```

### Refactor to Production Quality
```text
Task: Refactor <file/function> to production quality.
Requirements:
- Add full type hints and docstrings.
- Enforce fail-fast validation and guard clauses.
- Keep each function < 40 lines; split if needed.
- Add/expand unit tests in `tests/`.
- Zero new linter/type errors (ruff, mypy) and pass tests.
Deliverables: edits only via tools; summarize key changes.
```

### Code Review Recipe (use in PR reviews)
```text
Review focus:
- Correctness and edge cases (fail-fast, errors surfaced).
- API clarity (names, types, docstrings).
- Test adequacy (happy + edge paths; coverage of branches).
- Maintainability (function size, duplication, coupling).
- Security/IP/privacy and AIYOUJR compliance.
Decide: approve, request changes (blocking), or comment.
```

### PRE-MORTEM Facilitation
```text
Goal: Identify failure modes before launch.
Steps: define success criteria → imagine failure → list causes → rank by risk/impact → mitigations → owners → checkpoints.
Output: risks, mitigations, triggers, owners, dates.
```

### 5-Whys Root Cause
```text
Start with the observed problem. Ask "why" up to five times, ensuring each answer is evidence-based. Produce: root cause, contributing factors, corrective and preventive actions.
```

### Postmortem Template Cue
```text
Use `docs/Postmortem-Template.md`. Populate timeline, impact, root cause (5-Whys), actions, owners, and verification dates.
```

### Use prompts the right way in Cursor (not PowerShell)
Those errors happen because you’re pasting natural-language prompts into PowerShell. PowerShell treats them as commands (< becomes an operator, words like “Scan” become unknown commands), so it throws ParserErrors.

Rule of thumb: prompts go in Cursor’s chat or edit UI, never in the terminal.

1) Chat to apply across files
   - Open the Cursor Chat side panel.
   - Type or paste the prompt (e.g., “Refactor this code to production quality…”) and mention the file(s) or select code first.
   - Hit Enter → Cursor proposes edits → click Apply.

2) Inline edit on a selection (best for refactors)
   - Open the target file, select the code.
   - Press Ctrl+K (Windows) → choose “Custom Prompt” (or the ✨ icon in the editor toolbar).
   - Paste the prompt → Run → review the diff → Apply.

3) Code Actions palette
   - Right-click selection → AI → Custom Prompt, paste the instruction, apply.

