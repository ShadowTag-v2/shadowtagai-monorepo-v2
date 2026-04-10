"""
KPI tracking and reporting API endpoints
Tracks governance, safety, and monetization metrics
"""
from datetime import datetime, timedelta
from enum import Enum, StrEnum
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class KPICategory(StrEnum):
    """KPI categories"""
    SAFETY = "safety"
    COMPLIANCE = "compliance"
    MONETIZATION = "monetization"
    RELIABILITY = "reliability"
    GOVERNANCE = "governance"


class TimeRange(StrEnum):
    """Time range for KPI queries"""
    HOUR = "1h"
    DAY = "24h"
    WEEK = "7d"
    MONTH = "30d"
    QUARTER = "90d"


class KPIMetric(BaseModel):
    """Individual KPI metric"""
    name: str
    value: float
    unit: str
    target: float | None = None
    trend: str  # "up", "down", "stable"
    status: str  # "good", "warning", "critical"


class KPIDashboardResponse(BaseModel):
    """KPI dashboard response"""
    timestamp: datetime
    time_range: TimeRange
    categories: dict[KPICategory, list[KPIMetric]]
    overall_health: str  # "healthy", "warning", "critical"


@router.get("/dashboard", response_model=KPIDashboardResponse)
async def get_kpi_dashboard(time_range: TimeRange = TimeRange.DAY):
    """
    Get comprehensive KPI dashboard

    Categories:
    - Safety/Compliance: C2PA coverage, DSA compliance, brand safety
    - Monetization: Viewability, VAST success, CPM performance
    - Reliability: Latency, uptime, error rates
    - Governance: Risk assessments, audit completion
    """
    return KPIDashboardResponse(
        timestamp=datetime.utcnow(),
        time_range=time_range,
        categories={
            KPICategory.SAFETY: [
                KPIMetric(
                    name="C2PA Coverage",
                    value=82.5,
                    unit="%",
                    target=80.0,
                    trend="up",
                    status="good"
                ),
                KPIMetric(
                    name="Brand Safety Incidents",
                    value=0.12,
                    unit="per 10k views",
                    target=0.50,
                    trend="down",
                    status="good"
                ),
                KPIMetric(
                    name="Content Moderation Coverage",
                    value=99.8,
                    unit="%",
                    target=99.5,
                    trend="stable",
                    status="good"
                )
            ],
            KPICategory.COMPLIANCE: [
                KPIMetric(
                    name="EU AI Act Compliance",
                    value=95.0,
                    unit="%",
                    target=90.0,
                    trend="up",
                    status="good"
                ),
                KPIMetric(
                    name="DSA Transparency",
                    value=88.0,
                    unit="%",
                    target=85.0,
                    trend="stable",
                    status="good"
                ),
                KPIMetric(
                    name="WCAG 2.2 Compliance",
                    value=92.0,
                    unit="%",
                    target=95.0,
                    trend="up",
                    status="warning"
                )
            ],
            KPICategory.MONETIZATION: [
                KPIMetric(
                    name="OM SDK Viewability",
                    value=78.5,
                    unit="%",
                    target=70.0,
                    trend="up",
                    status="good"
                ),
                KPIMetric(
                    name="VAST Error Rate",
                    value=2.1,
                    unit="%",
                    target=5.0,
                    trend="down",
                    status="good"
                ),
                KPIMetric(
                    name="CPM Premium",
                    value=35.0,
                    unit="%",
                    target=30.0,
                    trend="up",
                    status="good"
                )
            ],
            KPICategory.RELIABILITY: [
                KPIMetric(
                    name="Overlay Latency P95",
                    value=125.0,
                    unit="ms",
                    target=150.0,
                    trend="stable",
                    status="good"
                ),
                KPIMetric(
                    name="API Uptime",
                    value=99.95,
                    unit="%",
                    target=99.9,
                    trend="stable",
                    status="good"
                ),
                KPIMetric(
                    name="SSAI Success Rate",
                    value=98.2,
                    unit="%",
                    target=95.0,
                    trend="up",
                    status="good"
                )
            ],
            KPICategory.GOVERNANCE: [
                KPIMetric(
                    name="Risk Assessments Completed",
                    value=156.0,
                    unit="count",
                    target=150.0,
                    trend="up",
                    status="good"
                ),
                KPIMetric(
                    name="Audit Coverage",
                    value=92.0,
                    unit="%",
                    target=90.0,
                    trend="stable",
                    status="good"
                ),
                KPIMetric(
                    name="Persona IQ Override",
                    value=160.0,
                    unit="IQ",
                    target=160.0,
                    trend="stable",
                    status="good"
                )
            ]
        },
        overall_health="healthy"
    )


@router.get("/category/{category}", response_model=list[KPIMetric])
async def get_category_kpis(category: KPICategory, time_range: TimeRange = TimeRange.DAY):
    """Get KPIs for specific category"""
    # This would fetch from actual metrics storage
    dashboard = await get_kpi_dashboard(time_range)
    return dashboard.categories.get(category, [])


@router.get("/metric/{metric_name}")
async def get_metric_history(
    metric_name: str,
    time_range: TimeRange = TimeRange.WEEK,
    granularity: str = "hour"
):
    """
    Get historical data for specific metric

    Returns time-series data for trending and analysis
    """
    # TODO: Implement actual time-series data retrieval
    return {
        "metric_name": metric_name,
        "time_range": time_range,
        "granularity": granularity,
        "data_points": [
            {
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "value": 80.0 + (i % 10)
            }
            for i in range(24)
        ]
    }


@router.get("/report/30-60-90")
async def get_gap_closure_report():
    """
    30-60-90 day gap closure plan status

    Tracks implementation of:
    - Governance frameworks
    - Adtech standards
    - Accessibility compliance
    - Infrastructure decisions
    """
    return {
        "plan_start_date": "2024-01-01",
        "current_day": 45,
        "phases": {
            "30_days": {
                "status": "completed",
                "items": [
                    {
                        "item": "Map YRM↔️NIST RMF↔️ISO 42001 controls",
                        "status": "completed",
                        "completion_date": "2024-01-25"
                    },
                    {
                        "item": "Choose adtech baseline: VAST 4.x + OM SDK",
                        "status": "completed",
                        "completion_date": "2024-01-28"
                    },
                    {
                        "item": "WCAG 2.2 audit + minors' defaults",
                        "status": "completed",
                        "completion_date": "2024-01-30"
                    }
                ]
            },
            "60_days": {
                "status": "in_progress",
                "items": [
                    {
                        "item": "C2PA Content Credentials live",
                        "status": "in_progress",
                        "progress": 75
                    },
                    {
                        "item": "SKAN/Topics instrumentation",
                        "status": "in_progress",
                        "progress": 60
                    },
                    {
                        "item": "OpenTelemetry + SBOM/SLSA pipeline",
                        "status": "completed",
                        "completion_date": "2024-02-10"
                    }
                ]
            },
            "90_days": {
                "status": "pending",
                "items": [
                    {
                        "item": "Advertiser dashboard (OM viewability + brand-safety)",
                        "status": "pending",
                        "target_date": "2024-03-15"
                    },
                    {
                        "item": "Publish ShadowTagAI Governance Report v0.1",
                        "status": "pending",
                        "target_date": "2024-03-20"
                    },
                    {
                        "item": "Infra decision: Blackwell + Trainium2/Azure Maia",
                        "status": "pending",
                        "target_date": "2024-03-25"
                    }
                ]
            }
        }
    }
