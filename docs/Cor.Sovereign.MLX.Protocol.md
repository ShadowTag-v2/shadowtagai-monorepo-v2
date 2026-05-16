# Cor. Sovereign MLX Protocol

## Purpose

Map the same high-level efficiency ideas onto the local Apple Silicon lab environment used by `uphillsnowball`.

This document is explicitly about the **lab path**, not the `counselconduit` production control plane.

## Scope boundary

This protocol applies to:
- local experimentation
- Apple Silicon runtime behavior
- unified-memory-aware local inference design
- prompt/cache reuse patterns for the lab

It does not redefine the business-facing product stack.

## Core claim

On Apple Silicon, the relevant advantage is not discrete VRAM slab management in the NVIDIA sense.

The important property is:
- **unified memory**
- shared CPU/GPU memory domain
- local inference weight reuse
- cache reuse across lightweight concurrent tasks

## Design principle

Load heavy local artifacts once.
Reuse them repeatedly.
Avoid redoing large prefill work for every local task.

## Local mapping

### 1. Model residency

Keep local model weights resident once where feasible.

Do not spin up multiple heavyweight isolated copies if one resident path plus shared routing can handle the workload.

### 2. Shared prompt/cache reuse

For repeated work against a stable doctrine/context:
- precompute or reuse prompt cache state where the local engine supports it
- avoid rebuilding the same large context repeatedly
- dispatch smaller task deltas against that shared context

### 3. Local swarm routing

Instead of treating each local request as a full isolated inference job:
- maintain one local routing layer
- preserve shared runtime state where possible
- dispatch narrow task deltas to the same resident engine

## Candidate local engines

This lab protocol can be explored with:
- MLX-native flows
- `llama.cpp` with Metal acceleration
- similar local Apple-Silicon-compatible inference backends

The exact engine is secondary to the architecture:
- one resident heavyweight path
- reused cache/context
- narrow deltas
- controlled concurrency

## Why this belongs to uphillsnowball

`uphillsnowball` is the internal Apple Silicon lab path.

Its purpose includes:
- performance experiments
- retrieval experiments
- OCR experiments
- local inference experiments
- operational tooling experiments

That makes it the right home for:
- unified-memory-aware routing
- local cache reuse experiments
- concurrency tests on resident local models

## What is shared locally

Examples of reusable local slab/context:
- stable doctrine text
- stable repo summaries
- stable evaluation prompts
- stable feature specs
- stable retrieval summaries

Do not mix volatile event-specific diffs into the base cache layer.

## Local concurrent work examples

- summarize three diffs
- run one retrieval evaluation
- generate one architecture note
- produce two OCR summaries

All of those should try to reuse the same stable local context where possible.

## Suggested components

- `labs/uphillsnowball/local_router.py`
- `labs/uphillsnowball/cache_slab.py`
- `labs/uphillsnowball/local_eval.py`
- `labs/uphillsnowball/runtime_stats.py`
- `labs/uphillsnowball/ane_bridge.py`

## ane_bridge role

`ane_bridge.py` should act as:
- a lightweight local task router
- a concurrency controller
- a shared-context dispatcher
- a bridge between high-level tasks and the local model runtime

It should not pretend to be the product control plane.

## Metrics

Track:
- warm vs cold run latency
- cache reuse rate
- average prompt size reduction
- total memory footprint
- concurrency degradation curve
- task throughput
- local energy/perf tradeoff

## Canonical split

### counselconduit
- production-facing
- Google-native
- business-facing
- commercial wedge

### pnkln
- doctrine
- control-plane logic
- routing principles
- operational standards

### uphillsnowball
- local Apple Silicon lab
- MLX / Metal / cache experiments
- runtime prototyping
- internal R&D

This protocol belongs only to the third.

## Non-goals

Do not:
- move production truth into the lab
- let local experiments redefine product architecture
- confuse local inference experiments with the commercial product story

## Business value

The lab can still matter economically.

It can improve:
- internal iteration speed
- eval velocity
- prototyping cost
- architectural confidence
- future margin decisions

But it remains a lab contribution, not the product itself.
