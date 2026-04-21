# Pitch Site Implementation Plan — LOCKED v2

> **Status:** LOCKED — Execute in a FRESH thread with command `"Execute labs/uphillsnowball/product-pitch-site/pitch_site_plan.md"`
> **Created:** 2026-04-21T20:12:00Z
> **Revision:** v2 — Autonomous DOM Execution Bridge replaces Meatware Bridge
> **Context Window:** This plan is self-contained. No prior conversation context is required.
> **Doctrine:** YOLO MODE (STATE A) — Browser Subagent for all UI interactions.

---

## Current State (Ground Truth from Thread Sweep)

### What Already Exists
```
labs/uphillsnowball/product-pitch-site/
├── pitch_site_plan.md         # THIS FILE (v2)
├── clone.js                   # ✅ website-scraper + Puppeteer plugin (our scraper)
├── package.json               # ✅ website-scraper 6.0 + puppeteer plugin 2.0
├── node_modules/              # ✅ Installed
├── clone-base/                # ✅ Raw UM clone output (156KB HTML + CSS + JS + images + fonts)
├── site/                      # ✅ ShadowTagAI branded site (26KB HTML + 31KB CSS + 6KB JS + OG image)
├── cloner-tool/               # ✅ JCodesMore/ai-website-cloner-template (Next.js 16 + shadcn + Tailwind 4)
│   ├── .git/                  # ⚠️ Nested .git — gitignored, do NOT commit
│   ├── src/                   # Next.js app structure
│   ├── scripts/               # Cloner scripts
│   └── package.json           # node>=24, Next 16.2.1, React 19.2.4, shadcn 4.1.0
└── (pending)
    ├── GEOMETRY_MAP.json      # Phase 2 output
    ├── COGNITIVE_PAYLOADS.md   # Phase 3 output
    ├── assets/                # Generated assets from Cognitive Suite
    └── assembled/             # Final deployable output
```

### What the `clone-base/` Contains
The `clone.js` script has already run against `unusualmachines.com`:
- `index.html` — 156KB full rendered DOM
- `css/` — Full stylesheet directory
- `fonts/` — Web fonts
- `images/` — All images captured
- `js/` — All interactive JavaScript (tabs, sliders, hover states)
- `js_1` — Additional JS bundle (417KB)
- `Emailapi2.asp`, `QuoteApi.asp` — UM backend stubs (ignore)
- `favicon.ico` — UM favicon (replace)

### What the `site/` Contains
Pre-built ShadowTagAI branded version (459 lines, 26KB) already mirrors the UM structural classes:
- `.header.header--fixed` → ShadowTagAI header with Kovel AI link
- `.homeBanner` → Hero with particles, metrics card (STAI ticker)
- `.homeHighlights` → Recent developments (4 news items)
- `.homeQuickAccess` → Products grid (KovelAI, CounselConduit, Oracle Studio, Judge #6)
- `.homeEvents` → Platform Architecture (3 arch-cards)
- `.homeMetrics` → By The Numbers (6 metric blocks with data-count animation)
- `.homeBusiness` → Revenue Architecture (Dual-Billing, Pricing Tiers, Unit Economics)
- `.homeContact` → Contact form with early access signup
- `.footer` → Footer with links

### What the `cloner-tool/` Is
The JCodesMore repo is a **Next.js 16 + Tailwind 4 + shadcn 4.1 template** for AI-assisted website cloning. It's NOT a scraper — it's a destination framework. The workflow is:
1. Use `clone.js` (or similar scraper) to capture raw HTML/CSS/JS
2. Feed the raw output to an AI coding agent
3. AI reconstructs the site in Next.js/React using shadcn components

> [!IMPORTANT]
> The cloner-tool requires Node >= 24. Verify with `node --version` before `npm install`.

---

## Product Pitch (COMMANDER MUST FILL IN)

> [!TIP]
> **Pitch auto-generated via Strategic Synthesis Protocol — derived from 7,755 LOC CounselConduit analysis, Kovel attestation HMAC-SHA256 mechanism, and Heppner (S.D.N.Y. 2026) doctrine.**

```
PRODUCT_PITCH = """
Every time your attorneys use ChatGPT, Claude, or any AI for client research, they risk
waiving attorney-client privilege — a malpractice exposure that no insurance policy covers
and no ethics board forgives. KovelAI routes every AI query through a sovereign, zero-trust
infrastructure that generates a cryptographic Kovel attestation receipt per session —
court-admissible proof that privilege was preserved, automatically, with zero workflow
disruption. Your firm either deploys privilege-preserving AI infrastructure or bets its
partnership on the hope that opposing counsel never subpoenas the AI transcripts.
"""
```

---

## Phase 1: Structural Clone Verification

### Objective
Verify the existing `clone-base/` captures all interactive elements from `unusualmachines.com` correctly.

### Execution Steps

```bash
# Step 1: Serve the raw clone locally
cd /Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball/labs/uphillsnowball/product-pitch-site
export PATH="/opt/homebrew/bin:$PATH"
npx -y http-server clone-base -p 8890 -c-1
```

```
# Step 2: Chrome DevTools MCP verification
navigate_page(url="http://localhost:8890", type="url")
take_screenshot()   # Visual baseline
take_snapshot()     # DOM structure
```

### If Clone is Incomplete
```bash
# Re-run the scraper
node clone.js
# Output goes to ./clone-base/
```

### Fallback: JCodesMore Direct
```bash
# If clone.js fails, use the JCodesMore cloner-tool directly
cd cloner-tool
export PATH="/opt/homebrew/bin:$PATH"
npm install  # Requires Node >= 24
# Then follow their scripts/ directory workflow
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
Extract exact pixel dimensions, aspect ratios, character limits, and grid structure from both the raw clone AND the existing `site/` branded version.

### Tool
**Chrome DevTools MCP** — `take_snapshot`, `evaluate_script`, `take_screenshot`

### Step 2.1: Serve + Navigate
```bash
npx -y http-server clone-base -p 8890 -c-1
```
```
navigate_page(url="http://localhost:8890", type="url")
```

### Step 2.2: Extract Hero Media Geometry
```javascript
() => {
  const hero = document.querySelector('video, .hero video, .hero-video, [class*="hero"] video, [class*="hero"] img, .homeBanner video, .homeBanner img');
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

## Phase 3: Autonomous DOM Execution Bridge

### Architecture

```
Agent writes precise prompts → COGNITIVE_PAYLOADS.md
Agent generates Veo 3.1 video programmatically → veo_pipeline.py (API)
Agent drives browser_subagent → authenticated Chrome instance
  → Google Labs FX  (image generation, inject prompts, download)
  → Google Gemini    (copywriting, character-constrained)
  → Google Flow/Opal (video, if Veo API fails)
```

### Output: `labs/uphillsnowball/product-pitch-site/COGNITIVE_PAYLOADS.md`

The agent auto-generates this file using GEOMETRY_MAP.json measurements. Contains:

### 3.1 — Copywriting (Gemini via browser_subagent)
- Navigate to `gemini.google.com` using authenticated Chrome
- Input product pitch + character constraints from GEOMETRY_MAP
- Extract copy per text node, mathematically constrained

### 3.2 — Image Generation (Labs FX via browser_subagent)
- Navigate to `labs.google/fx`
- Target prompt text areas via DOM selectors from `take_snapshot`
- Inject prompts with exact aspect ratios from GEOMETRY_MAP
- Click 'Generate', wait for network response
- Download resulting images to `assets/` folder

### 3.3 — Video (Veo 3.1 — PROGRAMMATIC FIRST)
```bash
# Primary: Direct API via veo_pipeline.py
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

**Fallback: Opal/Vids via browser_subagent** (if Veo API quota exceeded)

### 3.4 — Nano Banana 2 (Google Flow via browser_subagent)
- Navigate to `labs.google/fx/tools/flow`
- Generate NB2 images: glassmorphic vault icon, liquid grain textures
- Download watermark-free outputs

### Browser Subagent Authentication Protocol
```
browser_subagent navigates Chrome using the user's active profile.
The user MUST have an authenticated Google Labs session already open.
Agent uses take_snapshot → identify form elements → fill → click → wait_for → download
```

---

## Phase 4: Assembly & Stitch Integration

### 4.1 — Asset Placement
Replace image/video `src` attributes in `site/index.html` with downloaded assets from `assets/`.

### 4.2 — Copy Injection
Replace text nodes with character-constrained copy from Phase 3.1, verified against GEOMETRY_MAP limits.

### 4.3 — Branding Swap
- Swap all remaining UM references
- Update favicon, OG images, meta tags
- Inject brand fonts (Inter, Outfit, JetBrains Mono already in `site/`)

### 4.4 — Stitch MCP Design System
```
list_projects → identify target project
list_design_systems → get current tokens
create_design_system (if needed) → brand colors, typography, shapes
generate_screen_from_text → validate layout
apply_design_system → enforce tokens across screens
```

### 4.5 — CSS Validation Against GEOMETRY_MAP
Chrome DevTools MCP: re-measure all elements, diff against GEOMETRY_MAP, flag any dimension drift > 2px.

### 4.6 — Lighthouse Audit
```
chrome-devtools-mcp: lighthouse_audit
Target: P90+ / A95+ / BP95+ / SEO95+
```

---

## Phase 5: Deployment

### Firebase Hosting via MCP Doctrine
```
1. firebase_get_environment → verify auth
2. read_resource("firebase-mcp-server", "firebase://guides/init/hosting")  
3. firebase_init → hosting config for pitch site
4. Deploy via MCP-orchestrated CLI
5. Verify live URL
```

---

## Verification Checklist
- [ ] Phase 1: Clone loads locally with all interactive elements intact
- [ ] Phase 2: GEOMETRY_MAP.json contains valid measurements for all placeholders
- [ ] Phase 3.1: Copywriting extracted, character-constrained per text node
- [ ] Phase 3.2: Labs FX images downloaded to assets/ at correct aspect ratios
- [ ] Phase 3.3: Veo 3.1 video generated + compressed (hero-video-web.mp4)
- [ ] Phase 3.4: NB2 assets downloaded (vault icon, grain textures)
- [ ] Phase 4.1: All asset src tags updated in assembled HTML
- [ ] Phase 4.2: All text nodes replaced with constrained copy
- [ ] Phase 4.4: Stitch design system applied
- [ ] Phase 4.5: CSS dimensions match GEOMETRY_MAP within 2px tolerance
- [ ] Phase 4.6: Lighthouse meets P90/A95/BP95/SEO95 targets
- [ ] Phase 5: Deployed to Firebase Hosting and accessible

---

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Cloner repo broken | Fallback: website-scraper → httrack → manual Puppeteer |
| Node < 24 for cloner-tool | Use `clone.js` (our scraper) instead — works on Node 18+ |
| Site blocks scraping | `clone-base/` already exists — skip re-scraping |
| Google Labs auth expired | User must have active Google session in Chrome before execution |
| Labs FX UI changes | `take_snapshot` discovers current DOM; CSS selectors adapt dynamically |
| Wrong aspect ratio | sips/ImageMagick resize to GEOMETRY_MAP dimensions post-download |
| JS breaks after swap | Chrome DevTools MCP `evaluate_script` verifies all event listeners |
| Char overflow breaks CSS | Hard limits from Phase 2; prompts enforce EXACTLY N chars |
| Veo API quota exceeded | Fallback to Opal/Vids via browser_subagent |
| Context window exhaustion | This plan is self-contained; execute in fresh thread at 0% usage |

---

## File Map (Final State)
```
labs/uphillsnowball/product-pitch-site/
├── pitch_site_plan.md         # THIS FILE (v2, LOCKED)
├── GEOMETRY_MAP.json          # Phase 2 output
├── COGNITIVE_PAYLOADS.md      # Phase 3 output (prompts + constraints)
├── clone.js                   # Our Puppeteer scraper
├── package.json               # website-scraper deps
├── clone-base/                # Raw UM clone (156KB HTML + assets)
├── site/                      # ShadowTagAI branded version (current)
├── cloner-tool/               # JCodesMore Next.js template (gitignored)
├── assets/                    # Generated assets from Cognitive Suite
│   ├── hero-video.mp4         # Veo 3.1 raw
│   ├── hero-video-web.mp4     # CRF 28 compressed
│   ├── hero-poster.jpg        # First frame extract
│   ├── vault-icon.png         # NB2 glassmorphic vault
│   ├── grain-texture-*.png    # NB2 liquid grain textures
│   └── product-*.png          # Labs FX product images
└── assembled/                 # Final deployable output
    ├── index.html             # Assembled HTML
    ├── style.css              # Branded CSS
    ├── main.js                # Interactive JS
    └── assets/                # Production assets
```

> [!IMPORTANT]
> **To execute:** Open a fresh thread → `"Execute labs/uphillsnowball/product-pitch-site/pitch_site_plan.md"`
> **Prerequisites:**
> 1. Fill in PRODUCT_PITCH above
> 2. Verify `unusualmachines.com` accessible (or use existing `clone-base/`)
> 3. Google Labs authenticated in Chrome (for browser_subagent)
> 4. Node >= 18 for `clone.js`, Node >= 24 for `cloner-tool/`
