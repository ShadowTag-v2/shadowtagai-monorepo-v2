"""
Infrastructure Analysis Skill - pinkln Agent Architecture System

This skill provides comprehensive analysis capabilities for infrastructure components
in the PNKLN Core Stack™, including Judge #6 (enforcement/validation) and Gemini
Ingestion Layer (intelligence collection).

Capabilities:
- Comparative system analysis
- Performance metric evaluation
- Architecture assessment
- Cost optimization analysis
- Quality gate validation
- Ethical compliance review
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SystemType(Enum):
    """Types of infrastructure systems in PNKLN Stack."""

    JUDGE = "judge"  # Enforcement/validation systems
    INGESTION = "ingestion"  # Data collection/intelligence gathering
    INFERENCE = "inference"  # ML/AI inference systems
    STORAGE = "storage"  # Data persistence layers
    ORCHESTRATION = "orchestration"  # Workflow/scheduling systems


class MetricType(Enum):
    """Categories of metrics to analyze."""

    PERFORMANCE = "performance"  # Latency, throughput, runtime
    QUALITY = "quality"  # Accuracy, coverage, relevance
    COST = "cost"  # Financial efficiency
    COMPLIANCE = "compliance"  # Ethical, legal, standards
    INTEGRATION = "integration"  # System connectivity


@dataclass
class SystemSpec:
    """Specification for an infrastructure system."""

    name: str
    system_type: SystemType
    architecture: str
    key_metrics: dict[str, Any]
    integration_points: list[str]
    unique_features: list[str]
    cost_model: dict[str, Any]
    quality_focus: list[str]
    confidence_target: float = 0.7


@dataclass
class AnalysisResult:
    """Result of infrastructure analysis."""

    system_name: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    optimizations: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    confidence_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class InfrastructureAnalysisSkill:
    """
    Skill for analyzing infrastructure systems in PNKLN Core Stack™.

    This skill applies the pinkln philosophy to infrastructure analysis:
    - Question Everything: Challenge architectural assumptions
    - Obsess Over Details: Deep metric analysis
    - Plan Like Da Vinci: Strategic optimization planning
    - Simplify Ruthlessly: Identify unnecessary complexity
    - Iterate Relentlessly: Continuous improvement cycles
    """

    # Judge #6 Specification
    JUDGE_SIX_SPEC = SystemSpec(
        name="Judge #6",
        system_type=SystemType.JUDGE,
        architecture="Hybrid Gemini+PyTorch on GKE",
        key_metrics={
            "latency_p99": "≤90ms",
            "throughput": "high",
            "block_rate": "percentage",
            "coverage": "98%",
        },
        integration_points=[
            "Calls services in 4 namespaces",
            "Real-time validation",
            "Enforcement decisions",
        ],
        unique_features=[
            "ATP 5-19 compliance",
            "JR validation",
            "False positive/negative rate tracking",
        ],
        cost_model={"model": "per_validation", "unit": "API calls"},
        quality_focus=["False positive rate", "False negative rate", "Validation accuracy"],
        confidence_target=0.7,
    )

    # Gemini Ingestion Layer Specification
    GEMINI_INGESTION_SPEC = SystemSpec(
        name="Gemini Ingestion Layer",
        system_type=SystemType.INGESTION,
        architecture="GKE CronJob Multi-Container",
        key_metrics={
            "items_per_day": "volume",
            "sources": "diversity",
            "cost_per_item": "efficiency",
            "runtime": "~45 min/night",
        },
        integration_points=[
            "Called by services in 4 namespaces",
            "Batch processing",
            "Data distribution",
        ],
        unique_features=[
            "Ethical crawling (robots.txt, rate limiting)",
            "Tier classification (Tier 1/2/3)",
            "Multi-source coverage (YouTube, Twitter, News)",
            "AM briefing delivery",
        ],
        cost_model={"model": "monthly_operational", "amount": 77, "currency": "USD"},
        quality_focus=["Relevance", "Timeliness", "Completeness", "Source diversity"],
        confidence_target=0.6,  # Lower for pre-prod specs-only
    )

    def __init__(self):
        """Initialize the Infrastructure Analysis Skill."""
        self.analysis_history = []

    def analyze_system(
        self, spec: SystemSpec, focus_areas: list[MetricType] | None = None
    ) -> AnalysisResult:
        """
        Analyze a single infrastructure system.

        Args:
            spec: System specification to analyze
            focus_areas: Optional list of metric types to focus on

        Returns:
            AnalysisResult with findings and recommendations
        """
        result = AnalysisResult(system_name=spec.name)

        # Default to all metric types if not specified
        if focus_areas is None:
            focus_areas = list(MetricType)

        # Analyze based on system type
        if spec.system_type == SystemType.JUDGE:
            result = self._analyze_judge_system(spec, focus_areas)
        elif spec.system_type == SystemType.INGESTION:
            result = self._analyze_ingestion_system(spec, focus_areas)

        # Store in history
        self.analysis_history.append(result)

        return result

    def _analyze_judge_system(
        self, spec: SystemSpec, focus_areas: list[MetricType]
    ) -> AnalysisResult:
        """Analyze a judge/validation system."""
        result = AnalysisResult(system_name=spec.name)

        # Performance analysis
        if MetricType.PERFORMANCE in focus_areas:
            result.strengths.append("Low latency target (p99 ≤90ms) enables real-time enforcement")
            result.recommendations.append("Monitor p99 latency trends to detect degradation early")

        # Quality analysis
        if MetricType.QUALITY in focus_areas:
            result.strengths.append("High coverage target (98%) ensures comprehensive validation")
            result.weaknesses.append(
                "False positive/negative tracking requires continuous calibration"
            )
            result.recommendations.append("Implement A/B testing for validation rule changes")

        # Architecture analysis
        result.strengths.append(
            "Hybrid Gemini+PyTorch architecture balances NLP and ML capabilities"
        )
        result.optimizations.append("Consider caching validation results for repeated patterns")

        # Integration analysis
        if MetricType.INTEGRATION in focus_areas:
            result.risks.append(
                "Calling services in 4 namespaces creates coupling—monitor dependencies"
            )
            result.recommendations.append("Implement circuit breakers for downstream service calls")

        result.confidence_score = 0.75
        result.metadata = {
            "system_type": "judge",
            "analysis_date": "2024-11-15",
            "focus_areas": [f.value for f in focus_areas],
        }

        return result

    def _analyze_ingestion_system(
        self, spec: SystemSpec, focus_areas: list[MetricType]
    ) -> AnalysisResult:
        """Analyze an ingestion/collection system."""
        result = AnalysisResult(system_name=spec.name)

        # Performance analysis
        if MetricType.PERFORMANCE in focus_areas:
            result.strengths.append("45-minute nightly runtime is efficient for batch processing")
            result.optimizations.append("Consider parallelization in GKE to reduce runtime further")
            result.recommendations.append(
                "Track runtime trends to detect data volume growth impact"
            )

        # Cost analysis
        if MetricType.COST in focus_areas:
            result.strengths.append(
                f"Monthly operational cost of ${spec.cost_model['amount']} is economical"
            )
            result.recommendations.append("Analyze cost sensitivity if item volume doubles")
            result.optimizations.append(
                "Implement cost per tier to optimize high-value data collection"
            )

        # Compliance analysis
        if MetricType.COMPLIANCE in focus_areas:
            result.strengths.append(
                "Ethical crawling (robots.txt, rate limiting) reduces legal risks"
            )
            result.recommendations.append("Audit compliance logs regularly to ensure no violations")
            result.recommendations.append("Document transparency measures for stakeholder trust")

        # Quality analysis
        if MetricType.QUALITY in focus_areas:
            result.strengths.append(
                "Multi-dimensional quality focus (relevance, timeliness, completeness)"
            )
            result.weaknesses.append("Pre-prod specs limit confidence (target 60% vs 70% in prod)")
            result.recommendations.append(
                "Implement quality scoring per tier to prioritize high-value items"
            )
            result.optimizations.append(
                "Add source diversity metrics to prevent over-reliance on single sources"
            )

        # Architecture analysis
        result.strengths.append(
            "GKE CronJob multi-container approach enables scalability and fault tolerance"
        )
        result.optimizations.append(
            "Evaluate resource allocation per container for cost efficiency"
        )

        # Integration analysis
        if MetricType.INTEGRATION in focus_areas:
            result.strengths.append(
                "Being called by 4 namespaces positions ingestion as foundational layer"
            )
            result.risks.append("Downstream dependencies on ingestion quality—ensure SLAs")
            result.recommendations.append("Implement data quality gates before distribution")

        # Unique features analysis
        result.strengths.append("Tier classification enables strategic resource allocation")
        result.recommendations.append(
            "Analyze tier distribution to ensure 80/20 rule (80% value from 20% data)"
        )

        result.confidence_score = 0.65
        result.metadata = {
            "system_type": "ingestion",
            "analysis_date": "2024-11-15",
            "focus_areas": [f.value for f in focus_areas],
            "pre_production": True,
        }

        return result

    def comparative_analysis(self, spec1: SystemSpec, spec2: SystemSpec) -> dict[str, Any]:
        """
        Perform comparative analysis between two systems.

        Args:
            spec1: First system specification
            spec2: Second system specification

        Returns:
            Dictionary with comparative insights
        """
        analysis1 = self.analyze_system(spec1)
        analysis2 = self.analyze_system(spec2)

        comparison = {
            "systems": [spec1.name, spec2.name],
            "role_contrast": self._analyze_role_contrast(spec1, spec2),
            "metric_comparison": self._compare_metrics(spec1, spec2),
            "architecture_comparison": self._compare_architectures(spec1, spec2),
            "integration_analysis": self._analyze_integration_relationship(spec1, spec2),
            "combined_recommendations": self._generate_combined_recommendations(
                analysis1, analysis2
            ),
        }

        return comparison

    def _analyze_role_contrast(self, spec1: SystemSpec, spec2: SystemSpec) -> dict[str, str]:
        """Analyze the contrasting roles of two systems."""
        role_map = {
            SystemType.JUDGE: "Reactive validator - enforcement and validation",
            SystemType.INGESTION: "Proactive collector - intelligence gathering",
        }

        return {
            spec1.name: role_map.get(spec1.system_type, "Unknown role"),
            spec2.name: role_map.get(spec2.system_type, "Unknown role"),
            "relationship": self._determine_relationship(spec1.system_type, spec2.system_type),
        }

    def _determine_relationship(self, type1: SystemType, type2: SystemType) -> str:
        """Determine the relationship between two system types."""
        if type1 == SystemType.INGESTION and type2 == SystemType.JUDGE:
            return "Ingestion feeds Judge - upstream data collection for downstream validation"
        elif type1 == SystemType.JUDGE and type2 == SystemType.INGESTION:
            return (
                "Judge validates Ingestion output - downstream enforcement of upstream collection"
            )
        else:
            return "Parallel systems with potential integration points"

    def _compare_metrics(self, spec1: SystemSpec, spec2: SystemSpec) -> dict[str, Any]:
        """Compare metrics between systems."""
        return {
            "focus_shift": {
                spec1.name: list(spec1.key_metrics.keys()),
                spec2.name: list(spec2.key_metrics.keys()),
                "insight": "Metrics reflect system roles - speed vs. volume/diversity",
            },
            "cost_model": {
                spec1.name: spec1.cost_model.get("model", "unknown"),
                spec2.name: spec2.cost_model.get("model", "unknown"),
                "insight": "Per-operation vs. monthly totals reflects batch vs. real-time",
            },
        }

    def _compare_architectures(self, spec1: SystemSpec, spec2: SystemSpec) -> dict[str, Any]:
        """Compare architectural approaches."""
        return {
            spec1.name: {
                "architecture": spec1.architecture,
                "suitability": "Optimized for its role",
            },
            spec2.name: {
                "architecture": spec2.architecture,
                "suitability": "Optimized for its role",
            },
            "insights": [
                "Different architectures reflect different operational patterns",
                "Both leverage GKE for scalability",
                "Hybrid AI vs. CronJob shows real-time vs. batch approaches",
            ],
        }

    def _analyze_integration_relationship(
        self, spec1: SystemSpec, spec2: SystemSpec
    ) -> dict[str, Any]:
        """Analyze how systems integrate."""
        return {
            "data_flow": "Potential handoff between ingestion and validation",
            "recommendations": [
                "Analyze handoff points for optimization",
                "Ensure data format compatibility",
                "Monitor end-to-end latency from ingestion to validation",
            ],
            "potential_bottlenecks": [
                "Data volume from ingestion may overwhelm judge capacity",
                "Quality gates in ingestion should filter before judge",
            ],
        }

    def _generate_combined_recommendations(
        self, analysis1: AnalysisResult, analysis2: AnalysisResult
    ) -> list[str]:
        """Generate recommendations for the combined system."""
        return [
            "Implement end-to-end monitoring across both systems",
            "Create shared quality metrics to align goals",
            "Optimize data handoff between ingestion and validation",
            "Consider unified cost tracking for total PNKLN stack TCO",
            "Establish SLAs that account for both systems' characteristics",
            "Test failure modes where one system impacts the other",
        ]

    def generate_gemini_prompt(
        self, spec: SystemSpec, include_sections: list[str] | None = None
    ) -> str:
        """
        Generate a Gemini 2.0 Pro analysis prompt for a system.

        Args:
            spec: System specification
            include_sections: Optional list of sections to include

        Returns:
            Formatted prompt string for Gemini analysis
        """
        sections = include_sections or [
            "architecture",
            "metrics",
            "integration",
            "quality",
            "compliance",
            "optimization",
        ]

        prompt = f"""# {spec.name} Infrastructure Analysis

## System Overview
- **Type**: {spec.system_type.value}
- **Architecture**: {spec.architecture}
- **Confidence Target**: {spec.confidence_target * 100}%

## Analysis Objectives
Perform a comprehensive analysis of the {spec.name} system, applying rigorous
engineering principles and the pinkln philosophy of excellence.

"""

        if "architecture" in sections:
            prompt += f"""
### Architecture Analysis
Analyze the {spec.architecture} architecture:
- Scalability characteristics
- Fault tolerance mechanisms
- Resource allocation efficiency
- Technology choices and trade-offs
"""

        if "metrics" in sections:
            prompt += f"""
### Key Metrics Evaluation
Evaluate these metrics:
{self._format_metrics(spec.key_metrics)}

For each metric:
- Is the target appropriate for the system's role?
- What optimizations could improve it?
- What are the monitoring recommendations?
"""

        if "integration" in sections:
            prompt += f"""
### Integration Analysis
Integration points:
{self._format_list(spec.integration_points)}

Analyze:
- Coupling and cohesion
- Failure modes and resilience
- API contract clarity
"""

        if "quality" in sections:
            prompt += f"""
### Quality Focus Assessment
Quality dimensions:
{self._format_list(spec.quality_focus)}

Evaluate:
- Are these the right quality dimensions?
- How can quality be measured objectively?
- What gates should be implemented?
"""

        if "compliance" in sections and spec.system_type == SystemType.INGESTION:
            prompt += """
### Ethical Compliance Review
Evaluate compliance mechanisms:
- robots.txt adherence
- Rate limiting implementation
- Transparency measures
- Legal risk mitigation
"""

        if "optimization" in sections:
            prompt += """
### Optimization Opportunities
Identify:
1. Performance optimizations
2. Cost reduction opportunities
3. Quality improvements
4. Architectural simplifications

Apply the pinkln principle: "Simplify Ruthlessly"
"""

        prompt += f"""
## Output Requirements
Provide:
1. **Strengths** (3-5 key strengths)
2. **Weaknesses** (2-4 areas for improvement)
3. **Recommendations** (5-7 actionable items)
4. **Risk Assessment** (potential failure modes)
5. **Confidence Score** (0-1, targeting ≥{spec.confidence_target})

**Analysis Philosophy**: Apply the pinkln core directives - Question Everything,
Obsess Over Details, Simplify Ruthlessly, Iterate to Excellence.
"""

        return prompt

    def _format_metrics(self, metrics: dict[str, Any]) -> str:
        """Format metrics dictionary for prompt."""
        lines = []
        for key, value in metrics.items():
            lines.append(f"- **{key}**: {value}")
        return "\n".join(lines)

    def _format_list(self, items: list[str]) -> str:
        """Format list for prompt."""
        return "\n".join(f"- {item}" for item in items)


# Convenience functions


def analyze_judge_six() -> AnalysisResult:
    """Quick analysis of Judge #6 system."""
    skill = InfrastructureAnalysisSkill()
    return skill.analyze_system(skill.JUDGE_SIX_SPEC)


def analyze_gemini_ingestion() -> AnalysisResult:
    """Quick analysis of Gemini Ingestion Layer."""
    skill = InfrastructureAnalysisSkill()
    return skill.analyze_system(skill.GEMINI_INGESTION_SPEC)


def compare_judge_and_ingestion() -> dict[str, Any]:
    """Compare Judge #6 and Gemini Ingestion Layer."""
    skill = InfrastructureAnalysisSkill()
    return skill.comparative_analysis(skill.JUDGE_SIX_SPEC, skill.GEMINI_INGESTION_SPEC)


if __name__ == "__main__":
    # Demo usage
    skill = InfrastructureAnalysisSkill()

    print("=" * 70)
    print("PNKLN Infrastructure Analysis Skill Demo")
    print("=" * 70)

    # Analyze Judge #6
    print("\n--- Judge #6 Analysis ---")
    judge_result = skill.analyze_system(skill.JUDGE_SIX_SPEC)
    print(f"Strengths: {len(judge_result.strengths)}")
    print(f"Recommendations: {len(judge_result.recommendations)}")
    print(f"Confidence: {judge_result.confidence_score:.2%}")

    # Analyze Gemini Ingestion
    print("\n--- Gemini Ingestion Layer Analysis ---")
    ingestion_result = skill.analyze_system(skill.GEMINI_INGESTION_SPEC)
    print(f"Strengths: {len(ingestion_result.strengths)}")
    print(f"Recommendations: {len(ingestion_result.recommendations)}")
    print(f"Confidence: {ingestion_result.confidence_score:.2%}")

    # Comparative analysis
    print("\n--- Comparative Analysis ---")
    comparison = skill.comparative_analysis(skill.JUDGE_SIX_SPEC, skill.GEMINI_INGESTION_SPEC)
    print(f"Role Relationship: {comparison['role_contrast']['relationship']}")
    print(f"Combined Recommendations: {len(comparison['combined_recommendations'])}")
