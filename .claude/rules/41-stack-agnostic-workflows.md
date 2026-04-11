# Rule 41: Stack-Agnostic Workflow Principles
# Source: harikrishna8121999/antigravity-workflows AGENTS.md
# Created: 2026-04-11

## Purpose
Enforces five core principles for all workflows and skills to prevent stack-specific assumptions.

## The Five Principles

### 1. Stack-Agnostic
Never assume React, Next.js, or any specific framework.
- **ALWAYS** detect the project stack first
- Check `package.json`, `pyproject.toml`, `Cargo.toml`, config files
- Look at existing code for conventions before suggesting patterns

### 2. Question-Driven
Ask clarifying questions before implementing.
- Don't assume the user wants a specific technology
- Prefer multiple choice questions when possible
- One question per message for clarity

### 3. Progressive Disclosure
Load minimal context first, expand on demand.
- Don't dump entire file contents upfront
- Start with structure, then dive into specifics
- Respect context window budgets

### 4. Single Responsibility
One workflow = one task.
- Each skill does ONE thing well
- Don't combine unrelated operations
- Keep SKILL.md focused and scannable

### 5. Composable
Workflows can be combined for complex tasks.
- Skills should have clear input/output contracts
- No hidden dependencies between skills
- Document which skills chain together

## Workflow Format Standard

All workflows follow this structure:
```markdown
---
description: [5-10 word description]
---

# Workflow Name

Brief intro explaining the purpose.

## Guardrails
- Boundaries and constraints

## Steps
### 1. Understand Context
### 2. Analyze Project
### 3. [Implementation Steps]
### 4. Verify

## Principles
- Universal best practices
```

## Anti-Patterns
- ❌ "Just install React and..." (assumes React)
- ❌ Implementing before asking scope questions
- ❌ Loading entire codebase into context upfront
- ❌ One skill that does 5 different things
- ❌ Skills that only work with a specific framework
