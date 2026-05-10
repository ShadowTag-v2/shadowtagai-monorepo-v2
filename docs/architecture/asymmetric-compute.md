# Asymmetric Compute Hedge Fund

## The Philosophy
We do not treat AI compute linearly. Treating it linearly results in the "AI Compute Death Spiral," where 86% of margin is obliterated by unoptimized context windows.

## The Triad
1. **The Macro (Central Hive Mind)**: Heavy lifting, deep-reasoning parameters. Reserved purely for Q* derivations and multi-step agent reasoning. Cost is high, usage is sparse. O(1) invocation.
2. **The Micro (Edge Routers)**: Deterministic, cached, or lightweight evaluation tiers utilizing localized RAG and LanceDB vectors.
3. **Firestore Enterprise Pipelines**: Stateful storage of derived truths. If truth exists, serve it. Never recompute what you can query.

## The Profit & Loss Model (Split-Brain)
- **Target Margin**: > 80%
- **Execution Threshold**: If total `input_tokens * cost > P&L_Threshold`, traffic is routed dynamically to fallback endpoints or cached.
