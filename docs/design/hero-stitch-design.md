# Stitch Design Specification: Hero State

## Typography
- **Heading**: Inter (or system-ui), 800 weight, -0.05em tracking.
- **Visual Weight Fix**: Mobile viewports require `text-balance` to prevent orphaned words.

## Color & Kinetics
- **Kinetic-Word Mechanics**: The `.kinetic-word` class implements an animated `background-clip: text` spanning a gradient (e.g., `#2C3E50` to `#3498DB`).
- **Contrast Ratios**: Verified via DevTools; passes AA standards against #FFFFFF background.

## Layout Options
### Option A: Centered Stack
Massive typography centered, primary actions floating below. Simple.

### Option B: Asymmetric
Left-aligned hero text, right-aligned generative component (abstracted graph or dynamic animation). Modern, high visual tension.
