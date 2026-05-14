# GENAI TOOLBOX STRATEGY: THE DATABASE NEOCORTEX

> **CLASSIFICATION**: TIER 15 // INTERNAL
> **DATE**: 2026-02-03
> **STATUS**: DRAFT

## 1. The Concept

We are "folding in" the **Google GenAI Toolbox** to serve as the **Database Neocortex** for our agents.
Instead of raw SQL or Python drivers scattered across agents, we centralize database interaction through an **MCP Server (The Toolbox)**.

**Why?**

- **Abstraction**: Agents just ask "Get recent crimes", Toolbox handles the SQL.
- **Security**: Connection pooling and IAM auth are handled by the Toolbox sidecar.
- **Observability**: Out-of-the-box OpenTelemetry tracing for every DB hit.

## 2. Architecture: The Sidecar Pattern

We will deploy the Toolbox as a **Sidecar Container** in our Cloud Run services (`trinity-os`, `jetski-agent`).

    B -- gRPC (Pipeline Ops) --> D[(Firestore Native)]

````

### ETL Engine: Google LangExtract (The Reader)
We use `google/langextract` (Python Lib) on the **Agent Side** (Jetski/Hunter) to parse unstructured documents before storage.
*   **Role**: Converts PDFs/Webpages -> Structured JSON Entities with Grounding.
*   **Flow**: `Jetski(Read URL) -> LangExtract(Parse) -> Toolbox(Insert Memory)`.

### Advanced Query Engine (Pipeline Operations)
We leverage the **New Firestore Query Engine** (2025) to run server-side aggregations directly on the transactional store.
*   **Use Case**: Real-time "Crime Counts" and "Risk Summation" for Judge 6.
*   **Benefit**: No ETL to BigQuery needed for operational metrics.

### Human-in-the-Loop (IDE Access)
We also enable **You (The User)** to access the Neocortex directly from your IDE (Windsurf/Cursor) via the official MCP Client integration.
*   **Method**: `mcp.json` configuration in workspace root.
*   **Result**: You can ask standard `@alloydb` questions in your chat window.

### Advanced Query Engine (Pipeline Operations)
We leverage the **New Firestore Query Engine** (2025) to run server-side aggregations directly on the transactional store.
*   **Use Case**: Real-time "Crime Counts" and "Risk Summation" for Judge 6.
*   **Benefit**: No ETL to BigQuery needed for operational metrics.

## 3. Implementation Plan

### Phase 1: The Artifacts
1.  **`toolbox_config.yaml`**: Define the tools exposed to agents.
    *   `search_vectors`: Semantic search over embeddings.
    *   `insert_memory`: Store structured knowledge.
    *   `get_profile`: Retrieve target profiles.

### Phase 2: The Sidecar (Terraform)
Update `cloudrun.tf` (or `workstations.tf`) to include the Toolbox container:
```hcl
container {
    image = "us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest"
    args  = ["--tools-file", "/app/toolbox_config.yaml", "--port", "8080"]
}
````

### Phase 3: The Client (Python)

Update `agents/jetski_agent.py` to use an MCP Client to talk to the sidecar.

## 4. Immediate Actions

1.  **Define** `infrastructure/toolbox_config.yaml`.
2.  **Provision** the Sidecar in Terraform.
3.  **Refactor** `KnowledgeIndexer` to use the Toolbox.

## 5. "Fold In" Status

- [ ] **Strategy**: Defined (This Document).
- [ ] **Config**: `toolbox_config.yaml` created.
- [ ] **Deployment**: Terraform updated.
