# OMEGA ARCHITECTURE: JUGGERNAUT ↔ BRAKE
> **CLASSIFICATION**: TIER 30 // SOVEREIGN
> **MODE**: PURE SERVERLESS CLOUD RUN (NO REDIS)

## CONTROL FLOW DIAGRAM

```mermaid
graph TD
    %% Nodes
    User[Developer / Org Terminal]
    Uphill[UphillSnowball (God Mode)]
    GCA[Gemini Code Assist (1M Context)]

    subgraph "Cloud Run Service (ShadowTag Omega)"
        subgraph "Container 1: The Brain"
            Antigravity[Antigravity Orchestrator]
        end

        subgraph "Sidecar 1: The Muscle"
            n-autoresearch/Kosmos/BioAgents[n-autoresearch/Kosmos/BioAgents / Kosmos]
            Jetski[Jetski Browser]
        end

        subgraph "Sidecar 2: The Brake"
            Judge[Judge #6 / CSRMC]
            Audit[Audit Logger]
        end
    end

    subgraph "Data Layer (The Iceberg)"
        Firestore[Firestore (Learned Rules)]
        Iceberg[GKC Data Lake (Iceberg)]
        BigQuery[BigQuery (Telemetry)]
    end

    subgraph "Eco-Layer"
        Stripe[Stripe (Billing)]
        Market[Gemini Marketplace]
    end

    %% Flows
    User -- "Call of Question" --> GCA
    GCA -- "Plan / Intent" --> Uphill
    Uphill -- "Orchestrate" --> Antigravity

    Antigravity -- "Dispatch Task" --> n-autoresearch/Kosmos/BioAgents
    n-autoresearch/Kosmos/BioAgents -- "Research / Verify" --> Jetski
    Jetski -- "Ground Truth" --> n-autoresearch/Kosmos/BioAgents

    n-autoresearch/Kosmos/BioAgents -- "Proposed Code/Action" --> Judge
    Judge -- "Validate (NIST 800-53)" --> Firestore

    Judge -- "Approved" --> Antigravity
    Judge -- "Blocked" --> Audit

    Antigravity -- "Publish" --> Iceberg
    Antigravity -- "Billing Event" --> Stripe

    %% Styling
    style Judge fill:#ff9999,stroke:#333,stroke-width:2px,color:black
    style n-autoresearch/Kosmos/BioAgents fill:#99ff99,stroke:#333,stroke-width:2px,color:black
    style Antigravity fill:#9999ff,stroke:#333,stroke-width:4px,color:white
    style Uphill fill:#ffff99,stroke:#333,stroke-width:2px,color:black
```

## ECONOMIC FLOW

1.  **Usage**: User triggers `risk evaluate` or `plan assist`.
2.  **Meter**: Stripe micro-bill ($0.05–$1/run).
3.  **Validation**: Judge #6 validates (Cost: Compute).
4.  **Storage**: Proof stored in Iceberg/Firestore (Cost: $0.09/GB).
5.  **Revenue**: Enterprise License + Marketplace Fee Split.

## TECHNICAL SPEC: "THE HYBRID"
*   **Platform**: Google Cloud Run (Gen 2).
*   **Containers**:
    *   **Ingress**: Antigravity API (FastAPI).
    *   **Sidecar A**: Monkey Swarm (Python/Selenium/Jetski).
    *   **Sidecar B**: Judge #6 Sentinel (Static Analysis/Policy Engine).
*   **Data**: Firestore (No Redis). Apache Iceberg for long-term lake.
