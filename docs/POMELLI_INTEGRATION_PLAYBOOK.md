# Pomelli Integration Playbook

> Google Pomelli — AI-powered social media campaign generator for business brands.

## Overview

Google Pomelli (labs.google.com/pomelli) is a Google Labs experiment that analyzes a website
to extract brand DNA (name, colors, fonts, logo, images, brand values) and generates
social media campaigns from it.

## Integration Status

| Site | Pomelli Status | Logo | Images | Font | Brand Tone |
|------|:---:|:---:|:---:|:---:|:---:|
| kovelai.web.app | ✅ Onboarded | ❌ Needs upload | 0 auto-extracted | Inter | Legal AI, privilege |
| shadowtagai.web.app | ✅ Onboarded | ✅ Auto-detected | 2 auto-extracted | Inter | Sovereign, secure |

## Workflow

### Step 1: Onboarding
1. Navigate to `https://labs.google.com/u/0/pomelli/onboarding`
2. Enter the website URL
3. Click "Get started"
4. Pomelli crawls the site and extracts brand DNA
5. Review the "Business DNA" summary

### Step 2: Business DNA Review
Pomelli extracts:
- **Name**: From `<title>` or `<meta name="og:title">`
- **URL**: Canonical URL
- **Logo**: From `<link rel="icon">` or og:image
- **Fonts**: From computed CSS (prefers Google Fonts like Inter)
- **Images**: Key visual assets from the page
- **Colors**: Dominant color palette (extracted from CSS + images)

### Step 3: Campaign Generation
After confirming the Business DNA:
1. Click "Looks good"
2. Pomelli generates social media campaigns
3. Each campaign includes:
   - Headline + body copy
   - Suggested image/video concepts
   - Platform-specific formats (Instagram, X, LinkedIn, Facebook)
   - Hashtag suggestions
   - Posting schedule recommendations

### Step 4: Export & Use
- Download campaign assets
- Copy text to clipboard
- Export to Canva (if connected)
- Schedule via Buffer/Hootsuite integration

## SEO/Meta Requirements for Best Results

For optimal Pomelli extraction, ensure these meta tags are present:

```html
<meta property="og:title" content="KovelAI — Privilege-Preserving Legal AI" />
<meta property="og:description" content="The Shopify for Legal AI" />
<meta property="og:image" content="https://kovelai.web.app/og-image.png" />
<meta property="og:url" content="https://kovelai.web.app/" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
```

## Brand Values (Verified Against Product Copy)

### KovelAI
| Pomelli Value | Product Copy Match | Status |
|---------------|-------------------|--------|
| Legal AI | ✅ "Privilege-Preserving Legal AI" | Aligned |
| Data Sovereignty | ✅ "Zero-trust data pipeline" | Aligned |
| Secure | ✅ "HMAC-SHA256 Kovel attestation" | Aligned |
| Privacy-First | ✅ "Auto-logout + screen wipe" | Aligned |
| Monetization | ✅ "Dual-billing engine" | Aligned |

### ShadowTagAI
| Pomelli Value | Product Copy Match | Status |
|---------------|-------------------|--------|
| Sovereign AI | ✅ "Sovereign intelligence pipeline" | Aligned |
| Zero-Leakage | ✅ "Zero-trust cognitive routing" | Aligned |
| Authoritative | ✅ "Judge 6 policy gate" | Aligned |
| Technical | ✅ "14-block Gideon OS" | Aligned |
| Secure | ✅ "Betterleaks + Cor.30 framework" | Aligned |

## Pomelli Campaign Ideas (Generated)

### KovelAI Campaigns
1. **"Monetize Your Legal Expertise"** — LinkedIn, targeted at solo practitioners
2. **"Research Shouldn't Cost Your Peace"** — Instagram carousel, privacy angle
3. **"Secure Law Day's Digital Frontier"** — X thread, regulatory compliance

### ShadowTagAI Campaigns
1. **"Sovereign AI for Your Firm"** — LinkedIn, enterprise positioning
2. **"Data Sovereignty by Design"** — Blog post, thought leadership
3. **"Zero-Leakage AI Inference"** — X post, technical audience

## Maintenance

- Re-run Pomelli onboarding after major brand/copy changes
- Upload KovelAI logo when brand asset is finalized
- Monitor campaign performance via Pomelli analytics dashboard
- Update this playbook when new campaigns are generated
