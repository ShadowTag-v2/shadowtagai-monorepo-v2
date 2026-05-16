# ShadowTagAI: Economic + Control Flow Architecture
## "Juggernaut ↔ Brake" Model

This diagram represents the **ShadowTagAI** system running as a pure serverless Cloud Run architecture, orchestrated by Antigravity in "God Mode" (Uphill Snowball).

```mermaid
graph TD
    %% Styling
    classDef muscle fill:#2A2438,stroke:#6E56CF,stroke-width:2px,color:#F4F0FF;
    classDef revenue fill:#0E0B16,stroke:#FF4F00,stroke-width:2px,color:#F4F0FF;
    classDef brake fill:#05020A,stroke:#F4F0FF,stroke-width:2px,color:#F4F0FF;
    classDef gcp fill:#FFFFFF,stroke:#4285F4,stroke-width:2px,color:#000000;
    classDef storage fill:#E8EAED,stroke:#34A853,stroke-width:2px,color:#000000;

    subgraph User_Layer ["Developer / Org Terminal"]
        User(("Developer"))
        Antigravity["The muscle (uphillsnowball)<br/>Antigravity on Cloud Workstation"]:::muscle
    end

    subgraph Revenue_Engine ["ShadowTagAI Extension Core"]
        Extension["ShadowTagAI Core<br/>(Monkeys/Kosmos)"]:::revenue
        GeminiCA["Gemini Code Assist<br/>(1M Context)"]:::revenue
    end

    subgraph Control_Layer ["Judge 6 (Brake System)"]
        Judge["Judge CSRMC"]:::brake
        Policy["NIST 800-53 / PaC"]:::brake
    end

    subgraph Eco_Layer ["Google Cloud Services"]
        Stripe["Stripe (Billing)"]:::gcp
        PubSub["Pub/Sub (Telemetry)"]:::gcp
        GCP_Svcs["Snyk / Dynatrace"]:::gcp
    end

    subgraph Data_Layer ["Data Lake"]
        BigQuery["BigQuery (Logs/Search)"]:::storage
        Iceberg["GKC Data Lake (Iceberg)"]:::storage
        AuditVault["Audit Vault (AlloyDB?)"]:::storage
    end

    %% Flows
    User -->|Commands & Prompts| Antigravity
    Antigravity -->|Orchestrates| Extension
    Antigravity -->|Supervises| GeminiCA

    Extension -->|Plan / audit / Risk| GeminiCA
    Extension -->|Telemetry & Metrics| Judge

    Judge -->|Validates vs Policy| Policy
    Judge -->|Passes Validated Data Only| Eco_Layer

    Eco_Layer -->|Revenue Events| Stripe
    Eco_Layer -->|Telemetry| PubSub

    PubSub -->|Ingest| BigQuery
    Judge -->|Evidence| AuditVault
    Extension -->|Uploads Proofs| Iceberg

    %% Economic Overlay
    Stripe -.->|$$ Micro-bill| User
    Iceberg -.->|Liability Coverage| User
```

## Economic & Control Logic

### 🧠 Control Loop (Technical)
1. **Run 1 - Generator Chain**: Gemini Code Assist creates code/plan.
2. **Run 2 - Plan Mode**: Monkeys/Kosmos Reverse-engineers intent + risk.
3. **Run 3 - Validator Chain**: Judge/CSRMC executes audit, signs proof.
4. **Serverless Cloud Run**: Publishes outputs & billing artifact.

### ⚙️ Financial Flow
1. **Trigger**: User runs `shadowtagai risk eval` -> Stripe micro-bill ($0.05–$1/run).
2. **Audit**: Firestore invokes CSRMC validator -> Compliance Asset.
3. **Storage**: Proof uploaded to Iceberg Lake -> Liability coverage earned.
4. **Enterprise**: Licenses aggregate proofs -> $20–$3k/seat subscription.
