---
name: stitch-design-spec
description: >
  Enforces strict visual consistency and WCAG accessibility compliance by reading
  and linting the DESIGN.md semantic file before writing frontend UI components.
  Tier 2 procedural wrapper for the Tier 1 stitch_design_spec_manager JSON tool.
  Use before generating any React, Next.js, or A2UI generative frontend component,
  or when the user asks to change the aesthetic, colors, or typography.
---

# Spec-Driven Visual Design

## Tier Classification
- **This skill is Tier 2 (Brain)** — it instructs the agent on HOW to sequence Tier 1 JSON tools.
- **It does NOT replace** the `designmd-stitch-visual-mastery` global skill; it provides the project-scope routing.

## When to Use
- Before generating any React, Next.js, or A2UI generative frontend component
- When the user asks to change the aesthetic, colors, or typography
- When creating new pages or modifying existing UI
- When `DESIGN.md` exists anywhere in the project tree

## How to Use

### 1. Tokens are Roles
Treat colors as semantic roles. Never hardcode hex values in UI code.

| Token Role | Meaning | Example |
|-----------|---------|---------|
| `primary` | Main text/ink color | `#1A1C1E` |
| `neutral` | Canvas/background | `#F7F5F2` |
| `tertiary` | Accent/interaction (CTAs) | `#B8422E` |
| `on-primary` | Text ON a primary-colored surface | `#FFFFFF` |

### 2. Lint and Validate
Always execute the `stitch_design_spec_manager` JSON tool with the `lint` action
before finalizing any UI work:

```json
{
  "tool": "stitch_design_spec_manager",
  "action": "lint",
  "target": "./DESIGN.md"
}
```

### 3. WCAG Auto-Correction Loop
If the linter returns contrast ratio errors:
1. Identify the failing token pair (foreground vs background)
2. Darken the ink token OR lighten the canvas token
3. Re-lint until exit code 0
4. Update the Markdown prose to reflect the reasoning change

### 4. Scaffold from Spec
To generate spec-compliant components:

```json
{
  "tool": "stitch_design_spec_manager",
  "action": "scaffold",
  "target": "ButtonPrimary"
}
```

## 3-Tier Cascade Position
```
Tier 1 (Muscle): StitchMCP tools (create_design_system, apply_design_system)
  ↓ sequenced by
Tier 2 (Brain): THIS SKILL — reads DESIGN.md, decides when to lint/scaffold
  ↓ fallback to
Tier 3 (Discovery): npx @google/design.md CLI for unknown operations
```

## Anti-Patterns
- ❌ Generating UI without checking for a DESIGN.md first
- ❌ Hardcoding `#3B82F6` when `{colors.tertiary}` exists
- ❌ Skipping the lint step after modifying token values
- ❌ Using this skill to REPLACE StitchMCP — it SEQUENCES StitchMCP
