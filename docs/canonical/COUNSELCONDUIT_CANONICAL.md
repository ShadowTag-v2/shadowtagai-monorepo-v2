# CounselConduit — Canonical Business Plan
**Version:** March 2026 (Definitive)
**Supersedes:** counsel_conduit_asymmetric_ai_plan, broad_market_plan v1/v2, definitive_master_plan,
direct_access_gateway, final_blueprint, gcp_comprehensive_plan, investment_memo, offshore_master_plan,
omnibus_master_plan, onprem_reseller_plan, pitch_deck, pure_gateway_stack, sovereign_corporate_plan,
stateless_byok_plan, ultimate_master_plan, upl_shield_analysis, vpn_tunnel_model, vpn_tunnel_v2 (17 docs → 1)

---

## 1. The Problem
NY SB 7263 (Chatbot Liability) and State Bar ethics rules have paralyzed Big Tech's Law models.
If a consumer uses a public chatbot for legal advice, the AI creator is strictly liable.
Simultaneously, law firms leak privileged client data into multi-tenant LLMs daily — destroying
Attorney-Client Privilege and exposing evidence to e-discovery.

## 2. The Solution: Learned Intermediary Safe Harbor
CounselConduit is a **Stateless B2B Infrastructure Router**. By routing interactions exclusively
through our edge proxy into the licensed attorney's dashboard, we invoke the Learned Intermediary
Doctrine — legally transforming the AI from a consumer chatbot into protected Attorney Work Product.

**We absorb Big Tech's SB 7263 liability and transmute it into standard legal malpractice,
shielded entirely by the lawyer's existing malpractice insurance.**

## 3. The Magic Link Mechanic
1. Lawyer subscribes → receives Magic Link generator
2. Lawyer texts Magic Link to client
3. Client session runs through CounselConduit Edge Proxy → **60-minute ephemeral session, auto-evaporates**
4. Track A (Pacifier): Haiku-class model gathers facts, validates stress — no legal advice, UPL-clean
5. Track B (Oracle): Transcript + evidence async-routed to Claude-Law / Gemini-Law → full strategy memo
   deposited directly into firm's Clio/OneDrive vault via OAuth
6. Shadow Invoice API drops a 4.5-hour draft invoice onto the lawyer's desk

**The Arbitrage:** Lawyer bills client $1,575 for work synthesized in minutes.

## 4. Architecture (Split-Plane / Zero-Data)
| Plane | Host | What's stored |
|-------|------|---------------|
| Control Plane | CounselConduit (Delaware C-Corp) | Token counts, session duration, Stripe metadata ONLY |
| Data Plane | Firm's own AWS/GCP (LiteLLM proxy) | All prompts, answers, embeddings — **we never touch it** |
| Client Session | Cloudflare Zero Trust / Vercel Edge | RAM wiped on stream completion |

**If CounselConduit is subpoenaed: there is no hard drive to seize.**

## 5. Tech Stack
- Next.js 15 + TypeScript (Control Plane)
- Supabase (PostgreSQL: telemetry only — session_duration_seconds, tokens_consumed, model_routed)
- LiteLLM proxy (one-click deploy on firm's cloud)
- Stripe (subscription tiers)
- Clerk (attorney auth + MFA)
- Cloudflare Zero Trust (edge session isolation)

## 6. Pricing Tiers
| Tier | Price | Who |
|------|-------|-----|
| Starter | $1,500/mo | Solo practitioners / boutiques (1–5 attorneys) |
| Professional | $5,000/mo | Mid-market litigation (10–50 attorneys) |
| Enterprise | $15,000/mo | AmLaw 200 + F500 GC |
| On-Premise Enclave | $40,000/mo | Firms requiring physical hardware inside firewall |

## 7. Financial Projections
| Milestone | Timeline | ARR |
|-----------|----------|-----|
| TTFC (first paid) | 45–60 days | — |
| Pre-Seed close | Month 0–12 | $25K MRR → ~$300K ARR |
| Seed milestones | Month 12 | $2–3M ARR (50 firms) |
| Series A | Month 12–24 | $2–15M ARR (AmLaw 200 wedge) |
| Series B | Month 24–40 | $15M+ ARR (IB + Healthcare horizontal) |

**Raise:** Pre-Seed $2–3M → Series A $10–15M → Series B $30–50M

## 8. IP / Patent Claims (Priority)
1. Context-Bound Ephemeral Hash Routine (stateless routing proof)
2. UI Spoliation Mechanism — interface self-evaporates on session end (proves e-discovery impossibility)
3. Dual-Payload Router — Common Carrier / Telecom classification (exempts us as data processor)
4. Privilege Portal — compute-to-billable-hour ledger (from provisional_patent_claims.md)
5. Objective Options AST Intercept — blocks conclusive AI language, forces 3 objective paths

## 9. Competitive Moat
- Truepic, Digimarc, Harvey.ai: none of these are **infrastructure routers** — they are products
- We are legally closer to an ISP than a legal tech company
- First to obtain ethics board opinion letters across NY + CA = permanent wedge
- The "Learned Intermediary" framing has no prior art at scale

## 10. Exit
**Target:** Month 36–48
**Acquirers:** Thomson Reuters (Westlaw), LexisNexis, Clio, Microsoft (Co-Pilot for Legal)
**Thesis:** We become the malpractice insurance requirement for AI-in-law. Acquirer pays to retire the liability.
**Valuation:** $200M–$500M (10–15x ARR at $15–30M ARR)
