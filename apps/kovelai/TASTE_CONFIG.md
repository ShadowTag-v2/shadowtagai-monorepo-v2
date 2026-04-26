# taste-skill Configuration — KovelAI "Quiet Luxury" Profile
# Source: external_repos/taste-skill/skills/taste-skill/SKILL.md
# Calibrated for the KovelAI legal-tech landing page aesthetic.

## Active Baseline Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| DESIGN_VARIANCE | 6 | Professional legal-tech — more structured than artsy, but avoids clinical boredom. Split-screen hero allowed. |
| MOTION_INTENSITY | 5 | Subtle, premium motion (spring physics, stagger reveals) without overwhelming legal professionals. |
| VISUAL_DENSITY | 3 | "Quiet Luxury" — generous whitespace, art gallery spacing, breathing room between sections. |

## Anti-Slop Rules Applied

1. **THE LILA BAN**: No purple/blue AI gradients. KovelAI palette: Zinc/Slate base + Emerald accent.
2. **ANTI-CENTER BIAS**: Hero sections use split-screen (50/50) or left-aligned content/right-aligned asset.
3. **ANTI-EMOJI**: All icons from @phosphor-icons/react or @radix-ui/react-icons. Zero emojis.
4. **ANTI-CARD OVERUSE**: Features use divide-y or negative space grouping, not boxed cards.
5. **Serif BAN for UI**: Dashboard and interactive elements use exclusively Sans-Serif (Geist/Satoshi).

## Typography Lock

- **Headlines**: `text-4xl md:text-6xl tracking-tighter leading-none` (Geist or Satoshi)
- **Body**: `text-base text-gray-600 leading-relaxed max-w-[65ch]`
- **Viewport**: `min-h-[100dvh]` (never `h-screen`)
- **Layout**: CSS Grid (`grid grid-cols-1 md:grid-cols-3 gap-6`) over Flex-Math

## Performance Guardrails

- Grain/noise filters: fixed, pointer-events-none pseudo-elements only
- Animate ONLY via `transform` and `opacity`
- Z-index reserved for: Sticky Nav, Modals, Overlays
- framer-motion: `useMotionValue`/`useTransform` for continuous animations (not `useState`)
