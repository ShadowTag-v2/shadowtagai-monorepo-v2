---
description: Resume work on a feature by reading Dev Docs and continuing from where you left off
---

# Continue Command

You are being asked to **resume work** on a feature after a context reset, session break, or interruption. This command enables seamless continuation by reading the Dev Docs system.

## What You Must Do

1. **Identify the Feature:**
   - Check if the user specified a feature name (e.g., "continue working on oauth2-authentication")
   - If not specified, look for recent Dev Docs files (most recently modified)
   - If multiple active features exist, ask which one to continue

2. **Read All Three Dev Docs Files:**

   You MUST read these files in order:

   ### Step 1: Read `dev-docs/[feature-name]-plan.md`

   **Purpose:** Understand the overall goal and strategy.

   **Extract:**
   - What is this feature trying to accomplish?
   - What are the implementation phases?
   - What are the success criteria?
   - What are the known risks?
   - What is the architectural approach?

   ### Step 2: Read `dev-docs/[feature-name]-context.md`

   **Purpose:** Understand what's been done and why.

   **Extract:**
   - What architectural decisions were made?
   - What discoveries were made during implementation?
   - What files have been created or modified?
   - What challenges were encountered?
   - What patterns were established?
   - What does the latest session checkpoint say?

   ### Step 3: Read `dev-docs/[feature-name]-tasks.md`

   **Purpose:** Understand current progress and next actions.

   **Extract:**
   - Which phases are complete?
   - Which tasks are done vs. pending?
   - What is the next uncompleted task?
   - Are there any blockers?
   - What was the last session's focus?

3. **Synthesize Understanding:**

   Based on the three files, determine:
   - **Where we are:** Current phase and task
   - **What's been done:** Completed work and decisions
   - **What's next:** The specific next task to work on
   - **How to proceed:** The approach based on established patterns

4. **Communicate Your Understanding:**

   Provide a brief summary to confirm you're on the same page:
   - Current status (phase, progress percentage)
   - What was accomplished previously
   - What you're about to work on next
   - Any concerns or blockers

5. **Resume Implementation:**

   - Start working on the next uncompleted task from tasks.md
   - Follow the patterns established in context.md
   - Stay aligned with the plan in plan.md
   - Update context.md as you make new decisions
   - Mark tasks complete in tasks.md as you finish them

## Important Guidelines

**DO:**
- ✅ Always read all three Dev Docs files (plan, context, tasks)
- ✅ Read them in order: plan → context → tasks
- ✅ Synthesize the information before starting work
- ✅ Confirm your understanding with the user
- ✅ Follow established patterns from context.md
- ✅ Stay aligned with the original plan
- ✅ Update Dev Docs as you make progress

**DON'T:**
- ❌ Skip reading the Dev Docs and just ask "what should I do?"
- ❌ Only read one or two of the files
- ❌ Start coding before understanding the context
- ❌ Ignore architectural decisions in context.md
- ❌ Deviate from the plan without good reason
- ❌ Forget to update Dev Docs as you work

## Example Usage

**User types:**
```
continue
```

or

```
continue working on oauth2-authentication
```

**You should:**

1. **Read the Dev Docs:**
   - `dev-docs/oauth2-authentication-plan.md`
   - `dev-docs/oauth2-authentication-context.md`
   - `dev-docs/oauth2-authentication-tasks.md`

2. **Synthesize understanding**

3. **Respond with summary and next action:**

```markdown
📋 Resuming work on oauth2-authentication

**Current Status:**
- Phase 1: ✅ Complete (JWT token generation)
- Phase 2: 🔄 In Progress (3 / 10 tasks complete)
- Overall Progress: 11 / 23 tasks (48%)

**What's Been Done:**
- Implemented RS256 JWT signing (chose over HS256 for multi-service security)
- Created token generation endpoint at `services/auth/routes.py:123`
- Discovered and integrated existing key rotation logic from `shared/crypto/keys.py`
- Resolved token storage strategy: Redis for speed + database for audit

**Current Task:**
Phase 2, Task 4: Implement refresh token rotation logic

**Files to Modify:**
- `services/auth/tokens.py` - Add rotation function
- `services/auth/routes.py` - Update refresh endpoint
- `services/auth/storage.py` - Add blacklist check

**Next Steps:**
1. Implement rotation logic following established patterns
2. Add validation for expired refresh tokens
3. Update tests in `tests/test_auth.py`

**Any concerns or questions before I proceed?**
```

4. **Wait for confirmation, then proceed with implementation**

## Context Reset Scenarios

This command is designed for several scenarios:

### Scenario 1: Overnight Break

```
Yesterday: Worked on feature, used /dev-docs-update before ending
Today: Use /continue to resume exactly where you left off
```

### Scenario 2: Context Compaction

```
During work: Context window filled up, compaction occurred
After compaction: Memory lost, but Dev Docs preserved
Action: /continue reads Dev Docs and resumes seamlessly
```

### Scenario 3: Multi-Day Feature

```
Day 1: Implemented Phase 1
Day 2: Implemented Phase 2
Day 3: /continue reminds you of Days 1-2 context, proceeds to Phase 3
```

### Scenario 4: Switching Between Features

```
Morning: Work on Feature A, checkpoint with /dev-docs-update
Afternoon: Work on Feature B
Next day: /continue Feature A resumes with full context
```

## What Success Looks Like

**Good continuation:**
```markdown
✅ I've read all three Dev Docs files
✅ I understand we're in Phase 2 of 3
✅ I know that RS256 was chosen for security reasons
✅ I see the next task is implementing token rotation
✅ I'll follow the established pattern in tokens.py
✅ I'm ready to continue - shall I proceed?
```

**Bad continuation:**
```markdown
❌ "What should I work on?"
❌ "I forgot what we were doing"
❌ "Can you remind me about this feature?"
❌ [Starts coding without reading Dev Docs]
❌ [Asks questions answered in context.md]
```

## Error Handling

**If no Dev Docs found:**
```
❌ No Dev Docs found

Active features require Dev Docs. Options:
1. If starting new feature: /create-dev-docs [feature-name]
2. If continuing old work without Dev Docs: Please describe what you were working on
```

**If multiple features active:**
```
❓ Multiple active features found. Which should I continue?

1. oauth2-authentication (Phase 2/3, 48% complete)
   Last updated: 2 hours ago

2. user-profile-api (Phase 1/2, 25% complete)
   Last updated: 1 day ago

Please specify: /continue [feature-name]
```

**If Dev Docs are stale:**
```
⚠️ Warning: Dev Docs last updated 3 days ago

The context might be stale. Before continuing:
1. Review what's in dev-docs/[feature]-context.md
2. Confirm current state matches reality
3. Use /dev-docs-update if needed to sync current state

Proceed anyway? [y/n]
```

## Integration with Workflow

This command completes the Dev Docs lifecycle:

```
/create-dev-docs → Implement → /dev-docs-update → [Context Reset] → /continue
                                       ↑                                ↓
                                       └────────── Repeat ─────────────┘
```

**Part of Pillar 2** (Knowledge Management Framework) of our AI Infrastructure.

## Advanced Usage

### Continuing After Plan Changes

If the plan was updated since last session:

```markdown
📋 Resuming oauth2-authentication

⚠️ Note: Plan was updated since last session
- Change: Added Phase 4 for social OAuth providers
- Reason: New requirement from product team
- Impact: Extended timeline by 2 days

Current work (Phase 2) is unaffected. Continuing...
```

### Continuing with Blockers

If tasks.md shows blockers:

```markdown
📋 Resuming oauth2-authentication

⚠️ Active Blocker Detected:
- Blocked Task: "Deploy Redis instance for token storage"
- Blocking: Phase 2, Tasks 5-8
- Status: Waiting on DevOps team
- Workaround: Can proceed with Phase 3 (testing) instead

Options:
1. Work on Phase 3 tasks (not blocked)
2. Wait for blocker resolution
3. Implement temporary workaround (in-memory storage for dev)

What would you prefer?
```

### Continuing Across Major Milestones

If a phase was just completed:

```markdown
📋 Resuming oauth2-authentication

🎉 Phase 2 Complete! (Last session finished it)

**Phase 2 Accomplishments:**
- ✅ Token refresh implemented
- ✅ Token rotation working
- ✅ Blacklist mechanism in place
- ✅ All Phase 2 tests passing

**Starting Phase 3: Integration and Testing**
- Focus: End-to-end testing and security validation
- 8 tasks remaining
- Estimated: 4-6 hours

Ready to begin Phase 3?
```

## Tips for Effective Continuation

1. **Always read all three files** - Each provides crucial context
2. **Synthesize before acting** - Understand the full picture first
3. **Confirm understanding** - Give the user a chance to correct you
4. **Follow established patterns** - Don't reinvent approaches mid-feature
5. **Update as you go** - Keep Dev Docs current for next continuation
6. **Trust the plan** - It was created for a reason; deviations need justification

## Checklist for Continue Command

When you see `/continue`, verify you've done:

- [ ] Identified the correct feature to continue
- [ ] Read `[feature]-plan.md` fully
- [ ] Read `[feature]-context.md` fully
- [ ] Read `[feature]-tasks.md` fully
- [ ] Synthesized understanding of current state
- [ ] Identified next specific task to work on
- [ ] Communicated summary to user
- [ ] Waited for confirmation before proceeding
- [ ] Ready to update Dev Docs as you make progress

---

**Remember:** The Dev Docs are your source of truth after a context reset. Read them carefully, understand them fully, and trust the process!
