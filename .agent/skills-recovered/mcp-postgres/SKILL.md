---
name: "mcp-postgres"
description: "Native Postgres Connector. Replaces generic SQL injection MCP operations with strict parameterization rules."
---

# MCP: Postgres Server (Native Skill)

## Goal
To enforce secure, verifiable queries into the central Supabase/AlloyDB architecture defined by the ShadowTagAI stack.

## Rules of Engagement (COR.30 Compliance)
1. **Never Concatenate SQL:** You must exclusively generate code utilizing ORMs (like Prisma/Drizzle) or fully parameterized DB wrappers.
2. **Row-Level Security:** Assume all generated DB schemas require an active RLS (Row Level Security) constraint block.
3. **No Credential Shells:** Do not perform direct `psql` queries from the terminal that expose database URIs housing secrets in plain text.
