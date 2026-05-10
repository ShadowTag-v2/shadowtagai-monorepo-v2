```mermaid
graph TD
    %% Nodes
    Dev[Developer / Org Terminal]
    subgraph Cloud Workstation "Uphill Snowball"
        Antigravity[The Brain: Antigravity "God Mode"]
        Gemini[Gemini Code Assist 1M Context]
    end

    subgraph Revenue Engine "The Muscle"
        n-autoresearch/Kosmos/BioAgents[ShadowTag Extension Core "n-autoresearch/Kosmos/BioAgents/Kosmos"]
        Jobs[Research / Voting / Terminal]
    end

    subgraph Control Layer "The Brake"
        Judge[Judge CSRMC / Judge #6]
        Policy[Policy-as-Code / NIST 800-53]
    end

    subgraph Eco Layer "Google Cloud Services"
        Stripe[Stripe Billing]
        Snyk[GKC Snyk Security]
        PubSub[Pub/Sub Telemetry]
        Market[Gemini Extensions Marketplace]
    end

    subgraph Ledger "The Vault"
        Lake[GKC Data Lake Iceberg]
        Alloy[AlloyDB Audit Vault]
    end

    %% Flow - Control (Blue)
    Dev -- "Smart Actions / Commands" --> Antigravity
    Antigravity -- "Orchestrates" --> Gemini
    Antigravity -- "Dispatch" --> n-autoresearch/Kosmos/BioAgents
    n-autoresearch/Kosmos/BioAgents -- "Proposal" --> Judge
    Judge -- "Validated Data Only" --> Eco

    Gemini -. "Supervision" .- n-autoresearch/Kosmos/BioAgents

    %% Flow - Money (Green)
    Antigravity -- "Trigger Usage ($0.05-$1)" --> Stripe
    Judge -- "Evidence Asset" --> Lake
    Lake -- "Coverage Earned" --> Alloy
    Market -- "Revenue Split (80/20)" --> Stripe

    %% Styling
    style Dev fill:#f9f,stroke:#333
    style Antigravity fill:#ff9,stroke:#f66,stroke-width:4px
    style Judge fill:#f99,stroke:#f00,stroke-width:2px
    style Stripe fill:#9f9,stroke:#090

    linkStyle 6,7,8,9 stroke:#0f0,stroke-width:2px; %% Money links
    linkStyle 0,1,2,3,4 stroke:#00f,stroke-width:2px; %% Control links
```
