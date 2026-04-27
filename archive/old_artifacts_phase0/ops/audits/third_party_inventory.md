# Third-party inventory

## Google-native
- Vertex AI / Gemini (gemini-3.1-flash-lite-preview)
- Firebase MCP (auth, experimental:mcp)
- Developer Knowledge MCP
- Stitch MCP
- Chrome DevTools MCP
- GCP Cloud Run (counselconduit deployment target)
- GCP Cloud Logging (metering telemetry sink)

## AI Providers (Managed Mode)
- Google Gemini API (primary managed backend)
- OpenAI API (BYOK only, enterprise tier)
- Anthropic API (BYOK only, enterprise tier)

## Billing / Auth
- Stripe (subscription + usage-based billing)
- Supabase (PostgreSQL + Auth + Magic Links)
- Firebase Auth (alternative Magic Link provider)

## Local lab (uphillsnowball only)
- LanceDB (local vector store on Apple Silicon)
- MLX (Apple Neural Engine inference)
- Ruff (Python linting)
- Biome (JS/TS formatting)

## Review targets
- Remove stale non-canonical adapters from operational paths
- Keep all keys in `.env`
- Keep product/runtime split explicit
- Validate Zero Data Retention on all AI provider Enterprise agreements
