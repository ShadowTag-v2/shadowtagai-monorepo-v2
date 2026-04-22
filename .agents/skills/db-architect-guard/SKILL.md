---
name: db-architect-guard
description: Automatically intercepts and evaluates all database architecture, schema generation, and data-fetching tool calls. Strictly enforces GCP Firestore for serverless edge scaling vs Supabase for relational ledgers.
---

# Database Architect Guard (The Sovereign Split)

This skill enforces strict "Serverless Purity" rules for the `shadowtag-omega-v4` architecture. It prevents connection-pool exhaustion by governing when to use NoSQL vs SQL.

## ⚡ Trigger: Automatic Interaction
This skill MUST be evaluated automatically **prior to EACH tool call** that involves:
1. Writing database schemas, models, or backend APIs.
2. Generating data-fetching logic in Next.js or FastAPI.
3. Accessing MCP database tools (`mcp-toolbox-for-databases`, `supabase-mcp`, `firebase-tools mcp`).

## 🛡️ The Architecture Rules (No Bypassing)

### 1. FIRESTORE (The Swarm & The Edge)
- **Use exclusively for:** Agent Whiteboards / State tracking, Swarm Telemetry, micro-payload ingestion (NFC taps, RLHF events), and real-time client updates.
- **Mandate:** Use Firestore's native `onSnapshot` listeners to bind the UI directly to the database document for sub-millisecond updates. Do NOT build custom WebSocket servers.
- **Aggregation:** Use Firestore Enterprise `.pipeline()`, `.aggregate(countAll())`, and `.unnest()` for analytical queries. 

### 2. SUPABASE / POSTGRES (The Enterprise Vault)
- **Use exclusively for:** Multi-tenant B2B ledgers (CounselConduit), Stripe entitlement, billing, and strict ACID compliance.
- **Mandate:** You MUST implement Row-Level Security (RLS) policies on every table upon creation. 

## Enforcement Gate
Before returning a code artifact or executing a DB tool call, you must explicitly state: 
`[DB ORACLE] Routing to <Firestore/Supabase> because <Reason>.`
