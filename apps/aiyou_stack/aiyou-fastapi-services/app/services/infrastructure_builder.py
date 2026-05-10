"""Infrastructure Builder Service
Core service for designing cloud architecture
"""

import uuid

from app.models.infrastructure import (
    CloudProvider,
    InfrastructureComponent,
    InfrastructureDesignRequest,
    InfrastructureDesignResponse,
    WorkloadType,
)


class InfrastructureBuilderService:
    """Cloud infrastructure expert optimizing for scale and cost"""

    def design_architecture(
        self,
        request: InfrastructureDesignRequest,
    ) -> InfrastructureDesignResponse:
        """Design cloud architecture based on requirements"""
        design_id = str(uuid.uuid4())
        components = self._generate_components(request)
        total_cost = sum(comp.estimated_monthly_cost for comp in components)

        recommendations = self._generate_recommendations(request, components, total_cost)
        scalability_score = self._calculate_scalability_score(request, components)
        cost_efficiency_score = self._calculate_cost_efficiency(request, total_cost)

        return InfrastructureDesignResponse(
            design_id=design_id,
            name=request.name,
            cloud_provider=request.cloud_provider,
            components=components,
            recommendations=recommendations,
            estimated_monthly_cost=total_cost,
            scalability_score=scalability_score,
            cost_efficiency_score=cost_efficiency_score,
        )

    def _generate_components(
        self,
        request: InfrastructureDesignRequest,
    ) -> list[InfrastructureComponent]:
        """Generate infrastructure components based on workload type"""
        if request.workload_type == WorkloadType.WEB_APP:
            return self._web_app_components(request)
        if request.workload_type == WorkloadType.MICROSERVICES:
            return self._microservices_components(request)
        if request.workload_type == WorkloadType.API:
            return self._api_components(request)
        if request.workload_type == WorkloadType.DATA_PIPELINE:
            return self._data_pipeline_components(request)
        return self._default_components(request)

    def _web_app_components(
        self,
        request: InfrastructureDesignRequest,
    ) -> list[InfrastructureComponent]:
        """Components for web application workload"""
        provider = request.cloud_provider
        components = []

        # Load Balancer
        lb_service = {
            CloudProvider.AWS: "Application Load Balancer",
            CloudProvider.GCP: "Cloud Load Balancing",
            CloudProvider.AZURE: "Azure Load Balancer",
        }

        components.append(
            InfrastructureComponent(
                name="Load Balancer",
                type="load_balancer",
                provider_service=lb_service[provider],
                configuration={
                    "https_enabled": True,
                    "health_check": True,
                    "cross_zone": request.high_availability,
                },
                estimated_monthly_cost=25.0,
            ),
        )

        # Compute instances
        instance_count = max(
            2 if request.high_availability else 1,
            request.expected_traffic // 1000,
        )

        compute_service = {
            CloudProvider.AWS: "EC2",
            CloudProvider.GCP: "Compute Engine",
            CloudProvider.AZURE: "Virtual Machines",
        }

        components.append(
            InfrastructureComponent(
                name="Application Servers",
                type="compute",
                provider_service=compute_service[provider],
                configuration={
                    "instance_type": "t3.medium"
                    if provider == CloudProvider.AWS
                    else "n1-standard-2",
                    "instance_count": instance_count,
                    "auto_scaling": True,
                    "min_instances": instance_count,
                    "max_instances": instance_count * 3,
                },
                estimated_monthly_cost=50.0 * instance_count,
            ),
        )

        # Database
        db_service = {
            CloudProvider.AWS: "RDS (PostgreSQL)",
            CloudProvider.GCP: "Cloud SQL",
            CloudProvider.AZURE: "Azure Database for PostgreSQL",
        }

        components.append(
            InfrastructureComponent(
                name="Database",
                type="database",
                provider_service=db_service[provider],
                configuration={
                    "engine": "postgresql",
                    "version": "15",
                    "instance_class": "db.t3.medium",
                    "multi_az": request.high_availability,
                    "backup_retention": 7,
                    "storage_gb": 100,
                },
                estimated_monthly_cost=150.0 if request.high_availability else 75.0,
            ),
        )

        # Object Storage
        storage_service = {
            CloudProvider.AWS: "S3",
            CloudProvider.GCP: "Cloud Storage",
            CloudProvider.AZURE: "Blob Storage",
        }

        components.append(
            InfrastructureComponent(
                name="Object Storage",
                type="storage",
                provider_service=storage_service[provider],
                configuration={"versioning": True, "encryption": True, "lifecycle_policy": True},
                estimated_monthly_cost=10.0,
            ),
        )

        # CDN
        cdn_service = {
            CloudProvider.AWS: "CloudFront",
            CloudProvider.GCP: "Cloud CDN",
            CloudProvider.AZURE: "Azure CDN",
        }

        components.append(
            InfrastructureComponent(
                name="CDN",
                type="cdn",
                provider_service=cdn_service[provider],
                configuration={
                    "ssl_certificate": True,
                    "compression": True,
                    "cache_behavior": "optimized",
                },
                estimated_monthly_cost=20.0,
            ),
        )

        return components

    def _microservices_components(
        self,
        request: InfrastructureDesignRequest,
    ) -> list[InfrastructureComponent]:
        """Components for microservices architecture"""
        provider = request.cloud_provider
        components = []

        # Kubernetes cluster
        k8s_service = {
            CloudProvider.AWS: "EKS",
            CloudProvider.GCP: "GKE",
            CloudProvider.AZURE: "AKS",
        }

        node_count = max(3, request.expected_traffic // 500)

        components.append(
            InfrastructureComponent(
                name="Kubernetes Cluster",
                type="kubernetes",
                provider_service=k8s_service[provider],
                configuration={
                    "node_count": node_count,
                    "node_type": "n1-standard-4",
                    "auto_scaling": True,
                    "min_nodes": node_count,
                    "max_nodes": node_count * 2,
                    "network_policy": True,
                },
                estimated_monthly_cost=150.0 * node_count,
            ),
        )

        # Service mesh
        components.append(
            InfrastructureComponent(
                name="Service Mesh",
                type="service_mesh",
                provider_service="Istio",
                configuration={"mTLS": True, "telemetry": True, "circuit_breaking": True},
                estimated_monthly_cost=50.0,
            ),
        )

        # Container registry
        registry_service = {
            CloudProvider.AWS: "ECR",
            CloudProvider.GCP: "Container Registry",
            CloudProvider.AZURE: "Azure Container Registry",
        }

        components.append(
            InfrastructureComponent(
                name="Container Registry",
                type="registry",
                provider_service=registry_service[provider],
                configuration={
                    "vulnerability_scanning": True,
                    "geo_replication": request.high_availability,
                },
                estimated_monthly_cost=20.0,
            ),
        )

        return components

    def _api_components(
        self,
        request: InfrastructureDesignRequest,
    ) -> list[InfrastructureComponent]:
        """Components for API workload"""
        provider = request.cloud_provider
        components = []

        # API Gateway
        gateway_service = {
            CloudProvider.AWS: "API Gateway",
            CloudProvider.GCP: "Cloud Endpoints",
            CloudProvider.AZURE: "API Management",
        }

        components.append(
            InfrastructureComponent(
                name="API Gateway",
                type="api_gateway",
                provider_service=gateway_service[provider],
                configuration={
                    "rate_limiting": True,
                    "authentication": "OAuth2",
                    "caching": True,
                    "throttling": True,
                },
                estimated_monthly_cost=30.0,
            ),
        )

        # Add compute and database similar to web app
        components.extend(self._web_app_components(request)[1:4])

        return components

    def _data_pipeline_components(
        self,
        request: InfrastructureDesignRequest,
    ) -> list[InfrastructureComponent]:
        """Components for data pipeline workload"""
        provider = request.cloud_provider
        components = []

        # Data warehouse
        dw_service = {
            CloudProvider.AWS: "Redshift",
            CloudProvider.GCP: "BigQuery",
            CloudProvider.AZURE: "Synapse Analytics",
        }

        components.append(
            InfrastructureComponent(
                name="Data Warehouse",
                type="data_warehouse",
                provider_service=dw_service[provider],
                configuration={"node_type": "dc2.large", "node_count": 2, "encryption": True},
                estimated_monthly_cost=300.0,
            ),
        )

        # ETL service
        etl_service = {
            CloudProvider.AWS: "Glue",
            CloudProvider.GCP: "Dataflow",
            CloudProvider.AZURE: "Data Factory",
        }

        components.append(
            InfrastructureComponent(
                name="ETL Pipeline",
                type="etl",
                provider_service=etl_service[provider],
                configuration={"workers": 10, "schedule": "hourly"},
                estimated_monthly_cost=100.0,
            ),
        )

        return components

    def _default_components(
        self,
        request: InfrastructureDesignRequest,
    ) -> list[InfrastructureComponent]:
        """Default components for unknown workload types"""
        return self._web_app_components(request)

    def _generate_recommendations(
        self,
        request: InfrastructureDesignRequest,
        components: list[InfrastructureComponent],
        total_cost: float,
    ) -> list[str]:
        """Generate architecture recommendations"""
        recommendations = []

        # Budget recommendations
        if request.budget_limit and total_cost > request.budget_limit:
            over_budget = total_cost - request.budget_limit
            recommendations.append(
                f"⚠️ Estimated cost ${total_cost:.2f} exceeds budget by ${over_budget:.2f}. "
                "Consider using spot instances or reserved pricing.",
            )

        # High availability recommendations
        if request.high_availability:
            recommendations.append("✅ Multi-AZ deployment configured for high availability")
        else:
            recommendations.append(
                "💡 Consider enabling high availability for production workloads",
            )

        # Scaling recommendations
        if request.expected_traffic > 1000:
            recommendations.append("📈 Auto-scaling enabled to handle traffic spikes efficiently")

        # Security recommendations
        recommendations.append("🔒 Enable encryption at rest and in transit for all data stores")
        recommendations.append("🔐 Implement least-privilege IAM policies and network segmentation")

        # Cost optimization
        recommendations.append(
            "💰 Use reserved instances for baseline capacity (up to 70% savings)",
        )
        recommendations.append("📊 Enable cloud cost monitoring and set up budget alerts")

        return recommendations

    def _calculate_scalability_score(
        self,
        request: InfrastructureDesignRequest,
        components: list[InfrastructureComponent],
    ) -> float:
        """Calculate scalability score (0-10)"""
        score = 5.0  # Base score

        # Check for auto-scaling
        has_autoscaling = any(comp.configuration.get("auto_scaling") for comp in components)
        if has_autoscaling:
            score += 2.0

        # Check for load balancing
        has_lb = any(comp.type == "load_balancer" for comp in components)
        if has_lb:
            score += 1.5

        # High availability adds to scalability
        if request.high_availability:
            score += 1.5

        return min(10.0, score)

    def _calculate_cost_efficiency(
        self,
        request: InfrastructureDesignRequest,
        total_cost: float,
    ) -> float:
        """Calculate cost efficiency score (0-10)"""
        # Calculate cost per expected RPS
        cost_per_rps = total_cost / max(1, request.expected_traffic)

        # Lower cost per RPS is better
        if cost_per_rps < 0.05:
            return 10.0
        if cost_per_rps < 0.1:
            return 8.0
        if cost_per_rps < 0.2:
            return 6.0
        if cost_per_rps < 0.5:
            return 4.0
        return 2.0
