# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Technical Architecture & Agent Design Patterns
Production-ready stack for AI agent deployment
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Environment(Enum):
    """Deployment environments"""

    DEV = "development"
    STAGING = "staging"
    PROD = "production"


@dataclass
class TechStack:
    """Core technology stack configuration"""

    core_language: str = "Python 3.11+"
    orchestration: list[str] = field(default_factory=lambda: ["LangGraph", "CrewAI"])
    llm_provider: str = "OpenAI GPT-4 Turbo"

    memory_layer: dict[str, str] = field(
        default_factory=lambda: {
            "long_term": "Pinecone",
            "short_term": "Redis",
            "episodic": "Custom PostgreSQL schema",
        },
    )

    deployment: dict[str, str] = field(
        default_factory=lambda: {
            "dev": "Vertex AI Workbench",
            "prod": "GKE (Google Kubernetes Engine)",
        },
    )

    security: list[str] = field(
        default_factory=lambda: [
            "GCP Secret Manager",
            "Encryption at rest/transit",
            "SOC 2 Type II (Month 18 target)",
        ],
    )

    monitoring: str = "Datadog + custom dashboards"
    cloud_provider: str = "Google Cloud Platform (exclusive)"

    def get_deployment_target(self, env: Environment) -> str:
        """Get deployment target for environment"""
        if env == Environment.DEV:
            return self.deployment["dev"]
        return self.deployment["prod"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "language": self.core_language,
            "orchestration": self.orchestration,
            "llm": self.llm_provider,
            "memory": self.memory_layer,
            "deployment": self.deployment,
            "security": self.security,
            "monitoring": self.monitoring,
            "cloud": self.cloud_provider,
        }


@dataclass
class AgentDesignPattern:
    """AI agent architecture & guardrails"""

    framework: str = "ReAct (Reason + Act)"
    memory_types: list[str] = field(default_factory=lambda: ["short_term", "long_term", "episodic"])

    guardrails: list[str] = field(
        default_factory=lambda: [
            "Human-in-loop checkpoints",
            "Task manager loops",
            "Hallucination detection",
            "Output validation",
        ],
    )

    tools: str = "Custom API wrappers (Notion, Slack, HubSpot, Apollo, etc.)"

    def to_dict(self) -> dict[str, Any]:
        return {
            "framework": self.framework,
            "memory_types": self.memory_types,
            "guardrails": self.guardrails,
            "tools": self.tools,
        }


@dataclass
class IntegrationCatalog:
    """Third-party API integrations by vertical"""

    sales_automation: list[str] = field(
        default_factory=lambda: [
            "Apollo.io (lead scraping)",
            "LinkedIn Sales Navigator",
            "Gmail API",
            "HubSpot CRM",
        ],
    )

    content_repurposing: list[str] = field(
        default_factory=lambda: [
            "YouTube API",
            "Twitter/X API",
            "LinkedIn Publishing",
            "Medium API",
        ],
    )

    customer_support: list[str] = field(
        default_factory=lambda: ["Zendesk", "Intercom", "Slack", "Help Scout"],
    )

    meeting_intelligence: list[str] = field(
        default_factory=lambda: ["Zoom API", "Google Meet", "Calendly", "Notion"],
    )

    market_research: list[str] = field(
        default_factory=lambda: ["Crunchbase", "SimilarWeb", "SEMrush API", "Google Trends"],
    )

    workflow_orchestration: list[str] = field(
        default_factory=lambda: [
            "Zapier Webhooks",
            "Make (Integromat)",
            "Airtable",
            "Google Sheets API",
        ],
    )


# Singleton instances
TECH_STACK = TechStack()
AGENT_DESIGN = AgentDesignPattern()
INTEGRATIONS = IntegrationCatalog()
