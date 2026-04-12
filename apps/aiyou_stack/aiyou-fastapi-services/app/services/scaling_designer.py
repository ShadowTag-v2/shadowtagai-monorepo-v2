"""
Scaling Designer Service
Provides auto-scaling recommendations and configurations
"""

from typing import Any

from app.models.infrastructure import ScalingRecommendation


class ScalingDesignerService:
    """Service for designing scalable infrastructure"""

    def analyze_and_recommend(self, request: dict[str, Any]) -> ScalingRecommendation:
        """Analyze workload and provide scaling recommendations"""

        workload_type = request.get("workload_type", "web_app")
        expected_traffic = request.get("expected_traffic", 100)
        current_instances = request.get("current_instances", 2)
        peak_traffic_multiplier = request.get("peak_traffic_multiplier", 3)

        # Calculate scaling parameters
        min_instances = max(2, current_instances)  # At least 2 for HA
        max_instances = self._calculate_max_instances(expected_traffic, peak_traffic_multiplier)

        # CPU utilization target based on workload
        target_cpu = self._get_target_cpu_utilization(workload_type)

        # Cooldown periods
        scale_up_cooldown = 60  # 1 minute - respond quickly to increased load
        scale_down_cooldown = 300  # 5 minutes - be conservative when scaling down

        recommendations = self._generate_scaling_recommendations(
            workload_type, expected_traffic, min_instances, max_instances, target_cpu
        )

        return ScalingRecommendation(
            auto_scaling_enabled=True,
            min_instances=min_instances,
            max_instances=max_instances,
            target_cpu_utilization=target_cpu,
            scale_up_cooldown=scale_up_cooldown,
            scale_down_cooldown=scale_down_cooldown,
            recommendations=recommendations,
        )

    def _calculate_max_instances(self, expected_traffic: int, peak_multiplier: float) -> int:
        """Calculate maximum instances needed for peak traffic"""

        # Assume each instance can handle ~500 RPS comfortably
        rps_per_instance = 500

        peak_traffic = expected_traffic * peak_multiplier
        max_needed = int(peak_traffic / rps_per_instance) + 1

        # Cap at reasonable limits
        return min(max_needed, 50)

    def _get_target_cpu_utilization(self, workload_type: str) -> int:
        """Get target CPU utilization based on workload type"""

        targets = {
            "web_app": 70,  # Conservative for web apps
            "api": 75,  # APIs can handle higher CPU
            "microservices": 70,
            "data_pipeline": 80,  # Batch processing can use more CPU
            "ml_training": 85,  # ML workloads can max out CPU
            "batch_processing": 80,
        }

        return targets.get(workload_type, 70)

    def _generate_scaling_recommendations(
        self,
        workload_type: str,
        expected_traffic: int,
        min_instances: int,
        max_instances: int,
        target_cpu: int,
    ) -> list[str]:
        """Generate detailed scaling recommendations"""

        recommendations = []

        # Basic configuration
        recommendations.append(
            f"✅ Configured for {min_instances}-{max_instances} instances with {target_cpu}% CPU target"
        )

        # Traffic-based recommendations
        if expected_traffic > 1000:
            recommendations.append(
                "📈 High traffic expected: Consider using multiple availability zones for distribution"
            )
            recommendations.append(
                "🔄 Implement connection pooling and request queuing to handle traffic spikes"
            )

        # Scaling strategy
        recommendations.append(
            "⚡ Quick scale-up (60s cooldown) to handle sudden traffic increases"
        )
        recommendations.append("🐌 Conservative scale-down (300s cooldown) to prevent flapping")

        # Metric recommendations
        recommendations.append(
            "📊 Monitor additional metrics: Request latency, error rate, and queue depth"
        )

        # Advanced recommendations
        if workload_type in ["microservices", "api"]:
            recommendations.append("🎯 Consider predictive scaling based on time-of-day patterns")
            recommendations.append("🔧 Implement circuit breakers and rate limiting for resilience")

        # Cost optimization
        if max_instances > 10:
            recommendations.append("💰 Use a mix of on-demand and spot instances to reduce costs")
            recommendations.append(
                f"💡 Reserve capacity for {min_instances} baseline instances (up to 70% savings)"
            )

        # Testing recommendations
        recommendations.append("🧪 Perform load testing to validate scaling configuration")
        recommendations.append("📉 Set up alerts for scaling events and performance degradation")

        return recommendations
