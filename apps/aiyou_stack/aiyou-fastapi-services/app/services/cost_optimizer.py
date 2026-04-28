# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Cost Optimizer Service
Analyzes and optimizes cloud infrastructure costs
"""

from app.models.infrastructure import (
    CloudProvider,
    CostBreakdown,
    CostEstimateRequest,
    CostEstimateResponse,
)


class CostOptimizerService:
    """Service for cost estimation and optimization"""

    # Pricing data (simplified, per month)
    PRICING = {
        CloudProvider.AWS: {
            "compute": {"t3.small": 15.0, "t3.medium": 30.0, "t3.large": 60.0},
            "database": {"db.t3.small": 25.0, "db.t3.medium": 50.0, "db.t3.large": 100.0},
            "storage": 0.023,  # per GB
            "load_balancer": 20.0,
            "cdn": 0.085,  # per GB transferred
        },
        CloudProvider.GCP: {
            "compute": {"n1-standard-1": 25.0, "n1-standard-2": 50.0, "n1-standard-4": 100.0},
            "database": {"db-n1-standard-1": 30.0, "db-n1-standard-2": 60.0},
            "storage": 0.020,  # per GB
            "load_balancer": 18.0,
            "cdn": 0.08,  # per GB transferred
        },
        CloudProvider.AZURE: {
            "compute": {"B1s": 8.0, "B2s": 35.0, "D2s_v3": 70.0},
            "database": {"Basic": 15.0, "Standard": 50.0, "Premium": 150.0},
            "storage": 0.018,  # per GB
            "load_balancer": 22.0,
            "cdn": 0.087,  # per GB transferred
        },
    }

    def calculate_costs(self, request: CostEstimateRequest) -> CostEstimateResponse:
        """Calculate detailed cost estimate with optimization opportunities"""
        breakdown = self._calculate_breakdown(request)
        total_cost = sum(item.monthly_cost for item in breakdown)

        optimization_opportunities = self._identify_optimizations(request, breakdown)
        potential_savings = self._calculate_savings(optimization_opportunities, total_cost)

        return CostEstimateResponse(
            total_monthly_cost=total_cost,
            breakdown=breakdown,
            optimization_opportunities=optimization_opportunities,
            potential_savings=potential_savings,
        )

    def _calculate_breakdown(self, request: CostEstimateRequest) -> list[CostBreakdown]:
        """Calculate cost breakdown by component"""
        breakdown = []
        pricing = self.PRICING.get(request.cloud_provider, self.PRICING[CloudProvider.AWS])

        for component in request.components:
            component_type = component.get("type", "unknown")
            cost = 0.0
            cost_drivers = []

            if component_type == "compute":
                instance_type = component.get("instance_type", "t3.medium")
                instance_count = component.get("instance_count", 1)
                hours_ratio = request.hours_per_month / 730  # Normalize to full month

                base_cost = pricing["compute"].get(instance_type, 30.0)
                cost = base_cost * instance_count * hours_ratio

                cost_drivers.append(f"{instance_count} x {instance_type} instances")
                cost_drivers.append(f"{request.hours_per_month} hours/month")

            elif component_type == "database":
                instance_class = component.get("instance_class", "db.t3.medium")
                multi_az = component.get("multi_az", False)
                storage_gb = component.get("storage_gb", 100)

                base_cost = pricing["database"].get(instance_class, 50.0)
                cost = base_cost * (2 if multi_az else 1)
                cost += storage_gb * pricing["storage"]

                cost_drivers.append(f"{instance_class} instance")
                if multi_az:
                    cost_drivers.append("Multi-AZ deployment")
                cost_drivers.append(f"{storage_gb}GB storage")

            elif component_type == "storage":
                storage_gb = component.get("storage_gb", 1000)
                cost = storage_gb * pricing["storage"]
                cost_drivers.append(f"{storage_gb}GB storage")

            elif component_type == "load_balancer":
                cost = pricing["load_balancer"]
                cost_drivers.append("Application Load Balancer")

            elif component_type == "cdn":
                data_transfer_gb = component.get("data_transfer_gb", 1000)
                cost = data_transfer_gb * pricing["cdn"]
                cost_drivers.append(f"{data_transfer_gb}GB data transfer")

            else:
                # Default estimate for unknown types
                cost = 50.0
                cost_drivers.append("Estimated cost")

            breakdown.append(
                CostBreakdown(
                    component=component.get("name", component_type),
                    monthly_cost=cost,
                    cost_drivers=cost_drivers,
                ),
            )

        return breakdown

    def _identify_optimizations(
        self,
        request: CostEstimateRequest,
        breakdown: list[CostBreakdown],
    ) -> list[str]:
        """Identify cost optimization opportunities"""
        optimizations = []

        # Compute optimizations
        compute_costs = [b for b in breakdown if "instance" in b.component.lower()]
        if compute_costs:
            total_compute = sum(c.monthly_cost for c in compute_costs)
            if total_compute > 100:
                optimizations.append(
                    f"💰 Reserved Instances: Save up to 70% on ${total_compute:.2f}/month compute costs "
                    "(1-year commitment: 40% savings, 3-year: 70% savings)",
                )
                optimizations.append(
                    "⚡ Spot Instances: Use for non-critical workloads to save up to 90% "
                    "(potential savings: ${total_compute * 0.7:.2f}/month)",
                )

        # Storage optimizations
        storage_costs = [b for b in breakdown if "storage" in b.component.lower()]
        if storage_costs:
            total_storage = sum(c.monthly_cost for c in storage_costs)
            if total_storage > 50:
                optimizations.append(
                    "📦 Storage Tiering: Move infrequently accessed data to cheaper tiers "
                    "(potential savings: ${total_storage * 0.3:.2f}/month)",
                )

        # Database optimizations
        db_costs = [b for b in breakdown if "database" in b.component.lower()]
        if db_costs:
            total_db = sum(c.monthly_cost for c in db_costs)
            if total_db > 100:
                optimizations.append(
                    "🗄️ Database Right-sizing: Analyze actual usage to downsize instances "
                    "(typical savings: 20-40%)",
                )
                optimizations.append(
                    "⏰ Database Scheduling: Stop non-production databases during off-hours "
                    "(potential savings: ${total_db * 0.5:.2f}/month for dev/test)",
                )

        # General optimizations
        optimizations.append("🔍 Enable Cost Explorer and set up budget alerts to track spending")

        if request.hours_per_month < 730:
            optimizations.append(
                f"⏸️ Auto-shutdown: You're only running {request.hours_per_month} hours/month. "
                "Ensure auto-shutdown is configured for non-business hours",
            )

        optimizations.append(
            "🏷️ Tagging Strategy: Implement resource tagging for better cost allocation and tracking",
        )

        return optimizations

    def _calculate_savings(self, optimizations: list[str], total_cost: float) -> float:
        """Calculate estimated potential savings from optimizations"""
        # Conservative estimate: 20-30% savings from listed optimizations
        base_savings_rate = 0.25

        # Adjust based on cost scale
        if total_cost > 1000:
            base_savings_rate = 0.30  # More opportunities at scale
        elif total_cost < 100:
            base_savings_rate = 0.15  # Fewer opportunities at small scale

        return total_cost * base_savings_rate
