# Executing Plans: Batch Execution with Checkpoints

## When to Use

After writing a detailed implementation plan, use this skill to execute it systematically with progress tracking and rollback capability.

## Core Principles

1. **Follow the plan** - Execute steps in order
2. **Track progress** - Mark steps complete as you go
3. **Verify each step** - Test before moving to next step
4. **Create checkpoints** - Commit after logical groups
5. **Handle failures** - Know how to rollback

## Execution Process

### Phase 1: Review the Plan

Before starting, review the entire plan:

```
Checklist:
[ ] Read the full plan
[ ] Understand all steps
[ ] Check dependencies are ready
[ ] Verify tools/access available
[ ] Time-box: [X hours estimated]
```

### Phase 2: Execute in Batches

Group related steps into batches, execute batch, create checkpoint.

```
Batch 1: Backend Foundation
├─ Step 1: Create CSV service
├─ Step 2: Write CSV tests
└─ Checkpoint: Commit "Add CSV export service"

Batch 2: API Endpoint
├─ Step 3: Add export endpoint
├─ Step 4: Write endpoint tests
└─ Checkpoint: Commit "Add export API endpoint"

Batch 3: Frontend UI
├─ Step 5: Add export button
├─ Step 6: Implement download logic
└─ Checkpoint: Commit "Add export UI"

Batch 4: Integration & Testing
├─ Step 7: Integration tests
├─ Step 8: Manual testing
└─ Checkpoint: Commit "Complete export feature with tests"
```

### Phase 3: Verify Each Step

After completing each step:

```
Step Verification Checklist:
[ ] Code written as specified
[ ] Tests written and passing
[ ] No regressions (existing tests still pass)
[ ] Code reviewed (self-review)
[ ] Documented (comments, docstrings)
```

### Phase 4: Create Checkpoints

After each batch:

```
Checkpoint Checklist:
[ ] All batch steps complete
[ ] All tests passing
[ ] Code committed with clear message
[ ] Working state (could stop here if needed)
```

### Phase 5: Handle Issues

When something goes wrong:

```
Issue Response:
1. Stop and assess
2. Is it a blocker or can we work around?
3. Document the issue
4. Update the plan if needed
5. Decide: Fix now or defer?
```

## Example: Executing a Plan

### The Plan
```markdown
# Export Feature Implementation Plan

## Steps

### Backend
1. Create CSV service class in `app/services/csv_export.py`
2. Add tests in `tests/test_csv_export.py`
3. Add API endpoint in `app/api/routes/users.py`
4. Add endpoint tests in `tests/api/test_user_export.py`

### Frontend
5. Add export button to `src/components/UserList.tsx`
6. Add download logic to `src/services/userService.ts`
7. Add service tests in `tests/services/userService.test.ts`

### Integration
8. Integration tests in `tests/integration/test_export.py`
9. Manual testing
10. Documentation
```

### Batch 1: CSV Service

```
[BATCH 1: CSV Service Foundation]

Step 1: Create CSV service ✓
- Created app/services/csv_export.py
- Implemented generate_user_csv() method
- Handles escaping and formatting
- Self-review: ✓ Clean code, good naming

Step 2: Add CSV service tests ✓
- Created tests/test_csv_export.py
- Tests: basic data, special chars, empty, unicode
- All tests passing (4/4)
- Verified: No regressions (150/150 tests pass)

CHECKPOINT 1: Commit
git add app/services/csv_export.py tests/test_csv_export.py
git commit -m "Add CSV export service with tests

- Implement CSVExportService class
- Handle special characters and escaping
- Add comprehensive test coverage
- All tests passing"

Status: ✅ Checkpoint 1 complete
```

### Batch 2: API Endpoint

```
[BATCH 2: API Endpoint]

Step 3: Add API endpoint ✓
- Added /api/users/export to app/api/routes/users.py
- Uses CSVExportService from Step 1
- Returns CSV with correct headers
- Self-review: ✓ Error handling added

Step 4: Add endpoint tests ✓
- Created tests/api/test_user_export.py
- Tests: endpoint returns CSV, filters work, error cases
- All new tests passing (3/3)
- Verified: All tests passing (153/153)

CHECKPOINT 2: Commit
git add app/api/routes/users.py tests/api/test_user_export.py
git commit -m "Add user export API endpoint

- GET /api/users/export endpoint
- Supports same filters as user list
- Returns RFC 4180 compliant CSV
- Comprehensive test coverage
- All 153 tests passing"

Status: ✅ Checkpoint 2 complete
```

### Batch 3: Frontend

```
[BATCH 3: Frontend Implementation]

Step 5: Add export button ✓
- Updated src/components/UserList.tsx
- Added export button to toolbar
- Added loading state
- Self-review: ✓ Matches design system

Step 6: Add download logic ✓
- Updated src/services/userService.ts
- Added exportUsers() function
- Triggers download with correct filename
- Error handling for failed exports

Step 7: Add service tests ✓
- Created tests/services/userService.test.ts
- Tests: download trigger, filename, errors
- All new tests passing (3/3)
- Verified: All tests passing (156/156)

CHECKPOINT 3: Commit
git add src/components/UserList.tsx src/services/userService.ts tests/services/userService.test.ts
git commit -m "Add export UI and download logic

- Export button in UserList component
- exportUsers() service method
- File download with correct naming
- Loading and error states
- Full test coverage
- All 156 tests passing"

Status: ✅ Checkpoint 3 complete
```

### Batch 4: Integration & Polish

```
[BATCH 4: Integration Testing]

Step 8: Integration tests ✓
- Created tests/integration/test_export.py
- Tests full flow: UI → API → CSV → Download
- Verified filters applied correctly
- All integration tests passing (2/2)

Step 9: Manual testing ✓
[X] Export with no filters - Works
[X] Export with name filter - Works
[X] Export with date range - Works
[X] Names with commas - Works
[X] Names with quotes - Works
[X] Large dataset (500 records) - Works, 1.2s
[X] Empty dataset - Works, shows headers only
[X] Chrome - Works
[X] Firefox - Works
[X] Safari - Works

Step 10: Documentation ✓
- Updated docs/user-guide.md
- Added API docs in docs/api.md
- Updated CHANGELOG.md

CHECKPOINT 4: Commit
git add tests/integration/test_export.py docs/ CHANGELOG.md
git commit -m "Complete export feature with integration tests and docs

- Full integration test coverage
- Manual testing completed across browsers
- Documentation updated
- Feature ready for deployment
- All 158 tests passing"

Status: ✅ Checkpoint 4 complete

FEATURE COMPLETE ✅
```

## Tracking Progress

### Use a Checklist

```markdown
# Export Feature Progress

## Backend
- [x] Step 1: CSV service
- [x] Step 2: CSV tests
- [x] Step 3: API endpoint
- [x] Step 4: Endpoint tests

## Frontend
- [x] Step 5: Export button
- [x] Step 6: Download logic
- [x] Step 7: Service tests

## Integration
- [x] Step 8: Integration tests
- [x] Step 9: Manual testing
- [x] Step 10: Documentation

## Checkpoints
- [x] Checkpoint 1: CSV service complete
- [x] Checkpoint 2: API endpoint complete
- [x] Checkpoint 3: Frontend complete
- [x] Checkpoint 4: Feature complete
```

### Track in TODO Comments

```python
# TODO: Implementation Plan Progress
# [x] Step 1: CSV service
# [x] Step 2: CSV tests
# [x] Step 3: API endpoint
# [ ] Step 4: Endpoint tests  <- Currently here
# [ ] Step 5: Export button
```

## Handling Issues During Execution

### Issue: Unexpected Complexity

```
Plan Step: "Add export button" (estimated: 0.5h)
Reality: Need to refactor toolbar component first (adds 1.5h)

Response:
1. Document the issue
2. Update estimate: 0.5h → 2h
3. Update plan with new step:
   - Step 5a: Refactor toolbar component
   - Step 5b: Add export button
4. Continue execution
```

### Issue: Blocker Discovered

```
Plan Step: "Add API endpoint"
Blocker: CSV library has a bug with unicode

Response:
1. Document blocker
2. Research solutions:
   - Option A: Fix the library bug (4h)
   - Option B: Use different library (2h)
   - Option C: Implement custom CSV writer (6h)
3. Decision: Use different library (best ROI)
4. Update plan
5. Continue execution
```

### Issue: Test Failure

```
Step: "Add CSV service tests"
Issue: Test failing - special characters not escaped

Response:
1. Stop - don't continue to next step
2. Debug the issue (systematic debugging skill)
3. Fix the code
4. Verify tests pass
5. Update checkpoint
6. Continue to next step
```

## Batch Strategies

### Strategy 1: By Component

```
Batch 1: All backend work
Batch 2: All frontend work
Batch 3: Integration and testing

Pro: Clear separation
Con: Can't test end-to-end until late
```

### Strategy 2: By Feature Slice

```
Batch 1: Basic export (backend + frontend)
Batch 2: Add filters (backend + frontend)
Batch 3: Add error handling (backend + frontend)

Pro: End-to-end working early
Con: More context switching
```

### Strategy 3: By Risk

```
Batch 1: Risky/unknown parts first
Batch 2: Well-understood parts
Batch 3: Polish and testing

Pro: Discover issues early
Con: Might not have working feature until late
```

Choose based on:
- Team size (solo vs. team)
- Risk profile (known vs. unknown)
- Dependencies (parallel vs. sequential)

## Checkpoint Guidelines

### When to Create Checkpoints

Create a checkpoint when:
- ✅ Logical unit of work complete
- ✅ All tests passing
- ✅ Code is in working state
- ✅ Could pause work here if needed

Don't create checkpoint when:
- ❌ Tests failing
- ❌ Code incomplete
- ❌ Known bugs present
- ❌ Mid-refactor

### Good Checkpoint Commits

```bash
# ✅ Good: Clear, working state
git commit -m "Add CSV export service with tests

- Implement CSVExportService class
- Handle special characters and escaping
- Add comprehensive test coverage
- All 154 tests passing"

# ❌ Bad: Unclear, might not work
git commit -m "WIP export stuff"
```

## Progress Reporting

### Daily Standup Format

```
Yesterday:
- ✅ Completed Batch 1: CSV service (Steps 1-2)
- ✅ Completed Batch 2: API endpoint (Steps 3-4)
- Checkpoint: Backend complete, all tests passing

Today:
- [ ] Starting Batch 3: Frontend (Steps 5-7)
- Target: Complete export UI

Blockers:
- None
```

### Status Update Format

```
Export Feature Status Update

Progress: 60% complete (6/10 steps)

Completed:
✅ CSV service with tests
✅ API endpoint with tests

In Progress:
🔄 Frontend export button (80% done)

Upcoming:
⏳ Download logic
⏳ Integration tests

Timeline:
- Original estimate: 5.5h
- Time spent: 3.5h
- Remaining: ~2h
- On track for today ✓
```

## Rollback Strategy

### If Something Goes Wrong

```
Problem: Step 7 broke existing functionality

Rollback Options:

Option 1: Revert to last checkpoint
git reset --hard [checkpoint-3-commit]

Option 2: Fix forward
- Debug the issue
- Fix the code
- Verify tests pass
- Continue

Option 3: Shelve current work
git stash
- Work on fix separately
- Return to stash later

Choose based on:
- Severity (blocking vs. minor)
- Time (quick fix vs. long debug)
- State (checkpoint vs. mid-work)
```

## Remember

- **Follow the plan** - Don't skip steps
- **Verify each step** - Test before moving on
- **Create checkpoints** - Commit working states
- **Track progress** - Know where you are
- **Handle issues** - Document and adapt

**Systematic execution beats random coding every time.**
