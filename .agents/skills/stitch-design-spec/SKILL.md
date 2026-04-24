---
name: stitch-design-spec
description: >
  Enforces strict visual consistency and WCAG accessibility compliance by reading
  and linting the DESIGN.md semantic file before writing frontend UI components.
  Tier 2 procedural wrapper for the Tier 1 designmd-stitch-visual-mastery global
  skill. Use before generating any React, Next.js, or A2UI generative frontend
  component, or when the user asks to change the aesthetic, colors, or typography.
  Now includes Tailwind/DTCG export and the spec injection command.
---

# Spec-Driven Visual Design

## Tier Classification
- **This skill is Tier 2 (Brain)** — it instructs the agent on HOW to sequence Tier 1 JSON tools.
- **It does NOT replace** the `designmd-stitch-visual-mastery` global skill; it provides the project-scope routing.
- **Global skill version:** v3.0.0 (incorporates full `@google/design.md@0.1.1` CLI).

## When to Use
- Before generating any React, Next.js, or A2UI generative frontend component
- When the user asks to change the aesthetic, colors, or typography
- When creating new pages or modifying existing UI
- When `DESIGN.md` exists anywhere in the project tree
- When exporting design tokens to Tailwind or W3C DTCG format

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
Always lint before finalizing any UI work:
```bash
npx @google/design.md lint ./DESIGN.md
```

### 3. WCAG Auto-Correction Loop
If the linter returns contrast ratio warnings:
1. Identify the failing token pair (foreground vs background)
2. Darken the ink token OR lighten the canvas token
3. Re-lint until exit code 0
4. Update the Markdown prose to reflect the reasoning change

### 4. Export to Tailwind
When building Tailwind-based projects, export tokens directly:
```bash
npx @google/design.md export --format tailwind DESIGN.md > tailwind.theme.json
```

### 5. Diff for Version Control
Before committing design changes, verify no regressions:
```bash
npx @google/design.md diff DESIGN.md DESIGN-v2.md
```

## 3-Tier Cascade Position
```
Tier 1 (Muscle): StitchMCP tools (create_design_system, apply_design_system)
  ↓ sequenced by
Tier 2 (Brain): THIS SKILL — reads DESIGN.md, decides when to lint/export/scaffold
  ↓ fallback to
Tier 3 (Discovery): npx @google/design.md CLI for unknown operations
```

## CLI Quick Reference

| Command | Purpose |
|---------|---------|
| `lint DESIGN.md` | Validate structure + WCAG contrast |
| `diff old.md new.md` | Token-level change detection |
| `export --format tailwind DESIGN.md` | Generate Tailwind theme config |
| `export --format dtcg DESIGN.md` | Generate W3C DTCG tokens.json |
| `spec` | Output full format spec (for agent prompts) |
| `spec --rules-only --format json` | Output lint rules as JSON |

## Anti-Patterns
- ❌ Generating UI without checking for a DESIGN.md first
- ❌ Hardcoding `#3B82F6` when `{colors.tertiary}` exists
- ❌ Skipping the lint step after modifying token values
- ❌ Using this skill to REPLACE StitchMCP — it SEQUENCES StitchMCP
- ❌ Manually writing Tailwind configs instead of using `export`
- ❌ Guessing contrast ratios instead of running the linter
