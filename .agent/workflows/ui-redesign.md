# UI Redesign Workflow

## Goal

Improve existing UI without creating generic AI slop or breaking the design system.

## Steps

1. Run `/repo-pulse`.
2. Select or create a Beads issue.
3. Load:
   - `design.md`
   - `tokens.css`
   - `design/taste_profile.yaml`
   - `.ruler/design-system.md`
4. Audit current UI first:
   - hierarchy
   - spacing
   - typography
   - color roles
   - motion
   - accessibility
   - density
5. Apply the smallest high-leverage redesign.
6. Run:
   - Biome
   - design-system lint
   - relevant tests
7. Capture screenshot or video.
8. Write evidence.
9. Update Beads.
10. Stop after one bounded pass.
