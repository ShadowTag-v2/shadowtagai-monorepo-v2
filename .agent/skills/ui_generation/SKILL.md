---
name: UI Generation
description: BANS standard CSS guessing. UI components must use design tokens and pass Biome Gate 0.
---

# UI Generation

## Prohibition

**Ad-hoc CSS values are BANNED.** The following are Tier 1 violations:

- Hardcoded hex colors (`#ff0000`, `#333333`) instead of CSS custom properties
- Arbitrary pixel values for spacing without token reference
- Browser-default fonts (`Times New Roman`, `Arial`) instead of design system fonts
- Inline styles that bypass the design token system
- Any `.tsx` or `.css` file that fails `biome check`

## Mandatory Execution Path

### Design Token System

All UI components MUST reference tokens from the project's `globals.css` or equivalent design system file:

```css
/* Color tokens — use these, never raw hex */
var(--color-primary)
var(--color-secondary)
var(--color-accent)
var(--color-background)
var(--color-surface)
var(--color-text)
var(--color-text-muted)

/* Spacing tokens */
var(--space-xs)    /* 4px */
var(--space-sm)    /* 8px */
var(--space-md)    /* 16px */
var(--space-lg)    /* 24px */
var(--space-xl)    /* 32px */
var(--space-2xl)   /* 48px */

/* Typography tokens */
var(--font-primary)     /* Inter, system-ui */
var(--font-display)     /* Outfit, system-ui */
var(--font-mono)        /* JetBrains Mono, monospace */
```

### Biome Gate 0 (Mandatory Pre-Commit)

Every UI file MUST pass Biome linting before commit:

```bash
npx biome check apps/kovelai/site/src/ --fix
```

Biome enforces:
- Import sorting and deduplication
- React hooks rules
- Accessibility (a11y) rules
- TypeScript strict mode compliance
- No unused variables or imports

### Component Creation Workflow

1. **Check existing tokens** in `globals.css` before adding new ones
2. **Use Stitch MCP** for design system generation when available
3. **Reference DESIGN.md** spec format for token documentation
4. **Validate with Biome** before staging: `npx biome check --fix`
5. **Visual verify** with Chrome DevTools MCP screenshot

### Stitch MCP Integration

For new screen generation or design system updates:

```
Tools: generate_screen_from_text, create_design_system, apply_design_system
Use when: New page layouts, design system changes, A/B variant generation
```

### Accessibility Requirements

- Every interactive element: unique descriptive `id`
- Single `<h1>` per page with proper heading hierarchy
- `prefers-reduced-motion` support for all animations
- Skip navigation link as first focusable element
- Color contrast ratio ≥ 4.5:1 (WCAG AA)

## Detection Pattern

If any UI file contains hardcoded hex colors, browser-default fonts, or fails `biome check`, flag as `UI_TOKEN_VIOLATION` in `.beads/issues.jsonl`.

## Cross-References

- `apps/kovelai/site/src/app/globals.css` — Token definitions
- `~/.gemini/antigravity/skills/design-taste-frontend/SKILL.md` — Design taste rules
- `~/.gemini/antigravity/skills/stitch-design/SKILL.md` — Stitch integration
- `AGENTS.md` → Stack Lock (Next.js 16, Tailwind v4, shadcn/ui)
- `GEMINI.md` → TACSOP 5 Linting Doctrine (Biome)
