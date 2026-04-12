---
description: Initialize Dev Docs system for a new feature with plan, context, and tasks files
---

# Create Dev Docs Command

You are being asked to initialize the **Dev Docs system** for a new feature. This is a critical step in our AI-assisted development workflow that creates durable state management across sessions.

## What You Must Do

1. **Verify Prerequisites:**
   - Confirm that a comprehensive implementation plan has been created and approved
   - If no plan exists, STOP and create one first (research → plan → get approval)
   - The plan should include: executive summary, phases, tasks, risks, and success criteria

2. **Extract Feature Name:**
   - The feature name should be provided as an argument (e.g., `/create-dev-docs user-authentication`)
   - If no argument provided, ask the user for the feature name
   - Use kebab-case (lowercase with hyphens) for the feature name

3. **Create Three Dev Docs Files:**

   Create these files in the `dev-docs/` directory:

   ### File 1: `dev-docs/[feature-name]-plan.md`

   - Copy the structure from `dev-docs/TEMPLATE-plan.md`
   - Fill in with the approved implementation plan
   - Include all sections: executive summary, phases, architecture, testing, risks
   - This becomes the immutable specification for the feature
   - Be comprehensive and detailed

   ### File 2: `dev-docs/[feature-name]-context.md`

   - Copy the structure from `dev-docs/TEMPLATE-context.md`
   - Initialize with basic metadata (feature name, start date)
   - Leave most sections empty (they'll be filled during implementation)
   - Add a note in "Purpose" section explaining this feature
   - This will be updated continuously during development

   ### File 3: `dev-docs/[feature-name]-tasks.md`

   - Copy the structure from `dev-docs/TEMPLATE-tasks.md`
   - Extract tasks from the plan's phases
   - Create a checklist for each phase
   - Include all validation and testing tasks
   - Set all tasks to uncompleted ([ ] not [x])
   - This will track implementation progress

4. **Confirm Creation:**
   - List the three files created
   - Provide a brief summary of what's in each
   - Remind the user they can start implementation now
   - Mention that `/dev-docs-update [feature-name]` should be used to checkpoint progress

## Important Guidelines

**DO:**
- ✅ Ensure the plan is comprehensive before creating Dev Docs
- ✅ Use consistent naming: `[feature-name]-plan.md`, `[feature-name]-context.md`, `[feature-name]-tasks.md`
- ✅ Break down plan phases into specific, actionable tasks
- ✅ Include file references in tasks (e.g., "Create `services/auth/routes.py`")
- ✅ Set realistic task breakdowns (3-5 tasks per phase)

**DON'T:**
- ❌ Create Dev Docs without an approved plan
- ❌ Make tasks too vague ("implement the feature")
- ❌ Skip sections in the templates
- ❌ Start implementation before creating Dev Docs (for complex features)
- ❌ Use inconsistent file naming

## Example Usage

**User types:**
```
/create-dev-docs oauth2-authentication
```

**You should:**
1. Verify an OAuth2 authentication plan exists and is approved
2. Create:
   - `dev-docs/oauth2-authentication-plan.md` (filled with approved plan)
   - `dev-docs/oauth2-authentication-context.md` (initialized, mostly empty)
   - `dev-docs/oauth2-authentication-tasks.md` (checklist from plan phases)
3. Confirm creation with summary

**Your response might be:**
```markdown
✅ Dev Docs initialized for oauth2-authentication

**Created files:**
1. `dev-docs/oauth2-authentication-plan.md`
   - 3 implementation phases
   - Detailed API design
   - Risk analysis and testing strategy

2. `dev-docs/oauth2-authentication-context.md`
   - Initialized and ready for decision logging
   - Will track architectural decisions and discoveries

3. `dev-docs/oauth2-authentication-tasks.md`
   - 23 tasks across 3 phases
   - Includes testing and validation tasks
   - Ready to track progress

**Next steps:**
- Start implementing Phase 1 tasks
- Update context as decisions are made
- Mark tasks complete as you finish them
- Use `/dev-docs-update oauth2-authentication` to checkpoint progress
```

## Template Locations

- Plan template: `dev-docs/TEMPLATE-plan.md`
- Context template: `dev-docs/TEMPLATE-context.md`
- Tasks template: `dev-docs/TEMPLATE-tasks.md`

## When to Use This Command

**Use `/create-dev-docs` for:**
- Complex features requiring 3+ hours of work
- Multi-session tasks spanning multiple days
- Features requiring architectural decisions
- Anything where losing context would be costly

**Don't use for:**
- Simple bug fixes (< 30 minutes)
- Trivial changes (formatting, docs)
- One-off scripts

## Integration with Workflow

This command is **Pillar 2** of our AI Infrastructure Framework (Knowledge Management). It creates the durable state that survives context resets and enables seamless work resumption.

**Related commands:**
- `/dev-docs-update [feature-name]` - Checkpoint progress
- `/continue` - Resume work using Dev Docs

---

**Remember:** Dev Docs are the foundation of reliable, long-running AI-assisted development. Create them thoughtfully and maintain them diligently.
