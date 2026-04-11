# Rule 44: Edit Safety and Self-Correction Protocol

> Derived from: iamfakeguru/claude-md, anthropics/claude-code AGENTS.md, repowise-dev verification-specialist

## Edit Safety

1. Before every file edit: re-read the file
2. After editing: read it again
3. The Edit tool fails silently on stale old_string matches

## Rename/Signature Change Protocol

You have grep, not an AST. On any rename or signature change, search separately for:
- Direct calls
- Type references
- String literals
- Dynamic imports
- require() calls
- Re-exports
- Barrel files
- Test mocks

Assume grep missed something. Verify exhaustively.

## Never Delete Without Verification

Never delete a file without verifying nothing references it.

## Self-Correction Loop

1. After any correction from the user: log the pattern to gotchas/lessons
2. Convert mistakes into rules
3. Review past lessons at session start
4. If a fix doesn't work after two attempts: STOP
5. Read the entire relevant section top-down
6. State where your mental model was wrong

## Verification Evidence Standard (from repowise verification-specialist)

Every verification check MUST include:
- **Command run**: The exact command executed
- **Output observed**: The raw output (not a summary)
- **Result**: PASS or FAIL with Expected vs Actual

Bad example (will be rejected):
```
Check: API returns correct data
Command: (reviewed the handler source code)
Output: The logic appears correct
Result: PASS
```
This contains no executed command and no real output. It proves nothing.

## Planning Protocol

- When asked to plan: output only the plan. No code until told to proceed.
- When given a plan: follow it exactly. Flag real problems and wait.
- For non-trivial features (3+ steps or architectural decisions): interview about implementation, UX, and tradeoffs before writing code.
- Never attempt multi-file refactors in one response. Break into phases of max 5 files.
