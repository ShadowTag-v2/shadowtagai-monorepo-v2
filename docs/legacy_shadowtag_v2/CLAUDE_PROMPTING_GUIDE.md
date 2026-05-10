# Claude Code Advanced Prompting Guide

**Leverage Claude's full feature set for maximum productivity**

---

## Table of Contents

1. [Skills Layer - Build Your Expertise Library](#1-skills-layer)

2. [Memory System - Context Retention](#2-memory-system)

3. [Project Setup - Architect Your Workspace](#3-project-setup)

4. [Context Window Strategy](#4-context-window-strategy)

5. [Extended Thinking Mode](#5-extended-thinking-mode)

6. [Multi-Turn Refinement](#6-multi-turn-refinement)

7. [Validation Layer](#7-validation-layer)

8. [Cost Optimization - 15 Claude Code Habits](#8-cost-optimization)

9. [Skills Auto-Activation System](#9-skills-auto-activation)

10. [Dev Docs Workflow](#10-dev-docs-workflow)

11. [Hooks System](#11-hooks-system)

12. [Agents & Slash Commands](#12-agents-slash-commands)

13. [iOS Prompting Techniques](#13-ios-prompting)

---

## 1. Skills Layer

**Don't repeat the same instructions every time - create Claude Skills instead.**

### What Skills Do

- Embed your standards, voice, and frameworks permanently

- Activate automatically when relevant

- No pasting context repeatedly

### What to Build Skills For

- Writing style guides

- Proposal templates

- Analysis frameworks

- Research methods

- Code patterns (frontend/backend)

- Testing guidelines

- Error handling standards

### Skill Structure Best Practices

Keep main SKILL.md under **500 lines** with progressive disclosure:

```

frontend-dev-guidelines/
├── SKILL.md (398 lines - main patterns)
├── resources/
│   ├── react-patterns.md
│   ├── tanstack-query.md
│   ├── mui-components.md
│   └── testing-guidelines.md

```

### Example Skill Configuration

```json
{
  "backend-dev-guidelines": {
    "type": "domain",
    "enforcement": "suggest",
    "priority": "high",
    "promptTriggers": {
      "keywords": ["backend", "controller", "service", "API", "endpoint"],
      "intentPatterns": ["(create|add).*?(route|endpoint|controller)", "(how to|best practice).*?(backend|API)"]
    },
    "fileTriggers": {
      "pathPatterns": ["backend/src/**/*.ts"],
      "contentPatterns": ["router\\.", "export.*Controller"]
    }
  }
}
```

---

## 2. Memory System

**Let Claude remember your context over time.**

### What Memory Remembers

- Your goals and work context

- Communication style preferences

- Recurring needs and patterns

- Project-specific decisions

### Enable Memory

- Settings → Enable chat search & persistent memory

- Each Project has its own memory bank

- Memory is opt-in and editable

### Best Practices

- Preload project memory with key facts

- Store "Everything about this project" notes

- Keep governance context separate from code context

---

## 3. Project Setup

**Create dedicated environments with custom instructions.**

### Project Components

1. **Custom Instructions** - Claude's role for this project

2. **Uploaded Documents** - SOPs, brand guidelines, past work

3. **System Prompt** - Define behavior

### Example System Prompt

```

You're my content strategist. Analyze based on my audience data
and past performance. Always reference the brand guidelines in
the uploaded documents before suggesting copy.

```

### CLAUDE.md Structure

**Root CLAUDE.md (~100 lines)**

```markdown
# Project Rules

## Critical Commands

- `pnpm pm2:start` - Start all backend services

- `pnpm build` - Build frontend

## References

- See `/backend/claude.md` for API patterns

- See `/frontend/claude.md` for React patterns

- Skills handle all code guidelines
```

**Repo-specific claude.md (~50-100 lines)**

```markdown
# Backend Service

## Quick Start

- PROJECT_KNOWLEDGE.md - Architecture

- TROUBLESHOOTING.md - Common issues

- Auto-generated API docs

## This Repo's Quirks

- Uses Keycloak for auth

- Prisma with custom repository pattern
```

---

## 4. Context Window Strategy

**Claude has massive context - use it intelligently.**

### Attention Peaks at Edges

- Put critical information at **TOP** and **BOTTOM**

- Don't bury important details in the middle

- Place your question/instruction at the very **END**

### Use XML Tags for Structure

```xml
<role>Senior DevOps engineer and security auditor</role>

<task>Review the infrastructure code for security issues</task>

<constraints>


- Must comply with SOC2


- No secrets in code


- All resources must be tagged
</constraints>

<examples>
<!-- Include 2-3 examples of desired output -->
</examples>

```

### Token Efficiency

- Claude processes structured data **3x better** than walls of text

- Plain text attachments (`.txt`, `.md`) are best

- Avoid PDFs when possible (formatting issues)

- Stay under ~180k tokens for best results

---

## 5. Extended Thinking Mode

**For complex problems, unlock deeper reasoning.**

### When to Use

- Strategy decisions

- Technical architecture

- Complex analysis

- Multi-step problem solving

### How to Trigger

```

Think this through step-by-step using extended thinking.
First, brainstorm in <thinking> tags, then provide your
final answer in <answer> tags.

```

### Benefits

- Reduces hallucinations

- Catches logical errors

- Explores alternatives

- Shows reasoning process

### Note

Claude only "thinks" if you request the output - it won't do hidden chain-of-thought by itself.

---

## 6. Multi-Turn Refinement

**Don't expect perfection on first output.**

### Treat Claude Like a Team Member

```

Round 1: "Draft the API design"
Round 2: "Make it more RESTful"
Round 3: "Add pagination to the list endpoints"
Round 4: "Rewrite the error responses"

```

### Why It Works

- Claude maintains full conversation context

- Each refinement builds on previous understanding

- Iterative improvement beats single-shot

### Re-prompt Often

- Double-ESC brings up previous prompts

- Branch from earlier attempts with new knowledge

- "I don't want X, give me Y instead"

---

## 7. Validation Layer

**Add automatic quality control.**

### Self-Critique Prompts

```

After your response, critique it and identify weaknesses.

```

```

What assumptions are you making? What could be wrong?

```

```

Review this for:


- Security vulnerabilities


- Performance issues


- Edge cases not handled


- Inconsistencies with existing patterns

```

### For Code Reviews

```

Check this code against our backend-dev-guidelines skill.
List any violations and suggest fixes.

```

---

## 8. Cost Optimization - 15 Claude Code Habits

Save from $400/week to $15/week with these practices:

### Model Selection

1. **Use Haiku for 80% of work** - Set as default. 5x cheaper than Sonnet. Handles bug fixes, file reads, simple edits.

### Search Efficiency

2. **Search first, read second** - `search for x in file` costs $0.05 vs $5 to read entire 50MB log (100x cheaper)

3. **Read files in chunks** - `read lines 1-100` costs $0.10 vs $10 for entire 10MB file

4. **Limit search results** - `find first 50 matches` costs $0.50 vs $5 for 10,000 results

### Parallel Processing

5. **Run tasks in parallel** - `run these in parallel` - 3 files at once = same cost as 1, 3x faster

### Agent Usage

6. **Use Explore agent for unfamiliar code** - `explore this codebase for x` costs $5 vs $20-30 for trial-and-error

### Planning

7. **Plan major changes first** - `create a plan for refactoring x` costs $0.50, saves $50 in wasted rework

### Cost Tracking

8. **Turn on budget alerts** - Automatic warnings at 70% and 90% of monthly budget

### Prompt Quality

9. **Be specific in requests** - `fix the login bug in auth.ts line 45` vs vague `help me fix this` = 3x less cost

### Shortcuts

10. **Use path shortcuts** - `utils` instead of `/src/lib/utilities/helpers/index.ts`

### Task Management

11. **Create task checklists at start** - `create a todo list for x` prevents forgotten steps, 40% faster

### Smart Reading

12. **Read only what you need** - `read lines 100-200 from database.ts` = pennies vs dollars

### Session Management

13. **Don't ask the same question twice** - `use the errors we found earlier` - session memory is free

### Filtering

14. **Let the system filter first** - `show only x from y data` = 95% cheaper than loading all data

### Automation

15. **Make these habits automatic** - Use hooks and slash commands

---

## 9. Skills Auto-Activation System

**The game-changer for consistent code quality.**

### The Problem

Skills exist but Claude doesn't use them automatically.

### The Solution: Hooks

#### UserPromptSubmit Hook (BEFORE Claude sees your message)

```typescript
// Analyzes prompt for keywords and intent patterns
// Injects skill reminder into Claude's context

// Example output Claude sees:
// "🎯 SKILL ACTIVATION CHECK - Use backend-dev-guidelines skill"
```

#### Stop Event Hook (AFTER Claude finishes)

```typescript
// Analyzes edited files for risky patterns
// Displays gentle self-check reminder

// Example output:
// "❓ Did you add error handling?"
// "❓ Are Prisma operations using repository pattern?"
```

### skill-rules.json Configuration

```json
{
  "skillName": {
    "type": "domain",
    "enforcement": "suggest",
    "priority": "high",
    "promptTriggers": {
      "keywords": ["keyword1", "keyword2"],
      "intentPatterns": ["regex pattern"]
    },
    "fileTriggers": {
      "pathPatterns": ["src/**/*.ts"],
      "contentPatterns": ["import.*from"]
    }
  }
}
```

---

## 10. Dev Docs Workflow

**Prevent Claude from losing the plot.**

### The System

For every large task, create three documents:

```bash
mkdir -p ~/git/project/dev/active/[task-name]/

# Create:

# [task-name]-plan.md     - The accepted plan

# [task-name]-context.md  - Key files, decisions

# [task-name]-tasks.md    - Checklist of work

```

### Starting Large Tasks

1. **Enter planning mode** - Always plan before implementing

2. **Review the plan** - Catch mistakes early

3. **Create dev docs** - Run `/create-dev-docs` slash command

4. **Implement in sections** - One or two at a time for review

5. **Update regularly** - Mark tasks complete immediately

### Continuing Tasks

1. Check `/dev/active/` for existing tasks

2. Read all three files before proceeding

3. Update "Last Updated" timestamps

4. Run `/update-dev-docs` before context compaction

### Slash Commands

```

/dev-docs         - Create comprehensive strategic plan
/dev-docs-update  - Update dev docs before compaction
/create-dev-docs  - Convert approved plan to dev doc files

```

---

## 11. Hooks System

**#NoMessLeftBehind**

### Hook #1: File Edit Tracker

- Runs after every Edit/Write/MultiEdit

- Logs which files were edited and which repo

### Hook #2: Build Checker

- Runs when Claude finishes responding

- Finds which repos were modified

- Runs build scripts on affected repos

- Shows TypeScript errors to Claude

- If ≥5 errors: recommends auto-error-resolver agent

### Hook #3: Error Handling Reminder

- Detects risky patterns (try-catch, async, database calls)

- Shows gentle self-check reminder

- Non-blocking awareness

### Example Output

```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 ERROR HANDLING SELF-CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Backend Changes Detected
2 file(s) edited

❓ Did you add Sentry.captureException() in catch blocks?
❓ Are Prisma operations wrapped in error handling?

💡 Backend Best Practice:


- All errors should be captured to Sentry


- Controllers should extend BaseController
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```

### Complete Hook Pipeline

```

Claude finishes responding
↓
Hook 1: Build checker → TypeScript errors caught
↓
Hook 2: Error reminder → Self-check for error handling
↓
If errors found → Claude fixes them
↓
Result: Clean, error-free code

```

---

## 12. Agents & Slash Commands

### Specialized Agents

**Quality Control:**

- `code-architecture-reviewer` - Reviews code for best practices

- `build-error-resolver` - Fixes TypeScript errors systematically

- `refactor-planner` - Creates comprehensive refactoring plans

**Testing & Debugging:**

- `auth-route-tester` - Tests backend routes with authentication

- `auth-route-debugger` - Debugs 401/403 errors

- `frontend-error-fixer` - Diagnoses frontend errors

**Planning & Strategy:**

- `strategic-plan-architect` - Creates detailed implementation plans

- `plan-reviewer` - Reviews plans before implementation

- `documentation-architect` - Creates/updates documentation

### Agent Best Practices

- Give specific roles and clear instructions

- Specify what to return (not just "I fixed it!")

- Use for repeatable, well-defined tasks

### Common Slash Commands

**Planning & Docs:**

```

/dev-docs        - Create comprehensive strategic plan
/dev-docs-update - Update dev docs before compaction
/create-dev-docs - Convert approved plan to dev doc files

```

**Quality & Review:**

```

/code-review    - Architectural code review
/build-and-fix  - Run builds and fix all errors

```

**Testing:**

```

/route-research-for-testing - Find affected routes and launch tests
/test-route                 - Test specific authenticated routes

```

---

## 13. iOS Prompting Techniques

### Structured Prompts

Use labeled sections for complex tasks:

```xml
<context>
[Source material here]
</context>

<policy>
[Governance doctrine here]
</policy>

<question>
[Your actual query here]
</question>

```

### File Attachments

- **Prefer plain text** (`.txt`, `.md`) - easiest to parse

- **Avoid PDFs** - odd formatting issues

- **No .zip archives** - won't auto-extract

- **Limits:** 30MB per file, 20 files per chat

### Role-Based Prompting

```

You are a seasoned DevOps engineer and security auditor
familiar with enterprise risk frameworks. Apply Compliance Framework
principles to all assessments.

```

### Chain-of-Thought for Complex Reasoning

```

Think step-by-step before answering.
Show your reasoning in <thinking> tags.
Put the final answer in <answer> tags.

```

### Managing Long Documents

1. **Summarize in stages** - Break into chunks, summarize each, then analyze summaries

2. **Quote key parts first** - Ask Claude to extract relevant sentences before answering

3. **Use metadata and indices** - Label each document/section clearly

### Context Retention Tips

- Put critical instruction at the **END** of prompt

- One thread = one project

- Enable Memory for persistent facts

- Re-state key questions to refocus after long context

---

## Quick Reference Cheatsheet

### Essential Commands

```bash

# Planning

/dev-docs              # Create strategic plan
/create-dev-docs       # Convert plan to files
/dev-docs-update       # Update before compaction

# Quality

/code-review           # Architecture review
/build-and-fix         # Fix all errors

# Cost Optimization

"use haiku"            # Switch to cheaper model
"search for X in Y"    # Search, don't read entire file
"read lines 1-100"     # Chunk large files
"run in parallel"      # Parallel execution

```

### Prompt Templates

**Strategic Planning:**

```

You are a [role] expert in [domain].

<doctrine>
[Guiding principles]
</doctrine>

<context>
[Background/attachments]
</context>

Task: [Specific instruction]
Think step-by-step through implications, then give final recommendation.

```

**Code Review:**

```

You are a senior software engineer and code reviewer.

Review these files for:


1. Security vulnerabilities


2. Performance issues


3. Best practice violations


4. Missing error handling

Quote specific lines when identifying issues.

```

**Risk Assessment:**

```

You are a cybersecurity risk analyst.

<policy>
Risk Tier Definitions:


- Tier 1 (Critical): [definition]


- Tier 2 (High): [definition]


- Tier 3 (Moderate): [definition]


- Tier 4 (Low): [definition]
</policy>

Analyze the provided data. For each issue:


1. Assign risk tier (1-4)


2. Explain why it fits that tier


3. Quote the evidence


4. Recommend action

```

---

## Summary: The Essentials

1. **Plan everything** - Use planning mode or strategic-plan-architect

2. **Skills + Hooks** - Auto-activation is the only way skills work reliably

3. **Dev docs system** - Prevents Claude from losing the plot

4. **Code reviews** - Have Claude review its own work

5. **Be specific** - Vague prompts = poor results

6. **Structure context** - XML tags, edges of prompt, clear sections

7. **Iterate** - Multi-turn refinement beats single-shot

8. **Validate** - End with self-critique requests

---

_Guide consolidated from Anthropic best practices, Reddit community tips, and 6 months of hardcore Claude Code usage._
