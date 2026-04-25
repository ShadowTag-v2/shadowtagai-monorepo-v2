---
name: expert-agent-builder
description: >
  Uses Deep Research and NotebookLM to autonomously structure new Antigravity
  skills. Implements the DBS Framework (Direction, Blueprints, Solutions) with
  arXiv:2512.14982 "Rule of Three" prompt repetition for maximum retrieval
  accuracy. Triggers on: "create a new skill", "build a skill for X",
  "research and formalize X into a skill".
---

# Expert Agent Builder — DBS Framework with Physics-Aware Retrieval

## When to Use

- User asks to "create a new skill" or "build a skill for X"
- User says "research X and turn it into a skill"
- Agent identifies a gap in the skill registry that needs filling
- User invokes `/skill-create` or references DBS framework

## The DBS Framework

**D**irection → **B**lueprints → **S**olutions

### Phase 1: Direction (What + Why)

1. **Define the skill boundary:** What specific capability does this skill add?
2. **Identify activation triggers:** When should the agent auto-activate this skill?
3. **Cross-reference existing skills:** Does this overlap with anything in the registry?
4. **Write the YAML frontmatter:**
   ```yaml
   ---
   name: <kebab-case-name>
   description: >
     <1-3 sentence description including activation triggers>
   ---
   ```

### Phase 2: Blueprints (How — Research Phase)

**Use NotebookLM for zero-token research:**

1. Create a research notebook:
   ```
   notebooklm create "<Skill Topic> Research"
   ```

2. Add sources (docs, papers, repos):
   ```
   notebooklm source add "<relevant_file_or_url>"
   notebooklm source add-research "<topic keyword>"
   ```

3. **Apply the Rule of Three (arXiv:2512.14982):**

   For deep retrieval from non-reasoning inference, prompt repetition at **3x**
   reaches peak accuracy. This is the absolute highest ROI for data extraction.

   ```
   notebooklm ask "Organize findings into DBS framework: Direction, Blueprints, Solutions.

   Organize findings into DBS framework: Direction, Blueprints, Solutions.

   Organize findings into DBS framework: Direction, Blueprints, Solutions."
   ```

   > **PHYSICS NOTE (arXiv:2512.14982):**
   > The triple repetition exploits the mathematical property of causal masking
   > in transformer attention heads. The model reads the instruction 3 times
   > with progressively richer KV cache context, mimicking bidirectional
   > attention inside a unidirectional decoder. This yields up to 76% accuracy
   > improvement on data extraction tasks with ZERO latency penalty.

4. **Reasoning model exception:** If the target model uses extended thinking
   (Gemini Thinking, Claude extended thinking, o1/o3), do NOT repeat the prompt.
   Prompt repetition is redundant for reasoning models (per arXiv:2512.14982).

### Phase 3: Solutions (The Skill File)

1. Write the skill to the correct location:
   - **Global** (cross-project): `~/.gemini/antigravity/skills/<name>/SKILL.md`
   - **Workspace** (monorepo-specific): `.agents/skills/<name>/SKILL.md`
   - **Both** (redirect pattern): Workspace stub → Global canonical (or vice versa)

2. **Required sections in every skill:**
   ```markdown
   ## When to Use
   - List explicit triggers and intent detection patterns

   ## Core Protocol
   - Step-by-step operational instructions

   ## Anti-Patterns
   - What to NEVER do

   ## Cross-References
   - Links to related skills
   ```

3. **Post-creation validation:**
   - Verify the skill appears in the skill registry listing
   - Test activation by simulating a trigger phrase
   - Check for conflicts with existing skills

## The Redirect Pattern

When a skill applies to both global and workspace contexts:

```markdown
# Example: .agents/skills/<name>/SKILL.md (11 lines)
---
name: <name>
description: "<description>"
redirect: ~/.gemini/antigravity/skills/<name>/SKILL.md
---
# <Title>
> **CANONICAL SOURCE**: `~/.gemini/antigravity/skills/<name>/SKILL.md`
> This file is a redirect stub. The full skill lives in the global directory.
```

This follows the Rich Hickey doctrine: **one source of truth, no duplication.**

## Quality Gates

Before finalizing any skill:

1. **Frontmatter validates:** `name` is kebab-case, `description` is multi-sentence
2. **Line count > 50:** Stubs under 50 lines are likely incomplete
3. **Activation triggers defined:** "When to Use" section is mandatory
4. **Anti-patterns documented:** What NOT to do is as important as what to do
5. **Cross-references linked:** No orphan skills

## Anti-Patterns

- ❌ Creating skills without checking the existing registry for overlap
- ❌ Writing 9-line stubs and calling them "done"
- ❌ Applying prompt repetition to reasoning/thinking models
- ❌ Duplicating content between global and workspace (use redirect pattern)
- ❌ Missing activation triggers (skills without "When to Use" are dead weight)
- ❌ Research without NotebookLM delegation (wastes local API tokens)

## Cross-References

- **Prompt Repetition Boost:** `skills/prompt-repetition-boost/SKILL.md` (arXiv:2512.14982)
- **NotebookLM Orchestrator:** `skills/notebooklm-orchestrator/SKILL.md` (zero-token delegation)
- **NotebookLM Bridge:** `skills/notebooklm-bridge/SKILL.md` (full CLI API)
- **Obsidian Formatter:** `skills/obsidian-formatter/SKILL.md` (output formatting)
- **Skill Creator:** `skills/skill-creator/SKILL.md` (legacy, superseded by this)
- **Cor.30 Security Enforcer:** `skills/cor30-security-enforcer/SKILL.md` (security checks on new skills)
