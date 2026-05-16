# Cor. Cost Engineering

## Purpose

Define the cost-engineering hierarchy for the current `pnkln` stack.

This document connects:
- truth surfaces
- model spend
- routing
- cache reuse
- product packaging
- business leverage

## First rule

Do not optimize model spend on top of architectural confusion.

Fix truth first.

## Priority order

1. truth surfaces
2. cache reuse
3. swarm routing
4. tiered escalation
5. retrieval/eval discipline
6. product packaging
7. pricing and valuation

## 1. Truth surfaces

The highest-value cost optimization is removing structural ambiguity.

A confused repo/control plane creates:
- duplicated work
- duplicated prompts
- duplicated infra assumptions
- duplicated debugging
- duplicated model calls

Canonical truth must come first:
- one canonical monorepo manifest
- one canonical MCP config
- one canonical product/lab split

## 2. Cache reuse

Once truth is stable, reduce repeated prefill spend.

Principle:
- cache shared stable context once
- reuse it across many requests
- send only task deltas repeatedly

This applies most directly to the Google-native production path.

## 3. Swarm routing

Treat concurrent tasks as a work pool, not isolated full-context jobs.

The router should:
- attach shared cache/context where possible
- classify task complexity
- keep most work on the cheap fast path
- escalate rarely

## 4. Tiered escalation

Do not pay heavy-model prices for routine work.

Use the cheapest acceptable path for:
- extraction
- formatting
- summary generation
- low-risk transformation
- routine retrieval-grounded responses

Escalate only for:
- architectural anomalies
- high ambiguity
- high-risk review
- deep synthesis

## 5. Retrieval/eval discipline

Model cost without retrieval discipline becomes waste.

Needed:
- retrieval quality checks
- grounding pass rate
- false-support detection
- cache hit tracking
- cost-per-useful-task measurement

## 6. Product packaging

The commercial product must stay simple.

### counselconduit
This is the business-facing MVP.
It should present:
- a clean product story
- premium economics
- stateless workflow clarity
- BYOK-friendly adoption

### uphillsnowball
This remains:
- local lab
- runtime experimentation path
- internal R&D engine

### pnkln
This remains:
- doctrine
- control plane
- operator logic
- cost/routing discipline

## 7. Pricing and valuation

Pricing should sit on top of:
- actual retrieval quality
- latency and throughput confidence
- route efficiency
- cache reuse
- measured task economics

Not on top of unverified hype.

## Highest-value opportunities

### Opportunity 1
Fix truth surfaces first.
This unlocks every other optimization.

### Opportunity 2
Operationalize recovered code instead of redrafting it:
- green loop
- CSP collector
- retriever eval
- feature flags
- pricing model
- OCR summaries
- Drive-ingest daemon

### Opportunity 3
Use the recovered CounselConduit blueprint as the business-facing spec while `pnkln/uphillsnowball` remains the internal engine.

## Metrics to run the system by

Track:
- blended cost per task
- input tokens per completed task
- cache reuse rate
- fast-path completion rate
- escalation rate
- retrieval grounding pass rate
- latency by tier
- revenue-quality alignment

## Canonical split

- `counselconduit` = product
- `pnkln` = doctrine/control plane
- `uphillsnowball` = lab

That split is itself a cost optimization because it reduces architectural drift.
