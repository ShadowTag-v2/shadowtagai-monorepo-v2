# Dev Docs Template

This directory contains the development documentation workflow for managing large features and tasks.

## Purpose

The dev docs system prevents Claude from "losing the plot" during implementation by maintaining persistent context across sessions, even through auto-compaction events.

## Structure

For each large feature or task, create a subdirectory in `dev/active/` with three files:

```
dev/active/[feature-name]/
├── [feature-name]-plan.md      # The accepted implementation plan
├── [feature-name]-context.md   # Key files, decisions, and context
└── [feature-name]-tasks.md     # Checklist of work items
```

## File Templates

### 1. Plan File Template (`*-plan.md`)

```markdown
# [Feature Name] - Implementation Plan

**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
**Status**: [Planning | In Progress | Review | Complete]

## Executive Summary

[1-2 paragraph overview of what this feature does and why]

## Goals

- Goal 1
- Goal 2
- Goal 3

## Non-Goals

- What this feature explicitly does NOT include
- Future work that's out of scope

## Phases

### Phase 1: [Phase Name]

**Timeline**: [Estimate]
**Tasks**:

- Task 1.1
- Task 1.2

**Success Criteria**:

- Criteria 1
- Criteria 2

### Phase 2: [Phase Name]

[Repeat structure]

## Technical Approach

### Architecture Changes

[Describe any architectural changes needed]

### Key Components

1. **Component 1**: Description
2. **Component 2**: Description

### Integration Points

- Integration point 1
- Integration point 2

## Risks and Mitigations

| Risk   | Impact | Probability | Mitigation          |
| ------ | ------ | ----------- | ------------------- |
| Risk 1 | High   | Medium      | Mitigation strategy |

## Timeline

- Week 1: Phase 1
- Week 2: Phase 2
- Week 3: Testing and review

## Success Metrics

- Metric 1: Target value
- Metric 2: Target value
```

### 2. Context File Template (`*-context.md`)

```markdown
# [Feature Name] - Context

**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

## Key Files

### Modified Files

- `path/to/file1.py:123` - Description of changes
- `path/to/file2.py:45` - Description of changes

### New Files

- `path/to/new_file.py` - Purpose and description

### Related Files (Reference Only)

- `path/to/related.py` - Why it's relevant

## Architectural Decisions

### Decision 1: [Title]

**Date**: YYYY-MM-DD
**Context**: Why we needed to make this decision
**Decision**: What we decided
**Consequences**: Implications of this decision
**Alternatives Considered**: What else we looked at

### Decision 2: [Title]

[Repeat structure]

## Key Dependencies

- Dependency 1: Why needed, how used
- Dependency 2: Why needed, how used

## Assumptions

- Assumption 1
- Assumption 2

## Constraints

- Constraint 1
- Constraint 2

## Integration Points

### Upstream Dependencies

- Service/component that this depends on
- What data/functionality is needed

### Downstream Consumers

- Service/component that depends on this
- What data/functionality they expect

## Important Context Notes

- Note 1: Context that Claude needs to remember
- Note 2: Gotchas or tricky aspects
- Note 3: Decisions that were made and why

## Next Steps

1. Next immediate task
2. Following task
3. Future considerations

## Blockers

- [ ] Blocker 1: Description and who can unblock
- [ ] Blocker 2: Description and who can unblock

## Questions & Answers

**Q**: Question that came up during implementation?
**A**: Answer that was determined

## Resources

- Link 1: Documentation
- Link 2: Reference implementation
- Link 3: Design discussion
```

### 3. Tasks File Template (`*-tasks.md`)

```markdown
# [Feature Name] - Task Checklist

**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
**Progress**: X / Y tasks complete (Z%)

## Phase 1: [Phase Name]

### Setup & Planning

- [x] Create dev docs structure
- [x] Review existing codebase
- [ ] Task in progress

### Implementation

- [ ] Task 1: Brief description
  - [ ] Subtask 1.1
  - [ ] Subtask 1.2
- [ ] Task 2: Brief description

### Testing

- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Manual testing

### Documentation

- [ ] Update API docs
- [ ] Update architecture docs
- [ ] Add code comments

## Phase 2: [Phase Name]

[Repeat structure]

## Phase 3: [Phase Name]

[Repeat structure]

## Review & Launch

- [ ] Code review
- [ ] Security review
- [ ] Performance testing
- [ ] Deployment plan reviewed
- [ ] Rollback plan documented
- [ ] Monitoring configured
- [ ] Deployed to staging
- [ ] Deployed to production

## Post-Launch

- [ ] Monitor for errors (24 hours)
- [ ] Collect stakeholder feedback
- [ ] Performance tuning if needed
- [ ] Archive dev docs to /dev/completed/

## Notes

- Note 1: Important detail about a task
- Note 2: Dependency or blocker to be aware of
```

## Usage Workflow

### Starting a New Feature

1. **Enter Planning Mode**:

   ```
   Use Claude Code planning mode to research and create a comprehensive plan
   ```

2. **Create Dev Docs Directory**:

   ```bash
   mkdir -p dev/active/[feature-name]/
   ```

3. **Generate Dev Doc Files**:

   ```
   Ask Claude to create the three files based on the accepted plan
   ```

4. **Begin Implementation**:
   - Start with Phase 1, Task 1
   - Mark tasks as complete immediately after finishing
   - Update context file as decisions are made

### During Implementation

1. **Before Each Session**:
   - Read all three dev doc files
   - Note where you left off
   - Check for blockers

2. **During Work**:
   - Update tasks.md immediately when completing items
   - Add to context.md when making architectural decisions
   - Add new tasks if discovered during implementation

3. **Before Compaction**:
   - Run `/update-dev-docs` (or manually update)
   - Note next steps in context.md
   - Update "Last Updated" timestamps

4. **After Compaction (New Session)**:
   - Start with "Read dev/active/[feature-name]/\*.md files"
   - Continue from where you left off

### Completing a Feature

1. **Final Review**:
   - Ensure all tasks are marked complete
   - Update status to "Complete" in plan.md
   - Note any future work or follow-ups

2. **Archive**:

   ```bash
   mv dev/active/[feature-name] dev/completed/
   ```

3. **Update Documentation**:
   - Ensure all architecture docs reflect changes
   - Update README if needed
   - Note in CHANGELOG

## Best Practices

### For Plan Files

- ✅ Be specific about phases and tasks
- ✅ Include success criteria for each phase
- ✅ Document risks and mitigations upfront
- ❌ Don't make it too high-level (needs actionable detail)
- ❌ Don't skip the "Non-Goals" section

### For Context Files

- ✅ Update immediately when decisions are made
- ✅ Include file paths with line numbers when relevant
- ✅ Document "why" not just "what"
- ❌ Don't let it get stale (update Last Updated timestamp)
- ❌ Don't just list files without explaining relevance

### For Task Files

- ✅ Make tasks specific and measurable
- ✅ Break large tasks into subtasks
- ✅ Mark complete immediately (don't batch)
- ❌ Don't make tasks too vague ("implement feature X")
- ❌ Don't forget to add new tasks discovered during work

## Common Pitfalls

1. **Forgetting to Update Context**: Always note architectural decisions as they happen
2. **Tasks Too Vague**: "Add API endpoint" vs "Add POST /api/sources endpoint with Pydantic validation"
3. **Not Reading Before Starting**: Always read all three files at session start
4. **Stale Context Files**: Update "Last Updated" and next steps before compaction
5. **Skipping Small Tasks**: Even small features benefit from lightweight dev docs

## Example: Small Feature

For smaller features, you can use a simplified structure:

```markdown
# Small Feature - Quick Docs

**Created**: YYYY-MM-DD
**Status**: In Progress

## Goal

[One paragraph: what are we building and why]

## Tasks

- [ ] Task 1
- [ ] Task 2
- [ ] Write tests
- [ ] Deploy

## Key Files

- `file1.py:123` - Changes made
- `file2.py:45` - Changes made

## Notes

- Important context point 1
- Important context point 2
```

## Templates Location

Copy templates from this file when creating new dev docs, or use slash commands:

- `/create-dev-docs` - Create from accepted plan
- `/update-dev-docs` - Update before compaction

---

**Remember**: The dev docs system is insurance against context loss. Spend 2 minutes updating it to save 20 minutes re-figuring out what you were doing.
