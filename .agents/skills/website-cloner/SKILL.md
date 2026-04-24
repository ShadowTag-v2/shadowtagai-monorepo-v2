---
name: website-cloner
description: >
  Reverse-engineer and clone any website into a pixel-perfect modern codebase.
  Adapted from JCodesMore/ai-website-cloner-template (12.4k★, MIT).
  Uses Chrome DevTools MCP for browser automation and spec-driven extraction.
  Supports vanilla HTML/CSS, Vite, or Next.js output targets.
  Trigger on: "clone this site", "rebuild this page", "pixel-perfect copy",
  "reverse-engineer this website", "replicate this design".
---

# Website Cloner — Antigravity Skill

> **Origin:** Adapted from [JCodesMore/ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) (MIT).
> Ported for Antigravity's Chrome DevTools MCP, sequential execution, and multi-stack output.

## Prerequisites
- **Chrome DevTools MCP** must be connected and the target URL loaded in a browser tab
- Target URL must be accessible (not behind auth unless already logged in)
- Output directory established in the monorepo

## Guiding Principles

### 1. Completeness Beats Speed
Every component spec must contain **everything** needed to rebuild it: exact CSS values from `getComputedStyle()`, downloaded assets with local paths, real text content, interaction models. If a builder prompt requires guessing ANY value — a color, font size, padding — the extraction has failed.

### 2. Small Tasks, Perfect Results
Complex sections must be decomposed. **Complexity budget:** If a component spec exceeds ~150 lines of content, break it into sub-components. A features grid with 3 card variants = 3 specs + 1 wrapper spec.

### 3. Real Content, Real Assets
Extract actual text via `element.textContent`. Download every `<img>`, `<video>`, inline `<svg>`. Check for **layered assets** — multiple images stacked via absolute positioning or background-image layers.

### 4. Foundation First (Sequential, Non-Negotiable)
Before any component work: global CSS tokens, fonts, downloaded assets, base layout. Everything after this can be parallel.

### 5. Extract Appearance AND Behavior
For every element, extract:
- **Appearance:** Exact computed CSS via `getComputedStyle()`
- **Behavior:** What changes, what triggers it, how the transition works

### 6. Identify Interaction Model BEFORE Building
Before any interactive section: Is it click-driven, scroll-driven, hover-driven, or time-driven?
1. **Scroll first** — observe if things change as you scroll
2. If scroll-driven → extract mechanism (IntersectionObserver, scroll-snap, sticky, animation-timeline)
3. If not → test click/hover interactivity
4. Document explicitly: `INTERACTION MODEL: scroll-driven with IntersectionObserver`

### 7. Extract Every State
Tabbed content → click each tab, extract per-state content
Scroll-dependent → capture styles at position 0 AND after trigger
Hover states → before/after CSS values and transitions

## Pipeline

### Phase 1: Reconnaissance

#### 1A. Screenshots
Using Chrome DevTools MCP:
```
take_screenshot → full page at desktop (1440px)
resize_page → 390px width
take_screenshot → full page at mobile
```
Save to `docs/design-references/` or equivalent output directory.

#### 1B. Global Extraction
Run via `evaluate_script`:

```javascript
// Master extraction script — run once on the target page
(() => {
  const result = {};

  // Fonts
  result.fonts = [...new Set(
    [...document.querySelectorAll('*')].slice(0, 300)
      .map(el => getComputedStyle(el).fontFamily)
  )];

  // Colors from CSS custom properties
  result.customProperties = {};
  for (let sheet of document.styleSheets) {
    try {
      for (let rule of sheet.cssRules) {
        if (rule.selectorText === ':root' || rule.selectorText === 'html') {
          for (let i = 0; i < rule.style.length; i++) {
            const prop = rule.style[i];
            if (prop.startsWith('--')) {
              result.customProperties[prop] = rule.style.getPropertyValue(prop).trim();
            }
          }
        }
      }
    } catch(e) {}
  }

  // All images
  result.images = [...document.querySelectorAll('img')].map((img, i) => ({
    src: img.src,
    alt: img.alt,
    naturalWidth: img.naturalWidth,
    naturalHeight: img.naturalHeight,
    parentClasses: img.parentElement?.className,
    position: getComputedStyle(img).position,
    zIndex: getComputedStyle(img).zIndex
  }));

  // All videos
  result.videos = [...document.querySelectorAll('video')].map(v => ({
    src: v.src || v.querySelector('source')?.src,
    poster: v.poster,
    autoplay: v.autoplay,
    loop: v.loop
  }));

  // Background images
  result.backgroundImages = [...document.querySelectorAll('*')]
    .filter(el => {
      const bg = getComputedStyle(el).backgroundImage;
      return bg && bg !== 'none';
    })
    .map(el => ({
      url: getComputedStyle(el).backgroundImage,
      element: el.tagName + '.' + (el.className?.toString().split(' ')[0] || '')
    }));

  // SVG count
  result.svgCount = document.querySelectorAll('svg').length;

  // Favicons
  result.favicons = [...document.querySelectorAll('link[rel*="icon"]')]
    .map(l => ({ href: l.href, sizes: l.sizes?.toString() }));

  // Section map
  result.sections = [...document.querySelectorAll('section, header, nav, footer, main, [class*="section"], [class*="hero"], [class*="banner"]')]
    .map((sec, i) => {
      const rect = sec.getBoundingClientRect();
      return {
        index: i,
        tag: sec.tagName,
        className: sec.className?.toString().substring(0, 100),
        width: Math.round(rect.width),
        height: Math.round(rect.height),
        top: Math.round(rect.top + window.scrollY)
      };
    });

  return result;
})();
```

#### 1C. Mandatory Interaction Sweep
1. **Scroll sweep:** Scroll slowly top to bottom. At each section, observe:
   - Header changes? Record scroll trigger position
   - Elements animate in? Record type
   - Auto-switching tabs? Record mechanism
2. **Click sweep:** Click every interactive element — tabs, buttons, dropdowns
3. **Hover sweep:** Hover cards, buttons, links — record before/after CSS
4. **Responsive sweep:** Test at 1440px, 768px, 390px

Save findings to `docs/research/BEHAVIORS.md`.

#### 1D. Page Topology
Map every section top-to-bottom:
- Visual order
- Fixed/sticky vs flow
- Z-index layers
- Interaction model per section
- Dependencies between sections

Save to `docs/research/PAGE_TOPOLOGY.md`.

### Phase 2: Foundation

Sequential, do not parallelize:
1. Create global CSS with extracted design tokens (colors, fonts, spacing)
2. Download all assets (images, videos, SVGs, fonts) to output directory
3. Extract inline SVGs as components
4. Create TypeScript interfaces for content structures (if using TS)
5. Verify build/lint passes

### Phase 3: Component Extraction & Build

For each section in the topology:

#### Step 1: Extract
Per-component CSS extraction script:

```javascript
((selector) => {
  const el = document.querySelector(selector);
  if (!el) return JSON.stringify({ error: 'Not found: ' + selector });
  const props = [
    'fontSize','fontWeight','fontFamily','lineHeight','letterSpacing','color',
    'textTransform','textDecoration','backgroundColor','background',
    'padding','paddingTop','paddingRight','paddingBottom','paddingLeft',
    'margin','marginTop','marginRight','marginBottom','marginLeft',
    'width','height','maxWidth','minWidth','maxHeight','minHeight',
    'display','flexDirection','justifyContent','alignItems','gap',
    'gridTemplateColumns','gridTemplateRows',
    'borderRadius','border','borderTop','borderBottom','borderLeft','borderRight',
    'boxShadow','overflow','overflowX','overflowY',
    'position','top','right','bottom','left','zIndex',
    'opacity','transform','transition','cursor',
    'objectFit','objectPosition','mixBlendMode','filter','backdropFilter',
    'whiteSpace','textOverflow','WebkitLineClamp'
  ];
  function extractStyles(element) {
    const cs = getComputedStyle(element);
    const styles = {};
    props.forEach(p => {
      const v = cs[p];
      if (v && v !== 'none' && v !== 'normal' && v !== 'auto' && v !== '0px' && v !== 'rgba(0, 0, 0, 0)')
        styles[p] = v;
    });
    return styles;
  }
  function walk(element, depth) {
    if (depth > 4) return null;
    return {
      tag: element.tagName.toLowerCase(),
      classes: element.className?.toString().split(' ').slice(0, 5).join(' '),
      text: element.childNodes.length === 1 && element.childNodes[0].nodeType === 3
        ? element.textContent.trim().slice(0, 200) : null,
      styles: extractStyles(element),
      images: element.tagName === 'IMG'
        ? { src: element.src, alt: element.alt } : null,
      children: [...element.children].slice(0, 20).map(c => walk(c, depth + 1)).filter(Boolean)
    };
  }
  return JSON.stringify(walk(el, 0), null, 2);
})('SELECTOR');
```

#### Step 2: Write Component Spec
Create `docs/research/components/<name>.spec.md`:

```markdown
# <ComponentName> Specification

## Overview
- **Target file:** `src/components/<ComponentName>.tsx` (or .html/.css)
- **Screenshot:** `docs/design-references/<screenshot>.png`
- **Interaction model:** <static | click-driven | scroll-driven | time-driven>

## DOM Structure
<Element hierarchy>

## Computed Styles (exact getComputedStyle values)

### Container
- display: ...
- padding: ...
- (every relevant property)

### <Child element>
- fontSize: ...
- color: ...

## States & Behaviors

### <Behavior name>
- **Trigger:** <exact mechanism>
- **State A:** <before CSS values>
- **State B:** <after CSS values>
- **Transition:** <transition CSS>

## Per-State Content (if applicable)
<Content per tab/state>

## Assets
- <List of images, videos, SVGs used>

## Text Content (verbatim)
<All text, copy-pasted>

## Responsive Behavior
- **Desktop (1440px):** <layout>
- **Tablet (768px):** <changes>
- **Mobile (390px):** <changes>
```

#### Step 3: Build Component
Using the spec as the complete brief, build the component. Verify compilation.

#### Step 4: Assemble
Wire all components into the main page layout per topology.

### Phase 4: Visual QA Diff
1. Open original + clone side-by-side
2. Compare section by section at 1440px
3. Compare at 390px
4. Test all interactions
5. Fix discrepancies by re-checking specs

## Anti-Patterns (PROHIBITED)

- Building click-based UI when original is scroll-driven (or vice versa)
- Extracting only the default state (must get ALL tab/scroll states)
- Missing overlay/layered images
- Approximating CSS values instead of using `getComputedStyle()`
- Giving a builder too much scope (>150 lines = split it)
- Building without a spec file
- Skipping responsive extraction
- Using placeholder content instead of real extracted text

## Completion Report
When done, report:
- Total sections built
- Total components created
- Total spec files written
- Total assets downloaded
- Build/lint status
- Visual QA results
- Known gaps
