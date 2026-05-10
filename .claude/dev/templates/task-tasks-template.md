# [Task Name] - Task Checklist

**Created**: [Date]
**Last Updated**: [Date/Time]
**Progress**: [X/Y tasks completed]

---

## Board Metadata

```yaml
board_id: [board-id]
epic: [epic-name]
priority: [High/Medium/Low]
assignee: [assignee-name]
labels: [label1, label2, label3]
status: [To Do/In Progress/Review/Done]
```

---

## Task Completion Tracking

### Phase 1: [Phase Name from Plan]

#### Setup & Preparation
- [ ] Review strategic plan and architecture decisions
- [ ] Set up development environment
- [ ] Install required dependencies via uv
- [ ] Create feature branch: `feature/[task-name]`

#### Implementation
- [ ] [Specific implementation task 1]
  - Files: `path/to/file.py`
  - Notes: [Any relevant notes]
- [ ] [Specific implementation task 2]
  - Files: `path/to/file.py`
  - Notes: [Any relevant notes]
- [ ] [Specific implementation task 3]
  - Files: `path/to/file.py`
  - Notes: [Any relevant notes]

#### Testing (Phase 1)
- [ ] Write unit tests for [component 1]
- [ ] Write unit tests for [component 2]
- [ ] Verify coverage ≥ 98%
- [ ] All tests passing

**Phase 1 Checkpoint**: [Completion date/time when done]

---

### Phase 2: [Phase Name from Plan]

#### Core Implementation
- [ ] [Core task 1]
  - Files: `path/to/file.py`
  - Dependencies: [What this depends on]
  - Notes: [Any relevant notes]
- [ ] [Core task 2]
  - Files: `path/to/file.py`
  - Dependencies: [What this depends on]
  - Notes: [Any relevant notes]
- [ ] [Core task 3]
  - Files: `path/to/file.py`
  - Dependencies: [What this depends on]
  - Notes: [Any relevant notes]

#### Integration
- [ ] Integrate [component 1] with [component 2]
- [ ] Test integration points
- [ ] Handle edge cases

#### Testing (Phase 2)
- [ ] Write integration tests
- [ ] Test error handling paths
- [ ] Verify coverage maintained ≥ 98%
- [ ] All tests passing

**Phase 2 Checkpoint**: [Completion date/time when done]

---

### Phase 3: [Phase Name from Plan]

#### Validation & Polish
- [ ] Code review (self or agent)
- [ ] Refactor for clarity/performance
- [ ] Update documentation
- [ ] Add inline code comments where needed

#### Quality Gates
- [ ] Ruff formatting (auto-run by hook)
- [ ] MyPy type checking (strict mode)
- [ ] Pytest coverage ≥ 98% (Judge #6)
- [ ] CodeRabbit review (if available)
- [ ] No SAST/security issues

#### Testing (Phase 3)
- [ ] Manual testing of happy paths
- [ ] Manual testing of error paths
- [ ] Performance testing (if applicable)
- [ ] Load testing (if applicable)

#### Deployment Preparation
- [ ] Update CHANGELOG.md
- [ ] Update README.md if needed
- [ ] Migration scripts (if applicable)
- [ ] Environment variable documentation

**Phase 3 Checkpoint**: [Completion date/time when done]

---

## Post-Implementation

### Documentation
- [ ] Update PROJECT_KNOWLEDGE.md
- [ ] Update API documentation
- [ ] Add usage examples
- [ ] Document configuration options

### Board Sync
- [ ] Update board status to "Review"
- [ ] Add PR link to board card
- [ ] Update completion estimate

### Commit & PR
- [ ] Commit all changes with descriptive message
- [ ] Push to feature branch
- [ ] Create pull request
- [ ] Link PR to board epic/story
- [ ] Request code review

---

## Automated Checkpoints

> **Note**: Stop hooks will parse checkboxes above and automatically:
> - Update board status when phases complete
> - Log completion timestamps
> - Trigger agent handoffs (if configured)

### Board Update Log
- [Timestamp]: Updated status to [status] | [X/Y tasks complete]
- [Timestamp]: Updated status to [status] | [X/Y tasks complete]

---

## Notes & Issues Discovered

### Unexpected Challenges
1. **[Challenge 1]**
   - Discovered: [Date]
   - Impact: [What was affected]
   - Resolution: [How it was handled]
   - Time Impact: [+X hours]

2. **[Challenge 2]**
   - Discovered: [Date]
   - Impact: [What was affected]
   - Resolution: [How it was handled]
   - Time Impact: [+X hours]

### Scope Changes
1. **[Scope Change 1]**
   - Reason: [Why scope changed]
   - Added Tasks: [New tasks added]
   - Removed Tasks: [Tasks removed]

---

## Time Tracking

### Estimated vs Actual
- **Phase 1**: Estimated [X hrs] | Actual [Y hrs]
- **Phase 2**: Estimated [X hrs] | Actual [Y hrs]
- **Phase 3**: Estimated [X hrs] | Actual [Y hrs]
- **Total**: Estimated [X hrs] | Actual [Y hrs]

### Time by Activity
- Planning: [X hrs]
- Implementation: [X hrs]
- Testing: [X hrs]
- Debugging: [X hrs]
- Documentation: [X hrs]

---

## Completion Checklist

Final verification before marking task complete:

- [ ] All phases completed
- [ ] All tests passing
- [ ] Coverage ≥ 98%
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Board status synced
- [ ] PR created and approved
- [ ] Changes merged to main
- [ ] Post-merge verification complete

**Completed**: [Date/Time]
**Total Duration**: [X days/hours]

---

## Related Resources

- Plan: [task-name]-plan.md
- Context: [task-name]-context.md
- PR: [PR URL]
- Board Card: [Board card URL]
- Documentation: [Relevant doc links]
