# Component Spec: Hero Banner

**Source Section:** `.homeBanner` (index 2)
**Extracted from:** https://www.unusualmachines.com
**Target Component:** `src/components/Hero.tsx`

---

## Extracted Styles (getComputedStyle)

```css
.homeBanner {
  height: 648px;
  display: flex;
  justify-content: center;
  align-items: center; /* lg: center, sm: end */
  position: relative;
}

.homeBanner__bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 648px;
  background-image: url("USA_FC-1-1-1.jpg");
  background-size: cover;
  background-position: 50% 50%;
  z-index: 0; /* behind content */
}
```

## Structure

```
section.homeBanner.d-flex.justify-content-center.align-items-lg-center.zoom-in
  ├── figure.homeBanner__bg (absolute positioned background image)
  └── div.homeBanner__content (content overlay, z above bg)
       └── div.container
            └── div.row.no-gutters.justify-content-between.align-items-center
                 ├── div.homeBanner__content__text.col-lg-6
                 │    └── h2: "Here to serve the American drone industry."
                 └── div.homeBanner__content__quotations.col-lg-6
                      ├── h2: "NYSE: UMAC"
                      └── div#QuoteDiv (live stock ticker widget)
```

## Layout Pattern

- **Two-column layout** (6/6 grid on lg breakpoint)
- Left column: Hero headline (large text)
- Right column: Stock ticker / data widget
- Vertically centered within 648px hero
- Background image is full-bleed via absolute positioned `<figure>`

## Content Extracted

- **Headline:** "Here to serve the American drone industry."
- **Ticker label:** "NYSE: UMAC"
- **Stock price font:** 25px bold
- **Stock change font:** 19px

## Background Image

- **URL:** `https://cdn-sites-assets.mziq.com/wp-content/uploads/sites/1374/2024/07/USA_FC-1-1-1.jpg`
- **Rendering:** `cover`, centered, full-section fill
- **Pattern:** Cinematic American flag / industrial imagery

## KovelAI Adaptation Notes

- Replace headline with KovelAI value proposition
- Replace stock ticker with key metrics or CTA panel
- Replace background with our Veo-generated hero video (`hero-bg.mp4`)
- Maintain the two-column split layout (text left, widget right)
- Keep 648px min-height or vh-based equivalent
- Add gradient overlay on background for text readability
