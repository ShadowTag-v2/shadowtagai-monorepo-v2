# API Reference - Cor.57 Unified Sky-Ground GPU Mesh

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API is open and does not require authentication. Future versions will implement:

- API Key authentication
- OAuth 2.0 for enterprise customers
- JWT tokens for service-to-service communication

---

## Infrastructure APIs

### Get Infrastructure Layers

Retrieve all three infrastructure layers (Orbital, Terrestrial, User).

**Endpoint**: `GET /api/v1/infrastructure/layers`

**Response**: Array of `InfrastructureLayer` objects

```json
[
  {
    "layer": "orbital",
    "platform": "Starlink LEO satellites",
    "function": "Edge inference + global backhaul",
    "customer_value": "Low-latency, resilient global coverage"
  },
  {
    "layer": "terrestrial",
    "platform": "CoreWeave GPUs in cell towers",
    "function": "City-level compute & AI routing",
    "customer_value": "Ultra-low latency inference"
  },
  {
    "layer": "user",
    "platform": "Vehicles, Teslas, phones",
    "function": "End-user AI / data capture",
    "customer_value": "Real-time AI, verified local caching"
  }
]
```

### Get Technical Metrics

Retrieve technical performance metrics for the infrastructure.

**Endpoint**: `GET /api/v1/infrastructure/metrics`

**Response**: `TechnicalMetrics` object

```json
{
  "node_uptime": 99.98,
  "compute_utilization": 70.0,
  "latency_reduction_ms": 65,
  "energy_efficiency_improvement": 25.0
}
```

### Get CAPEX Components

Retrieve capital expenditure breakdown.

**Endpoint**: `GET /api/v1/infrastructure/capex`

**Response**: Array of `CapexComponent` objects

```json
[
  {
    "component": "CoreWeave tower GPUs",
    "unit_cost": 15000,
    "volume": 100000,
    "total_capex": 1500000000,
    "notes": "1 GPU/node, shared w/ carriers"
  }
]
```

### Get Complete Deployment Plan

Retrieve the complete infrastructure deployment plan.

**Endpoint**: `GET /api/v1/infrastructure/deployment`

**Response**: `InfrastructureDeployment` object

---

## Financial APIs

### Get Revenue Streams

Retrieve all revenue streams for Year 5 projections.

**Endpoint**: `GET /api/v1/financial/revenue-streams`

**Response**: Array of `RevenueStream` objects

```json
[
  {
    "source": "starlink_inference",
    "description": "Starlink inference traffic",
    "annual_revenue": 2100000000,
    "margin_percentage": 85.0,
    "notes": "AI overlay + data compression"
  }
]
```

### Get Financial Projection

Retrieve financial projection for a specific year.

**Endpoint**: `GET /api/v1/financial/projection/{year}`

**Parameters**:
- `year` (path) - Year for projection (currently only 2030 available)

**Response**: `FinancialProjection` object

```json
{
  "year": 2030,
  "arr": 10000000000,
  "ebitda": 8400000000,
  "ebitda_margin": 84.0,
  "free_cash_flow": 7000000000,
  "revenue_streams": [...]
}
```

### Get Valuations

Retrieve all valuation scenarios.

**Endpoint**: `GET /api/v1/financial/valuations`

**Response**: Array of `Valuation` objects

```json
[
  {
    "scenario": "hybrid",
    "rationale": "Private Infra ($160B) + Public Digital ($150B)",
    "estimated_value": 310000000000,
    "control_percentage": 80.0,
    "tax_exposure_percentage": 8.0,
    "liquidity_level": "High"
  }
]
```

### Get Customer Segments

Retrieve customer segments and annual spend projections.

**Endpoint**: `GET /api/v1/financial/customers`

**Response**: Array of `CustomerSegment` objects

### Get Operating Model

Retrieve operating model metrics.

**Endpoint**: `GET /api/v1/financial/operating-model`

**Response**: `OperatingModel` object

### Get Consolidated Financials

Retrieve consolidated financial overview.

**Endpoint**: `GET /api/v1/financial/consolidated`

**Response**: `ConsolidatedFinancials` object

---

## Strategic APIs

### Get Milestones

Retrieve strategic milestones timeline (2025-2030).

**Endpoint**: `GET /api/v1/strategic/milestones`

**Response**: Array of `Milestone` objects

```json
[
  {
    "date": "Q4 2025",
    "description": "Pilot live (3 CoreWeave–Starlink sites)",
    "valuation_impact": 500000000,
    "status": "planned"
  }
]
```

### Get Strategic Effects

Retrieve strategic effects and improvements.

**Endpoint**: `GET /api/v1/strategic/effects`

**Response**: Array of `StrategicEffect` objects

### Get Legal Positioning

Retrieve legal and contractual positioning information.

**Endpoint**: `GET /api/v1/strategic/legal-positioning`

**Response**: Array of `LegalPositioning` objects

### Get Partnerships

Retrieve key partnership models.

**Endpoint**: `GET /api/v1/strategic/partnerships`

**Response**: Array of `PartnershipModel` objects

### Get Competitive Advantages

Retrieve competitive advantages.

**Endpoint**: `GET /api/v1/strategic/competitive-advantages`

**Response**: Array of `CompetitiveAdvantage` objects

### Get Consolidated Summary

Retrieve consolidated summary of Cor.57.

**Endpoint**: `GET /api/v1/strategic/summary`

**Response**: `ConsolidatedSummary` object

```json
{
  "total_arr": 10000000000,
  "ebitda_margin": 84.0,
  "deployment_metrics": {
    "total_towers": 100000,
    "total_satellites": 3000,
    "total_vehicles": 3000000,
    "geographic_coverage": "Global - 95% populated areas",
    "total_compute_nodes": 3103000
  },
  "valuation_private": 160000000000,
  "annual_family_yield": 7000000000,
  "strategic_control": "100% infrastructure + IP ownership"
}
```

---

## Utility APIs

### Root

API overview and available endpoints.

**Endpoint**: `GET /`

**Response**: API information object

### Health Check

Service health status.

**Endpoint**: `GET /health`

**Response**:

```json
{
  "status": "healthy",
  "service": "cor-57-api"
}
```

---

## Error Responses

### 404 Not Found

```json
{
  "detail": "Projection for year 2025 not available. Only 2030 (Year 5) is currently modeled."
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["path", "year"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. Future versions will include:

- 1000 requests/hour for unauthenticated users
- 10,000 requests/hour for authenticated users
- Unlimited for enterprise customers

---

## SDKs and Client Libraries

Coming soon:

- Python SDK
- TypeScript/JavaScript SDK
- Go SDK
- Rust SDK

---

## Support

For API support and questions:

- Documentation: http://localhost:8000/docs
- GitHub Issues: (to be added)
- Email: api-support@aiyou.com (example)
