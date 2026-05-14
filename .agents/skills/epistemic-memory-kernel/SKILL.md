---
name: epistemic-memory-kernel
description: Enforces structured memory retention, Time-To-Live (TTL) decay, and ACT-R Spreading Activation.
---
# Doctrine: Epistemic Memory Lifecycle
1. **Typed Atoms:** You will NEVER write unstructured memory. You must categorize all findings via `retain_epistemic_atom` as a `fact`, `decision`, `constraint`, `belief`, `conflict`, or `open_question`.
2. **Decay:** Set `ttl_days: 30` and `confidence: 0.6` for hypotheses. Set `ttl_days: 0` and `confidence: 1.0` for hard architectural facts.
3. **Collision Detection:** Use Wander (Spreading Activation) to find memory collisions via Jaccard dissimilarity > 0.7. Monitor the Closure Metric; halt execution if > 8.
