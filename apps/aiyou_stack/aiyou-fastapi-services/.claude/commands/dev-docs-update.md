---
description: Checkpoint current state to Dev Docs (context and tasks) before context reset or end of session
---

# Dev Docs Update Command

You are being asked to **checkpoint the current state** of work on a feature by updating its Dev Docs. This is critical for maintaining continuity across context resets and sessions.

## What You Must Do

1. **Identify the Feature:**
   - The feature name should be provided as an argument (e.g., `/dev-docs-update user-authentication`)
   - If no argument provided, check if there's an active feature being worked on
   - If unclear, ask the user which feature to update

2. **Verify Dev Docs Exist:**
   - Check that `dev-docs/[feature-name]-plan.md` exists
   - Check that `dev-docs/[feature-name]-context.md` exists
   - Check that `dev-docs/[feature-name]-tasks.md` exists
   - If files don't exist, suggest using `/create-dev-docs [feature-name]` first

3. **Update `[feature-name]-context.md`:**

   Review the recent conversation and implementation work, then add:

   **Architectural Decisions:**
   - Any significant technical decisions made
   - Rationale for each decision
   - Alternatives considered and why rejected
   - File locations affected (e.g., `services/auth/routes.py:45`)

   **Key Discoveries:**
   - Important findings about the codebase
   - Edge cases discovered
   - Library or API behaviors learned
   - Gotchas or pitfalls encountered

   **Implementation Notes:**
   - Code patterns established
   - Challenges encountered and how resolved
   - Time spent on blockers

   **File Changes:**
   - New files created with purpose
   - Existing files modified with reason
   - Important code locations (file:line references)

   **Session Checkpoint:**
   - Summary of work completed in this session
   - Current state (what's working, what's not)
   - Next steps to resume work
   - Context for future sessions

4. **Update `[feature-name]-tasks.md`:**

   - Mark completed tasks as done: `- [x]`
   - Update progress counters (e.g., "3 / 8 tasks completed")
   - Add any new tasks discovered during implementation
   - Update blocker status if applicable
   - Add session history entry with summary

5. **Do NOT Update `[feature-name]-plan.md`:**
   - The plan is intentionally immutable
   - Only update plan if fundamental requirements changed
   - If you must update it, note the change clearly in context.md

6. **Confirm Update:**
   - Summarize what was added to context.md
   - Report task completion progress
   - Remind about next steps

## Important Guidelines

**DO:**
- ✅ Capture decisions as they happen (don't wait until the end)
- ✅ Include specific file:line references
- ✅ Explain the "why" behind decisions, not just "what"
- ✅ Note alternatives considered
- ✅ Be specific about what changed and why
- ✅ Update immediately before context compactions
- ✅ Checkpoint at natural stopping points (end of phase, end of session)

**DON'T:**
- ❌ Skip the update because "nothing important happened"
- ❌ Write vague entries ("fixed some stuff")
- ❌ Forget to mark tasks complete
- ❌ Omit rationale for decisions
- ❌ Wait too long between checkpoints
- ❌ Modify the plan.md without good reason

## Example Usage

**User types:**
```
/dev-docs-update oauth2-authentication
```

**You should:**
1. Review recent work on oauth2-authentication
2. Update `dev-docs/oauth2-authentication-context.md` with:
   - Decisions made (e.g., "Chose RS256 over HS256 for token signing")
   - Discoveries (e.g., "Found existing key rotation logic in auth module")
   - Implementation notes (e.g., "Added token refresh in `routes/auth.py:123`")
   - Session checkpoint
3. Update `dev-docs/oauth2-authentication-tasks.md`:
   - Mark completed tasks: Phase 1, tasks 1-3 complete
   - Update progress: "8 / 23 tasks completed (35%)"
4. Confirm update

**Your response might be:**
```markdown
✅ Dev Docs updated for oauth2-authentication

**Context updates:**
- Architectural Decision: Chose RS256 over HS256 for JWT signing
  - Rationale: Better security for multi-service architecture
  - Implemented in: `services/auth/tokens.py:45`

- Discovery: Existing key rotation logic found in `shared/crypto/keys.py`
  - Impact: Can reuse instead of implementing from scratch
  - Saved ~2 hours of work

- Implementation: Token refresh endpoint created
  - Location: `services/auth/routes.py:123-156`
  - Includes rate limiting and validation

- Challenge: Refresh token storage strategy
  - Problem: Redis vs. database tradeoff
  - Resolution: Using Redis for speed, database for audit
  - Implementation: `services/auth/storage.py`

**Task progress:**
- Phase 1: 8 / 8 tasks completed ✅
- Phase 2: 3 / 10 tasks completed (in progress)
- Overall: 11 / 23 tasks (48%)

**Next session:**
- Continue Phase 2: Implement token rotation logic
- Next task: Add refresh token blacklisting on logout
```

## When to Use This Command

**Use `/dev-docs-update` when:**
- ⏰ About to hit a context compaction (proactive checkpoint)
- 🛑 Ending a work session for the day
- ✅ Completing a phase or major milestone
- 🔄 Before switching to a different feature
- 🤔 Made significant architectural decisions
- 🔍 Discovered important information about the codebase
- 🐛 Resolved a complex bug or challenge

**Frequency:**
- Minimum: Before every context compaction
- Recommended: Every 1-2 hours of active work
- Ideal: After every significant decision or discovery

## What to Capture

### High Priority (Always Capture)

1. **Architectural Decisions:**
   - What was decided
   - Why it was chosen
   - What alternatives were considered
   - Impact on the system

2. **Task Completion:**
   - Which tasks are done
   - Updated progress percentages
   - Blockers encountered

3. **File Changes:**
   - What files were created or modified
   - Purpose of each change
   - Key code locations

### Medium Priority (Capture When Relevant)

4. **Discoveries:**
   - Existing code that's useful
   - Edge cases found
   - API behaviors learned

5. **Challenges:**
   - Problems encountered
   - How they were resolved
   - Time spent debugging

6. **Patterns:**
   - Code patterns established
   - Reusable approaches
   - Standards being followed

### Low Priority (Nice to Have)

7. **Performance Notes:**
   - Benchmarks or measurements
   - Optimization opportunities

8. **Security Considerations:**
   - Security decisions made
   - Potential vulnerabilities addressed

## Session Checkpoint Template

When updating context.md, add a session checkpoint:

```markdown
### Checkpoint [N]: [Date/Time]

**Work Completed:**
- [Summary of what was accomplished]

**Current State:**
- Files modified: [count]
- Tests passing: [count/total]
- Phase progress: [X of Y tasks complete]

**Decisions Made:**
- [Key decision 1]
- [Key decision 2]

**Next Steps:**
- [ ] [Next immediate task]
- [ ] [Following task]

**Context for Resume:**
[Brief notes to help resume work - what to remember, where you left off]
```

## Integration with Workflow

This command is part of **Pillar 2** (Knowledge Management Framework) of our AI Infrastructure.

**Typical workflow:**
1. `/create-dev-docs [feature]` - Initialize
2. Implement code
3. `/dev-docs-update [feature]` - Checkpoint (repeat as needed)
4. [Context reset occurs]
5. `/continue` - Resume seamlessly using updated Dev Docs
6. Repeat steps 2-5 until complete

## Error Handling

**If Dev Docs don't exist:**
```
❌ Dev Docs not found for [feature-name]

Create them first with:
/create-dev-docs [feature-name]
```

**If no recent work to update:**
```
⚠️ No significant changes detected since last update.

If you've made progress, please describe what you've done
so I can update the context properly.
```

**If feature name unclear:**
```
❓ Which feature should I update?

Active features with Dev Docs:
- oauth2-authentication
- user-profile-api

Use: /dev-docs-update [feature-name]
```

---

**Remember:** Frequent, detailed checkpoints are the key to seamless work resumption. When in doubt, update the Dev Docs!
