# KovelAI Frontend Scope — v11.0 Target

> **Version**: v1.0 | **Last Updated**: 2026-04-22
> **Status**: Specification — No code implementation in v10.0

---

## Overview

The KovelAI frontend is currently a hybrid:
- **Static SPA**: `public/index.html` (771 lines, production-deployed)
- **Next.js stub**: `src/app/page.tsx` (13 lines, placeholder)
- **Static pages**: chat, dashboard, onboarding, portal, pricing, transcripts, etc.

This document specifies the v11.0 frontend buildout scope, including the Invisible Meter, warm handoff, session recap, layman summary, and premium SaaS design patterns.

---

## 1. Invisible Meter UI Spec

### Purpose
Track client engagement time without showing the client. The "Invisible Meter" is the key metric: **average client spends >45 minutes per session**.

### Architecture
```
┌─ Client Browser ──────────────────────────────────┐
│                                                    │
│  [HIDDEN STATE]                                    │
│  • session_start: Date.now()                       │
│  • message_count: 0                                │
│  • interaction_depth: 0 (S.E.U. layer tracker)     │
│  • last_activity: Date.now()                       │
│                                                    │
│  [VISIBLE TO CLIENT]                               │
│  • NO timer                                        │
│  • NO "are you still there?" prompts               │
│  • Ambient micro-animations (pulsing orbs, glow)   │
│  • Progressive depth indicators (subtle)           │
│                                                    │
│  [VISIBLE TO ATTORNEY DASHBOARD]                   │
│  • Real-time session duration                      │
│  • Message count and depth                         │
│  • S.E.U. layer progression                        │
│  • Engagement score (0-100)                        │
│  • Alert at >45 min (target met)                   │
│                                                    │
└────────────────────────────────────────────────────┘
```

### Design Principles
1. **No visible timer** — session timer is hidden from client
2. **No interrupts** — no "are you still there?" prompts
3. **Ambient micro-animations** — typing indicators, subtle glow, pulsing orbs
4. **Progressive depth** — start with reassurance, gradually surface actionable intelligence
5. **"One More Thing" cadence** — end every response with a gentle hook

### Implementation
- Client-side: `requestAnimationFrame` loop tracking `performance.now()` deltas
- Server-side: `session_pin_monitor.py` tracks heartbeat + message count
- Attorney dashboard: real-time WebSocket feed of session metrics

---

## 2. Warm Handoff UI Spec

### Purpose
When client complexity exceeds threshold θ, seamlessly hand off to a human attorney.

### Trigger Conditions
- Complexity score from Oracle Studio > 0.7
- Risk score from Judge 6 > 0.5
- Client explicitly requests attorney
- Session duration > 60 minutes
- Vent Mode emotional intensity > HIGH

### UX Flow
```
┌─ Client View ──────────────────────────────────────┐
│                                                     │
│  "Based on what you've shared, I think it would    │
│   be really valuable for you to speak directly     │
│   with an attorney who specializes in this area.   │
│                                                     │
│   We've found someone who can take this further    │
│   for you."                                        │
│                                                     │
│   ┌──────────────────────────────────────────┐      │
│   │ 🟢 Attorney Name is available            │      │
│   │    Specialization: [Practice Area]       │      │
│   │                                          │      │
│   │    [Connect Now]  [Schedule for Later]   │      │
│   └──────────────────────────────────────────┘      │
│                                                     │
│  "Your session summary will be shared with them    │
│   so you don't have to repeat anything."           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Attorney Notification
- Google Workspace Chat message with session summary
- Email with structured brief (from Vent Mode summarizer)
- Dashboard badge with real-time session link

---

## 3. Session Recap Component Spec

### Purpose
Frame every session ending as an emotional victory.

### Display Template
```
┌─ Session Recap ─────────────────────────────────────┐
│                                                      │
│  ✨ Here's what you now understand that you didn't   │
│     before:                                          │
│                                                      │
│  1. [Key insight extracted from session]              │
│  2. [Key insight extracted from session]              │
│  3. [Key insight extracted from session]              │
│                                                      │
│  📋 Key Terms Explained:                             │
│  • [Jargon Term] — [Layman explanation]              │
│  • [Jargon Term] — [Layman explanation]              │
│                                                      │
│  📎 Action Items:                                    │
│  □ [Action with timeline]                            │
│  □ [Action with timeline]                            │
│                                                      │
│  💬 "You're doing the right thing by understanding   │
│      this. Take your time — we're here whenever      │
│      you need us."                                   │
│                                                      │
│  [Return to Overview]  [Print Summary]               │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Data Source
- `oracle_studio.py` → `session_recap` field
- `vent_mode.py` → `VentIntakeSummary` entity extraction
- `empathy_templates.py` → `get_warm_close()` for closing message

---

## 4. Layman Summary Rendering Spec

### Purpose
Auto-detect legal jargon and footnote with plain-English translations.

### Pattern
```
Response text with inline jargon references¹ and legal terms².

──────────────────────────────────────────────
¹ Summary judgment — When a court decides a case 
  without a full trial because the key facts are 
  not in dispute.
² Statute of limitations — The deadline for filing 
  a lawsuit. After this deadline, you generally 
  can't bring the case to court.
```

### Implementation
1. Oracle Studio Stage 7 (Format) generates `layman_footnotes[]`
2. Frontend renders inline superscript markers
3. Footnotes display in a collapsible panel below the response
4. Attorney can toggle between "Client View" and "Legal View"

---

## 5. Premium SaaS Design Reference (unusualmachines.com)

### Design Patterns to Adopt
Based on premium SaaS design patterns (analogous to unusualmachines.com aesthetic):

| Pattern | Implementation |
|---------|---------------|
| **Dark hero with luminous accents** | Deep navy (#0a0f1e) + gold (#c9a96e) — EXISTING |
| **Cinematic video backgrounds** | Hero video (`legal-data-arch.mp4`) — EXISTING |
| **Glassmorphism cards** | Frosted glass UI panels with backdrop-filter |
| **Micro-animations** | Scroll-triggered reveals, hover state transitions |
| **Typography hierarchy** | Inter 300–800, clear h1→h6 progression |
| **Asymmetric layouts** | Break grid monotony with staggered sections |
| **Particle/motion backgrounds** | Subtle animated mesh gradient (GPU-accelerated) |
| **Testimonial rotator** | Client success stories (anonymized) |
| **Pricing toggle** | Monthly/Annual with savings highlight |
| **CTA gradient buttons** | Gold→amber gradient with hover glow |

### Current State (v10.0)
- `DESIGN_SYSTEM.md` exists with navy/gold palette
- Static HTML SPA deployed to Firebase Hosting
- Hero video live on CDN
- Lighthouse: P93+ / A93+ / BP100 / SEO100

### v11.0 Target
- Rebuild on Next.js App Router (from `src/app/page.tsx`)
- Component library with design system tokens
- Responsive (mobile-first)
- PWA manifest + service worker (existing `sw.js`)
- Scroll-driven animations (Intersection Observer API)
- Citation UI (from Perplexity Paradigm spec)
