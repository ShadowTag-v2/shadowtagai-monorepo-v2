---
name: skillify
description: >
  Captures the current session's repeatable process as a reusable
  SKILL.md file following the agentskills.io standard.
  Adapted from Claude Code's /skillify (internal) and kk-r/skillify-skill (OSS).
---

# Skillify — Session-to-Skill Converter

Convert any Antigravity session into a portable, reusable SKILL.md file.

## When to Use

Use when the user says "skillify", "save this as a skill", "make this repeatable",
"convert this session to a skill", or after completing a significant workflow.

## Inputs

- `$description` (optional): Brief description of the skill to capture.

## Goal

Produce a well-structured SKILL.md that captures:
1. What was done in this session
2. The exact steps taken (in order)
3. Tools used and permissions needed
4. Success criteria for each step
5. Edge cases and corrections made during the session

## Steps

### 1. Analyze the Session (Context Reconstruction)

Since we don't have direct session memory APIs, reconstruct context from:
1. **Git diff** — `git diff --stat HEAD~3..HEAD` to see what changed
2. **Git log** — `git log --oneline -10` for recent commits
3. **Project detection** — identify package.json, requirements.txt, Makefile, etc.
4. **Artifacts** — check brain/ directory for session artifacts

**Success criteria**: You have a clear understanding of the repeatable process.

### 2. Interview the User (4 Rounds)

**Round 1: High-level confirmation**
- Suggest a name and description for the skill
- Suggest high-level goals and success criteria
- Ask user to confirm or rename

**Round 2: More details**
- Present the high-level steps as a numbered list
- Identify required arguments/inputs
- Ask where to save: repo (.agents/skills/) or personal (~/.gemini/skills/)

**Round 3: Breaking down each step**
For each major step, clarify:
- What does this step produce that later steps need?
- What proves success? (concrete criteria)
- Should the user confirm before proceeding? (for irreversible actions)
- Are any steps independent and could run in parallel?
- Hard constraints or preferences?

**Round 4: Final questions**
- Confirm trigger phrases for when to invoke
- Any gotchas or edge cases?

**Success criteria**: All 4 rounds completed, user is satisfied.

### 3. Generate the SKILL.md

Write the file using this format:

```markdown
---
name: {{skill-name}}
description: {{one-line description}}
---

# {{Skill Title}}

Description of what this skill does.

## When to Use

Use when... (trigger phrases)

## Inputs

- `$arg_name`: Description

## Goal

Clearly stated goal with defined artifact or criteria for completion.

## Steps

### 1. Step Name
What to do. Be specific and actionable. Include commands when appropriate.

**Success criteria**: How to know this step is done.
```

**Per-step annotations** (optional but recommended):
- **Success criteria** — REQUIRED on every step
- **Human checkpoint** — For irreversible actions (merging, deploying, sending)
- **Rules** — Hard constraints from user corrections during the session

**Success criteria**: Valid SKILL.md ready for review.

### 4. Review and Save

1. Output the complete SKILL.md for user review
2. Ask for confirmation before writing
3. Save to the chosen location
4. Tell the user how to invoke it

**Success criteria**: File saved, user informed of the skill name and path.

## Judge #6 Governance

All generated skills are subject to Judge #6 review:
- No hardcoded secrets or API keys in skill files
- No skills that bypass security gates
- No skills that auto-approve irreversible actions without human checkpoints
- Skills that touch auth, payments, or deployment MUST include human checkpoints

## Cross-Platform Compatibility

Generated skills use the agentskills.io standard frontmatter, making them
portable across 30+ agent platforms:
- Claude Code: `.claude/skills/`
- Antigravity: `~/.gemini/skills/` or `.agents/skills/`
- Cursor: `.cursor/skills/`
- Gemini CLI: `~/.gemini/skills/`
