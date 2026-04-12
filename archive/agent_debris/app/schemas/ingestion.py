"""
Gemini Ingestion Layer data models for intelligence collection and analysis
Integrated with Cor.57 Unified Sky-Ground GPU Mesh
"""
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum, StrEnum


class DataTier(StrEnum):
    """Data quality tier classification"""
    TIER_1 = "tier_1"  # High-value, verified sources
    TIER_2 = "tier_2"  # Medium-value, partially verified
    TIER_3 = "tier_3"  # Low-value, unverified


class SourceType(StrEnum):
    """Intelligence source types"""
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    NEWS = "news"
    REDDIT = "reddit"
    GITHUB = "github"
    SATELLITE_TELEMETRY = "satellite_telemetry"
    TOWER_METRICS = "tower_metrics"
    VEHICLE_DATA = "vehicle_data"
    DEFENSE_FEEDS = "defense_feeds"


class ComplianceStatus(StrEnum):
    """Ethical compliance status"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    PENDING_REVIEW = "pending_review"


class IngestionMetrics(BaseModel):
    """Core ingestion performance metrics"""
    items_per_day: int = Field(..., description="Total items ingested per day")
    unique_sources: int = Field(..., description="Number of unique sources accessed")
    cost_per_item: float = Field(..., description="Cost per item in USD")
    average_relevance_score: float = Field(..., ge=0, le=100, description="Average relevance score (0-100)")
    timeliness_score: float = Field(..., ge=0, le=100, description="Data timeliness score (0-100)")
    completeness_percentage: float = Field(..., ge=0, le=100, description="Data completeness percentage")
    runtime_minutes: float = Field(..., description="Runtime in minutes for nightly job")

    class Config:
        json_schema_extra = {
            "example": {
                "items_per_day": 125000,
                "unique_sources": 47,
                "cost_per_item": 0.000616,
                "average_relevance_score": 87.3,
                "timeliness_score": 92.1,
                "completeness_percentage": 94.5,
                "runtime_minutes": 43.2
            }
        }


class EthicalComplianceMetrics(BaseModel):
    """Ethical crawling and compliance metrics"""
    robots_txt_compliance: float = Field(..., ge=0, le=100, description="robots.txt compliance percentage")
    rate_limiting_adherence: float = Field(..., ge=0, le=100, description="Rate limiting adherence percentage")
    transparency_score: float = Field(..., ge=0, le=100, description="Transparency score")
    legal_violations: int = Field(..., description="Number of legal violations detected")
    ethical_flags: int = Field(..., description="Number of ethical flags raised")
    compliance_status: ComplianceStatus

    class Config:
        json_schema_extra = {
            "example": {
                "robots_txt_compliance": 99.8,
                "rate_limiting_adherence": 98.5,
                "transparency_score": 95.0,
                "legal_violations": 0,
                "ethical_flags": 2,
                "compliance_status": "compliant"
            }
        }


class SourceCoverage(BaseModel):
    """Multi-source coverage metrics"""
    source_type: SourceType
    items_collected: int = Field(..., description="Items collected from this source")
    coverage_percentage: float = Field(..., ge=0, le=100, description="Coverage percentage of available data")
    reliability_score: float = Field(..., ge=0, le=100, description="Source reliability score")
    tier_distribution: dict[DataTier, int] = Field(..., description="Distribution across data tiers")

    class Config:
        json_schema_extra = {
            "example": {
                "source_type": "twitter",
                "items_collected": 45000,
                "coverage_percentage": 78.3,
                "reliability_score": 85.0,
                "tier_distribution": {
                    "tier_1": 12000,
                    "tier_2": 25000,
                    "tier_3": 8000
                }
            }
        }


class TierClassification(BaseModel):
    """Data tier classification and distribution"""
    tier: DataTier
    item_count: int = Field(..., description="Number of items in this tier")
    percentage: float = Field(..., ge=0, le=100, description="Percentage of total items")
    average_cost: float = Field(..., description="Average cost per item in USD")
    quality_score: float = Field(..., ge=0, le=100, description="Quality score for this tier")

    class Config:
        json_schema_extra = {
            "example": {
                "tier": "tier_1",
                "item_count": 35000,
                "percentage": 28.0,
                "average_cost": 0.00142,
                "quality_score": 94.5
            }
        }


class GKEArchitecture(BaseModel):
    """GKE CronJob architecture configuration"""
    cluster_name: str = Field(default="shadowtag-omega-v4-ingestion-cluster")
    namespace: str = Field(default="intelligence-pipeline")
    cron_schedule: str = Field(default="0 2 * * *", description="Cron schedule (2 AM daily)")
    container_count: int = Field(..., description="Number of containers in the pod")
    cpu_allocation: str = Field(..., description="CPU allocation per container")
    memory_allocation: str = Field(..., description="Memory allocation per container")
    average_runtime_minutes: float = Field(..., description="Average runtime in minutes")
    success_rate: float = Field(..., ge=0, le=100, description="Job success rate percentage")

    class Config:
        json_schema_extra = {
            "example": {
                "cluster_name": "shadowtag-omega-v4-ingestion-cluster",
                "namespace": "intelligence-pipeline",
                "cron_schedule": "0 2 * * *",
                "container_count": 4,
                "cpu_allocation": "2000m",
                "memory_allocation": "4Gi",
                "average_runtime_minutes": 45.0,
                "success_rate": 99.7
            }
        }


class QualityGates(BaseModel):
    """Quality gates for ingestion validation"""
    minimum_items_per_day: int = Field(..., description="Minimum items threshold")
    minimum_sources: int = Field(..., description="Minimum unique sources threshold")
    maximum_cost_per_item: float = Field(..., description="Maximum acceptable cost per item")
    minimum_relevance_score: float = Field(..., ge=0, le=100, description="Minimum relevance score")
    gates_passed: int = Field(..., description="Number of quality gates passed")
    gates_total: int = Field(..., description="Total number of quality gates")
    overall_status: str = Field(..., description="Overall quality gate status")

    class Config:
        json_schema_extra = {
            "example": {
                "minimum_items_per_day": 100000,
                "minimum_sources": 40,
                "maximum_cost_per_item": 0.001,
                "minimum_relevance_score": 85.0,
                "gates_passed": 4,
                "gates_total": 4,
                "overall_status": "PASSED"
            }
        }


class AMBriefingMetrics(BaseModel):
    """AM Briefing delivery effectiveness metrics"""
    delivery_time: str = Field(..., description="Target delivery time (e.g., '06:00 AM')")
    on_time_delivery_rate: float = Field(..., ge=0, le=100, description="On-time delivery percentage")
    average_items_per_briefing: int = Field(..., description="Average items per briefing")
    user_engagement_score: float = Field(..., ge=0, le=100, description="User engagement score")
    actionability_score: float = Field(..., ge=0, le=100, description="Intelligence actionability score")
    format_quality: str = Field(..., description="Briefing format quality assessment")

    class Config:
        json_schema_extra = {
            "example": {
                "delivery_time": "06:00 AM",
                "on_time_delivery_rate": 98.5,
                "average_items_per_briefing": 45,
                "user_engagement_score": 89.3,
                "actionability_score": 91.7,
                "format_quality": "Excellent"
            }
        }


class OperationalCostBreakdown(BaseModel):
    """Monthly operational cost breakdown"""
    gke_infrastructure: float = Field(..., description="GKE infrastructure cost in USD")
    api_calls: float = Field(..., description="API calls cost in USD")
    data_storage: float = Field(..., description="Data storage cost in USD")
    network_egress: float = Field(..., description="Network egress cost in USD")
    gemini_api: float = Field(..., description="Gemini API cost in USD")
    total_monthly_cost: float = Field(..., description="Total monthly cost in USD")

    class Config:
        json_schema_extra = {
            "example": {
                "gke_infrastructure": 28.50,
                "api_calls": 18.75,
                "data_storage": 12.30,
                "network_egress": 8.45,
                "gemini_api": 9.00,
                "total_monthly_cost": 77.00
            }
        }


class IngestionIntegration(BaseModel):
    """Integration with PNKLN Core Stack and Cor.57 infrastructure"""
    called_by_services: list[str] = Field(..., description="Services that trigger ingestion")
    feeds_into_services: list[str] = Field(..., description="Services that consume ingested data")
    namespace_count: int = Field(default=4, description="Number of Kubernetes namespaces")
    integration_points: int = Field(..., description="Number of integration points")
    data_handoff_latency_ms: int = Field(..., description="Average data handoff latency in ms")

    class Config:
        json_schema_extra = {
            "example": {
                "called_by_services": [
                    "starlink-orbital-monitor",
                    "tower-terrestrial-analytics",
                    "vehicle-mesh-collector",
                    "defense-intelligence-hub"
                ],
                "feeds_into_services": [
                    "judge-six-validator",
                    "am-briefing-generator",
                    "strategic-dashboard",
                    "defense-reporting"
                ],
                "namespace_count": 4,
                "integration_points": 8,
                "data_handoff_latency_ms": 125
            }
        }


class GeminiIngestionLayer(BaseModel):
    """Complete Gemini Ingestion Layer analysis model"""
    timestamp: str = Field(..., description="Analysis timestamp")
    version: str = Field(default="2.0", description="Ingestion layer version")
    architecture: GKEArchitecture
    ingestion_metrics: IngestionMetrics
    ethical_compliance: EthicalComplianceMetrics
    source_coverage: list[SourceCoverage]
    tier_classification: list[TierClassification]
    quality_gates: QualityGates
    am_briefing: AMBriefingMetrics
    operational_costs: OperationalCostBreakdown
    integration: IngestionIntegration
    confidence_score: float = Field(..., ge=0, le=100, description="Overall analysis confidence (target ≥60%)")
    recommendations: list[str] = Field(default_factory=list, description="Optimization recommendations")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-11-15T08:30:00Z",
                "version": "2.0",
                "confidence_score": 68.5,
                "recommendations": [
                    "Increase Tier 1 source coverage by 15%",
                    "Optimize GKE container resource allocation",
                    "Expand Twitter API rate limits for better coverage"
                ]
            }
        }


class IngestionVsValidation(BaseModel):
    """Comparison model: Ingestion Layer vs Judge #6 Validator"""
    component: str
    ingestion_layer: str = Field(..., description="Ingestion Layer characteristic")
    judge_six: str = Field(..., description="Judge #6 characteristic")
    strategic_impact: str = Field(..., description="Impact on Cor.57 infrastructure")

    class Config:
        json_schema_extra = {
            "example": {
                "component": "Architecture",
                "ingestion_layer": "GKE CronJob Multi-Container (Batch)",
                "judge_six": "Hybrid Gemini+PyTorch (Real-time)",
                "strategic_impact": "Complementary: Ingestion feeds validated data to Judge #6"
            }
        }
