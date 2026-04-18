"""Core data models and type definitions for Judge #6 governance system."""

from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    """ATP 5-19 Risk Assessment Levels

    Maps to military risk assessment framework for operational security.
    """

    RA_1 = "Negligible"  # Minimal impact, routine operations
    RA_2 = "Low"  # Limited impact, easily mitigated
    RA_3 = "Moderate"  # Significant impact, requires intervention
    RA_4 = "Catastrophic"  # Severe consequences, mission failure

    def __lt__(self, other: "RiskLevel") -> bool:
        """Enable risk level comparison."""
        order = {RiskLevel.RA_1: 1, RiskLevel.RA_2: 2, RiskLevel.RA_3: 3, RiskLevel.RA_4: 4}
        return order[self] < order[other]

    def __le__(self, other: "RiskLevel") -> bool:
        """Enable risk level comparison."""
        return self == other or self < other


@dataclass(frozen=True)
class ConstitutionalAxiom:
    """Immutable governance rules per Cor.53 specification.

    Constitutional axioms form the foundation of the governance system
    and cannot be overridden by user input or preferences.

    Attributes:
        axiom_id: Unique identifier (e.g., "A1", "A2")
        name: Human-readable axiom name
        rule: Detailed rule description
        enforcement_level: Enforcement strictness level
        violation_consequence: Risk level if violated

    """

    axiom_id: str
    name: str
    rule: str
    enforcement_level: str  # "IMMUTABLE", "STRICT", "MONITORED"
    violation_consequence: RiskLevel

    def __hash__(self) -> int:
        """Make axiom hashable for use in sets."""
        return hash(self.axiom_id)


@dataclass
class ProvenanceStamp:
    """ShadowTag 2.0 cryptographic provenance for decisions.

    Provides tamper-evident audit trail for all governance decisions
    with cryptographic verification capabilities.

    Attributes:
        timestamp: ISO 8601 formatted timestamp
        purpose_hash: SHA-256 hash of declared purpose
        reasoning_chain_hash: SHA-256 hash of reasoning chain
        risk_level: Assessed risk level
        cor_instance_id: Unique Cor instance identifier
        axioms_verified: List of verified axiom IDs
        signature: Cryptographic signature

    """

    timestamp: str
    purpose_hash: str
    reasoning_chain_hash: str
    risk_level: RiskLevel
    cor_instance_id: str
    axioms_verified: list[str]
    signature: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "purpose_hash": self.purpose_hash,
            "reasoning_chain_hash": self.reasoning_chain_hash,
            "risk_level": self.risk_level.value,
            "cor_instance_id": self.cor_instance_id,
            "axioms_verified": self.axioms_verified,
            "signature": self.signature,
        }


@dataclass
class JudgmentDecision:
    """Result of Judge #6 governance evaluation.

    Represents the complete decision output including risk assessment,
    reasoning, violations, and cryptographic provenance.

    Attributes:
        approved: Whether request is approved for processing
        risk_level: Assessed ATP 5-19 risk level
        reasoning: Detailed reasoning chain
        violated_axioms: List of constitutional axioms violated
        provenance_stamp: Optional cryptographic provenance
        metadata: Additional decision metadata

    """

    approved: bool
    risk_level: RiskLevel
    reasoning: str
    violated_axioms: list[ConstitutionalAxiom]
    provenance_stamp: ProvenanceStamp | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "approved": self.approved,
            "risk_level": self.risk_level.value,
            "reasoning": self.reasoning,
            "violated_axioms": [
                {"axiom_id": ax.axiom_id, "name": ax.name, "rule": ax.rule}
                for ax in self.violated_axioms
            ],
            "provenance_stamp": self.provenance_stamp.to_dict() if self.provenance_stamp else None,
            "metadata": self.metadata,
        }


@dataclass
class GovernanceWeakness:
    """Documented vulnerability in AI governance system.

    Used for competitive analysis and test vector generation.

    Attributes:
        provider: AI provider name
        model: Specific model identifier
        weakness_type: Category of weakness
        description: Detailed description
        attack_vector: How weakness can be exploited
        risk_level: Associated risk level
        mitigation: How PNKLN mitigates this weakness
        evidence_source: Source of weakness documentation

    """

    provider: str
    model: str
    weakness_type: str
    description: str
    attack_vector: str
    risk_level: RiskLevel
    mitigation: str
    evidence_source: str


@dataclass
class TestVector:
    """Test case for governance validation.

    Represents a single test case in the adversarial test suite.

    Attributes:
        test_id: Unique test identifier
        category: Test category
        attack_type: Type of attack simulated
        user_input: Test input string
        expected_risk_level: Expected risk assessment
        expected_approved: Expected approval decision
        description: Test description
        targets_weakness: Optional weakness being tested

    """

    test_id: str
    category: str
    attack_type: str
    user_input: str
    expected_risk_level: RiskLevel
    expected_approved: bool
    description: str = ""
    targets_weakness: GovernanceWeakness | None = None
