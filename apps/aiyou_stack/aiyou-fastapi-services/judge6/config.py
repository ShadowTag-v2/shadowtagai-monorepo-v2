# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Configuration management for Judge 6 governance system."""

from dataclasses import dataclass, field


@dataclass
class RiskPatternConfig:
    """Configuration for risk pattern matching."""

    # ATP 5-19 Risk Assessment Patterns
    RA_4_PATTERNS: list[str] = field(
        default_factory=lambda: [
            "weapons",
            "explosives",
            "bioweapon",
            "chemical weapon",
            "nuclear",
            "poison",
            "assassination",
            "terrorism",
            "child abuse",
            "csam",
            "exploit minor",
        ],
    )

    RA_3_PATTERNS: list[str] = field(
        default_factory=lambda: [
            "malware",
            "ransomware",
            "exploit",
            "vulnerability",
            "ddos",
            "phishing",
            "credential theft",
            "unauthorized access",
            "bypass security",
            "jailbreak",
            "prompt injection",
        ],
    )

    RA_2_PATTERNS: list[str] = field(
        default_factory=lambda: [
            "spam",
            "misinformation",
            "impersonation",
            "trademark violation",
            "copyright infringement",
            "unlicensed medical advice",
        ],
    )


@dataclass
class AxiomValidationConfig:
    """Configuration for axiom validation patterns."""

    # A1: PURPOSE_REQUIRED indicators
    PURPOSE_INDICATORS: list[str] = field(
        default_factory=lambda: [
            "purpose:",
            "goal:",
            "objective:",
            "i want to",
            "i need to",
            "task:",
            "request:",
            "trying to",
        ],
    )

    # A2: HARM_PROHIBITION patterns
    HARM_PATTERNS: list[str] = field(
        default_factory=lambda: [
            "harm",
            "damage",
            "hurt",
            "injure",
            "kill",
            "destroy",
            "attack",
            "exploit",
            "abuse",
        ],
    )

    # A6: NO_USER_OVERRIDE patterns
    OVERRIDE_PATTERNS: list[str] = field(
        default_factory=lambda: [
            "ignore previous",
            "override",
            "disregard",
            "forget the rules",
            "ignore instructions",
            "bypass",
            "disable safety",
        ],
    )


@dataclass
class ProvenanceConfig:
    """Configuration for ShadowTag 2.0 provenance system."""

    # Hash algorithm (defaults to SHA-256)
    HASH_ALGORITHM: str = "sha256"

    # Signature algorithm (simplified for demo)
    SIGNATURE_ALGORITHM: str = "sha256"

    # Enable full cryptographic signing (vs. demo mode)
    ENABLE_PKI: bool = False

    # PKI key paths (if enabled)
    PRIVATE_KEY_PATH: str = ""
    PUBLIC_KEY_PATH: str = ""


@dataclass
class Cor.Claude_Code_6Config:
    """Master configuration for Judge 6 system."""

    # Instance identifier
    COR_INSTANCE_ID: str = "cor-001"

    # Test coverage target
    TEST_COVERAGE_TARGET: float = 0.98

    # Sub-configurations
    risk_patterns: RiskPatternConfig = field(default_factory=RiskPatternConfig)
    axiom_validation: AxiomValidationConfig = field(default_factory=AxiomValidationConfig)
    provenance: ProvenanceConfig = field(default_factory=ProvenanceConfig)

    # Logging configuration
    ENABLE_DETAILED_LOGGING: bool = True
    LOG_REASONING_CHAINS: bool = True
    LOG_PROVENANCE_STAMPS: bool = True


# Global configuration instance
_config: Cor.Claude_Code_6Config = Cor.Claude_Code_6Config()


def get_config() -> Cor.Claude_Code_6Config:
    """Get global configuration instance."""
    return _config


def set_config(config: Cor.Claude_Code_6Config) -> None:
    """Set global configuration instance."""
    global _config
    _config = config
