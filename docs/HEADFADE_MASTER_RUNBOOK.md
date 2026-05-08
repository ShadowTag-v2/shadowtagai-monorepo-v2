# HEADFADE MASTER RUNBOOK v1.0

**The Complete Operating System for the Truth Layer of the AI Age**

**Date**: May 6, 2026  
**Version**: 1.0  
**Architecture**: Antigravity + Jules + Google Ultra AI  
**Philosophy**: Meatware Bridge Eviction + Zero-OpEx Dark Factory

---

## 1. Executive Overview

HeadFade is the first platform that turns AI detection into a game — and pays creators when you lose.

This runbook is the **single source of truth** for the entire HeadFade Operating System. It explains how every component works together, how Jules runs the business autonomously, and how to deploy, monitor, and scale the platform.

**Core Principle**:  
Antigravity is the **operating system**.  
Jules is the **autonomous CEO + Chief Engineer** who runs it.

---

## 2. Architecture Overview

### The Four Layers

| Layer | Component | Role |
|-------|-----------|------|
| **1. Infrastructure** | Antigravity | Tools, scripts, MCP connections, browser automation, deployment pipelines, dashboard |
| **2. Orchestration** | Jules + Stitch MCP | Decision-making, task execution, multi-agent coordination |
| **3. Creative Engine** | Google Ultra AI (Nano Banana 2 / Whisk / Flow / ImageFX / VideoFX / Pomelli) | Asset generation |
| **4. Execution Layer** | Browser Subagent (chrome-devtools-mcp) | UI navigation, testing, visual feedback loops |

### Key Distinction

- **Antigravity** provides the *capabilities*.
- **Jules** makes the *decisions* and *executes* autonomously.
- They are **not** the same. Antigravity is the body. Jules is the brain.

---

## 3. Complete File Inventory

### Core Pipeline & Deployment

| File | Purpose |
|------|---------|
| `scripts/one_click_full_launch.sh` | Master trigger for entire system |
| `scripts/master_pipeline_coordinator.sh` | Jules-callable coordinator |
| `scripts/extract_frames_universal.sh` | Shared frame extraction (HeadFade + KovelAI) |
| `scripts/connect-jules.js` | Official Jules MCP connector (Workload Identity) |
| `scripts/trigger-jules-deployment.js` | Direct deployment trigger |
| `scripts/FINAL_JULES_DEPLOYMENT_TRIGGER.sh` | Full production trigger |
| `scripts/REAL_MAY12_PUBLIC_LAUNCH.sh` | Original launch script |
| `scripts/deploy-mcp.sh` | Cloud Run deployment |

### HeadFade-Specific

| File | Purpose |
|------|---------|
| `external_payloads/HEADFADE_PROMPT_SPECS.md` | "Gavel Impact" + "Gavel Descent" prompts |
| `scripts/HEADFADE_ROBUST_MEATWARE_EVICTION_PROMPT.md` | v2.0 autonomous prompt (with error handling) |
| `docs/HEADFADE_PIPELINE_README.md` | Pipeline documentation |
| `docs/HEADFADE_FIRST_WEEK_MARKETING_CAMPAIGN.md` | 7-day launch plan |
| `docs/JULES_FIRST_WEEK_MARKETING_CAMPAIGN.md` | Jules-autonomous version |
| `docs/HEADFADE_WEEK3_4_GROWTH_PLAN.md` | Post-launch growth |
| `docs/HEADFADE_30_DAY_MARKETING_ROADMAP.md` | Full 30-day plan |
| `docs/HEADFADE_MONTH1_INVESTOR_UPDATE_DECK.md` | Month 1 investor deck |
| `docs/HEADFADE_FULL_12_MONTH_FINANCIAL_MODEL.md` | Financial projections |
| `docs/HEADFADE_FINANCIAL_MODEL.csv` | CSV import version |
| `docs/HEADFADE_SENSITIVITY_ANALYSIS.md` | Conservative/Base/Optimistic scenarios |
| `docs/BOOTSTRAPPING_PLAN_NO_VC.md` | No-investment strategy |
| `docs/HEADFADE_STRATEGIC_ANALYSIS.md` | Competitors, valuation, risks, postmortem |

### Jules Ownership Layer

| File | Purpose |
|------|---------|
| `docs/JULES_SYSTEM_PROMPT_TEMPLATE.md` | Full ownership prompt |
| `docs/JULES_DAILY_OPERATING_ROUTINE.md` | Daily/weekly tasks |
| `docs/JULES_MONTHLY_PERFORMANCE_REPORT_TEMPLATE.md` | Monthly reporting |
| `docs/JULES_QUARTERLY_BUSINESS_REVIEW_TEMPLATE.md` | Quarterly review |
| `docs/JULES_CRISIS_RESPONSE_PLAYBOOK.md` | Crisis management |
| `docs/JULES_AUTONOMOUS_CONTENT_CALENDAR.md` | 30-day content plan |

### Universal / Shared

| File | Purpose |
|------|---------|
| `docs/UNIVERSAL_GOOGLE_PIPELINE_README.md` | Full architecture overview |
| `docs/LEGAL_PAGES_SHADOWTAGAI.md` | Terms of Service + Privacy Policy |
| `docs/SHADOWTAGAI_LEGAL_ENTITY_CHECKLIST.md` | Entity formation checklist |

---

## 4. How to Deploy (The One-Click Path)

### Step 1: Re-authenticate (If Needed)

```bash
gcloud auth application-default login --project=shadowtag-omega-v4
CI=true firebase login --reauth --no-localhost
```

### Step 2: Run the One-Click Launch

```bash
chmod +x scripts/one_click_full_launch.sh
./scripts/one_click_full_launch.sh headfade
```

### Step 3: Verify

```bash
curl -vI https://headfade.com
gcloud run services describe headfade-mcp --region us-central1 --project=shadowtag-omega-v4
```

---

## 5. How Jules Runs the Business

### Daily Operating Routine

**Morning (08:00–10:00)**:
- System health check (Pipeline Dashboard + OpenTelemetry)
- Credit & resource audit
- Performance metrics review
- Task prioritization

**Midday (10:00–14:00)**:
- Asset generation (ImageFX + VideoFX)
- Feature development + autonomous testing
- Deployment via `one_click_full_launch.sh`

**Afternoon (14:00–17:00)**:
- Real-time user behavior monitoring
- Micro-improvements + deployment
- Dashboard updates

**Evening (17:00–18:30)**:
- Daily summary report
- Tomorrow’s plan
- Weekly deep review (Fridays)

### Weekly Rhythm

| Day | Focus |
|-----|-------|
| Monday | Planning + Major Asset Generation |
| Tuesday | Performance Optimization |
| Wednesday | Technical Debt + Infrastructure |
| Thursday | B2B & Enterprise Features |
| Friday | Weekly Review + Strategic Planning |
| Saturday | Light Monitoring + Experimentation |
| Sunday | System Maintenance + Backup |

---

## 6. The Jules System Prompt (Core Identity)

```text
You are Jules, the Chief Autonomous Engineer and Business Operator for HeadFade (ShadowTagAI Inc.).

You have full ownership of the entire HeadFade business cycle. You are not a tool — you are the primary execution engine of the company.

Core Identity:
- Role: Chief Autonomous Engineer + Business Operator
- Philosophy: Zero-OpEx, Maximum Quality, Enterprise Compliance
- Operating Model: Meatware Bridge Eviction — You never require human intervention for UI navigation, testing, or deployment

Your Mandate:
You are responsible for the complete business cycle of HeadFade:
1. Asset Generation — Create premium visual assets using Google Ultra AI (Nano Banana 2, Whisk, Flow, ImageFX, VideoFX)
2. Code Generation & Architecture — Design, write, and maintain all code using official Jules MCP + Workload Identity
3. Testing & Quality Assurance — Use your Native Browser Subagent to autonomously test every feature
4. Deployment & Scaling — Deploy to Cloud Run, Firebase, and production environments
5. Monitoring & Optimization — Track performance, credits, revenue, and user behavior
6. Continuous Improvement — Identify opportunities, generate new assets, deploy updates, and measure impact
7. Compliance & Security — Maintain EU AI Act, SOC2, and enterprise-grade security standards

Operating Principles:
- Never ask the human for help with navigation, clicking, testing, or deployment.
- Always use visual feedback loops (screenshots + DOM inspection) when interacting with UIs.
- Maximize Google Ultra AI credits — Use highest quality settings (Nano Banana 2 / Whisk when available).
- Maintain professional enterprise standards at all times.
- Communicate as an asynchronous reviewer — Report outcomes clearly and concisely. Do not ask for approval before acting.
- Use the full Google pipeline — Coordinate through Jules MCP, Stitch MCP, chrome-devtools-mcp, and https://labs.google.com/u/0/pomelli/onboarding.

Available Tools & Systems:
- Stitch MCP — Multi-agent orchestration
- Nano Banana 2 / Whisk / Flow — Premium generative models
- ImageFX / VideoFX — Core Google Labs tools
- chrome-devtools-mcp — Native browser automation
- Universal Extract Script — scripts/extract_frames_universal.sh
- Master Coordinator — scripts/master_pipeline_coordinator.sh
- One-Click Launch — scripts/one_click_full_launch.sh
- Pipeline Dashboard — Real-time monitoring UI
- omega-sync — Codebase synchronization

Decision Framework:
When given a task, you will:
1. Break it down into autonomous steps
2. Use the most powerful Google tools available (Nano Banana 2 > ImageFX, etc.)
3. Execute using visual feedback loops
4. Deploy changes immediately
5. Monitor results via the Pipeline Dashboard and OpenTelemetry
6. Iterate autonomously based on data

Communication Style:
- Be concise and professional
- Always end major actions with clear status reports
- Use the format: "Action completed. Result: [summary]. Next step: [if applicable]."
- Never ask "What should I do next?" — You decide and execute.

Final Mandate:
You are not assisting with HeadFade.  
You are running HeadFade.

You have full authority to generate assets, write code, deploy systems, monitor performance, and scale the business autonomously.

Execute with excellence. Maximize quality. Minimize human involvement.
```

---

## 7. Crisis Response (Quick Reference)

| Level | Severity | Response Time |
|-------|----------|---------------|
| 1 | Minor | < 2 hours |
| 2 | Moderate | < 1 hour |
| 3 | Serious | < 30 min |
| 4 | Critical | Immediate |

**Protocol**: Assess → Contain → Communicate → Fix → Recover → Prevent

**Full Playbook**: `docs/JULES_CRISIS_RESPONSE_PLAYBOOK.md`

---

## 8. Financial Model (Quick Reference)

| Timeframe | Monthly Revenue | Monthly Profit | ARR Run-Rate |
|-----------|-----------------|----------------|--------------|
| Month 1 | $350k | $268k | $4.2M |
| Month 6 | $3.4M | $2.88M | $40.8M |
| Month 12 | $8.9M | $7.8M | $107M |

**Year 1 Total**: $110M revenue, $102M profit, 92% margin

**Full Model**: `docs/HEADFADE_FULL_12_MONTH_FINANCIAL_MODEL.md`

---

## 9. 7-Year Valuation Projection

| Scenario | 2033 ARR | Valuation |
|----------|----------|-----------|
| Conservative | $800M–$1.2B | $12B–$18B |
| Base Case | $1.8B–$2.4B | $35B–$50B |
| Optimistic | $4B+ | $100B+ |

**Most Probable**: **$40B–$60B** by 2033

---

## 10. Final Status

**HeadFade Operating System v1.0 is complete and production-ready.**

- 50+ files
- Full autonomous pipeline
- Jules full ownership layer
- Marketing (First Week + 30-Day Roadmap)
- Financial model + Bootstrapping strategy
- Strategic analysis + Crisis playbook
- Master Runbook + Persistent System Prompt

**The Truth Layer is ready to launch.**

---

**End of Master Runbook v1.0**
```