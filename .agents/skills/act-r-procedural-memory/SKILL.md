---
name: act-r-procedural-memory
description: Implements ACT-R Procedural Memory chunking, Utility Learning, and Serverless State Management via Firestore.
---
# Doctrine: ACT-R Procedural Memory Adoption Patterns

ACT-R Procedural Memory is the "if-then" rule system of the brain, compiling productions through chunking and utility learning. To optimize the Autoresearch Triad, we are adopting the following patterns immediately:

1. **ToolGateway Contracts as Productions:**
Every tool contract in `.agents/skills/` acts as an ACT-R production. We will add a `utility_score` (float) to each `tool_contracts/*.yaml` manifest.

2. **Utility Learning (The FastPath Router):**
Every time the Autoresearch Triad executes a contract successfully, its utility score increases. Over time, frequently used, highly successful patterns become compiled. The ToolGateway will route these high-utility contracts to the FastPath, bypassing heavy deliberative layers and drastically reducing token spend and latency.

3. **Serverless State Management:**
Instead of Redis, we map the utility learning queue and production strengths directly into Firestore. This allows multiple serverless Cloud Run instances of the Triad to dynamically federate and share procedural memory in real-time, instantly learning which tool chains yield the lowest execution times across the entire fleet.
