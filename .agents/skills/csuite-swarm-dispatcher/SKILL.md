---
name: C-Suite Swarm Dispatcher
description: Routes Cor.71 C-Suite Swarm troop activations through MCP servers with Jules orchestration and Pomelli A/B testing.
version: 1.0.0
tags: [csuite, mcp, routing, headfade, revenue, pomelli, jules]
---

# C-Suite Swarm Dispatcher — MCP-First Persona Routing

## Purpose

This skill routes C-Suite Swarm troop activations to the correct MCP servers.
Each troop is a **persona-constrained agent** that only loads context relevant to its domain,
cutting token usage by ~40% and eliminating hallucination from irrelevant context.

## Knowledge Item Reference

**ALWAYS** read these KIs before executing any troop activation:
- `knowledge/csuite-swarm-headfade-strategy/artifacts/strategy.md` — Full troop definitions, revenue milestones, MCP routing table
- `knowledge/v26-zenith-obsidian-cloudrun/artifacts/implementation_plan.md` — Cloud Run infrastructure plan

## Troop Activation Protocol

### Step 1: Identify the Troop

| Activation Keyword | Troop | Role |
|--------------------|-------|------|
| `Troop Alpha` / `CEO` / `distribution` / `embed` | Alpha | CEO Squadron — Strategy + Distribution |
| `Troop Bravo` / `JD` / `legal` / `compliance` | Bravo | JD Squadron — Legal + Compliance |
| `Troop Charlie` / `CTO` / `architecture` / `perf` | Charlie | CTO Squadron — Architecture + Performance |
| `Troop Delta` / `CFO` / `revenue` / `upsell` / `funnel` | Delta | CFO Squadron — Revenue + Profit |
| `Troop Echo` / `MD` / `medical` / `verification` | Echo | MD Squadron — Scientific Verification |

### Step 2: Load Troop-Specific Context ONLY

**CRITICAL**: Do NOT load full codebase context. Each troop has a scoped context budget:

- **Alpha**: Design specs, Firebase Data Connect docs, market analysis
- **Bravo**: Security rules, legal frameworks, *Heppner* case law, BUSINESS_CONTEXT_LOCKED.md
- **Charlie**: Cloud Run docs, Lighthouse baselines, kernel_chain/ code, Dockerfile
- **Delta**: Stripe config (from secrets), Firestore analytics, pricing models, BUSINESS_CONTEXT_LOCKED.md
- **Echo**: HIPAA requirements, data flow diagrams, PII inventory

### Step 3: Route Through MCP Servers

```
MCP ROUTING TABLE
─────────────────────────────────────────────────────────────
Troop Alpha → StitchMCP → firebase-mcp → sequential-thinking
Troop Bravo → google-developer-knowledge → sequential-thinking → firebase-mcp
Troop Charlie → chrome-devtools-mcp → firebase-mcp → sequential-thinking
Troop Delta → firebase-mcp (Firestore) → sequential-thinking → stripe-mcp
Troop Echo → sequential-thinking → google-developer-knowledge
─────────────────────────────────────────────────────────────
```

**Execution order**: Primary MCP first → Secondary for verification → Tertiary for cross-check.

### Step 4: Jules Integration

After troop produces output, dispatch to Jules:
1. **Code changes** → Jules creates a GitHub issue with the diff
2. **Infrastructure changes** → Jules creates a Cloud Task
3. **Design changes** → Jules triggers Pomelli A/B test

### Step 5: Pomelli Integration

Pomelli runs A/B variants of troop outputs:
1. **UI changes** (Alpha/Delta) → Deploy variant A and B via StitchMCP
2. **Performance changes** (Charlie) → Run Lighthouse on both variants
3. **Security changes** (Bravo) → Test rule variants against Firestore emulator

## Revenue Milestone Execution

### Milestone 1: Beachhead ($3k MRR) — Charlie leads
```
1. firebase-mcp: Deploy kernel_chain/executor.py to Cloud Run
2. chrome-devtools-mcp: Lighthouse audit — verify p99≤90ms
3. sequential-thinking: Validate Judge#6 enforcement at 10M decisions/year
4. Jules: Create monitoring Cloud Task
```

### Milestone 2: Upsell Redesign ($15k MRR) — Delta leads
```
1. firebase-mcp: Query Firestore for user journey drop-off analytics
2. sequential-thinking: Monte Carlo simulation on conversion paths
3. StitchMCP: Generate high-converting funnel screen variants
4. Pomelli: A/B test top 3 variants
5. Jules: Deploy winner to production
```

### Milestone 3: Risk Simulation ($10k MRR) — Delta + Bravo
```
1. sequential-thinking: Monte Carlo churn simulation (10K iterations)
2. google-developer-knowledge: Research retention best practices
3. firebase-mcp: Query Firestore for churn indicators
4. sequential-thinking: CFO + Lawyer vote on drop-off countermeasures
5. Jules: Deploy retention patches as Cloud Tasks
```

### Milestone 4: Distribution Play ($50k MRR) — Alpha leads
```
1. sequential-thinking: Strategy Diamond + Blue Ocean analysis
2. StitchMCP: Design HeadFade Embed <iframe> Player
3. firebase-mcp: Set up Firebase Data Connect for embed data
4. chrome-devtools-mcp: Lighthouse audit on embed widget
5. Pomelli: A/B test embed placement strategies
6. Jules: Create publisher outreach task queue
```

## Prompt Repetition (arXiv:2512.14982)

When delegating to Flash-Lite workers via Jules or Pomelli:
- **Repeat the constraint 3x** in the prompt
- **DO NOT repeat** for Gemini Thinking or reasoning models
- This applies to: NotebookLM queries, Pomelli swarm directives, sub-agent tasks

## Anti-Patterns (PROHIBITED)

- Loading full codebase context for any single troop (40% token waste)
- Activating multiple troops simultaneously without Jules orchestration
- Bypassing MCP routing with raw terminal commands
- Using BullMQ for any queue operation (Cloud Tasks ONLY)
- Running Monte Carlo simulations without sequential-thinking MCP
