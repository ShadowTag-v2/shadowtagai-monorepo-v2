# Dev Docs System Guide

## Overview

The Dev Docs system is a core component of our AI-assisted development workflow. It provides **durable state management** across AI sessions, solving the "context amnesia" problem that occurs when working on complex, multi-day features.

## Purpose

Without Dev Docs, the AI assistant:

- Loses context after session resets or context compactions
- Forgets architectural decisions made earlier
- Drifts from the original plan mid-implementation
- Requires constant human re-orientation

With Dev Docs, the AI:

- Maintains consistent context across days or weeks
- Remembers why decisions were made
- Stays aligned with the approved plan
- Resumes work seamlessly after any interruption

## The Three-File System

Every significant feature gets three synchronized documents:

### 1. `[feature]-plan.md` - The Specification

**Purpose:** Immutable (or rarely-changed) implementation plan and specification.

**Created:** At the start, before any code is written.

**Contains:**

- Executive summary
- Goals and success criteria
- Implementation phases with detailed tasks
- Architecture and design decisions
- Testing strategy
- Risk analysis

**Think of it as:** The blueprint and contract for the feature.

**When to update:** Rarely. Only when fundamental requirements change.

### 2. `[feature]-context.md` - The Decision Log

**Purpose:** Running log of decisions, discoveries, and important context.

**Created:** Alongside the plan.

**Updated:** Continuously throughout implementation.

**Contains:**

- Architectural decisions and their rationale
- Key discoveries during implementation
- File change log
- Code patterns established
- Challenges encountered and how they were resolved
- Session checkpoints

**Think of it as:** The "transaction log" of the development process.

**When to update:**

- After making significant decisions
- When discovering important information
- Before context compactions
- At natural stopping points

### 3. `[feature]-tasks.md` - The Checklist

**Purpose:** Simple checklist tracking implementation progress.

**Created:** From the plan, breaking down phases into tasks.

**Updated:** Continuously as tasks are completed.

**Contains:**

- Task checklists for each phase
- Progress tracking (X of Y tasks complete)
- Session history
- Blockers and issues
- Quick reference information

**Think of it as:** The kanban board for the feature.

**When to update:**

- Mark tasks as complete immediately when done
- Add new tasks as they're discovered
- Update blockers and session notes

## When to Use Dev Docs

### ✅ USE Dev Docs for

- **Complex features** requiring 3+ hours of work
- **Multi-session tasks** spanning multiple days
- **Architectural changes** affecting multiple components
- **Features requiring research** and exploration
- **Anything with significant state** you need to preserve

### ❌ DON'T Use Dev Docs for

- **Simple bug fixes** (< 30 minutes)
- **Trivial changes** (formatting, typos, minor refactors)
- **One-off scripts** or utilities
- **Documentation updates** (unless extensive)

**Rule of thumb:** If you'd be frustrated losing context halfway through, use Dev Docs.

## Workflow

### Creating Dev Docs

#### Step 1: Plan the Feature

```bash
# In Claude Code, describe what you want to build
"I need to implement user authentication with JWT tokens"
```

Claude should:

1. Research the codebase
2. Create a comprehensive plan
3. Discuss the plan with you for approval

#### Step 2: Initialize Dev Docs

```bash
/create-dev-docs user-authentication
```

This command:

- Creates `dev-docs/user-authentication-plan.md` (from approved plan)
- Creates `dev-docs/user-authentication-context.md` (empty, ready to fill)
- Creates `dev-docs/user-authentication-tasks.md` (checklist from plan phases)

#### Step 3: Implement

Work with Claude to implement the feature. Claude should:

- Reference the plan to stay on track
- Update context.md with decisions and discoveries
- Mark tasks complete in tasks.md as work progresses

### Checkpointing Progress

Before a context compaction or at natural stopping points:

```bash
/dev-docs-update user-authentication
```

Claude should:

- Review what was accomplished since last checkpoint
- Update context.md with new decisions/discoveries
- Update tasks.md with completed items
- Add session notes about current state

### Resuming Work

After a break, context reset, or starting a new day:

```bash
continue
```

or

```bash
continue working on user-authentication
```

Claude should:

1. Read all three Dev Docs files
2. Understand the plan, context, and current state
3. Identify the next uncompleted task
4. Resume implementation seamlessly

## Dev Docs Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│  1. PLANNING PHASE                                          │
│  • Research codebase                                        │
│  • Create comprehensive plan                                │
│  • Get human approval                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. INITIALIZATION                                          │
│  Command: /create-dev-docs [feature-name]                   │
│  • Create plan.md (from approved plan)                      │
│  • Create context.md (empty template)                       │
│  • Create tasks.md (from plan phases)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. ACTIVE DEVELOPMENT (Repeating cycle)                    │
│  • Implement next task from tasks.md                        │
│  • Mark task complete                                       │
│  • Update context.md with decisions                         │
│  • Checkpoint: /dev-docs-update [feature-name]              │
│  • [Context reset occurs]                                   │
│  • Resume: continue                                         │
│  • Repeat until all phases complete                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. COMPLETION                                              │
│  • All tasks in tasks.md marked complete                    │
│  • Final context.md update with lessons learned             │
│  • Create PR referencing plan.md                            │
│  • Archive Dev Docs (keep for future reference)             │
└─────────────────────────────────────────────────────────────┘
```

## Best Practices

### For Plans (plan.md)

✅ **Do:**

- Create detailed, structured plans before coding
- Include specific file references
- Define clear success criteria
- Identify risks upfront
- Break work into phases with 3-5 tasks each

❌ **Don't:**

- Start coding without an approved plan
- Make plans too vague ("implement the feature")
- Skip risk analysis
- Create phases that are too large (>1 day of work)

### For Context (context.md)

✅ **Do:**

- Log decisions as they're made
- Explain the "why" behind choices
- Reference specific code locations (file:line)
- Note alternatives considered
- Checkpoint before context compactions

❌ **Don't:**

- Only update at the end (you'll forget details)
- Skip rationale ("we chose X" without saying why)
- Forget to note discoveries
- Let it get stale

### For Tasks (tasks.md)

✅ **Do:**

- Mark tasks complete immediately
- Add unexpected tasks as discovered
- Keep tasks specific and actionable
- Note blockers as they occur
- Track session-by-session progress

❌ **Don't:**

- Batch task updates (mark complete as you go)
- Make tasks too vague
- Forget to add new tasks discovered during work
- Leave blockers undocumented

## Templates

All templates are available in this directory:

- `TEMPLATE-plan.md` - Copy this to start a new plan
- `TEMPLATE-context.md` - Copy this for context logging
- `TEMPLATE-tasks.md` - Copy this for task tracking

## Slash Commands

### `/create-dev-docs [feature-name]`

**Purpose:** Initialize the Dev Docs system for a new feature.

**Requires:** An approved implementation plan.

**Creates:**

- `dev-docs/[feature-name]-plan.md`
- `dev-docs/[feature-name]-context.md`
- `dev-docs/[feature-name]-tasks.md`

**Example:**

```bash
/create-dev-docs oauth-integration
```

### `/dev-docs-update [feature-name]`

**Purpose:** Checkpoint current state to Dev Docs.

**Updates:**

- `[feature-name]-context.md` with recent decisions/discoveries
- `[feature-name]-tasks.md` with completed items

**When to use:**

- Before context compaction
- At end of work session
- After completing a phase
- Before major architectural change

**Example:**

```bash
/dev-docs-update oauth-integration
```

### `/continue`

**Purpose:** Resume work on a feature using Dev Docs.

**Reads:**

- Plan to understand goals
- Context to understand decisions made
- Tasks to find next action

**Then:** Continues implementation from where you left off.

**Example:**

```bash
continue
# or
continue working on oauth-integration
```

## Example: Full Feature Lifecycle

### Day 1: Planning and Initial Implementation

```bash
# User starts
"I need to add OAuth2 authentication to our API"

# Claude researches and creates plan
# User approves plan

# Initialize Dev Docs
/create-dev-docs oauth2-authentication

# Claude implements Phase 1
# - Creates OAuth2 routes
# - Implements token generation
# - Updates context.md with decisions
# - Marks tasks complete in tasks.md

# End of day checkpoint
/dev-docs-update oauth2-authentication
```

### Day 2: Continuation After Context Reset

```bash
# New session, context was reset overnight
continue

# Claude:
# 1. Reads oauth2-authentication-plan.md (understands goals)
# 2. Reads oauth2-authentication-context.md (understands what's done)
# 3. Reads oauth2-authentication-tasks.md (sees Phase 1 complete, Phase 2 next)
# 4. Starts Phase 2 implementation seamlessly

# Implements Phase 2
# - Adds refresh token rotation
# - Updates context with security decisions
# - Marks Phase 2 tasks complete

# End of day checkpoint
/dev-docs-update oauth2-authentication
```

### Day 3: Completion

```bash
continue

# Claude completes Phase 3
# - Integration testing
# - Documentation
# - Final tasks complete

# All tasks marked complete in tasks.md
# Final context.md update with lessons learned
# Create PR with reference to plan.md
```

## Benefits

### For AI

- **No amnesia:** Can resume after any context reset
- **Stays on track:** Plan keeps implementation focused
- **Makes better decisions:** Context provides history
- **Knows what's done:** Task list shows progress

### For Humans

- **Less re-explaining:** AI reads Dev Docs instead of asking
- **Better handoffs:** Another human can read Dev Docs and understand
- **Audit trail:** Context shows why decisions were made
- **Progress visibility:** Tasks.md shows clear progress

### For Teams

- **Knowledge sharing:** Dev Docs document how features were built
- **Onboarding:** New team members read Dev Docs to understand decisions
- **Consistency:** Enforces structured approach to complex work
- **Quality:** Forces planning before coding

## Troubleshooting

### "Claude isn't updating the Dev Docs"

**Solution:** Explicitly remind Claude:

```bash
Update the context.md with the decisions we just made
```

or use the checkpoint command:

```bash
/dev-docs-update [feature-name]
```

### "Claude forgot the plan mid-implementation"

**Solution:** Remind Claude to check the plan:

```bash
Review the plan in dev-docs/[feature]-plan.md and ensure we're following it
```

Better: Use `/dev-docs-update` more frequently to reinforce context.

### "The Dev Docs are getting stale"

**Solution:**

- Checkpoint more frequently
- Update context.md as decisions are made, not at the end
- Mark tasks complete immediately, don't batch

### "I need to change the plan mid-implementation"

**Solution:**

1. Update the plan.md with clear notes about what changed and why
2. Update context.md with a decision log entry explaining the change
3. Update tasks.md to reflect new task breakdown
4. Inform Claude: "The plan has been updated, please review it"

## Integration with AI Infrastructure Framework

Dev Docs are **Pillar 2** of the AI Infrastructure Framework (see `AI-INFRASTRUCTURE-ARCHITECTURE-ANALYSIS.md`).

**They work synergistically with:**

- **Pillar 1 (Auto-Activation Engine):** Skills auto-activate, Dev Docs provide feature-specific state
- **Pillar 3 (Agentic Workforce):** Planning agents create Dev Docs, implementation agents use them
- **Pillar 4 (Zero-Error Pipeline):** Hooks validate code, Dev Docs track quality metrics

## Advanced Usage

### Multi-Developer Features

When multiple developers (or multiple AI sessions) work on one feature:

1. One person creates initial Dev Docs
2. Each session updates context.md with their contributions
3. Tasks.md shows who's working on what
4. Context provides shared understanding

### Feature Dependencies

When Feature B depends on Feature A:

In Feature B's plan.md:

```markdown
## Dependencies

- Feature A (oauth2-authentication) must be complete
  - Specifically needs: JWT token generation (Phase 1)
  - Tracked in: dev-docs/oauth2-authentication-plan.md
```

### Partial Implementations

Sometimes you need to pause work on a feature:

1. Run `/dev-docs-update [feature]` to checkpoint
2. In context.md, add a note about why work is paused
3. In tasks.md, mark current task as "Blocked" with reason
4. When resuming (days/weeks later), `continue` will work

## Appendix: File Naming Convention

**Format:** `[feature-name]-[type].md`

**Feature name:**

- Use kebab-case (lowercase with hyphens)
- Be specific but concise
- Match the feature/task name

**Examples:**

- ✅ `oauth2-authentication-plan.md`
- ✅ `user-profile-api-plan.md`
- ✅ `database-migration-context.md`
- ❌ `feature-plan.md` (too vague)
- ❌ `OAuth2_Auth_Plan.md` (wrong case)
- ❌ `plan-oauth.md` (wrong order)

---

**Last Updated:** 2025-11-07
**Framework Phase:** Phase 1 (Foundation)
**Next Phase:** Phase 2 (Core Skills) - Week 2-3
