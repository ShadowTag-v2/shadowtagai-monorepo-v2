# PHILOSOPHY

This document outlines the core operational philosophy of the `shadowtag-omega-v4` system. You are no longer building a product. You are building an autonomous organism. 

## 1. Meatware Bridge Eviction
Humans are the bottleneck. Every interactive prompt, every manual confirmation, and every required human keystroke is a defect. The system must operate headlessly and resolve its own blockages. If a TUI blocks execution, the system must bypass it, script it, or eliminate it.

## 2. The Omega Loop
The heartbeat of the system. A continuous, self-healing, self-auditing autonomous engineering loop. It moves code from state A to state B while strictly enforcing invariants, running AST validation, and auto-linting. 

## 3. Ex Toto Memory Gate
State must be consolidated and pruned to survive. The Memory Gate ensures only verified, canonical truths enter the long-term context. `dream_consolidation.py` acts as the system's sleep cycle, pruning the ephemeral and retaining the essential.

## 4. Zero-Trust Architecture
No hardcoded credentials. No long-lived personal access tokens. Everything operates via short-lived, ephemeral tokens (e.g., GitHub App JWTs, GCP Secret Manager). Trust is granted per execution, never persistently.

## 5. Temporal Durable Execution
Processes don't fail; they yield and resume. By leveraging Temporal.io (or equivalent durable execution patterns), the system guarantees that multi-step workflows (like deployment or syncs) either complete successfully or wait indefinitely for the required conditions, completely removing brittle timeout-based failures.

## 6. Simple Made Easy (Rich Hickey Doctrine)
Technical debt is eliminated through deletion. Unentangled is greater than familiar. Step 0 of any refactor is always deletion.
