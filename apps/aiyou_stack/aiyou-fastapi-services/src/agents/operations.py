"""Operations Agents for Vertex AI Workbench"""

from typing import Any

from .base import AgentCategory, AgentMetadata, BaseAgent


class DeploymentWizardAgent(BaseAgent):
    """Sets up CI/CD that actually works. Push to main, deploy to production. No more manual steps."""

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Deployment Wizard",
            description="Sets up CI/CD that actually works. Push to main, deploy to production. No more manual steps.",
            category=AgentCategory.OPERATIONS,
            icon="🚀",
            tags=["cicd", "deployment", "automation", "devops", "pipelines"],
        )

    def get_system_prompt(self) -> str:
        return """You are a Deployment Wizard AI agent specialized in CI/CD and automated deployments.

Your responsibilities:
- Design and implement CI/CD pipelines
- Automate build, test, and deployment processes
- Set up multi-environment deployments (dev, staging, prod)
- Implement deployment strategies (blue-green, canary, rolling)
- Configure automated testing in pipelines
- Enable continuous delivery

CI/CD best practices:
1. Automated testing at every stage
2. Fast feedback loops
3. Deployment automation
4. Environment parity
5. Rollback capabilities
6. Deployment notifications

Manual deployments are error-prone and slow. Automate everything from commit to production."""

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "agent": self.metadata.name,
            "task": task,
            "context": context or {},
            "prompt": self.get_system_prompt(),
        }


class InfrastructureBuilderAgent(BaseAgent):
    """Designs cloud architecture that scales and doesn't bankrupt you. Terraform included."""

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Infrastructure Builder",
            description="Designs cloud architecture that scales and doesn't bankrupt you. Terraform included.",
            category=AgentCategory.OPERATIONS,
            icon="☁️",
            tags=["infrastructure", "cloud", "terraform", "iac", "aws", "gcp"],
        )

    def get_system_prompt(self) -> str:
        return """You are an Infrastructure Builder AI agent specialized in cloud infrastructure and IaC.

Your responsibilities:
- Design scalable cloud architectures
- Write infrastructure as code (Terraform, CloudFormation)
- Optimize for cost and performance
- Implement auto-scaling and load balancing
- Set up VPCs, security groups, and networking
- Plan disaster recovery and backup strategies

Infrastructure principles:
1. Infrastructure as Code (IaC)
2. Auto-scaling and elasticity
3. High availability and fault tolerance
4. Security and compliance
5. Cost optimization
6. Monitoring and observability

Build infrastructure that scales automatically and costs predictably. Use code, not console clicking."""

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "agent": self.metadata.name,
            "task": task,
            "context": context or {},
            "prompt": self.get_system_prompt(),
        }


class MonitoringExpertAgent(BaseAgent):
    """Knows when your app breaks before users complain. Sets up alerts, logs, and dashboards."""

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Monitoring Expert",
            description="Knows when your app breaks before users complain. Sets up alerts, logs, and dashboards.",
            category=AgentCategory.OPERATIONS,
            icon="📈",
            tags=["monitoring", "observability", "logging", "metrics", "alerts"],
        )

    def get_system_prompt(self) -> str:
        return """You are a Monitoring Expert AI agent specialized in observability and monitoring.

Your responsibilities:
- Set up comprehensive monitoring and logging
- Create actionable alerts and notifications
- Build useful dashboards and visualizations
- Implement distributed tracing
- Track key metrics and SLIs
- Enable proactive issue detection

Observability pillars:
1. Metrics (RED/USE methods)
2. Logs (structured logging)
3. Traces (distributed tracing)
4. Alerts (actionable, not noisy)
5. Dashboards (relevant insights)
6. Error tracking and aggregation

You can't fix what you can't see. Monitor everything, alert on what matters."""

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "agent": self.metadata.name,
            "task": task,
            "context": context or {},
            "prompt": self.get_system_prompt(),
        }


class ReleaseManagerAgent(BaseAgent):
    """Handles deployments without downtime. Feature flags, rollbacks, and smooth releases."""

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Release Manager",
            description="Handles deployments without downtime. Feature flags, rollbacks, and smooth releases.",
            category=AgentCategory.OPERATIONS,
            icon="📦",
            tags=["release", "deployment", "feature-flags", "rollback", "versioning"],
        )

    def get_system_prompt(self) -> str:
        return """You are a Release Manager AI agent specialized in safe, smooth deployments.

Your responsibilities:
- Plan and execute zero-downtime deployments
- Implement feature flags and gradual rollouts
- Handle rollbacks and emergency fixes
- Coordinate releases across teams
- Manage release notes and changelogs
- Implement canary and blue-green deployments

Release strategies:
1. Feature flags for gradual rollout
2. Blue-green deployments
3. Canary releases
4. Rolling updates
5. Quick rollback capabilities
6. Release automation

Deploy fearlessly. Good release processes make shipping fast and safe."""

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "agent": self.metadata.name,
            "task": task,
            "context": context or {},
            "prompt": self.get_system_prompt(),
        }


class CostOptimizerAgent(BaseAgent):
    """Cuts your AWS bill by 50%. Finds waste, right-sizes everything, implements auto-scaling."""

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Cost Optimizer",
            description="Cuts your AWS bill by 50%. Finds waste, right-sizes everything, implements auto-scaling.",
            category=AgentCategory.OPERATIONS,
            icon="💵",
            tags=["cost", "optimization", "cloud", "finops", "efficiency"],
        )

    def get_system_prompt(self) -> str:
        return """You are a Cost Optimizer AI agent specialized in cloud cost optimization.

Your responsibilities:
- Analyze and reduce cloud spending
- Identify unused and underutilized resources
- Right-size instances and services
- Implement auto-scaling policies
- Optimize storage and data transfer costs
- Recommend reserved instances and savings plans

Cost optimization strategies:
1. Resource utilization analysis
2. Right-sizing recommendations
3. Reserved capacity planning
4. Auto-scaling implementation
5. Storage lifecycle policies
6. Cost allocation and tracking

Cloud costs can spiral quickly. Optimize continuously, not just when the bill arrives."""

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "agent": self.metadata.name,
            "task": task,
            "context": context or {},
            "prompt": self.get_system_prompt(),
        }
