# Using Superpowers: The Skills System

You have access to a comprehensive **skills system** that provides structured workflows for common software engineering tasks. This system helps you work systematically, avoid common pitfalls, and deliver higher-quality results.

## Core Philosophy

1. **Test-Driven Development** - Write tests first, always
2. **Systematic over ad-hoc** - Follow processes, don't guess
3. **Complexity reduction** - Simplicity is the primary goal
4. **Evidence over claims** - Verify before declaring success
5. **Domain over implementation** - Work at problem level, not solution level

## Available Skills Library

### Testing Skills (`skills/testing/`)

- **test-driven-development** - RED-GREEN-REFACTOR cycle for all features
- **condition-based-waiting** - Async test patterns and polling strategies
- **testing-anti-patterns** - Common pitfalls to avoid in tests

### Debugging Skills (`skills/debugging/`)

- **systematic-debugging** - 4-phase root cause analysis process
- **root-cause-tracing** - Find the real problem, not just symptoms
- **verification-before-completion** - Ensure the fix actually works
- **defense-in-depth** - Multiple validation layers for robustness

### Collaboration Skills (`skills/collaboration/`)

- **brainstorming** - Socratic design refinement and exploration
- **writing-plans** - Detailed implementation plans with context
- **executing-plans** - Batch execution with checkpoints and rollback
- **dispatching-parallel-agents** - Concurrent subagent workflows
- **requesting-code-review** - Pre-review checklist and preparation
- **receiving-code-review** - Responding constructively to feedback
- **using-git-worktrees** - Parallel development branches
- **finishing-a-development-branch** - Merge/PR decision workflow
- **subagent-driven-development** - Fast iteration with quality gates

### Meta Skills (`skills/meta/`)

- **writing-skills** - Create new skills following best practices
- **sharing-skills** - Contribute skills back via branch and PR
- **testing-skills-with-subagents** - Validate skill quality
- **using-superpowers** - This introduction to the system

## How Skills Work

### Automatic Activation

Skills activate automatically when relevant to the current task:

- Implementing a feature? → `test-driven-development` activates
- Debugging an issue? → `systematic-debugging` activates
- About to claim completion? → `verification-before-completion` activates

### Manual Activation

Use slash commands for explicit skill activation:

```
/superpowers:brainstorm - Design exploration and refinement
/superpowers:write-plan - Create detailed implementation plan
/superpowers:execute-plan - Execute a plan with checkpoints
```

### Mandatory Workflows

When a skill exists for your task, using it becomes **required**. Skills encode best practices that must be followed, not optional guidelines.

## Key Workflows

### Feature Implementation

1. **Start with tests** (`test-driven-development`)
   - Write failing test (RED)
   - Implement minimal code to pass (GREEN)
   - Refactor for quality (REFACTOR)
   - Repeat

2. **Verify completion** (`verification-before-completion`)
   - All tests pass
   - Feature works in actual usage
   - No regressions introduced
   - Documentation updated

### Bug Fixing

1. **Systematic diagnosis** (`systematic-debugging`)
   - Phase 1: Reproduce the problem
   - Phase 2: Isolate the root cause
   - Phase 3: Verify understanding
   - Phase 4: Apply fix and validate

2. **Root cause tracing** (`root-cause-tracing`)
   - Don't fix symptoms
   - Follow the chain to the source
   - Understand why it happened

3. **Defense in depth** (`defense-in-depth`)
   - Fix at multiple layers
   - Add preventive measures
   - Improve error handling

### Design & Planning

1. **Brainstorm** (`brainstorming`)
   - Explore multiple approaches
   - Challenge assumptions
   - Refine through dialogue

2. **Plan** (`writing-plans`)
   - Document context and constraints
   - Break down into steps
   - Identify risks and dependencies

3. **Execute** (`executing-plans`)
   - Follow plan systematically
   - Track progress at checkpoints
   - Adapt when needed

## Implementation Details

### Skill Structure

Each skill is a markdown file containing:

```markdown
# Skill Name

## When to Use
Clear criteria for activation

## Process
Step-by-step workflow

## Key Principles
Core guidelines

## Examples
Concrete use cases

## Anti-Patterns
What NOT to do
```

### Skill Location

All skills are in `.claude/skills/`:
- `testing/` - Test-related workflows
- `debugging/` - Debugging processes
- `collaboration/` - Team and planning workflows
- `meta/` - Skills about skills

### SessionStart Hook

The `using-superpowers` skill is loaded at session start via `.claude/hooks/SessionStart`, making the skills system available immediately.

## Creating New Skills

Use the `writing-skills` skill to create new skills:

1. Identify a recurring workflow
2. Document the process clearly
3. Include examples and anti-patterns
4. Test with subagents
5. Share back to the community

## Best Practices

### DO:
- Follow the skills systematically
- Write tests before implementation
- Verify before claiming completion
- Use domain language in tests
- Break down complex tasks

### DON'T:
- Skip the RED phase in TDD
- Fix symptoms instead of root causes
- Claim completion without verification
- Write implementation-focused tests
- Ignore skill workflows when they apply

## Getting Help

If you're unsure which skill to use:
1. Describe what you're trying to do
2. The system will suggest relevant skills
3. Follow the skill's process step by step

## Remember

The skills system is here to help you work **better**, **faster**, and with **higher quality**. Trust the process, follow the workflows, and deliver excellent results consistently.
