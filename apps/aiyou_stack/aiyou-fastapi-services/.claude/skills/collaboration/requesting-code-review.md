# Requesting Code Review

## When to Use

Before submitting code for review (pull request, code review, etc.). Use this checklist to ensure your code is review-ready.

## Pre-Review Checklist

### 1. Self-Review First

**Review your own code before asking others to review it.**

```
Self-Review Checklist:
[ ] Read through all changed files
[ ] Check for debug statements, console.logs
[ ] Verify no commented-out code
[ ] Check for TODOs that should be done
[ ] Look for obvious improvements
[ ] Ensure consistent formatting
[ ] Remove unnecessary changes
```

### 2. Tests Pass

**Never submit code with failing tests.**

```
Testing Checklist:
[ ] All unit tests pass
[ ] All integration tests pass
[ ] No test skipped (unless documented why)
[ ] New code has test coverage
[ ] Coverage didn't decrease
[ ] Tests are meaningful (not just for coverage)
```

### 3. Code Quality

**Clean code is easier to review.**

```
Quality Checklist:
[ ] No code duplication
[ ] Functions are focused (single responsibility)
[ ] Names are clear and descriptive
[ ] Complex logic is commented
[ ] No magic numbers (use constants)
[ ] Error handling is present
[ ] Edge cases are handled
```

### 4. Documentation

**Help reviewers understand the changes.**

```
Documentation Checklist:
[ ] PR description explains WHAT and WHY
[ ] Complex algorithms have comments
[ ] Public APIs have docstrings
[ ] README updated if needed
[ ] CHANGELOG updated
[ ] Migration guide if breaking changes
```

### 5. Scope

**Keep reviews focused and manageable.**

```
Scope Checklist:
[ ] PR addresses one concern (not multiple features)
[ ] Changed files < 10 (ideally)
[ ] Lines changed < 500 (ideally)
[ ] No unrelated changes
[ ] No reformatting unrelated code
```

## Writing a Good PR Description

### Template

```markdown
## Summary
[One paragraph: what does this PR do?]

## Why
[Why is this change needed? What problem does it solve?]

## Changes
- [High-level change 1]
- [High-level change 2]
- [High-level change 3]

## Testing
[How was this tested?]
- [ ] Unit tests added/updated
- [ ] Manual testing performed
- [ ] Tested in [environment]

## Screenshots (if UI changes)
[Before/after screenshots]

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented if so)
- [ ] Ready for review
```

### Example

```markdown
## Summary
Add CSV export functionality to user list page

## Why
Users need to analyze user data in Excel. Currently they screenshot or manually
copy-paste, which is error-prone. This PR adds a CSV export button that
downloads the currently visible user list.

## Changes
- Added `CSVExportService` for generating CSV from user data
- Added `/api/users/export` endpoint that respects current filters
- Added export button to `UserList` component
- Handles special characters (quotes, commas) correctly
- Includes comprehensive test coverage

## Testing
- [x] Unit tests added for CSV service (5 tests)
- [x] Unit tests added for API endpoint (3 tests)
- [x] Frontend tests added for export button (3 tests)
- [x] Integration test for full flow
- [x] Manually tested in Chrome, Firefox, Safari
- [x] Tested with 500 record dataset (completes in 1.2s)
- [x] Tested special characters in names and emails

## Performance
- Tested with up to 1000 records
- Response time: ~1.5s for 500 records
- Memory usage: stable (streaming response)

## Screenshots
[Screenshot of export button in UI]
[Screenshot of downloaded CSV in Excel]

## Checklist
- [x] All tests pass (158/158)
- [x] Documentation updated (user guide, API docs)
- [x] CHANGELOG.md updated
- [x] No breaking changes
- [x] Ready for review
```

## Preparing for Common Review Comments

### Anticipate Questions

```
Common Questions:
- Why did you choose this approach?
  → Document in PR description or code comments

- Why this library over alternatives?
  → Explain in comments or PR description

- What's the performance impact?
  → Include benchmarks in PR

- How do we test this?
  → Point to test files and test plan

- What happens if X fails?
  → Show error handling in code
```

### Address Known Issues

```
If you know something is imperfect:

BAD: Hope reviewers don't notice
GOOD: Call it out explicitly

Example:
> Note: The CSV generation currently loads all data into memory.
> This works fine for our current use case (max 1000 records), but
> if we need to support larger exports in the future, we should
> implement streaming. Tracked in #1234.
```

## Review Request Message

### Good Review Request

```
@reviewers: This PR adds CSV export to the user list.

Key areas to focus on:
1. CSV generation logic (src/services/csv_export.py) - does it handle edge cases?
2. API endpoint security (src/api/routes/users.py) - any auth/permission issues?
3. UI placement (src/components/UserList.tsx) - does it fit the design?

Note: The export is currently synchronous, which is fine for our use case
(<1000 records), but we may need async for larger datasets in the future.

Estimated review time: ~15 minutes
```

### Bad Review Request

```
BAD: "Please review"
BAD: "Done, merge when ready"
BAD: "Fixed the thing"

These don't help reviewers know:
- What changed
- What to focus on
- How long it'll take
- What decisions were made
```

## Making Review Easy

### 1. Small, Focused PRs

```
❌ HARD TO REVIEW: 2000 lines, 15 files, 3 features
✅ EASY TO REVIEW: 200 lines, 3 files, 1 feature

Split large work into multiple PRs:
- PR 1: Add CSV service (backend)
- PR 2: Add export endpoint (API)
- PR 3: Add export UI (frontend)
```

### 2. Clear Commit History

```
❌ BAD:
- "wip"
- "fix"
- "more fixes"
- "final fix"

✅ GOOD:
- "Add CSVExportService with special char handling"
- "Add /api/users/export endpoint"
- "Add export button to UserList component"
- "Add comprehensive test coverage"
```

### 3. Highlight Important Parts

```markdown
## Key Changes

### CSV Generation (HIGH PRIORITY)
`src/services/csv_export.py`
- Please review the escaping logic carefully
- Handles quotes, commas, newlines per RFC 4180

### Security (HIGH PRIORITY)
`src/api/routes/users.py`
- Verify permission checks are correct
- Export respects same auth as user list

### UI (MEDIUM PRIORITY)
`src/components/UserList.tsx`
- Standard button placement
- Follows existing patterns
```

### 4. Add Context

```python
# Context for reviewers:
# We use csv.writer() instead of manual string building because:
# 1. Handles escaping automatically (RFC 4180 compliant)
# 2. More maintainable
# 3. Less error-prone
# 4. Standard library (no dependencies)

def generate_csv(users):
    output = io.StringIO()
    writer = csv.writer(output)
    # ...
```

## Responding to Review Comments

### During Review

```
✅ GOOD RESPONSES:
- "Good catch! Fixed in commit abc123"
- "Great question. I chose X because Y. Thoughts?"
- "You're right, let me refactor this"
- "I'll create a follow-up issue for that"

❌ BAD RESPONSES:
- "That's not a bug"
- "Works on my machine"
- "This is good enough"
- "We can fix it later"
```

### After Review

```
When all comments addressed:
"@reviewer All comments addressed:
- Fixed escaping issue (commit abc123)
- Added error handling (commit def456)
- Refactored CSV service (commit ghi789)
- Ready for re-review"
```

## Red Flags (Fix Before Review)

```
🚩 Tests disabled or skipped
🚩 Debug statements (console.log, print, debugger)
🚩 Commented-out code
🚩 TODO comments that should be done
🚩 Temporary files committed (.DS_Store, *.swp)
🚩 Secrets or credentials in code
🚩 Failing tests
🚩 Linter errors
🚩 Merge conflicts
🚩 Unrelated changes
```

## Final Checklist

Before clicking "Request Review":

```
[ ] Self-reviewed all changes
[ ] All tests passing
[ ] Code is clean and documented
[ ] PR description is clear and complete
[ ] Scope is focused and reasonable
[ ] Known issues are documented
[ ] Review areas are highlighted
[ ] Commits are clean and logical
[ ] No red flags present
[ ] I would approve this PR if I were the reviewer
```

## Remember

- **Self-review first** - catch obvious issues yourself
- **Make it easy** - small, focused, well-documented PRs
- **Add context** - explain decisions and trade-offs
- **Highlight key areas** - guide reviewers to what matters
- **Be responsive** - address feedback promptly and professionally

**Good code reviews start with good review requests.**
