# HeadFade GTM Funnel

```mermaid
graph TD
    A[Twitter Launch Thread] --> B[HeadFade Landing Page]
    C[B2B Outreach Emails] --> B
    D[Organic SEO/Content] --> B
    
    B --> E{User Action}
    E -->|Consumer| F[Take Gamified Turing Test]
    E -->|Developer| G[Read API Docs]
    E -->|Enterprise| H[Book Demo / API Trial]
    
    F --> I[Sign up to Save Score]
    G --> J[Generate API Key]
    H --> K[Stripe Billing Activation]
    
    I --> L[Active User (Truth Layer Node)]
    J --> L
    K --> L
```
