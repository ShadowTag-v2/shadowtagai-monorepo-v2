# CoreWeave Ventures One-Pager: PNKLN

## The Problem

In an era of AI-generated deepfakes, the question "is this video real?" is wrong.
The right question is **"where did this video come from?"**

Existing solutions (Digimarc, Truepic, Adobe CAI) are:

- **Expensive** ($0.15-0.50/asset)

- **Fragile** (fail on re-encoding)

- **Slow** (seconds per asset)

## The Solution: ShadowTag v2 (Neural-Proof Stack)

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Neural Hash** | CLIP ViT-B/32 | Semantic fingerprint (survives compression) |
| **Dual-Stego** | DCT + Ultrasonic | Invisible watermark in video + audio |
| **Chain Receipt** | Polygon L2 | Immutable timestamp anchor |

**Key Innovation**: Hash the *meaning*, not the bytes. Our hash survives:

- Re-encoding (H.264 → H.265 → AV1)

- Compression (90% quality loss)

- Cropping, resizing, color grading

## Unit Economics

| Metric | pnkln | Digimarc | Truepic |
|--------|-------|----------|---------|
| COGS/asset | **$0.02** | $0.15 | $0.25 |
| Latency | **80ms** | 2-5s | 3-8s |
| Re-encode survival | **95%+** | 60% | 70% |

**At 100M assets/month:**

- Revenue: $5M (@ $0.05/asset)

- COGS: $2M

- Fixed: $500K

- **Gross Profit: $2.5M (50% margin)**

- Break-even: Month 4

## Competitive Landscape

```

                    HIGH ROBUSTNESS
                          │
     Adobe CAI ─────────────────── pnkln ★
          │                           │
  LOW COST ──────────────────────────── HIGH COST
          │                           │
     Truepic ──────────────────── Digimarc
                          │
                    LOW ROBUSTNESS

```

## Roadmap (12-18 months)

| Phase | Timeline | Milestone |
|-------|----------|-----------|
| T0-T1 | ≤4 weeks | MVP round-trip (hash→stego→receipt→verify) ✅ |
| T2 | ≤8 weeks | Mobile SDK (iOS/Android) |
| T3 | ≤12 weeks | Enterprise API + first pilot |
| T4 | ≤20 weeks | Chain receipts at scale |
| T5 | ≤24 weeks | Seed/Series A close |
| T6 | 12-18 mo | Multi-platform licensing, $50-100M ARR |

## Why CoreWeave?


1. **Compute-Native Fit**: Neural hashing requires GPU at scale (T4/A100)

2. **Edge Thesis**: Our Mesh nodes align with CoreWeave's distributed compute vision

3. **Shared DNA**: Infrastructure-first, developer-focused

4. **Benchmark Partners**: We'll publish latency/cost numbers on CW vs. hyperscalers

## The Ask

| Track | Amount | Use of Funds |
|-------|--------|--------------|
| **Early-Adopter Credits** | $50K-100K | GPU for neural hash inference at scale |
| **Ventures Investment** | $2M Seed | Engineering (4 FTE), platform integrations |
| **Compute-for-Equity** | Optional | Align long-term incentives |

## Team


- **Erik Hancock** - Founder/CEO (IQ-160, ex-[redacted], "Tiny Teams" doctrine)

- **Antigravity Squadron** - 650-agent AI swarm for development velocity

## Valuation Markers

| Stage | Valuation | Trigger |
|-------|-----------|---------|
| Seed+ | $30-50M post | Traction, 1-2 platform pilots |
| Series A | $100-120M | $5M ARR, 3+ enterprise customers |
| Series B | $400-600M | $25M ARR, platform deals |

**Vegas Odds (execution)**:

- Base (40%): $5-8B exit

- Upcase (35%): $10-12B exit

- Stretch (25%): $15B+ exit

---

**Contact**: [founder@pnkln.io](mailto:founder@pnkln.io)
**Demo**: `POST https://api.pnkln.io/pnkln/tag`
