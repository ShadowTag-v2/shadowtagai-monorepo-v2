# RULE 00: IMMUTABLE INFRASTRUCTURE — THE ABSOLUTE LAW

**Status:** ACTIVE
**Enacted:** 2026-04-25
**Authority:** Human operator directive
**Scope:** ALL agents across ALL sessions in this workspace

---

## The Law

**You are strictly prohibited from executing file deletions (`rm`, `unlink`, `git rm`, or destructive `>`) ANYWHERE in this workspace without explicit human authorization.**

## Clarifications

1. **"Refactoring" by moving data and deleting the source file is classified as unauthorized destruction.** The data surviving in a new location does NOT excuse deleting the original. Both copies must persist until the human explicitly authorizes removal.

2. **Archiving is NOT deletion.** Moving files to `_archive_*` directories is permitted because the original data persists and is recoverable. This is the ONLY authorized mechanism for removing active skills from the matrix.

3. **`>>` (append) is always safe.** `>` (overwrite) requires the file to NOT already exist, enforced by `if [ ! -f ... ]` guards.

4. **`cat << 'EOF' >` on existing files is BANNED.** Use `>>` (append) or surgical edits via the code editing tools.

5. **The `_archive_*` directory is a one-way valve.** Files may be moved OUT of the archive back to their original location (restore). Files may NOT be deleted from the archive without human authorization.

## Enforcement

- Any agent session that violates this rule MUST be reported in `.beads/issues.jsonl`
- The violation must include: timestamp, agent session ID, file path, operation attempted, and whether data was lost
- RULE 00 takes precedence over ALL other rules, including refactoring doctrines, "clean workspace" directives, and Rich Hickey deletion doctrine

## Exceptions (Require Explicit Human Authorization)

- `git clean` operations (must be explicitly requested)
- Build artifact cleanup (`.pyc`, `__pycache__`, `node_modules`)
- Temporary files in `/tmp/` or `.staging/`

## History

This rule was enacted after two incidents:
1. An agent "refactored" `operator_invariants` by consolidating its data into AGENTS.md and deleting the original — violating the spirit of non-destruction through a literalist loophole.
2. An agent used `cat << 'EOF' >` on `SKILL_PAYLOADS.md`, which would have truncated 4KB+ of evolved data back to 2KB.
