# Y Combinator W27 Application — KovelAI (Draft)

## Company

**Company Name:** KovelAI, Inc.
**URL:** https://kovelai.com
**Description (one line):** Privilege-preserving AI research router for law firms — the "Cloudflare for legal AI."
**Founded:** 2026
**Location:** Austin, TX (remote-first)
**Category:** B2B SaaS / Legal Tech / AI Infrastructure

---

## Founders

### Erik Hanson — CEO/CTO
- Solo technical founder
- Built entire platform (30+ modules, 4-layer security architecture) in <30 days
- Background: [your background here]
- Contact: founder@shadowtagai.com

---

## What does your company do?

KovelAI is a privilege-preserving AI research router that lets law firms use AI (Gemini,
Claude, GPT-4, Grok, Perplexity) for client research without breaking attorney-client
privilege.

When lawyers use ChatGPT directly, the research potentially becomes discoverable.
Under *United States v. Heppner* (S.D.N.Y., 2026), AI-generated work product routed
through a proper privilege structure is protected. KovelAI is that structure.

We're a zero-data router — we never store client queries or AI responses. Every session
generates a cryptographic Kovel attestation receipt (HMAC-SHA256) that proves the
communication was privileged, without revealing its contents.

---

## Why did you pick this idea?

1. **Every law firm in America is using AI.** 78% of AmLaw 200 firms have AI policies.
   But none of them have solved the privilege problem.

2. **$350B legal market.** US legal services market. AI adoption is accelerating but
   privilege fears are the #1 blocker.

3. **Regulatory tailwind.** *Heppner* created a clear legal framework. Firms that route AI
   through a Kovel-structured intermediary get privilege protection. Those that don't are exposed.

4. **Zero-data is the moat.** Unlike Casetext (acquired by Thomson Reuters, $650M) or Harvey
   ($2B valuation), we never touch client data. This is architecturally different — we're
   infrastructure, not an AI legal assistant.

---

## What's your progress?

- **Product:** 30+ modules shipped, production on Cloud Run + Firebase Hosting
- **Architecture:** 4-layer security (Injection Shield → Genesis Block → MCP Gateway → Approval)
- **Compliance:** Cor.30 security checklist enforced, SOC 2 prep underway
- **Lighthouse:** A100/BP100/SEO100
- **Revenue model:** Dual-billing via Stripe Connect (client pays lawyer, lawyer pays us)
- **Pricing:** Solo $299/mo, Practice $599/mo, Enterprise $999/mo (all LLM costs included)
- **Customers:** Pre-launch, 3 LOIs from mid-size firms

---

## What's your revenue model?

**Dual-billing engine (Stripe Connect):**

1. **Client → Lawyer:** Client subscribes to AI research portal. Funds flow to lawyer's
   Stripe account. $79 per outcome to IOLTA + $20 KovelAI platform fee.

2. **Lawyer → KovelAI:** Auto-scaling tiered subscription. Solo $299/mo → Practice $599/mo → Enterprise $999/mo.
   ALL LLM API costs included. 85%+ gross margin (context caching reduces LLM costs by 85%).

3. **CLE Revenue:** $49/credit hour for AI competency courses (CLE applications filed in CA, NY, TX).

---

## How much money do you want to raise?

**$500K** on a SAFE note (standard YC terms) to:
1. Hire first sales hire (legal vertical AE) — $150K
2. SOC 2 Type II certification — $27K
3. First 6 months of compute/infrastructure — $50K
4. Remaining: runway to $1M ARR

---

## What's the long-term vision?

**Year 1:** 50 law firms, $600K ARR
**Year 2:** 500 firms + enterprise, $6M ARR
**Year 3:** Platform (marketplace for legal AI tools), $25M ARR

**Exit comp:** Casetext ($650M, Thomson Reuters), Harvey ($2B valuation), Perplexity ($9B for search UX)

KovelAI's endgame is becoming the **privilege infrastructure layer** that all legal AI
products route through. Not another AI legal assistant — the trust layer underneath all of them.

---

## What's unique about your technical approach?

1. **Zero-data router:** We never see, store, or log client queries. Architecturally impossible
   to produce in discovery.

2. **Kovel attestation receipts:** Cryptographic proof of privileged communication without
   revealing content (HMAC-SHA256 hash).

3. **Genesis Block evidence chain:** FRE 902(14) compliant hash chains for court-admissible
   evidence provenance.

4. **Agent-native architecture:** Not a chatbot wrapper. Built for agentic AI — multi-step
   research pipelines with attorney approval gates (ABA Rule 5.3).

5. **Context caching:** 85% LLM cost reduction via Gemini Context Caching API for large
   discovery document processing.

---

## Demo

https://kovelai.com/demo

(To be built: interactive walkthrough of privilege-preserving research flow)
