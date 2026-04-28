# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Technical Architecture & Stack Configuration"""

from dataclasses import dataclass, field
from enum import Enum


class DeploymentEnvironment(Enum):
    """Deployment environment types"""

    DEV = "development"
    STAGING = "staging"
    PROD = "production"


@dataclass
class TechStack:
    """Core technology stack configuration"""

    # Core Language
    core_language: str = "Python 3.11+"

    # Orchestration
    orchestration: list[str] = field(default_factory=lambda: ["LangGraph", "CrewAI"])

    # LLM Provider
    llm_provider: str = "OpenAI GPT-4 Turbo"

    # Memory Layer
    memory_layer: dict[str, str] = field(
        default_factory=lambda: {
            "long_term": "Pinecone",
            "short_term": "Redis",
            "episodic": "Custom PostgreSQL schema",
        },
    )

    # Deployment
    deployment: dict[str, str] = field(
        default_factory=lambda: {
            "dev": "Vertex AI Workbench",
            "prod": "GKE (Google Kubernetes Engine)",
        },
    )

    # Security
    security: list[str] = field(
        default_factory=lambda: [
            "GCP Secret Manager",
            "Encryption at rest/transit",
            "SOC 2 Type II (Month 18 target)",
        ],
    )

    # Monitoring
    monitoring: str = "Datadog + custom dashboards"


@dataclass
class AgentDesignPattern:
    """Agent architecture pattern"""

    # Framework
    framework: str = "ReAct (Reason + Act)"

    # Memory Types
    memory_types: list[str] = field(default_factory=lambda: ["short_term", "long_term", "episodic"])

    # Guardrails
    guardrails: list[str] = field(
        default_factory=lambda: [
            "Human-in-loop checkpoints",
            "Task manager loops",
            "Hallucination detection",
            "Output validation",
        ],
    )

    # Tools
    tools: str = "Custom API wrappers (Notion, Slack, HubSpot, Apollo, etc.)"


@dataclass
class DevelopmentConstraints:
    """Code development constraints and standards"""

    max_function_length: int = 20  # lines
    external_libraries: str = "Approval required"
    test_coverage: float = 0.80  # 80% minimum on critical paths
    output_format: str = "monospace for all technical content"

    # Shipping Philosophy
    shipping_philosophy: list[str] = field(
        default_factory=lambda: [
            "Stupid simple > fancy",
            "Ship fast > perfect",
            "Real utility > general-purpose",
            "Evidence-only decisions",
        ],
    )

    # Guardrails
    guardrails: list[str] = field(
        default_factory=lambda: [
            "No feature without user interview (n≥10)",
            "No new vertical without $5K+ pilot demand",
            "No hire without founder doing job 3+ months first",
        ],
    )


@dataclass
class APIIntegration:
    """Third-party API integration specs"""

    name: str
    purpose: str
    authentication: str
    rate_limits: str = "TBD"
    cost_per_call: float = 0.0
    sla: str = "99.9%"


class IntegrationRegistry:
    """Registry of all external API integrations"""

    INTEGRATIONS = {
        "apollo": APIIntegration(
            name="Apollo.io",
            purpose="Lead scraping and enrichment",
            authentication="API Key",
            rate_limits="1000 calls/day (free tier)",
            cost_per_call=0.01,
        ),
        "openai": APIIntegration(
            name="OpenAI GPT-4 Turbo",
            purpose="Core LLM inference",
            authentication="API Key",
            rate_limits="10K TPM (tokens per minute)",
            cost_per_call=0.01,  # $0.01/1K tokens avg
        ),
        "pinecone": APIIntegration(
            name="Pinecone",
            purpose="Vector database for long-term memory",
            authentication="API Key",
            rate_limits="Serverless (auto-scale)",
            cost_per_call=0.0001,
        ),
        "redis": APIIntegration(
            name="Redis Cloud",
            purpose="Short-term context cache",
            authentication="Connection string",
            rate_limits="Unlimited (dedicated instance)",
            cost_per_call=0.0,
        ),
        "hubspot": APIIntegration(
            name="HubSpot CRM",
            purpose="CRM integration for sales agent",
            authentication="OAuth 2.0",
            rate_limits="100 calls/10 seconds",
            cost_per_call=0.0,
        ),
        "slack": APIIntegration(
            name="Slack API",
            purpose="Notifications and human-in-loop alerts",
            authentication="OAuth 2.0",
            rate_limits="1 call/second per workspace",
            cost_per_call=0.0,
        ),
        "notion": APIIntegration(
            name="Notion API",
            purpose="Knowledge base and documentation storage",
            authentication="Internal Integration Token",
            rate_limits="3 requests/second",
            cost_per_call=0.0,
        ),
    }


@dataclass
class SecurityConfig:
    """Security configuration and standards"""

    # Secret Management
    secret_manager: str = "GCP Secret Manager"

    # Encryption
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    tls_version: str = "1.3"

    # Compliance Targets
    soc2_target_month: int = 18
    iso27001_target: bool = False
    gdpr_compliant: bool = True
    hipaa_compliant: bool = False

    # Audit
    audit_logging: bool = True
    audit_retention_days: int = 365

    # Access Control
    rbac_enabled: bool = True
    mfa_required: bool = True


def get_tech_stack_config() -> dict:
    """Generate complete tech stack configuration"""
    stack = TechStack()
    pattern = AgentDesignPattern()
    constraints = DevelopmentConstraints()
    security = SecurityConfig()

    return {
        "stack": {
            "language": stack.core_language,
            "orchestration": stack.orchestration,
            "llm": stack.llm_provider,
            "memory": stack.memory_layer,
            "deployment": stack.deployment,
            "security": stack.security,
            "monitoring": stack.monitoring,
        },
        "agent_pattern": {
            "framework": pattern.framework,
            "memory_types": pattern.memory_types,
            "guardrails": pattern.guardrails,
            "tools": pattern.tools,
        },
        "development": {
            "constraints": {
                "max_function_length": constraints.max_function_length,
                "external_libraries": constraints.external_libraries,
                "test_coverage": constraints.test_coverage,
                "output_format": constraints.output_format,
            },
            "philosophy": constraints.shipping_philosophy,
            "guardrails": constraints.guardrails,
        },
        "integrations": {
            name: {
                "name": integration.name,
                "purpose": integration.purpose,
                "authentication": integration.authentication,
                "rate_limits": integration.rate_limits,
                "cost_per_call": integration.cost_per_call,
                "sla": integration.sla,
            }
            for name, integration in IntegrationRegistry.INTEGRATIONS.items()
        },
        "security": {
            "secret_management": security.secret_manager,
            "encryption": {
                "at_rest": security.encryption_at_rest,
                "in_transit": security.encryption_in_transit,
                "tls_version": security.tls_version,
            },
            "compliance": {
                "soc2_target_month": security.soc2_target_month,
                "iso27001": security.iso27001_target,
                "gdpr": security.gdpr_compliant,
                "hipaa": security.hipaa_compliant,
            },
            "audit": {
                "enabled": security.audit_logging,
                "retention_days": security.audit_retention_days,
            },
            "access": {"rbac": security.rbac_enabled, "mfa": security.mfa_required},
        },
    }


if __name__ == "__main__":
    import json

    config = get_tech_stack_config()
    print(json.dumps(config, indent=2))
