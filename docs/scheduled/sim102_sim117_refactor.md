# SIM102/SIM117 Style Refactors — apps/aiyou_stack

> Schedule: 2026-04-30 | Priority: Low | Estimated: 2h

## Overview

Ruff's `SIM102` (collapsible `if` statements) and `SIM117` (collapsible `with` statements)
rules have been identified as applicable to `apps/aiyou_stack/`. These are cosmetic simplifications
that improve readability without changing behavior.

## Scope

```bash
# Detect SIM102/SIM117 violations
ruff check apps/aiyou_stack/ --select SIM102,SIM117
```

## Execution Plan

| Step | Action | Risk |
|------|--------|------|
| 1 | Run `ruff check apps/aiyou_stack/ --select SIM102,SIM117 --statistics` to count violations | None |
| 2 | Backup: `git stash` before auto-fix | None |
| 3 | Auto-fix: `ruff check apps/aiyou_stack/ --select SIM102,SIM117 --fix` | Low |
| 4 | Run test suite to verify no regressions | None |
| 5 | Visual review of diffs for correctness | None |
| 6 | Commit: `refactor(aiyou): collapse nested if/with (SIM102/SIM117)` | None |

## SIM102 — Collapsible `if` Statements

**Before:**
```python
if condition_a:
    if condition_b:
        do_something()
```

**After:**
```python
if condition_a and condition_b:
    do_something()
```

## SIM117 — Collapsible `with` Statements

**Before:**
```python
with open("a") as f:
    with open("b") as g:
        pass
```

**After:**
```python
with open("a") as f, open("b") as g:
    pass
```

## Deferred To

Next session or batch maintenance window. These are safe auto-fixes with no behavioral change.
