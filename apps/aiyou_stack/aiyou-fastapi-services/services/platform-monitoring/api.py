"""Platform Monitoring API

Unified monitoring and cost tracking API for PNKLN Core Stack™

Endpoints:
- GET / - Dashboard UI
- GET /health - Health check
- GET /metrics/platform - Aggregated platform metrics
- GET /metrics/services - Per-service metrics
- GET /costs/status - Budget status
- GET /costs/breakdown - Cost breakdown
- GET /costs/optimization - Optimization suggestions
- GET /costs/revenue-requirements - Required revenue for margin
- GET /ai/recommendations - AI-powered optimization recommendations
- GET /ai/insights - Platform insights with AI analysis
"""

from pathlib import Path

import uvicorn
from cost_tracker import CostCategory, CostTracker
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from metrics_aggregator import MetricsAggregator
from pydantic import BaseModel
from stripe_billing import (
    BillingInterval,
    StripeBillingService,
    calculate_pricing,
)
from vertex_ai_integration import VertexAIService

# Create FastAPI app
app = FastAPI(
    title="PNKLN Platform Monitoring API",
    description="Unified monitoring and cost tracking for V2X Mesh + Gemini Ingestion",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
metrics_aggregator = MetricsAggregator()
cost_tracker = CostTracker()
vertex_ai_service = VertexAIService()
billing_service = StripeBillingService()


# Pydantic models
class HealthResponse(BaseModel):
    status: str
    timestamp: str


class CostRecordRequest(BaseModel):
    service: str
    category: str
    amount: float
    description: str


class CreateCustomerRequest(BaseModel):
    email: str
    name: str
    metadata: dict | None = None


class CreateSubscriptionRequest(BaseModel):
    customer_id: str
    vehicle_count: int
    billing_interval: str = "month"


class UpdateSubscriptionRequest(BaseModel):
    subscription_id: str
    new_vehicle_count: int


class AttachPaymentMethodRequest(BaseModel):
    customer_id: str
    payment_method_id: str


class WebhookEvent(BaseModel):
    payload: bytes
    signature: str


# Dashboard endpoint
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the monitoring dashboard"""
    dashboard_path = Path(__file__).parent / "dashboard.html"
    if not dashboard_path.exists():
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard_path.read_text()


# Health endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check"""
    from datetime import datetime

    return HealthResponse(status="healthy", timestamp=datetime.now().isoformat())


# Metrics endpoints
@app.get("/metrics/platform")
async def get_platform_metrics():
    """Get aggregated platform metrics"""
    metrics = await metrics_aggregator.collect_all_metrics()

    return {
        "timestamp": metrics.timestamp.isoformat(),
        "services": {
            "total": metrics.total_services,
            "healthy": metrics.healthy_services,
            "degraded": metrics.degraded_services,
            "unhealthy": metrics.unhealthy_services,
        },
        "performance": {
            "requests_per_second": metrics.platform_requests_per_second,
            "avg_latency_ms": metrics.platform_avg_latency_ms,
            "error_rate": metrics.platform_error_rate,
        },
        "resources": {
            "cpu_percent": metrics.platform_cpu_usage_percent,
            "memory_mb": metrics.platform_memory_usage_mb,
        },
        "business": {
            "daily_items": metrics.daily_items_processed,
            "daily_cost": metrics.daily_cost_dollars,
            "monthly_projection": metrics.monthly_cost_projection,
        },
        "alerts": metrics.active_alerts,
    }


@app.get("/metrics/services")
async def get_service_metrics(service: str | None = None):
    """Get per-service metrics"""
    metrics = await metrics_aggregator.collect_all_metrics()

    services = {}

    if metrics.v2x_metrics and (not service or service == "v2x-mesh"):
        services["v2x-mesh"] = {
            "service_type": "v2x_mesh",
            "timestamp": metrics.v2x_metrics.timestamp.isoformat(),
            "performance": {
                "requests_per_second": metrics.v2x_metrics.requests_per_second,
                "avg_latency_ms": metrics.v2x_metrics.avg_latency_ms,
                "p99_latency_ms": metrics.v2x_metrics.p99_latency_ms,
                "error_rate": metrics.v2x_metrics.error_rate,
            },
            "resources": {
                "cpu_percent": metrics.v2x_metrics.cpu_usage_percent,
                "memory_mb": metrics.v2x_metrics.memory_usage_mb,
                "active_connections": metrics.v2x_metrics.active_connections,
            },
            "business": {
                "items_processed": metrics.v2x_metrics.items_processed,
                "cost_dollars": metrics.v2x_metrics.cost_dollars,
            },
            "health": metrics.v2x_metrics.health_status.value,
            "uptime_seconds": metrics.v2x_metrics.uptime_seconds,
        }

    if metrics.ingestion_metrics and (not service or service == "gemini-ingestion"):
        services["gemini-ingestion"] = {
            "service_type": "ingestion",
            "timestamp": metrics.ingestion_metrics.timestamp.isoformat(),
            "performance": {
                "runtime_minutes": metrics.ingestion_metrics.avg_latency_ms / 60000,
                "error_rate": metrics.ingestion_metrics.error_rate,
            },
            "resources": {
                "cpu_percent": metrics.ingestion_metrics.cpu_usage_percent,
                "memory_mb": metrics.ingestion_metrics.memory_usage_mb,
            },
            "business": {
                "items_processed": metrics.ingestion_metrics.items_processed,
                "cost_dollars": metrics.ingestion_metrics.cost_dollars,
            },
            "health": metrics.ingestion_metrics.health_status.value,
            "last_run_age_seconds": metrics.ingestion_metrics.uptime_seconds,
        }

    return {"services": services}


@app.get("/metrics/performance-summary")
async def get_performance_summary():
    """Get performance summary"""
    return metrics_aggregator.get_performance_summary()


# Cost endpoints
@app.post("/costs/record")
async def record_cost(request: CostRecordRequest):
    """Record a cost entry"""
    try:
        category = CostCategory(request.category)
        cost_tracker.record_cost(
            service=request.service,
            category=category,
            amount=request.amount,
            description=request.description,
        )
        return {"status": "recorded"}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {request.category}") from None


@app.get("/costs/status")
async def get_cost_status():
    """Get budget status"""
    status = cost_tracker.get_budget_status()
    alerts = cost_tracker.get_alerts()

    return {
        "budget_status": status,
        "alerts": [
            {
                "type": a.alert_type,
                "service": a.service,
                "current_spend": a.current_spend,
                "budget": a.budget,
                "utilization_percent": a.utilization_percent,
                "recommendation": a.recommendation,
            }
            for a in alerts
        ],
    }


@app.get("/costs/breakdown")
async def get_cost_breakdown(service: str | None = None, days: int = 30):
    """Get cost breakdown by category"""
    breakdown = cost_tracker.get_cost_breakdown_by_category(service, days)

    return {
        "service": service or "all",
        "period_days": days,
        "breakdown": breakdown,
        "total": sum(breakdown.values()),
    }


@app.get("/costs/monthly")
async def get_monthly_costs(service: str | None = None):
    """Get monthly costs"""
    costs = cost_tracker.get_monthly_costs(service)

    return {"service": service or "all", "monthly_costs": costs}


@app.get("/costs/optimization")
async def get_optimization_suggestions():
    """Get cost optimization suggestions"""
    suggestions = cost_tracker.get_optimization_suggestions()

    return {
        "suggestions": suggestions,
        "total_potential_savings": sum(s["potential_savings"] for s in suggestions),
    }


@app.get("/costs/revenue-requirements")
async def get_revenue_requirements(margin_percent: float = 70.0):
    """Get required revenue for target margin"""
    requirements = cost_tracker.get_revenue_requirements(margin_percent)

    return requirements


@app.get("/costs/per-item")
async def get_cost_per_item(service: str, items_processed: int):
    """Calculate cost per item"""
    cost = cost_tracker.get_cost_per_item(service, items_processed)

    return {"service": service, "items_processed": items_processed, "cost_per_item": cost}


@app.get("/costs/report")
async def get_cost_report():
    """Get comprehensive cost report"""
    return cost_tracker.export_cost_report()


# AI-powered insights endpoints
@app.get("/ai/recommendations")
async def get_ai_recommendations():
    """Get AI-powered optimization recommendations"""
    # Gather current metrics
    metrics = await metrics_aggregator.collect_all_metrics()

    cost_data = {
        "gemini-ingestion": metrics.ingestion_metrics.cost_dollars
        if metrics.ingestion_metrics
        else 0,
        "v2x-mesh": metrics.v2x_metrics.cost_dollars if metrics.v2x_metrics else 0,
    }

    performance_data = {
        "avg_latency_ms": metrics.platform_avg_latency_ms,
        "error_rate": metrics.platform_error_rate,
    }

    budget_data = cost_tracker.budgets

    # Get AI recommendations
    recommendations = await vertex_ai_service.get_optimization_recommendations(
        cost_data,
        performance_data,
        budget_data,
    )

    return {
        "recommendations": [
            {
                "id": rec.recommendation_id,
                "type": rec.analysis_type.value,
                "priority": rec.priority,
                "title": rec.title,
                "description": rec.description,
                "impact": rec.impact_estimate,
                "steps": rec.implementation_steps,
                "savings": rec.estimated_savings_dollars,
                "confidence": rec.confidence_score,
            }
            for rec in recommendations
        ],
        "total_recommendations": len(recommendations),
        "total_potential_savings": sum(rec.estimated_savings_dollars for rec in recommendations),
    }


@app.get("/ai/insights")
async def get_ai_insights():
    """Get comprehensive platform insights with AI analysis"""
    # Gather all metrics
    metrics = await metrics_aggregator.collect_all_metrics()

    all_metrics = {
        "daily_cost": metrics.daily_cost_dollars,
        "avg_latency_ms": metrics.platform_avg_latency_ms,
        "error_rate": metrics.platform_error_rate,
        "cpu_percent": metrics.platform_cpu_usage_percent,
        "memory_mb": metrics.platform_memory_usage_mb,
    }

    cost_data = {
        "gemini-ingestion": metrics.ingestion_metrics.cost_dollars
        if metrics.ingestion_metrics
        else 0,
        "v2x-mesh": metrics.v2x_metrics.cost_dollars if metrics.v2x_metrics else 0,
    }

    performance_data = {
        "avg_latency_ms": metrics.platform_avg_latency_ms,
        "error_rate": metrics.platform_error_rate,
    }

    # Get AI insights
    insights = await vertex_ai_service.get_platform_insights(
        all_metrics,
        cost_data,
        performance_data,
    )

    return insights


@app.get("/ai/capacity-forecast")
async def get_capacity_forecast(growth_rate: float = 0.15):
    """Get AI-powered capacity forecasting"""
    metrics = await metrics_aggregator.collect_all_metrics()

    current_capacity = {
        "cores": 8,  # Current compute
        "storage_gb": 100,
        "monthly_cost": metrics.monthly_cost_projection,
    }

    forecast = await vertex_ai_service.analyzer.predict_capacity_needs(
        growth_rate,
        current_capacity,
    )

    return forecast


# Billing endpoints
@app.post("/billing/customers")
async def create_customer(request: CreateCustomerRequest):
    """Create a new Stripe customer"""
    result = await billing_service.create_customer(
        email=request.email,
        name=request.name,
        metadata=request.metadata,
    )
    return result


@app.get("/billing/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get customer details"""
    result = await billing_service.get_customer(customer_id)
    return result


@app.post("/billing/payment-methods")
async def attach_payment_method(request: AttachPaymentMethodRequest):
    """Attach payment method to customer"""
    result = await billing_service.attach_payment_method(
        customer_id=request.customer_id,
        payment_method_id=request.payment_method_id,
    )
    return result


@app.post("/billing/subscriptions")
async def create_subscription(request: CreateSubscriptionRequest):
    """Create a new subscription"""
    billing_interval = BillingInterval(request.billing_interval)
    result = await billing_service.create_subscription(
        customer_id=request.customer_id,
        vehicle_count=request.vehicle_count,
        billing_interval=billing_interval,
    )
    return result


@app.get("/billing/subscriptions/{subscription_id}")
async def get_subscription(subscription_id: str):
    """Get subscription details"""
    result = await billing_service.get_subscription(subscription_id)
    return result


@app.patch("/billing/subscriptions")
async def update_subscription(request: UpdateSubscriptionRequest):
    """Update subscription vehicle count"""
    result = await billing_service.update_subscription_quantity(
        subscription_id=request.subscription_id,
        new_vehicle_count=request.new_vehicle_count,
    )
    return result


@app.delete("/billing/subscriptions/{subscription_id}")
async def cancel_subscription(subscription_id: str, immediate: bool = False):
    """Cancel a subscription"""
    result = await billing_service.cancel_subscription(
        subscription_id=subscription_id,
        immediate=immediate,
    )
    return result


@app.get("/billing/invoices/upcoming/{customer_id}")
async def get_upcoming_invoice(customer_id: str):
    """Get upcoming invoice preview"""
    result = await billing_service.get_upcoming_invoice(customer_id)
    return result


@app.get("/billing/invoices/{customer_id}")
async def list_invoices(customer_id: str, limit: int = 10):
    """List customer invoices"""
    result = await billing_service.list_invoices(customer_id, limit)
    return result


@app.get("/billing/pricing")
async def get_pricing(vehicle_count: int):
    """Calculate pricing for vehicle count"""
    pricing = calculate_pricing(vehicle_count)
    return pricing


@app.post("/billing/webhooks")
async def handle_stripe_webhook(payload: bytes = None, stripe_signature: str = None):
    """Handle Stripe webhooks

    Verifies signature and processes events
    """
    # In production, get payload from request body and signature from header
    # For now, this is a placeholder structure
    if not payload or not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing payload or signature")

    event = billing_service.verify_webhook_signature(payload, stripe_signature)
    if not event:
        raise HTTPException(status_code=400, detail="Invalid signature")

    result = await billing_service.handle_webhook_event(event)
    return result


@app.get("/billing/revenue-report")
async def get_revenue_report(start_date: str, end_date: str):
    """Get revenue report for date range

    Args:
        start_date: ISO format date (YYYY-MM-DD)
        end_date: ISO format date (YYYY-MM-DD)

    """
    from datetime import datetime

    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    result = await billing_service.get_revenue_report(start, end)
    return result


# Prometheus metrics endpoint
@app.get("/prometheus")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    metrics = await metrics_aggregator.collect_all_metrics()

    lines = [
        "# HELP platform_services_total Total number of services",
        "# TYPE platform_services_total gauge",
        f"platform_services_total {metrics.total_services}",
        "",
        "# HELP platform_services_healthy Number of healthy services",
        "# TYPE platform_services_healthy gauge",
        f"platform_services_healthy {metrics.healthy_services}",
        "",
        "# HELP platform_requests_per_second Platform requests per second",
        "# TYPE platform_requests_per_second gauge",
        f"platform_requests_per_second {metrics.platform_requests_per_second}",
        "",
        "# HELP platform_latency_ms Platform average latency in milliseconds",
        "# TYPE platform_latency_ms gauge",
        f"platform_latency_ms {metrics.platform_avg_latency_ms}",
        "",
        "# HELP platform_error_rate Platform error rate",
        "# TYPE platform_error_rate gauge",
        f"platform_error_rate {metrics.platform_error_rate}",
        "",
        "# HELP platform_daily_cost_dollars Daily cost in dollars",
        "# TYPE platform_daily_cost_dollars gauge",
        f"platform_daily_cost_dollars {metrics.daily_cost_dollars}",
        "",
        "# HELP platform_items_processed Daily items processed",
        "# TYPE platform_items_processed counter",
        f"platform_items_processed {metrics.daily_items_processed}",
    ]

    from fastapi.responses import PlainTextResponse

    return PlainTextResponse("\n".join(lines))


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8080, log_level="info", reload=True)
