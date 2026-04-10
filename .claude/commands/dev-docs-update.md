# /dev-docs-update - Update Development Documentation

Updates existing dev-docs before context compaction to preserve progress.

## Usage

```
/dev-docs-update [task-slug]
```

If no task-slug provided, updates the most recent dev-docs.

## What It Does

1. **Reviews Current Progress** - Checks git diff, completed tasks
2. **Updates tasks.md** - Marks completed items `[x]`, notes blockers
3. **Updates context.md** - Adds new key files and decisions
4. **Updates plan.md** - Adjusts timeline if needed

## Example

```
/dev-docs-update erc8004-reputation-api
```

Updates files in `dev/active/erc8004-reputation-api/` based on current state.

## Prompt

When you invoke this command, Claude will:

1. **Assess Progress**
   ```bash
   # Check what's changed since last update
   git diff dev/active/erc8004-reputation-api/

   # Review task checklist
   cat dev/active/erc8004-reputation-api/erc8004-reputation-api-tasks.md
   ```

2. **Update tasks.md**
   - Mark completed tasks: `- [x] Task 1.1`
   - Add blockers: `- [ ] Task 2.3 - BLOCKED: Waiting for API key`
   - Note next steps: `## Next Session: Start Phase 3`

3. **Update context.md**
   - Add new key files discovered during work
   - Document decisions made (e.g., "Chose Redis over Memcached for persistence")
   - Update risks if new ones emerged

4. **Adjust plan.md** (if needed)
   - Extend deadlines if behind schedule
   - Add new phases if scope expanded
   - Update agent assignments if expertise gaps found

## When to Use

- **Before context compaction** - Preserve progress before Claude forgets
- **End of shift** - Handoff to next shift with updated status
- **After major milestone** - Document completion of phase
- **When blocked** - Note blockers for human review

## Benefits

- **Never lose progress** - Files survive context resets
- **Smooth handoffs** - Next shift knows exactly where you left off
- **Accurate timelines** - Plan reflects reality, not initial estimates
- **Audit trail** - History of decisions and pivots

## Integration

- Updates OPORD in Context Index with new status
- Logs update event with timestamp
- Tags with "dev-docs-update" and task slug
- Notifies SwarmOrchestrator of status change

## Example Output

```markdown
# Tasks: ERC-8004 Reputation API

## Phase 1: Schema Design ✅ COMPLETE
- [x] Task 1.1 - Define Pydantic models
- [x] Task 1.2 - Create API schema

## Phase 2: Service Layer 🔄 IN PROGRESS
- [x] Task 2.1 - Web3 integration
- [x] Task 2.2 - Redis caching
- [ ] Task 2.3 - Error handling - BLOCKED: Need Sentry DSN

## Phase 3: API Endpoints ⏸️ NOT STARTED
- [ ] Task 3.1 - Create router
- [ ] Task 3.2 - Add validation

## Next Session
Start Task 2.3 once Sentry DSN is provided. Then proceed to Phase 3.

## Blockers
1. Sentry DSN needed for error tracking - Escalated to human
```
