# /dev-docs - Create Development Documentation

Creates OPORD-formatted development documentation for complex tasks.

## Usage

```

/dev-docs "Task description here"

```

## What It Does


1. **Analyzes Task** - Breaks down requirements and dependencies

2. **Creates Directory** - `dev/active/[task-slug]/`

3. **Generates Files**:

   - `[task-slug]-plan.md` - Full OPORD (5 paragraphs)

   - `[task-slug]-context.md` - Key files and decisions

   - `[task-slug]-tasks.md` - Checklist with phases

## Example

```

/dev-docs "Implement ERC-8004 reputation tracking API"

```

Creates:

```

dev/active/erc8004-reputation-api/
├── erc8004-reputation-api-plan.md
├── erc8004-reputation-api-context.md
└── erc8004-reputation-api-tasks.md

```

## Prompt

When you invoke this command, Claude will:


1. **Gather Context**

   - Scan relevant files in the codebase

   - Identify dependencies and blockers

   - Assess agent availability and expertise


2. **Create OPORD Plan** (`plan.md`)
   ```markdown
   # OPORD [NUMBER] - [TASK TITLE]

   ## 1. SITUATION
   [Enemy forces, friendly forces, attachments, civil considerations]

   ## 2. MISSION
   [WHO, WHAT, WHEN, WHERE, WHY]

   ## 3. EXECUTION
   [Commander's intent, concept of operations, tasks, coordinating instructions]

   ## 4. SERVICE SUPPORT
   [Logistics, personnel, medical/error handling]

   ## 5. COMMAND & SIGNAL
   [Command structure, communication channels, succession]
   ```


3. **Document Context** (`context.md`)
   ```markdown
   # Context: [TASK TITLE]

   ## Key Files

   - `path/to/file` - Purpose

   ## Key Decisions

   1. Decision - Rationale

   ## Dependencies

   - External: APIs, libraries

   - Internal: Services, contracts

   ## Risks

   1. Risk - Mitigation

   ## Success Criteria

   - [ ] Measurable criterion
   ```


4. **Generate Checklist** (`tasks.md`)
   ```markdown
   # Tasks: [TASK TITLE]

   ## Phase 1: [Name]

   - [ ] Task 1.1

   - [ ] Task 1.2

   ## Phase 2: [Name]

   - [ ] Task 2.1

   ## Quality Gates

   - [ ] All tests pass

   - [ ] Code review approved
   ```

## Benefits


- **Survives Context Compaction** - Files persist across sessions

- **Clear Roadmap** - Phases and milestones defined upfront

- **Audit Trail** - All decisions documented

- **Team Coordination** - Multiple agents can reference same plan

## Integration


- Automatically logs OPORD to Context Index

- Tags with task slug and "dev-docs"

- Assigns OPORD number from global counter

- Notifies assigned agents via SwarmOrchestrator

## Best Practices


1. **Use for tasks >4 hours** - Smaller tasks don't need full OPORD

2. **Update regularly** - Use `/dev-docs-update` before context compaction

3. **Review plan** - Get user approval before execution

4. **Mark tasks complete** - Update `tasks.md` as you progress
