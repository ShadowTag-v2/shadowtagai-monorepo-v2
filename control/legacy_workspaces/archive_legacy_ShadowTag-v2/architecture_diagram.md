```mermaid
graph TD
    %% NODES
    subgraph "God Mode (UphillSnowball)"
        Dev[Developer / Org Terminal]
        Brain[Antigravity Brain]
    end

    subgraph "Core Engine (Cloud Run)"
        Kosmos[Kosmos Extension Core]
        Judge[Judge CSRMC Validator]
        Services[Google Cloud Services]
        Lake[GKC Data Lake]
    end

    %% FLOWS
    Dev -->|Commands / Intent| Brain
    Brain -->|Orchestrates| Kosmos

    Kosmos -->|Plan / Audit / Risk| Judge
    Judge -->|Validated Data Only| Services

    Services -->|Billing Event| Stripe[Stripe ($)]
    Services -->|Telemetry| PubSub[Pub/Sub]
    Services -->|Logs| BigQuery[BigQuery]

    Services -->|Revenue / Events| Lake

    %% FEEDBACK LOOPS
    Judge -.->|Rollback Trigger| Kosmos
    Lake -.->|Audit Feed ($)| Dev

    %% STYLING
    style Dev fill:#f9f,stroke:#333
    style Brain fill:#bbf,stroke:#333
    style Kosmos fill:#bfb,stroke:#333
    style Judge fill:#fbb,stroke:#333
    style Services fill:#ddd,stroke:#333
    style Lake fill:#eee,stroke:#333
```
