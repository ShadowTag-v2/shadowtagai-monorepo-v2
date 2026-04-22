---
name: dynamic-tool-acquisition
description: >
  Standard Operating Procedure for filling capability gaps using the Vercel Agent
  Skills CLI (npx skills). Tier 2 procedural wrapper for the Tier 3 fallback.
  Instead of failing or hallucinating scripts, use this procedural fallback to
  discover and execute community skills dynamically.
  Use when the user asks for a specific operational or analytical task that has
  no hardcoded JSON tool (e.g., SEO audit, Lighthouse check, bundle size analysis,
  i18n translation audit, 3D spline animation).
---

# Dynamic Tool Acquisition

## Tier Classification
- **This skill is Tier 2 (Brain)** — it instructs the agent on HOW to use the Tier 3 fallback.
- **It does NOT replace** the `dynamic-skill-execution` global skill; it provides the project-scope routing SOP.

## When to Use
- User asks for a capability NOT covered by any Tier 1 MCP JSON tool
- User asks for a capability NOT covered by any installed Tier 2 skill
- Instead of saying "I can't do that" or hallucinating a bash script

## The Think-Act-Observe Discovery Loop

### Step 1: Discover
Execute the `vercel_dynamic_skills_cli` JSON tool with the `discover` action:

```json
{
  "tool": "vercel_dynamic_skills_cli",
  "action": "discover",
  "query_or_skill_name": "lighthouse performance audit",
  "cli_arguments": ""
}
```

**Underlying command:** `CI=true npx -y skills --skill find-skills --query "lighthouse performance audit"`

### Step 2: Observe
Parse the CLI output for:
- Exact skill name
- Required arguments
- Description of what it does

### Step 3: Execute
Execute the discovered skill as a black box:

```json
{
  "tool": "vercel_dynamic_skills_cli",
  "action": "execute",
  "query_or_skill_name": "lighthouse-audit",
  "cli_arguments": "--url https://counselconduit.run.app"
}
```

**Underlying command:** `CI=true npx -y skills --skill lighthouse-audit --url https://counselconduit.run.app`

## 3-Tier Cascade Position
```
Tier 1 (Muscle): MCP JSON tools — tried FIRST
  ↓ not available
Tier 2 (Brain): .agents/skills/ — check for procedural guidance
  ↓ no matching skill
Tier 3 (Discovery): THIS SKILL triggers npx skills CLI discovery
```

## Guardrails
- ✅ Always use `CI=true` prefix (Headless CLI Protocol)
- ✅ Always use `npx -y` (zero-install)
- ✅ Treat discovered scripts as black boxes — don't modify them
- ❌ Never skip Tier 1 and Tier 2 checks before using Tier 3
- ❌ Never hallucinate a bash script when a community skill exists
- ❌ Never install skills from untrusted repos without reviewing SKILL.md first
