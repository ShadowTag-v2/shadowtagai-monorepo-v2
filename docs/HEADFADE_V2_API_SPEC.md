# HeadFade V2 API Technical Specification

## 1. Overview
The HeadFade V2 API is a zero-trust, edge-native, multi-protocol interface designed to support the expanding synthetic content economy. It serves as the primary infrastructure for the Agent-to-Agent Licensing Marketplace and the Multi-Model Provenance Expansion.

## 2. Architectural Paradigms
- **Zero-Trust Infrastructure**: All API endpoints require mutual TLS (mTLS) and cryptographically signed request payloads.
- **Edge-Native Deployment**: Distributed execution via Cloudflare Workers / Fastly Compute@Edge for low-latency global access (< 50ms p99 latency).
- **Multi-Protocol Interface**: 
  - **RESTful API**: For standard B2B integrations and legacy clients.
  - **GraphQL API**: For optimized, sparse data fetching in complex frontends.
  - **Model Context Protocol (MCP)**: Native integration for autonomous AI agents connecting directly to the HeadFade Provenance Ledger.

## 3. Core Domains

### 3.1 Provenance Ledger API
Handles the cryptographic lineage of synthetic assets across 12+ foundation models (Sora, Veo 2, Luma, Kling 2.0, etc.).

- `POST /v2/provenance/asset`
  - Registers a new synthetic asset.
  - Requires: `model_id`, `prompt_hash`, `generation_timestamp`, `creator_identity_sig`.
  - Returns: `asset_uuid`, `c2pa_manifest`.

- `GET /v2/provenance/asset/{asset_uuid}/lineage`
  - Retrieves the full Remix Tree v2 lineage.
  - Returns the acyclic directed graph of the asset's history.

- `POST /v2/provenance/verify`
  - Verifies an external asset against the HeadFade ledger.
  - Supports binary upload or URI validation.

### 3.2 Agent Licensing Marketplace API
Facilitates smart-contract-based licensing between autonomous systems.

- `POST /v2/marketplace/license`
  - Executes a new license agreement.
  - Parameters: `asset_uuid`, `license_tier`, `agent_buyer_sig`.
  - Triggers internal Stripe Connect flow for revenue share split.

- `GET /v2/marketplace/pricing/dynamic`
  - Returns real-time algorithmic market clearing prices for specific asset categories or prompt patterns.

### 3.3 Regulatory Compliance API
Ensures compliance with EU AI Act Article 52, US Executive Orders, and C2PA standards.

- `GET /v2/compliance/report/{asset_uuid}`
  - Generates a localized regulatory transparency report based on the requester's IP/jurisdiction.

- `POST /v2/compliance/watermark/embed`
  - Embeds invisible, cryptographically signed watermarks into generated media payloads.

## 4. Security & Authentication
- **Authentication**: JWTs via JWKS for external clients; MCP-native auth for agentic clients.
- **Rate Limiting**: Tiered based on pricing (Self-serve: 100 req/sec; Professional: 1000 req/sec; Enterprise: Custom).
- **Data Residency**: Strict regional routing to comply with GDPR and CCPA.

## 5. Webhook Events
Clients can subscribe to real-time events on the Remix Tree or Marketplace:
- `asset.provenance_updated`
- `license.executed`
- `compliance.audit_triggered`

## 6. Deprecation of V1
The V1 REST endpoints (`/v1/*`) will enter a 12-month deprecation cycle starting at the launch of V2, with a hard sunset scheduled for Q3 2027.
