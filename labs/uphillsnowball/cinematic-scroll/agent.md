# agent.md — Cinematic Scroll Website Template

## Project Description
Premium cinematic scroll-stopping website with frame-by-frame animation driven by scroll position.
100% Google-native pipeline: Nano Banana 2/Pro → Veo 3.1 → ffmpeg → scroll hero.

## Design System

### Colors
- **Primary**: `hsl(200, 100%, 60%)` (electric cyan)
- **Secondary**: `hsl(280, 100%, 65%)` (vivid purple)
- **Accent**: `hsl(340, 100%, 60%)` (hot magenta)
- **Backgrounds**:
  - Dark: `hsl(220, 20%, 8%)` — primary surface
  - Card: `hsl(220, 20%, 12%)` — elevated surfaces
  - Glass: `rgba(255, 255, 255, 0.05)` — glassmorphism panels
- **Text**:
  - Primary: `hsl(0, 0%, 95%)`
  - Secondary: `hsl(0, 0%, 65%)`
  - Accent: inherited from primary palette

### Typography
- **Headings**: `'Outfit', sans-serif` — weight: 700/800
- **Body**: `'Inter', sans-serif` — weight: 400/500
- **Code**: `'JetBrains Mono', monospace`
- **Scale**: fluid clamp() — min 1rem, preferred 1.25vw, max 1.5rem

### Elements
- **Border radius**: 16px (cards), 12px (buttons), 999px (pills)
- **Glassmorphism**: backdrop-filter: blur(20px) + border: 1px solid rgba(255,255,255,0.1)
- **Shadows**: 0 8px 32px rgba(0,0,0,0.4)
- **Gradients**: linear-gradient(135deg, primary, secondary)

## Page Sections

### 1. Navigation
- Fixed top, glassmorphism background
- Logo left, links center, CTA right
- Scroll progress indicator (thin gradient bar)
- Hide on scroll down, show on scroll up

### 2. Hero (Cinematic Scroll)
- Full viewport height × N (N = frame count ratio)
- Frame images loaded from `/frames/` directory
- Canvas element draws current frame based on scroll position
- Overlay text with parallax offset
- Formula: `frameIndex = Math.floor(scrollProgress * totalFrames)`

### 3. Story Section
- Horizontal scroll within vertical scroll (scroll-snap)
- Each card: image + text block
- Fade-in on intersection (IntersectionObserver)

### 4. Features
- 3D model viewer (Three.js + .glb file)
- Rotation tied to scroll position
- Feature cards with glassmorphism
- Icons with gradient fills

### 5. Reviews / Testimonials
- Infinite marquee (CSS animation)
- Star ratings + avatar + quote
- Pause on hover

### 6. Footer
- Gradient top border
- Social links, newsletter form, copyright
- Wave SVG separator

## Global Animations
- **Scroll-triggered**: IntersectionObserver + CSS classes
- **Page transitions**: Fade + slide (300ms ease-out)
- **Micro-interactions**: Button hover scale(1.02), link underline slide
- **Loading**: Skeleton screens with shimmer gradient
- **Performance**: `will-change: transform` on animated elements, `content-visibility: auto` for off-screen

## File Structure
```
project/
├── index.html
├── css/
│   ├── reset.css
│   ├── design-tokens.css
│   ├── components.css
│   └── animations.css
├── js/
│   ├── scroll-engine.js      # Frame sequence controller
│   ├── nav.js                 # Navigation behavior
│   ├── intersection.js        # Scroll-triggered animations
│   └── three-viewer.js        # 3D model integration
├── frames/                    # Extracted video frames
│   ├── frame_0001.png
│   ├── frame_0002.png
│   └── ...
├── assets/
│   ├── fonts/
│   ├── icons/
│   └── models/                # .glb 3D models
└── agent.md                   # This file
```

## Hard Rules
1. NO video playback for scroll effects — frames only (video = choppy/trash)
2. NO Tailwind — vanilla CSS with design tokens
3. NO React/Vue/Svelte — vanilla JS only (unless explicitly requested)
4. ALL images must be lazy-loaded except hero frames
5. ALL animations must respect `prefers-reduced-motion`
6. MUST score 90+ Lighthouse performance
7. MUST have semantic HTML (h1 hierarchy, ARIA labels)
8. Canvas rendering for frame sequences (NOT img tag swapping)
9. Preload first 10 frames, lazy-load rest via IntersectionObserver
10. Dark mode ONLY (no light mode toggle needed)
