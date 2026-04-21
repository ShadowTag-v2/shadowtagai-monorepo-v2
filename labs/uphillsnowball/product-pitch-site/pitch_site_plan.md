# Pitch Site Implementation Plan — LOCKED

> **Status:** LOCKED — Execute in a FRESH thread with command `"Execute pitch_site_plan.md"`
> **Created:** 2026-04-21T19:17:00Z
> **Context Window:** This plan is self-contained. No prior conversation context is required.
> **Doctrine:** YOLO MODE (STATE A) — Meatware Bridge for UI-only tools.

---

## Mission

Clone the structural skeleton of [unusualmachines.com](https://www.unusualmachines.com/), extract its exact DOM geometry (pixel dimensions, character limits, grid breakpoints), generate cognitive suite payloads for Google Labs UI tools, and then assemble a premium product pitch site with our own branding, copy, and AI-generated assets.

## Product Pitch (COMMANDER MUST FILL IN)

> [!CAUTION]
> **Before executing this plan, replace this block with your 2-3 sentence product pitch.**
> Example: "KovelAI is the Shopify for Legal AI — a privilege-preserving routing tier that lets law firms monetize client AI research while maintaining attorney-client privilege under the Heppner doctrine."

```
PRODUCT_PITCH = """
[COMMANDER: INSERT YOUR 2-3 SENTENCE PRODUCT PITCH HERE]
"""
```

---

## Phase 1: The 1:1 Structural Clone

### Objective
Produce a pixel-perfect local replica of `unusualmachines.com` with all interactive JavaScript (tabs, sliders, hover states) and CSS grid intact.

### Primary Tool
[JCodesMore/ai-website-cloner-template](https://github.com/JCodesMore/ai-website-cloner-template) — Puppeteer-based headless cloner that captures rendered DOM, not just raw HTML.

### Execution Steps

```bash
# Step 1: Clone the cloner repo (sparse, no .git)
cd /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/labs/uphillsnowball/product-pitch-site
git clone --depth 1 https://github.com/JCodesMore/ai-website-cloner-template.git cloner-tool
cd cloner-tool
npm install
```

```bash
# Step 2: Run the cloner against the target
node clone.js --url "https://www.unusualmachines.com/" --output "../cloned-site"
```

```bash
# Step 3: Verify the clone
cd ../cloned-site
npx -y http-server -p 8890 -c-1
```

### Fallback Strategy
If the JCodesMore repo fails or is broken:

```bash
# Fallback A: website-scraper with Puppeteer plugin
npx -y website-scraper --urls "https://www.unusualmachines.com/" \
  --directory "../cloned-site" \
  --plugins website-scraper-puppeteer

# Fallback B: httrack
httrack "https://www.unusualmachines.com/" -O "../cloned-site" -r3 --near --robots=0

# Fallback C: Manual Puppeteer snapshot script
```

### Verification Criteria (Chrome DevTools MCP)
- [ ] Local site loads at localhost:8890
- [ ] All interactive tabs/sliders function identically to production
- [ ] All images load (no broken src tags)
- [ ] CSS grid layout matches production at 1280px viewport
- [ ] JavaScript event listeners are attached and firing

---

## Phase 2: DOM Geometry & Context Extraction

### Objective
Extract the exact pixel dimensions, aspect ratios, character limits, and grid structure from the cloned site.

### Tool
**Chrome DevTools MCP** — `take_snapshot`, `evaluate_script`, `take_screenshot`

### Step 2.1: Serve + Navigate
```bash
npx -y http-server cloned-site -p 8890 -c-1
```
```
navigate_page(url="http://localhost:8890", type="url")
```

### Step 2.2: Extract Hero Media Geometry
```javascript
() => {
  const hero = document.querySelector('video, .hero video, .hero-video, [class*="hero"] video, [class*="hero"] img');
  if (!hero) return { error: 'No hero media found' };
  const rect = hero.getBoundingClientRect();
  const computed = window.getComputedStyle(hero);
  return {
    type: hero.tagName, width: Math.round(rect.width), height: Math.round(rect.height),
    aspectRatio: (rect.width / rect.height).toFixed(4),
    naturalWidth: hero.naturalWidth || hero.videoWidth || null,
    naturalHeight: hero.naturalHeight || hero.videoHeight || null,
    objectFit: computed.objectFit, objectPosition: computed.objectPosition,
    sources: hero.tagName === 'VIDEO'
      ? Array.from(hero.querySelectorAll('source')).map(s => ({ src: s.src, type: s.type }))
      : [{ src: hero.src }]
  };
}
```

### Step 2.3: Extract ALL Image Placeholders
```javascript
() => {
  return Array.from(document.querySelectorAll('img')).map((img, i) => {
    const rect = img.getBoundingClientRect();
    const computed = window.getComputedStyle(img);
    return {
      index: i,
      selector: img.id ? '#'+img.id : (img.className ? '.'+img.className.split(' ')[0] : 'img:nth-of-type('+(i+1)+')'),
      src: img.src, alt: img.alt,
      width: Math.round(rect.width), height: Math.round(rect.height),
      aspectRatio: rect.height > 0 ? (rect.width / rect.height).toFixed(4) : 'N/A',
      naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight,
      objectFit: computed.objectFit, visible: rect.width > 0 && rect.height > 0
    };
  }).filter(img => img.visible);
}
```

### Step 2.4: Extract Text Node Character Limits
```javascript
() => {
  const textMap = [];
  const measureText = (container, label) => {
    container.querySelectorAll('h1,h2,h3,h4,h5,h6,p,span,li,a,button,[class*="title"],[class*="desc"],[class*="text"]')
      .forEach((el, i) => {
        const rect = el.getBoundingClientRect();
        const computed = window.getComputedStyle(el);
        if (rect.width === 0 || el.textContent.trim().length === 0) return;
        textMap.push({
          container: label, tag: el.tagName,
          currentText: el.textContent.trim().substring(0, 100),
          charCount: el.textContent.trim().length,
          containerWidth: Math.round(rect.width),
          fontSize: computed.fontSize, fontWeight: computed.fontWeight,
          lineHeight: computed.lineHeight,
          maxLines: Math.round(rect.height / parseFloat(computed.lineHeight)) || 1
        });
      });
  };
  document.querySelectorAll('[role="tabpanel"],.tab-content,.tab-pane,[class*="tab-"],[class*="slider"],[class*="slide"]')
    .forEach((c, i) => measureText(c, 'interactive-'+i));
  document.querySelectorAll('section,[class*="section"],main > div')
    .forEach((s, i) => measureText(s, 'section-'+i));
  return textMap;
}
```

### Step 2.5: Extract Grid Breakpoints
```javascript
() => {
  return Array.from(document.querySelectorAll('section,[class*="section"],main > div,.container,[class*="container"]'))
    .map((s, i) => {
      const computed = window.getComputedStyle(s);
      const rect = s.getBoundingClientRect();
      return {
        index: i, display: computed.display,
        gridTemplateColumns: computed.gridTemplateColumns,
        flexDirection: computed.flexDirection, gap: computed.gap,
        padding: computed.padding, width: Math.round(rect.width),
        maxWidth: computed.maxWidth, children: s.children.length
      };
    }).filter(s => s.width > 0);
}
```

### Step 2.6: Output
Save combined data to: `labs/uphillsnowball/product-pitch-site/GEOMETRY_MAP.json`

---

## Phase 3: The Meatware Bridge (Cognitive Suite Delegation)

### Output: `labs/uphillsnowball/product-pitch-site/COGNITIVE_PAYLOADS.md`

The agent auto-generates this file using GEOMETRY_MAP.json measurements. Contains exact copy-paste prompts for:

### 3.1 — Mariner (Copywriting)
URL: https://gemini.google.com/mariner — One prompt per text node, character-constrained.

### 3.2 — Labs FX / Whisk (Image Gen)
URL: https://labs.google/fx — Prompts with exact aspect ratios from GEOMETRY_MAP.

### 3.3 — Opal (Structured Workflow)
URL: https://opal.google/ — Node-box configs for competitor analysis + pitch refinement.

### 3.4 — Flow (Visual Pipeline)
URL: https://labs.google/fx/tools/flow — NB2 generate → style transfer chain.

### 3.5 — Veo 3.1 (PROGRAMMATIC — No Meatware)
```bash
python scripts/veo_pipeline.py \
  --prompt "Cinematic product showcase..." --model "veo-3.1" \
  --aspect-ratio "16:9" --duration 8 \
  --output "labs/uphillsnowball/product-pitch-site/assets/hero-video.mp4"

# Post-process
ffmpeg -i assets/hero-video.mp4 -c:v libx264 -crf 28 -preset slow \
  -c:a aac -b:a 128k -movflags +faststart -vf "scale=1280:-2" \
  assets/hero-video-web.mp4
ffmpeg -i assets/hero-video-web.mp4 -vframes 1 -ss 00:00:02 assets/hero-poster.jpg
```

---

## Phase 4: Assembly & Stitch Integration

### 4.1 — Asset Placement (human downloads from Labs UIs to assets/)
### 4.2 — Branding Swap (agent: text, images, video, colors, fonts, logo, metadata, favicon)
### 4.3 — Stitch MCP Design System (list_projects → list_design_systems → generate_screen → apply_design_system)
### 4.4 — CSS Validation against GEOMETRY_MAP
### 4.5 — Lighthouse Audit (chrome-devtools-mcp/lighthouse_audit, target P90/A95/BP95/SEO95)

---

## Phase 5: Deployment
Firebase Hosting via MCP doctrine (firebase_get_environment → firebase_init → deploy)

---

## Verification Checklist
- [ ] Phase 1: Clone loads locally w/ interactive elements
- [ ] Phase 2: GEOMETRY_MAP.json valid
- [ ] Phase 3: COGNITIVE_PAYLOADS.md generated
- [ ] Phase 3.5: Veo 3.1 video generated + compressed
- [ ] Phase 4: All branding swapped, CSS validated
- [ ] Phase 4.5: Lighthouse meets targets
- [ ] Phase 5: Deployed + accessible

---

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Cloner repo broken | Fallback: website-scraper → httrack → manual Puppeteer |
| Site blocks scraping | puppeteer-extra-plugin-stealth |
| Labs UI changes | COGNITIVE_PAYLOADS includes screenshots + CSS selectors |
| Wrong aspect ratio | sips/ImageMagick resize to GEOMETRY_MAP dimensions |
| JS breaks after swap | Chrome DevTools MCP evaluate_script verifies listeners |
| Char overflow | Hard limits from Phase 2; prompts enforce EXACTLY N chars |

---

## File Map
```
labs/uphillsnowball/product-pitch-site/
├── pitch_site_plan.md         # THIS FILE
├── GEOMETRY_MAP.json          # Phase 2 output
├── COGNITIVE_PAYLOADS.md      # Phase 3 output
├── cloner-tool/               # Phase 1 cloner repo
├── cloned-site/               # Phase 1 output
├── assets/                    # Phase 3+4 generated assets
└── assembled/                 # Phase 4 final output (deployable)
```

> [!IMPORTANT]
> **To execute:** Open a fresh thread → `"Execute labs/uphillsnowball/product-pitch-site/pitch_site_plan.md"`
> **Prerequisites:** Fill in PRODUCT_PITCH, verify unusualmachines.com accessible, Google Labs auth'd
