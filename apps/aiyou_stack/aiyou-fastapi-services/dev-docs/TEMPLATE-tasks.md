# [Feature Name] - Task Checklist

**Feature:** [Feature Name]
**Status:** [Not Started / In Progress / Completed]
**Started:** [Date]
**Target Completion:** [Date]

---

## Quick Status

**Overall Progress:** [X / Y] tasks completed ([XX%])

**Current Phase:** [Phase Name]

**Last Updated:** [Date/Time]

**Blockers:** [None / Description of any blocking issues]

---

## Phase 1: [Phase Name]

**Status:** [Not Started / In Progress / Completed]
**Progress:** [X / Y] tasks completed

### Setup and Prerequisites

- [ ] Create project structure for [component]
- [ ] Install required dependencies: [list]
- [ ] Set up environment variables in `.env`
- [ ] Create database migrations (if needed)

### Core Implementation

- [ ] **Task 1:** [Specific, actionable task]
  - Files: `[path/to/file.py]`
  - Details: [Additional context if needed]
  - Depends on: [Prerequisites]

- [ ] **Task 2:** [Another specific task]
  - Files: `[path/to/file.py]`
  - Details: [Context]

- [ ] **Task 3:** [Third task]
  - Files: `[list of files]`

### Testing

- [ ] Write unit tests for [component]
  - Test file: `tests/unit/test_[feature].py`
  - Coverage target: [XX%]

- [ ] Write integration tests for [component]
  - Test file: `tests/integration/test_[feature].py`

- [ ] Verify all Phase 1 tests pass
  - Command: `pytest tests/ -k "phase1"`

### Documentation

- [ ] Add docstrings to all new functions/classes
- [ ] Update API documentation (OpenAPI/Swagger)
- [ ] Document any new configuration options

### Phase 1 Validation

- [ ] Code review completed
- [ ] All tests passing
- [ ] Type checking passes: `mypy [files]`
- [ ] Code formatted: `black [files]`
- [ ] No lint errors: `flake8 [files]`
- [ ] Performance targets met: [specific metrics]

**Phase 1 Completed:** [ ] Yes / Date: [_______]

---

## Phase 2: [Phase Name]

**Status:** [Not Started / In Progress / Completed]
**Progress:** [X / Y] tasks completed

### Core Implementation

- [ ] **Task 1:** [Specific task]
  - Files: `[path/to/file.py]`
  - Depends on: Phase 1 completion

- [ ] **Task 2:** [Another task]
  - Files: `[files]`
  - Details: [Context]

- [ ] **Task 3:** [Third task]
  - Files: `[files]`

### Integration

- [ ] Integrate [Component A] with [Component B]
  - Files: `[integration files]`
  - Test integration with: [test description]

- [ ] Add error handling for [scenarios]
- [ ] Implement validation for [inputs]

### Testing

- [ ] Write integration tests
  - Test file: `tests/integration/test_[feature]_phase2.py`

- [ ] Test error scenarios:
  - [ ] Invalid input handling
  - [ ] Network failure scenarios
  - [ ] Database error handling

- [ ] Verify all Phase 2 tests pass

### Documentation

- [ ] Update context.md with Phase 2 decisions
- [ ] Document integration points
- [ ] Add usage examples

### Phase 2 Validation

- [ ] All tests passing
- [ ] Integration verified
- [ ] Error handling validated
- [ ] Performance acceptable

**Phase 2 Completed:** [ ] Yes / Date: [_______]

---

## Phase 3: [Phase Name]

**Status:** [Not Started / In Progress / Completed]
**Progress:** [X / Y] tasks completed

### Core Implementation

- [ ] **Task 1:** [Specific task]
  - Files: `[files]`

- [ ] **Task 2:** [Another task]
  - Files: `[files]`

### Optimization and Polish

- [ ] Performance optimization:
  - [ ] [Specific optimization 1]
  - [ ] [Specific optimization 2]

- [ ] Security hardening:
  - [ ] Input validation review
  - [ ] Authentication/authorization verification
  - [ ] Security scan: [tool/process]

- [ ] Code cleanup:
  - [ ] Remove debug code
  - [ ] Remove TODO comments
  - [ ] Refactor any code smells

### Testing

- [ ] End-to-end testing
  - Test file: `tests/e2e/test_[feature]_e2e.py`

- [ ] Load testing (if applicable)
  - Tool: [locust / k6 / other]
  - Target: [requests per second]

- [ ] Manual testing checklist:
  - [ ] [Manual test scenario 1]
  - [ ] [Manual test scenario 2]
  - [ ] [Manual test scenario 3]

### Documentation

- [ ] Complete API documentation
- [ ] Update CLAUDE.md with new feature info
- [ ] Create user-facing documentation (if needed)
- [ ] Update README if necessary

### Phase 3 Validation

- [ ] All tests passing (unit + integration + e2e)
- [ ] Performance targets met
- [ ] Security review completed
- [ ] Documentation complete

**Phase 3 Completed:** [ ] Yes / Date: [_______]

---

## Final Validation and Deployment

**Status:** [Not Started / In Progress / Completed]

### Pre-Deployment Checklist

- [ ] **Code Quality:**
  - [ ] All tests passing: `pytest`
  - [ ] Type checking passes: `mypy services/`
  - [ ] No lint errors: `flake8 services/`
  - [ ] Code formatted: `black --check services/`
  - [ ] Import sorting verified: `isort --check services/`

- [ ] **Testing:**
  - [ ] Unit test coverage ≥ [target]%
  - [ ] Integration tests passing
  - [ ] E2E tests passing
  - [ ] Manual testing completed

- [ ] **Security:**
  - [ ] Security review completed
  - [ ] No sensitive data in code/logs
  - [ ] Authentication/authorization verified
  - [ ] Input validation comprehensive

- [ ] **Performance:**
  - [ ] Load testing completed
  - [ ] Performance targets met
  - [ ] No memory leaks detected
  - [ ] Database queries optimized

- [ ] **Documentation:**
  - [ ] API documentation complete
  - [ ] Code documentation (docstrings) complete
  - [ ] CLAUDE.md updated
  - [ ] README updated (if needed)
  - [ ] Migration guide (if needed)

- [ ] **Configuration:**
  - [ ] Environment variables documented
  - [ ] `.env.example` updated
  - [ ] Configuration files updated
  - [ ] Database migrations created

### Deployment Tasks

- [ ] Create pull request
  - Branch: `[branch-name]`
  - Base: `main`
  - Description: [Link to plan.md]

- [ ] Code review
  - Reviewer: [Name]
  - Feedback addressed: [ ]

- [ ] CI/CD pipeline passes
  - [ ] Build successful
  - [ ] Tests passing in CI
  - [ ] Deployment checks passing

- [ ] Merge to main
  - Merge commit: [hash]
  - Merged by: [Name]
  - Date: [Date]

### Post-Deployment Validation

- [ ] Services started successfully
  - Check: `pm2 list`
  - All services running: [ ]

- [ ] Health checks passing
  - Endpoint: `[health check URL]`
  - Response: [Expected response]

- [ ] Smoke tests passing
  - [ ] [Critical path 1] working
  - [ ] [Critical path 2] working
  - [ ] [Critical path 3] working

- [ ] Monitoring active
  - [ ] Logs being generated
  - [ ] Metrics being collected
  - [ ] Alerts configured

- [ ] Rollback plan verified
  - Rollback procedure documented: [ ]
  - Rollback tested: [ ]

**Deployment Completed:** [ ] Yes / Date: [_______]

---

## Additional Tasks and Notes

### Discovered During Implementation

- [ ] **Unexpected Task 1:** [Description]
  - Added: [Date]
  - Priority: [High/Medium/Low]
  - Status: [Not Started / In Progress / Completed]

- [ ] **Unexpected Task 2:** [Description]
  - Added: [Date]
  - Priority: [High/Medium/Low]
  - Status: [Status]

### Technical Debt to Address

- [ ] **Debt Item 1:** [Description]
  - Location: `[file.py:line]`
  - Priority: [High/Medium/Low]
  - Target: [When to address]

- [ ] **Debt Item 2:** [Description]
  - Location: [Where]
  - Priority: [Priority]

### Future Enhancements

- [ ] **Enhancement 1:** [Description]
  - Value: [Why this would be valuable]
  - Effort: [Estimate]
  - Priority: [High/Medium/Low]

- [ ] **Enhancement 2:** [Description]
  - Value: [Value]
  - Effort: [Estimate]

---

## Blockers and Issues

### Active Blockers

**Blocker 1:** [Description]

- **Impact:** [What's blocked]
- **Owner:** [Who's responsible for resolution]
- **Status:** [Status]
- **Workaround:** [Temporary solution if any]

### Resolved Issues

**Issue 1:** [Description]

- **Resolved:** [Date]
- **Resolution:** [How it was resolved]

---

## Session History

### Session 1: [Date]

**Duration:** [Hours]

**Tasks Completed:**

- [x] [Task 1]
- [x] [Task 2]

**Progress:** [Summary of work done]

**Blockers Encountered:** [None / Description]

**Next Session Focus:** [What to work on next]

---

### Session 2: [Date]

**Duration:** [Hours]

**Tasks Completed:**

- [x] [Task]

**Progress:** [Summary]

**Blockers Encountered:** [Issues]

**Next Session Focus:** [Focus]

---

## Progress Tracking

### Timeline

| Milestone        | Target Date | Actual Date | Status |
| ---------------- | ----------- | ----------- | ------ |
| Phase 1 Complete | [Date]      | [Date]      | ⏳/✅  |
| Phase 2 Complete | [Date]      | [Date]      | ⏳/✅  |
| Phase 3 Complete | [Date]      | [Date]      | ⏳/✅  |
| Deployment       | [Date]      | [Date]      | ⏳/✅  |

### Velocity Tracking

**Estimated Total Tasks:** [Count]
**Completed Tasks:** [Count]
**Remaining Tasks:** [Count]
**Completion Rate:** [XX%]

**Estimated Hours Remaining:** [Hours]
**Projected Completion Date:** [Date]

---

## Quick Reference

### Key Files

| Purpose     | File Location          |
| ----------- | ---------------------- |
| Main entry  | `[file.py]`            |
| Core logic  | `[file.py]`            |
| API routes  | `[file.py]`            |
| Data models | `[file.py]`            |
| Tests       | `tests/[test_file].py` |

### Commands

```bash
# Run feature
[command to run/test the feature]

# Run tests
pytest tests/test_[feature].py

# Type check
mypy [files]

# Format code
black [files] && isort [files]
```

### Related Documentation

- Plan: `dev-docs/[feature]-plan.md`
- Context: `dev-docs/[feature]-context.md`
- CLAUDE.md: Section [X]

---

**Feature Owner:** [Name/Team]
**Last Updated:** [Date and Time]
**Next Review:** [Date]

---

## Legend

- ⏳ In Progress
- ✅ Completed
- ❌ Blocked
- ⚠️ At Risk
- 🔄 Needs Rework

---

## Notes

[Any additional notes, reminders, or context that doesn't fit elsewhere]

- [Note 1]
- [Note 2]
