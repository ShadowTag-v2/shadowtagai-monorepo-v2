# Cor. Gemini Aegaeon Protocol

## Purpose

Map Aegaeon-style prefill/decode disaggregation onto Google-native Gemini infrastructure in a way that is operationally useful for `counselconduit` and consistent with the `pnkln` control plane.

This is a cost-engineering and concurrency pattern, not a claim about direct control over Google's underlying GPU memory.

## Core claim

Aegaeon achieved large savings by separating:

- prefill
- decode
- active model residency
- request scheduling

In the Gemini-native stack, the closest practical equivalents are:

- **prefill reuse** → Gemini context caching
- **decode fan-out** → shared-cache multi-request routing
- **token-level scheduling** → swarm router / work queue
- **heavy-model escalation** → tiered routing only when required

## Design principle

Do not resend large shared context into multiple concurrent agent calls.

Cache the shared context once.
Reference the cache repeatedly.
Send only the task-specific delta to each worker request.

## What counts as shared context

The shared slab should contain only stable, high-reuse material such as:

- canonical system instructions
- monorepo architecture summary
- repo truth surfaces
- merge truth surfaces
- operator doctrine
- core retrieval/index summaries
- stable product specs
- stable rulesets and evaluation criteria

It should not contain volatile per-request diffs that change every call.

## Gemini-native mapping

### 1. Disaggregating prefill with a context cache slab

Instead of paying full input-token cost repeatedly for the same large context:

1. Build one **master context slab**
2. Create one Gemini context cache from that slab
3. Reuse the cache id across multiple concurrent agent tasks
4. Send only the small delta per request

### 2. Swarm routing

Treat several concurrent `gemini-3.1-flash-lite-preview` calls as one logical worker pool.

The router:

- accepts incoming work
- classifies work by complexity
- attaches the same cache reference when appropriate
- sends only request-specific diffs
- escalates only exceptional cases

### 3. Decode tiering

Use the cheaper fast path for most work.

#### Fast path

`gemini-3.1-flash-lite-preview` for:

- extraction
- formatting
- lightweight planning
- summarization
- PR shaping
- retrieval-grounded response generation

#### Heavy path

Escalate only when needed for:

- deep architecture reasoning
- major ambiguity
- difficult cross-system reconciliation
- high-risk review

## Example architecture

### Shared slab contents

- canonical monorepo summary
- current repo-root truth
- current MCP/control-plane truth
- `counselconduit` business-facing product spec
- `uphillsnowball` lab/runtime spec
- evaluation rules
- retrieval rules
- coding/operator rules

### Example concurrent events

- 3 PR reviews
- 2 UI-triggered summarizations
- 1 retrieval evaluation run
- 1 pricing-model analysis

All 7 tasks can reference the same shared context cache, while each sends only:

- a diff
- a query
- a small payload
- a task-specific instruction

## Practical savings logic

### Baseline

Without caching:

- repeated large shared prefill
- each worker repays the same input-token burden

### Cached model

With caching:

- shared context is created once
- later requests reference the cache
- only task deltas are sent repeatedly

### Result

Operational spend can fall substantially whenever:

- the shared prompt/context is large
- reuse is high
- concurrency is nontrivial
- most work stays on the fast path

## What this is not

This is not:

- direct VRAM management
- physical GPU residency control
- exact replication of Aegaeon internals on Google-managed infrastructure

It is:

- a practical cost/concurrency analogue
- a prompt-and-routing architecture
- a way to reduce repeated prefill costs

## Intended use in this workspace

### counselconduit

Use this protocol for:

- retrieval-grounded legal workflow processing
- concurrent task handling
- product-facing cost discipline
- high-speed, low-friction agent work

### pnkln

Use this protocol for:

- control-plane routing
- queue discipline
- cache-aware agent orchestration
- operational cost engineering

### uphillsnowball

Use it as a conceptual reference only.
The local lab uses a different physical runtime model.

## Router rules

1. Cache stable shared context
2. Never duplicate massive shared prefill if cache reuse is possible
3. Send only deltas to the fast path
4. Escalate only when fast-path signals require it
5. Measure:
   - cache hit rate
   - fast-path share
   - escalation rate
   - average input tokens per request
   - cost per completed task

## Suggested implementation pieces

- `services/context_slab.py`
- `services/swarm_router.py`
- `services/escalation_policy.py`
- `services/cost_telemetry.py`
- `services/cache_registry.py`

## Metrics

Track at minimum:

- cache creation count
- cache reuse count
- input tokens saved
- fast-path completion rate
- escalation frequency
- blended cost per task
- median latency
- p95 latency

## Business effect

The value is not just lower model spend.

It also improves:

- throughput
- predictability
- concurrency handling
- margin
- packaging confidence for `counselconduit`

## Canonical split

- `counselconduit` = business-facing Google-native product
- `pnkln` = control-plane and operational doctrine
- `uphillsnowball` = local experimentation lab

This protocol belongs primarily to the first two.
