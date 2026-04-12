# PNKLN Platform Monitoring Service

Unified monitoring, cost tracking, AI insights, and billing for the PNKLN Core Stack™ (V2X Mesh + Gemini Ingestion).

## Architecture

```

┌─────────────────────────────────────────────────────────────┐
│                  Platform Monitoring API                     │
│                    (FastAPI + Uvicorn)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Metrics    │  │ Vertex AI    │  │   Stripe     │    │
│  │ Aggregator   │  │ Integration  │  │   Billing    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │     Cost     │  │  Dashboard   │                       │
│  │   Tracker    │  │   (HTML/JS)  │                       │
│  └──────────────┘  └──────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    ┌─────────────┐      ┌─────────────┐     ┌─────────────┐
    │  V2X Mesh   │      │   Gemini    │     │   Stripe    │
    │   Network   │      │  Ingestion  │     │     API     │
    └─────────────┘      └─────────────┘     └─────────────┘

```

## Features

### 1. **Unified Metrics Aggregation**


- Collects metrics from V2X Mesh and Gemini Ingestion services

- Platform-wide health monitoring (healthy/degraded/unhealthy)

- Real-time performance tracking (latency, throughput, error rates)

- Resource utilization monitoring (CPU, memory)

- Prometheus metrics export

### 2. **Cost Tracking & Budget Management**


- Per-service budget tracking ($3,300/month total)

  - Gemini Ingestion: $77/month

  - V2X Mesh: $3,200/month

  - Platform Monitoring: $50/month

- Budget alerts (75% warning, 90% critical)

- Cost breakdown by category (compute, storage, network, API calls)

- Revenue requirement calculations (70% margin target)

- Optimization suggestions

### 3. **AI-Powered Insights (Vertex AI / Gemini 2.0 Pro)**


- Cost optimization recommendations

- Performance tuning suggestions

- Anomaly detection

- Predictive capacity planning

- Intelligent alerting with business impact analysis

### 4. **Stripe Billing Integration**


- Customer management

- Usage-based subscriptions

- Multi-tier pricing:

  - **Starter**: $11/vehicle/month (1-100 vehicles)

  - **Growth**: $9/vehicle/month (101-500 vehicles)

  - **Enterprise**: $7/vehicle/month (500+ vehicles)

- Payment method management

- Invoice generation

- Webhook handling

- Revenue reporting (MRR, ARR)

### 5. **Interactive Dashboard**


- Real-time platform health visualization

- Budget utilization gauges

- Cost breakdown charts

- AI recommendations display

- Revenue requirement calculator

- Auto-refresh every 30 seconds

## API Endpoints

### Metrics


- `GET /metrics/platform` - Aggregated platform metrics

- `GET /metrics/services` - Per-service metrics

- `GET /metrics/performance-summary` - Performance summary

### Cost Tracking


- `POST /costs/record` - Record cost entry

- `GET /costs/status` - Budget status with alerts

- `GET /costs/breakdown` - Cost breakdown by category

- `GET /costs/optimization` - Optimization suggestions

- `GET /costs/revenue-requirements` - Revenue calculations

### AI Insights


- `GET /ai/recommendations` - AI optimization recommendations

- `GET /ai/insights` - Comprehensive platform insights

- `GET /ai/capacity-forecast` - Capacity forecasting

### Billing


- `POST /billing/customers` - Create customer

- `GET /billing/customers/{id}` - Get customer

- `POST /billing/payment-methods` - Attach payment method

- `POST /billing/subscriptions` - Create subscription

- `GET /billing/subscriptions/{id}` - Get subscription

- `PATCH /billing/subscriptions` - Update subscription

- `DELETE /billing/subscriptions/{id}` - Cancel subscription

- `GET /billing/invoices/{customer_id}` - List invoices

- `GET /billing/pricing?vehicle_count={n}` - Calculate pricing

- `POST /billing/webhooks` - Stripe webhook handler

- `GET /billing/revenue-report` - Revenue report

### Other


- `GET /` - Dashboard UI

- `GET /health` - Health check

- `GET /prometheus` - Prometheus metrics

## Deployment

### Local Development

```bash
cd services/platform-monitoring

# Install dependencies

pip install -r requirements.txt

# Set environment variables

export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_WEBHOOK_SECRET="whsec_..."
export V2X_MESH_API_URL="http://localhost:8010"
export GEMINI_INGESTION_STATUS_URL="http://localhost:8000"

# Run the service

uvicorn api:app --host 0.0.0.0 --port 8080 --reload

```

Access dashboard at: `http://localhost:8080`

### Docker Deployment

```bash

# Build image

docker build -t platform-monitoring:latest .

# Run container

docker run -d \
  -p 8080:8080 \
  -e STRIPE_SECRET_KEY="sk_test_..." \
  -e STRIPE_WEBHOOK_SECRET="whsec_..." \
  -e V2X_MESH_API_URL="http://v2x-mesh:8010" \
  -e GEMINI_INGESTION_STATUS_URL="http://gemini-ingestion:8000" \
  --name platform-monitoring \
  platform-monitoring:latest

```

### GKE Deployment

```bash

# 1. Build and push to GCR

export PROJECT_ID="your-gcp-project"
docker build -t gcr.io/${PROJECT_ID}/platform-monitoring:latest .
docker push gcr.io/${PROJECT_ID}/platform-monitoring:latest

# 2. Update manifests

sed -i "s/PROJECT_ID/${PROJECT_ID}/g" infrastructure/k8s/platform-monitoring-deployment.yaml

# 3. Create namespace and deploy

kubectl apply -f infrastructure/k8s/platform-monitoring-deployment.yaml

# 4. Get external IP

kubectl get service platform-monitoring-external -n platform-monitoring

# 5. Configure Stripe webhook

# Set webhook URL to: http://<EXTERNAL_IP>/billing/webhooks

# Select events: payment_intent.*, customer.subscription.*, invoice.*

```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `STRIPE_SECRET_KEY` | Stripe API secret key | - |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | - |
| `V2X_MESH_API_URL` | V2X Mesh API endpoint | `http://v2x-mesh-gateway.v2x-mesh.svc.cluster.local:8010` |
| `GEMINI_INGESTION_STATUS_URL` | Gemini Ingestion status endpoint | `http://gemini-ingestion-status.gemini-ingestion.svc.cluster.local:8000` |
| `BUDGET_GEMINI_INGESTION` | Monthly budget for Gemini | `77.0` |
| `BUDGET_V2X_MESH` | Monthly budget for V2X | `3200.0` |
| `BUDGET_PLATFORM_MONITORING` | Monthly budget for monitoring | `50.0` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Usage Examples

### Calculate Pricing for Fleet Size

```bash
curl http://localhost:8080/billing/pricing?vehicle_count=250

```

Response:

```json
{
  "tier": "growth",
  "plan_name": "Growth Plan",
  "vehicle_count": 250,
  "price_per_vehicle": 9.0,
  "monthly_cost": 2250.0,
  "yearly_cost": 22950.0,
  "yearly_savings": 4050.0,
  "features": [
    "All Starter features",
    "Advanced Analytics",
    "Custom Integrations",
    "Priority Support",
    "99.9% Uptime SLA",
    "Dedicated Account Manager"
  ]
}

```

### Create Customer and Subscription

```bash

# 1. Create customer

curl -X POST http://localhost:8080/billing/customers \
  -H "Content-Type: application/json" \
  -d '{
    "email": "redacted@shadowtag-v4.local",
    "name": "Example Fleet Inc",
    "metadata": {"company": "Example Inc", "fleet_size": "250"}
  }'

# Response: {"customer_id": "cus_...", ...}

# 2. Attach payment method (from Stripe.js)

curl -X POST http://localhost:8080/billing/payment-methods \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cus_...",
    "payment_method_id": "pm_..."
  }'

# 3. Create subscription

curl -X POST http://localhost:8080/billing/subscriptions \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "cus_...",
    "vehicle_count": 250,
    "billing_interval": "month"
  }'

# Response includes subscription_id, tier, amount, etc.

```

### Get AI Recommendations

```bash
curl http://localhost:8080/ai/recommendations

```

Response:

```json
{
  "recommendations": [
    {
      "id": "cost-opt-001",
      "type": "cost_optimization",
      "priority": "high",
      "title": "Implement Gemini API Response Caching",
      "description": "45% of calls are for similar content...",
      "impact": "$27/month savings (35% reduction)",
      "steps": [
        "Add Redis cache layer",
        "Implement content-based cache keys",
        "Set 24-hour TTL",
        "Monitor cache hit rate"
      ],
      "savings": 27.0,
      "confidence": 0.85
    }
  ],
  "total_recommendations": 2,
  "total_potential_savings": 627.0
}

```

### Get Revenue Requirements

```bash
curl http://localhost:8080/costs/revenue-requirements?margin_percent=70

```

Response:

```json
{
  "total_monthly_cost": 3300.0,
  "required_monthly_revenue": 11000.0,
  "per_vehicle_revenue_1k": 11.0,
  "per_vehicle_revenue_10k": 1.1
}

```

## Cost Model

### Operating Costs (1,000 Vehicles)


- **V2X Mesh**: ~$3,200/month ($3.17/vehicle)

  - Compute: $2,800/month (8 nodes)

  - Storage: $200/month

  - Network: $150/month

  - Load Balancer: $50/month


- **Gemini Ingestion**: $77/month

  - Gemini API: $60/month

  - Compute (batch): $15/month

  - Storage: $2/month


- **Platform Monitoring**: $50/month

  - Compute: $30/month

  - Storage: $10/month

  - Monitoring tools: $10/month

**Total**: $3,327/month for 1,000 vehicles

### Revenue Model (70% Margin)

To achieve 70% gross margin:

- **Required Revenue**: $11,000/month

- **Price per Vehicle**: $11/month

**At Scale**:

- 1,000 vehicles: $11k MRR ($132k ARR)

- 5,000 vehicles: $45k MRR ($540k ARR)

- 10,000 vehicles: $70k MRR ($840k ARR) - with volume discounts

### Path to Profitability


- **Week 1-2**: Deploy platform, test with 10 vehicles

- **Week 3-4**: Onboard first 50 paying customers

- **Month 2**: Reach 200 vehicles ($2,200 MRR)

- **Month 3**: Reach 500 vehicles ($5,000 MRR)

- **Month 4**: Reach 1,000 vehicles ($10,000+ MRR) - **Profitable**

## Monitoring & Alerts

### Budget Alerts


- **Warning (75%)**: Email notification to admin

- **Critical (90%)**: Email + Slack notification + Auto-scaling freeze

### Health Monitoring


- **Healthy**: All services responding, error rate < 1%

- **Degraded**: Some latency issues, error rate 1-5%

- **Unhealthy**: Service down or error rate > 5%

### AI-Powered Alerts

Intelligent alerts that correlate metrics and suggest actions:

- "High cost + high latency = under-provisioned → Scale up 50%"

- "Low utilization + high cost = over-provisioned → Scale down 30%"

## Security

### API Security


- CORS enabled for dashboard access

- Stripe webhook signature verification

- Environment-based secrets management

- GKE Workload Identity for GCP access

### Network Policies


- Ingress: Allow from external (LoadBalancer)

- Egress: Allow to V2X, Gemini, Vertex AI, Stripe

- DNS resolution enabled

### Payment Security


- PCI compliance through Stripe

- Client-side tokenization (Stripe.js/Elements)

- No card data stored on servers

- Webhook signature verification

## Performance

### API Latency


- Health check: < 10ms

- Metrics aggregation: < 100ms

- AI recommendations: < 500ms

- Dashboard load: < 2s

### Scalability


- Horizontal scaling: 2-5 pods (HPA)

- CPU target: 70%

- Memory target: 80%

- Handles 1,000 req/s per pod

## Development

### Running Tests

```bash
pytest tests/ -v

```

### Code Formatting

```bash
black . --line-length 100

```

### API Documentation

Interactive docs available at:

- Swagger UI: `http://localhost:8080/docs`

- ReDoc: `http://localhost:8080/redoc`

## Support


- **Documentation**: See `/docs` endpoint

- **Issues**: GitHub Issues

- **Email**: redacted@shadowtag-v4.local

## License

Proprietary - PNKLN Core Stack™

---

**Built with**: FastAPI, Stripe, Vertex AI, Chart.js, GKE
