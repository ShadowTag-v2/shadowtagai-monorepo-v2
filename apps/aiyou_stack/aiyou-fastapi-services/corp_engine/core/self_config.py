# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Self-Configuring AI Engine
===========================
Auto-configures platform based on customer profile.
Ports itself to emerging frameworks/LLMs/protocols.
"""

import hashlib
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class IndustryVertical(StrEnum):
    AEROSPACE = "aerospace"
    DEFENSE = "defense"
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    LEGAL = "legal"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    TECHNOLOGY = "technology"
    GOVERNMENT = "government"
    EDUCATION = "education"


class CompanySize(StrEnum):
    STARTUP = "startup"  # <50 employees
    SMB = "smb"  # 50-500 employees
    ENTERPRISE = "enterprise"  # 500-5000 employees
    MEGA = "mega"  # >5000 employees


class AIConfigProfile(BaseModel):
    """AI-generated configuration for tenant"""

    generated_at: datetime
    config_hash: str

    # Model routing
    primary_model: str
    fallback_model: str
    specialized_models: dict[str, str]  # task -> model mapping

    # Intel filtering
    intel_categories: list[str]
    intel_priority_keywords: list[str]
    excluded_sources: list[str]

    # Compliance
    data_residency: str
    encryption_standard: str
    audit_level: str

    # Integration recommendations
    recommended_integrations: list[str]
    api_protocols: list[str]

    # Update strategy
    auto_update_enabled: bool
    update_schedule: str
    rollback_enabled: bool


class SelfConfiguringEngine:
    """AI engine that auto-configures based on tenant profile.
    Monitors emerging tech and auto-ports to new frameworks.
    """

    # Industry-specific configurations
    INDUSTRY_CONFIGS = {
        IndustryVertical.AEROSPACE: {
            "intel_categories": [
                "materials",
                "propulsion",
                "avionics",
                "regulations",
                "supply_chain",
            ],
            "compliance": ["ITAR", "AS9100"],
            "specialized_models": {"technical_analysis": "gemini-3-pro", "docs": "gemini-3-flash"},
            "data_residency": "us-only",
        },
        IndustryVertical.DEFENSE: {
            "intel_categories": [
                "cybersecurity",
                "weapons_systems",
                "logistics",
                "contracts",
                "clearance",
            ],
            "compliance": ["FedRAMP", "CMMC", "ITAR"],
            "specialized_models": {
                "classification": "gemini-3-pro",
                "summarization": "gemini-3-flash",
            },
            "data_residency": "us-gov",
        },
        IndustryVertical.FINTECH: {
            "intel_categories": ["regulations", "blockchain", "payments", "fraud", "market_trends"],
            "compliance": ["SOC2", "PCI-DSS", "GDPR"],
            "specialized_models": {"risk_analysis": "gemini-3-pro", "reporting": "gemini-3-flash"},
            "data_residency": "multi-region",
        },
        IndustryVertical.HEALTHCARE: {
            "intel_categories": [
                "clinical_trials",
                "devices",
                "pharma",
                "regulations",
                "ai_diagnostics",
            ],
            "compliance": ["HIPAA", "FDA", "GDPR"],
            "specialized_models": {"medical_nlp": "gemini-3-pro", "docs": "gemini-3-flash"},
            "data_residency": "hipaa-compliant",
        },
        IndustryVertical.LEGAL: {
            "intel_categories": [
                "case_law",
                "regulations",
                "contracts",
                "compliance",
                "litigation",
            ],
            "compliance": ["ABA", "GDPR", "attorney-client"],
            "specialized_models": {"legal_analysis": "gemini-3-pro", "research": "gemini-3-flash"},
            "data_residency": "jurisdiction-aware",
        },
    }

    # Size-based configurations
    SIZE_CONFIGS = {
        CompanySize.STARTUP: {
            "api_rate_limit": 100,
            "update_schedule": "weekly",
            "audit_level": "basic",
        },
        CompanySize.SMB: {
            "api_rate_limit": 500,
            "update_schedule": "daily",
            "audit_level": "standard",
        },
        CompanySize.ENTERPRISE: {
            "api_rate_limit": 2000,
            "update_schedule": "continuous",
            "audit_level": "comprehensive",
        },
        CompanySize.MEGA: {
            "api_rate_limit": -1,  # unlimited
            "update_schedule": "real-time",
            "audit_level": "forensic",
        },
    }

    # Emerging tech watchlist (auto-updated from Nightly Intel Pipeline)
    EMERGING_TECH_WATCHLIST = [
        "gemini-3-pro",  # 1501 Elo, Deep Think mode
        "gemini-3-flash",  # Fast inference
        "claude-opus-4.5",  # Current conversation
        "gpt-5",
        "llama-4",
        "mistral-large-3",
        "deepseek-r2",
        "qwen-3",
    ]

    def __init__(self):
        self.config_cache: dict[str, AIConfigProfile] = {}

    def generate_config(
        self,
        tenant_id: str,
        industry: IndustryVertical,
        company_size: CompanySize,
        tech_stack: list[str],
        regulatory_requirements: list[str],
    ) -> AIConfigProfile:
        """Generate AI configuration based on tenant profile"""
        # Get base configs
        industry_config = self.INDUSTRY_CONFIGS.get(
            industry,
            self.INDUSTRY_CONFIGS[IndustryVertical.TECHNOLOGY],
        )
        size_config = self.SIZE_CONFIGS.get(company_size, self.SIZE_CONFIGS[CompanySize.SMB])

        # Merge regulatory requirements
        all_compliance = list(set(industry_config.get("compliance", []) + regulatory_requirements))

        # Determine data residency
        data_residency = industry_config.get("data_residency", "multi-region")
        if "FedRAMP" in all_compliance or "ITAR" in all_compliance:
            data_residency = "us-gov"
        elif "HIPAA" in all_compliance:
            data_residency = "hipaa-compliant"

        # Generate config hash for versioning
        config_input = (
            f"{tenant_id}:{industry}:{company_size}:{sorted(tech_stack)}:{sorted(all_compliance)}"
        )
        config_hash = hashlib.sha256(config_input.encode()).hexdigest()[:16]

        # Determine recommended integrations based on tech stack
        integrations = self._recommend_integrations(tech_stack, industry)

        config = AIConfigProfile(
            generated_at=datetime.utcnow(),
            config_hash=config_hash,
            primary_model="gemini-3-pro",
            fallback_model="gemini-3-flash",
            specialized_models=industry_config.get("specialized_models", {}),
            intel_categories=industry_config.get("intel_categories", []),
            intel_priority_keywords=self._extract_keywords(industry, tech_stack),
            excluded_sources=[],
            data_residency=data_residency,
            encryption_standard="AES-256-GCM",
            audit_level=size_config.get("audit_level", "standard"),
            recommended_integrations=integrations,
            api_protocols=["REST", "gRPC", "WebSocket"],
            auto_update_enabled=True,
            update_schedule=size_config.get("update_schedule", "daily"),
            rollback_enabled=True,
        )

        self.config_cache[tenant_id] = config
        return config

    def _recommend_integrations(
        self,
        tech_stack: list[str],
        industry: IndustryVertical,
    ) -> list[str]:
        """Recommend integrations based on tech stack"""
        integrations = []

        # Common integrations
        integrations.append("slack")
        integrations.append("github")

        # Tech-specific
        if "kubernetes" in tech_stack or "k8s" in tech_stack:
            integrations.extend(["argocd", "prometheus", "grafana"])
        if "python" in tech_stack:
            integrations.append("jupyter")
        if "terraform" in tech_stack:
            integrations.append("terraform-cloud")
        if "aws" in tech_stack:
            integrations.append("aws-bedrock")
        if "gcp" in tech_stack:
            integrations.append("vertex-ai")

        # Industry-specific
        if industry == IndustryVertical.LEGAL:
            integrations.extend(["clio", "westlaw", "lexisnexis"])
        elif industry == IndustryVertical.FINTECH:
            integrations.extend(["plaid", "stripe", "bloomberg"])
        elif industry == IndustryVertical.HEALTHCARE:
            integrations.extend(["epic-fhir", "cerner"])

        return list(set(integrations))

    def _extract_keywords(self, industry: IndustryVertical, tech_stack: list[str]) -> list[str]:
        """Extract priority keywords for intel filtering"""
        keywords = list(tech_stack)

        # Industry keywords
        if industry == IndustryVertical.AEROSPACE:
            keywords.extend(["nasa", "faa", "spacex", "boeing", "lockheed"])
        elif industry == IndustryVertical.DEFENSE:
            keywords.extend(["dod", "darpa", "pentagon", "nist", "cisa"])
        elif industry == IndustryVertical.FINTECH:
            keywords.extend(["sec", "fed", "basel", "swift", "defi"])

        return keywords

    async def check_for_updates(self, tenant_id: str) -> dict[str, Any]:
        """Check for new frameworks/LLMs that tenant should adopt"""
        current_config = self.config_cache.get(tenant_id)
        if not current_config:
            return {"updates_available": False}

        # Check against emerging tech watchlist
        updates = []
        for tech in self.EMERGING_TECH_WATCHLIST:
            if tech not in current_config.primary_model:
                updates.append(
                    {
                        "type": "model_upgrade",
                        "from": current_config.primary_model,
                        "to": tech,
                        "recommendation": f"Consider upgrading to {tech} for improved performance",
                    },
                )

        return {
            "updates_available": len(updates) > 0,
            "updates": updates,
            "auto_port_available": True,
        }

    async def auto_port(self, tenant_id: str, target_framework: str) -> dict[str, Any]:
        """Auto-port tenant configuration to new framework"""
        current_config = self.config_cache.get(tenant_id)
        if not current_config:
            return {"success": False, "error": "No config found"}

        # Create new config with updated framework
        new_config = current_config.model_copy()
        new_config.primary_model = target_framework
        new_config.generated_at = datetime.utcnow()

        self.config_cache[tenant_id] = new_config

        return {
            "success": True,
            "previous_model": current_config.primary_model,
            "new_model": target_framework,
            "config_hash": new_config.config_hash,
        }


# Global instance
self_config_engine = SelfConfiguringEngine()
