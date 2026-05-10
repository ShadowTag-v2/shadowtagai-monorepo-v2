---
name: stitch-design-spec
description: Enforces strict visual consistency and WCAG accessibility compliance by reading and linting the DESIGN.md semantic file before writing frontend UI components.
---
# Spec-Driven Visual Design

## When to use this skill
- Before generating any React, Next.js, or A2UI generative frontend component.
- When the user asks to change the aesthetic, colors, or typography.

## How to use it
1. **Tokens are Roles:** Treat colors as semantic roles (e.g., `primary` = main text ink, `neutral` = canvas background). Do not use hardcoded hex values in UI code.
2. **Lint and Validate:** Always execute your `stitch_design_spec_manager` JSON tool with the `lint` action before finalizing UI.
3. **WCAG Auto-Correction:** If the linter returns contrast ratio errors, adjust the frontmatter hex values in `DESIGN.md` until the linter passes with exit code 0.
