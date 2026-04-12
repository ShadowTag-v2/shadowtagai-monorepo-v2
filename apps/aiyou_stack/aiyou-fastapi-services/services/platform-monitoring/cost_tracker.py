"""
Cost Tracking & Optimization

Monitors costs across platform services:
- V2X Mesh: $3.17/vehicle/month (city-scale)
- Gemini Ingestion: $77/month budget
- Platform overhead: Monitoring, API gateway

Target: Keep total cost <$250/month for MVP (1000 vehicles)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class CostCategory(Enum):
    """Cost categories"""

    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    API_CALLS = "api_calls"
    EXTERNAL_SERVICES = "external_services"


@dataclass
class CostEntry:
    """Single cost entry"""

    timestamp: datetime
    service: str
    category: CostCategory
    amount_dollars: float
    description: str
    metadata: dict = field(default_factory=dict)


@dataclass
class BudgetAlert:
    """Budget alert"""

    alert_type: str  # "warning", "critical"
    service: str
    current_spend: float
    budget: float
    utilization_percent: float
    recommendation: str


class CostTracker:
    """
    Track and optimize costs across platform

    Budget Targets:
    - Ingestion: $77/month
    - V2X Mesh (1k vehicles): $3,170/month
    - Monitoring: $50/month
    - Total: ~$3,300/month for 1k vehicles
    """

    def __init__(self):
        self.cost_entries: list[CostEntry] = []

        # Monthly budgets
        self.budgets = {
            "gemini-ingestion": 77.0,
            "v2x-mesh": 3200.0,  # Slightly under $3.17/vehicle for 1k
            "platform-monitoring": 50.0,
            "total": 3300.0,
        }

        # Alert thresholds
        self.warning_threshold = 0.75  # 75% of budget
        self.critical_threshold = 0.90  # 90% of budget

    def record_cost(
        self,
        service: str,
        category: CostCategory,
        amount: float,
        description: str,
        metadata: dict | None = None,
    ):
        """Record a cost entry"""
        entry = CostEntry(
            timestamp=datetime.now(),
            service=service,
            category=category,
            amount_dollars=amount,
            description=description,
            metadata=metadata or {},
        )

        self.cost_entries.append(entry)

        # Keep history manageable (last 10k entries)
        if len(self.cost_entries) > 10000:
            self.cost_entries = self.cost_entries[-5000:]

    def get_monthly_costs(self, service: str | None = None) -> dict[str, float]:
        """Get costs for current month"""
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)

        costs = {}

        for entry in self.cost_entries:
            if entry.timestamp < month_start:
                continue

            if service and entry.service != service:
                continue

            service_key = entry.service
            if service_key not in costs:
                costs[service_key] = 0.0

            costs[service_key] += entry.amount_dollars

        # Add total
        costs["total"] = sum(costs.values())

        return costs

    def get_budget_status(self) -> dict[str, dict]:
        """Get budget utilization status"""
        monthly_costs = self.get_monthly_costs()

        status = {}

        for service, budget in self.budgets.items():
            current = monthly_costs.get(service, 0.0)
            utilization = (current / budget) * 100 if budget > 0 else 0

            # Determine status
            if utilization >= self.critical_threshold * 100:
                health = "critical"
            elif utilization >= self.warning_threshold * 100:
                health = "warning"
            else:
                health = "healthy"

            status[service] = {
                "budget": budget,
                "current": current,
                "remaining": budget - current,
                "utilization_percent": utilization,
                "health": health,
                "projected_month_end": self._project_month_end(service, current),
            }

        return status

    def _project_month_end(self, service: str, current_spend: float) -> float:
        """Project spending at month end"""
        now = datetime.now()
        days_in_month = (datetime(now.year, now.month + 1, 1) - timedelta(days=1)).day
        day_of_month = now.day

        if day_of_month == 0:
            return current_spend

        daily_avg = current_spend / day_of_month
        projected = daily_avg * days_in_month

        return projected

    def get_alerts(self) -> list[BudgetAlert]:
        """Get active budget alerts"""
        status = self.get_budget_status()
        alerts = []

        for service, data in status.items():
            if data["health"] == "critical":
                alerts.append(
                    BudgetAlert(
                        alert_type="critical",
                        service=service,
                        current_spend=data["current"],
                        budget=data["budget"],
                        utilization_percent=data["utilization_percent"],
                        recommendation=self._get_recommendation(service, data),
                    )
                )
            elif data["health"] == "warning":
                alerts.append(
                    BudgetAlert(
                        alert_type="warning",
                        service=service,
                        current_spend=data["current"],
                        budget=data["budget"],
                        utilization_percent=data["utilization_percent"],
                        recommendation=self._get_recommendation(service, data),
                    )
                )

        return alerts

    def _get_recommendation(self, service: str, data: dict) -> str:
        """Get cost optimization recommendation"""
        if service == "gemini-ingestion":
            if data["utilization_percent"] > 90:
                return "Reduce Gemini API calls: Implement caching, batch requests, or reduce analysis frequency"
            return "Consider optimizing: Use cheaper external APIs, implement aggressive caching"

        elif service == "v2x-mesh":
            if data["utilization_percent"] > 90:
                return "Scale down: Reduce peer count, implement more aggressive rate limiting, or optimize GPU usage"
            return "Optimize: Review GPU utilization, implement better compression, reduce beacon frequency"

        elif service == "platform-monitoring":
            if data["utilization_percent"] > 90:
                return "Reduce metrics: Decrease collection frequency, prune unused metrics, compress storage"
            return "Optimize: Implement metric sampling, reduce retention period"

        return "Monitor closely and review cost breakdown"

    def get_cost_breakdown_by_category(
        self, service: str | None = None, days: int = 30
    ) -> dict[str, float]:
        """Get cost breakdown by category"""
        cutoff = datetime.now() - timedelta(days=days)

        breakdown = {}

        for entry in self.cost_entries:
            if entry.timestamp < cutoff:
                continue

            if service and entry.service != service:
                continue

            category = entry.category.value
            if category not in breakdown:
                breakdown[category] = 0.0

            breakdown[category] += entry.amount_dollars

        return breakdown

    def get_cost_per_item(self, service: str, items_processed: int) -> float:
        """Calculate cost per item"""
        monthly_costs = self.get_monthly_costs(service)
        service_cost = monthly_costs.get(service, 0.0)

        if items_processed == 0:
            return 0.0

        return service_cost / items_processed

    def get_optimization_suggestions(self) -> list[dict]:
        """Get cost optimization suggestions"""
        suggestions = []

        # Analyze Gemini Ingestion costs
        ingestion_breakdown = self.get_cost_breakdown_by_category("gemini-ingestion")
        api_cost = ingestion_breakdown.get("api_calls", 0)

        if api_cost > 50:  # >$50/month on APIs
            suggestions.append(
                {
                    "service": "gemini-ingestion",
                    "priority": "high",
                    "category": "api_calls",
                    "current_cost": api_cost,
                    "potential_savings": api_cost * 0.4,  # 40% savings
                    "action": "Implement Gemini API caching - cache repeated analyses for 24hrs",
                    "roi": "High - immediate 40% reduction in API costs",
                }
            )

        # Analyze V2X costs
        v2x_breakdown = self.get_cost_breakdown_by_category("v2x-mesh")
        compute_cost = v2x_breakdown.get("compute", 0)

        if compute_cost > 2000:  # >$2k/month on compute
            suggestions.append(
                {
                    "service": "v2x-mesh",
                    "priority": "medium",
                    "category": "compute",
                    "current_cost": compute_cost,
                    "potential_savings": compute_cost * 0.2,  # 20% savings
                    "action": "Use spot instances for non-critical pods, implement auto-scaling",
                    "roi": "Medium - 20% reduction in compute costs",
                }
            )

        # Analyze storage
        storage_cost = sum(
            self.get_cost_breakdown_by_category(s).get("storage", 0)
            for s in ["gemini-ingestion", "v2x-mesh", "platform-monitoring"]
        )

        if storage_cost > 100:  # >$100/month on storage
            suggestions.append(
                {
                    "service": "platform",
                    "priority": "low",
                    "category": "storage",
                    "current_cost": storage_cost,
                    "potential_savings": storage_cost * 0.5,  # 50% savings
                    "action": "Implement data lifecycle: Archive to Nearline after 30 days, Coldline after 90 days",
                    "roi": "High - 50% reduction in storage costs",
                }
            )

        return suggestions

    def get_revenue_requirements(self, margin_percent: float = 70.0) -> dict[str, float]:
        """Calculate required revenue to maintain margin"""
        monthly_costs = self.get_monthly_costs()
        total_cost = monthly_costs.get("total", 0.0)

        # Required revenue for target margin
        required_revenue = total_cost / (1 - margin_percent / 100)

        return {
            "total_monthly_cost": total_cost,
            "target_margin_percent": margin_percent,
            "required_monthly_revenue": required_revenue,
            "required_mrr": required_revenue,
            "per_vehicle_revenue_1k": required_revenue / 1000,  # Assuming 1k vehicles
            "per_vehicle_revenue_10k": required_revenue / 10000,  # At scale
        }

    def export_cost_report(self) -> dict:
        """Export comprehensive cost report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "budget_status": self.get_budget_status(),
            "monthly_costs": self.get_monthly_costs(),
            "alerts": [
                {
                    "type": a.alert_type,
                    "service": a.service,
                    "current": a.current_spend,
                    "budget": a.budget,
                    "utilization": a.utilization_percent,
                    "recommendation": a.recommendation,
                }
                for a in self.get_alerts()
            ],
            "cost_breakdown": {
                service: self.get_cost_breakdown_by_category(service)
                for service in self.budgets
                if service != "total"
            },
            "optimization_suggestions": self.get_optimization_suggestions(),
            "revenue_requirements": self.get_revenue_requirements(),
        }


# Example usage
if __name__ == "__main__":
    tracker = CostTracker()

    # Record some costs
    tracker.record_cost(
        "gemini-ingestion", CostCategory.API_CALLS, 2.50, "Gemini API - 1000 items analyzed"
    )
    tracker.record_cost("v2x-mesh", CostCategory.COMPUTE, 100.0, "GKE compute - daily cost")
    tracker.record_cost(
        "gemini-ingestion", CostCategory.EXTERNAL_SERVICES, 0.50, "NewsAPI - 100 requests"
    )

    # Get report
    report = tracker.export_cost_report()

    print("Cost Report:")
    print(f"  Monthly Costs: ${report['monthly_costs'].get('total', 0):.2f}")
    print(f"  Alerts: {len(report['alerts'])}")
    for alert in report["alerts"]:
        print(
            f"    - [{alert['type'].upper()}] {alert['service']}: {alert['utilization']:.0f}% of budget"
        )
    print(f"  Optimization Suggestions: {len(report['optimization_suggestions'])}")
    for suggestion in report["optimization_suggestions"]:
        print(
            f"    - {suggestion['action']} (potential savings: ${suggestion['potential_savings']:.2f}/month)"
        )

    # Revenue requirements
    rev_req = report["revenue_requirements"]
    print("\n  Required Revenue:")
    print(f"    - Monthly: ${rev_req['required_monthly_revenue']:.2f}")
    print(f"    - Per Vehicle (1k): ${rev_req['per_vehicle_revenue_1k']:.2f}/month")
    print(f"    - Per Vehicle (10k): ${rev_req['per_vehicle_revenue_10k']:.2f}/month")
