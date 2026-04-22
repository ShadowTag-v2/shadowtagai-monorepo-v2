"""Gemini AI integration service for intelligent analysis."""

import json
import time
import uuid
from datetime import datetime

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from app.models.gemini import (
    AnalysisSection,
    AnalysisType,
    ComparisonAnalysisRequest,
    ComparisonAnalysisResponse,
    ConfidenceLevel,
    GeminiAnalysisRequest,
    GeminiAnalysisResponse,
)


class GeminiService:
    """Service for interacting with Google Gemini AI for analysis tasks."""

    def __init__(
        self, api_key: str | None = None, model_name: str = "gemini-3.1-flash-lite-preview"
    ):
        """Initialize the Gemini service.

        Args:
            api_key: Google AI API key
            model_name: Gemini model to use

        """
        self.api_key = api_key
        self.model_name = model_name
        self.model = None

        if GEMINI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)

    def is_available(self) -> bool:
        """Check if Gemini is available and configured."""
        return GEMINI_AVAILABLE and self.model is not None

    async def analyze(self, request: GeminiAnalysisRequest) -> GeminiAnalysisResponse:
        """Perform analysis using Gemini AI.

        Args:
            request: Analysis request

        Returns:
            Analysis response

        Raises:
            ValueError: If Gemini is not available

        """
        if not self.is_available():
            raise ValueError("Gemini AI is not available. Check API key configuration.")

        start_time = time.time()

        # Build the prompt based on analysis type
        prompt = self._build_prompt(request)

        # Call Gemini API
        try:
            response = self.model.generate_content(prompt)
            analysis_text = response.text
        except Exception as e:
            raise ValueError(f"Gemini API error: {e!s}")

        # Parse the response
        sections = self._parse_analysis_sections(analysis_text, request.confidence_threshold)

        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(sections)

        # Extract key findings and recommendations
        key_findings, recommendations, risks = self._extract_insights(sections)

        # Generate executive summary
        executive_summary = self._generate_executive_summary(analysis_text, key_findings)

        analysis_time = time.time() - start_time

        return GeminiAnalysisResponse(
            analysis_id=str(uuid.uuid4()),
            analysis_type=request.analysis_type,
            target=request.target,
            overall_confidence=overall_confidence,
            confidence_level=self._get_confidence_level(overall_confidence),
            sections=sections,
            executive_summary=executive_summary,
            key_findings=key_findings,
            recommendations=recommendations,
            risks=risks,
            model_used=self.model_name,
            analysis_time_seconds=analysis_time,
        )

    def _build_prompt(self, request: GeminiAnalysisRequest) -> str:
        """Build the analysis prompt for Gemini."""
        if request.analysis_type == AnalysisType.INGESTION_LAYER:
            return self._build_ingestion_layer_prompt(request)
        if request.analysis_type == AnalysisType.COMPLIANCE_AUDIT:
            return self._build_compliance_audit_prompt(request)
        if request.analysis_type == AnalysisType.COVERAGE_ANALYSIS:
            return self._build_coverage_analysis_prompt(request)
        return self._build_generic_prompt(request)

    def _build_ingestion_layer_prompt(self, request: GeminiAnalysisRequest) -> str:
        """Build prompt for ingestion layer analysis."""
        prompt = f"""
You are an expert system architect analyzing the "{request.target}" Ingestion Layer.

## Analysis Context
{request.context or "N/A"}

## Architecture Specifications
{request.architecture_specs or "Not provided"}

## Current Metrics
{json.dumps(request.metrics_data, indent=2) if request.metrics_data else "Not provided"}

## Documentation
{request.documentation or "Not provided"}

## Analysis Requirements

Perform a comprehensive analysis of this ingestion layer system. Your analysis should cover:

### 1. Architecture Analysis
- System type (e.g., GKE CronJob Multi-Container)
- Strengths and weaknesses
- Scalability assessment
- Fault tolerance

### 2. Key Metrics Analysis
- Daily items ingested
- Source diversity
- Cost per item efficiency
- Runtime performance (~45 min/night target)

### 3. Quality Gates Assessment
- Items ingested per day
- Number of active sources
- Cost per item optimization
- Relevance, timeliness, completeness scores

### 4. Ethical Compliance
- robots.txt adherence
- Rate limiting compliance
- Transparency and attribution
- Terms of service compliance

### 5. Multi-Source Coverage
- Coverage across different source types (YouTube, Twitter, News, RSS, etc.)
- Source diversity score
- Identified gaps
- Recommendations for expanding coverage

### 6. Tier Classification
- Tier 1/2/3 distribution
- Optimization of high-value (Tier 1) sources
- Balance assessment

### 7. AM Briefing Delivery Effectiveness
- Delivery timeliness
- Content quality and relevance
- Completeness of information

### 8. Integration Points
- How services call this ingestion layer
- Namespace integration (across 4 namespaces)
- API contracts and dependencies

### 9. Cost Model
- Monthly operational cost (~$77 target)
- Cost optimization opportunities
- ROI assessment

### 10. Production Readiness
- Critical blockers
- Risk assessment
- Next steps for deployment

## Output Format

Provide structured analysis with:
- Clear section headers
- Confidence scores for each finding
- Specific, actionable recommendations
- Risk identification

Minimum confidence threshold: {request.confidence_threshold * 100}%

Be thorough, objective, and provide evidence-based analysis.
"""
        return prompt.strip()

    def _build_compliance_audit_prompt(self, request: GeminiAnalysisRequest) -> str:
        """Build prompt for compliance audit."""
        prompt = f"""
You are an ethical compliance auditor analyzing "{request.target}" for adherence to best practices.

## System Information
{request.architecture_specs or "Not provided"}

## Current Compliance Data
{json.dumps(request.metrics_data, indent=2) if request.metrics_data else "Not provided"}

## Audit Requirements

Perform a compliance audit covering:

1. **robots.txt Compliance**
   - Are robots.txt files being respected?
   - Any violations detected?

2. **Rate Limiting**
   - Are rate limits being honored?
   - Risk of being blocked?

3. **Terms of Service**
   - Compliance with platform ToS
   - License adherence

4. **Transparency**
   - User-agent identification
   - Attribution practices
   - Data usage transparency

5. **Privacy and Data Handling**
   - PII handling
   - Data retention policies
   - User consent

Provide:
- Compliance score (0-1)
- List of violations
- Recommendations for improvement
- Risk assessment

Minimum confidence: {request.confidence_threshold * 100}%
"""
        return prompt.strip()

    def _build_coverage_analysis_prompt(self, request: GeminiAnalysisRequest) -> str:
        """Build prompt for coverage analysis."""
        prompt = f"""
You are a data intelligence analyst evaluating source coverage for "{request.target}".

## Source Data
{json.dumps(request.metrics_data, indent=2) if request.metrics_data else "Not provided"}

## Analysis Goals

Analyze multi-source coverage:

1. **Source Diversity**
   - Types of sources (YouTube, Twitter, News, RSS, Web, API)
   - Geographic diversity
   - Topic diversity

2. **Tier Distribution**
   - Tier 1 (high-value) coverage
   - Tier 2 (medium-value) coverage
   - Tier 3 (low-value) coverage
   - Balance assessment

3. **Coverage Gaps**
   - Missing source types
   - Underrepresented areas
   - Competitor comparison

4. **Quality Metrics**
   - Relevance scores by source
   - Timeliness by source
   - Completeness by source

5. **Recommendations**
   - New sources to add
   - Sources to deprecate
   - Priority actions

Provide diversity score (0-1) and specific recommendations.

Minimum confidence: {request.confidence_threshold * 100}%
"""
        return prompt.strip()

    def _build_generic_prompt(self, request: GeminiAnalysisRequest) -> str:
        """Build generic analysis prompt."""
        prompt = f"""
Analyze the following system: "{request.target}"

Type: {request.analysis_type.value}

## Context
{request.context or "N/A"}

## Architecture
{request.architecture_specs or "Not provided"}

## Metrics
{json.dumps(request.metrics_data, indent=2) if request.metrics_data else "Not provided"}

## Documentation
{request.documentation or "Not provided"}

Provide a comprehensive analysis with:
- Key findings
- Recommendations
- Risk assessment
- Confidence scores

Minimum confidence: {request.confidence_threshold * 100}%
"""
        return prompt.strip()

    def _parse_analysis_sections(
        self,
        analysis_text: str,
        confidence_threshold: float,
    ) -> list[AnalysisSection]:
        """Parse analysis text into sections."""
        # Simple section parsing (can be enhanced)
        sections = []

        # Split by common headers
        lines = analysis_text.split("\n")
        current_section = None
        current_content = []

        for line in lines:
            # Check if this is a header (starts with ## or **bold**)
            if line.strip().startswith("##") or (
                line.strip().startswith("**") and line.strip().endswith("**")
            ):
                # Save previous section
                if current_section and current_content:
                    sections.append(
                        self._create_section(
                            current_section,
                            "\n".join(current_content),
                            confidence_threshold,
                        ),
                    )

                # Start new section
                current_section = line.strip().lstrip("#").strip("*").strip()
                current_content = []
            elif line.strip():
                current_content.append(line)

        # Add final section
        if current_section and current_content:
            sections.append(
                self._create_section(
                    current_section,
                    "\n".join(current_content),
                    confidence_threshold,
                ),
            )

        return sections

    def _create_section(
        self,
        section_name: str,
        content: str,
        base_confidence: float,
    ) -> AnalysisSection:
        """Create an analysis section."""
        # Extract findings and recommendations
        findings = []
        recommendations = []

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                item = line[2:].strip()
                if "recommend" in item.lower() or "should" in item.lower():
                    recommendations.append(item)
                else:
                    findings.append(item)

        return AnalysisSection(
            section_name=section_name,
            content=content,
            confidence=base_confidence,
            key_findings=findings[:5],  # Top 5
            recommendations=recommendations[:5],  # Top 5
        )

    def _calculate_overall_confidence(self, sections: list[AnalysisSection]) -> float:
        """Calculate overall confidence from sections."""
        if not sections:
            return 0.0
        return sum(s.confidence for s in sections) / len(sections)

    def _extract_insights(
        self,
        sections: list[AnalysisSection],
    ) -> tuple[list[str], list[str], list[str]]:
        """Extract key findings, recommendations, and risks from sections."""
        findings = []
        recommendations = []
        risks = []

        for section in sections:
            findings.extend(section.key_findings)
            recommendations.extend(section.recommendations)

            # Extract risks (lines containing risk-related keywords)
            for line in section.content.split("\n"):
                if any(
                    keyword in line.lower()
                    for keyword in ["risk", "issue", "problem", "concern", "vulnerability"]
                ):
                    risks.append(line.strip().lstrip("-*").strip())

        return findings[:10], recommendations[:10], risks[:10]

    def _generate_executive_summary(self, analysis_text: str, key_findings: list[str]) -> str:
        """Generate executive summary."""
        # Take first paragraph or first 500 characters
        lines = analysis_text.split("\n\n")
        summary = lines[0] if lines else analysis_text[:500]

        if len(key_findings) > 0:
            summary += f"\n\nKey highlights: {', '.join(key_findings[:3])}"

        return summary[:1000]  # Limit to 1000 chars

    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert numeric confidence to level."""
        if confidence >= 0.7:
            return ConfidenceLevel.HIGH
        if confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    async def compare_systems(
        self,
        request: ComparisonAnalysisRequest,
    ) -> ComparisonAnalysisResponse:
        """Compare two systems (e.g., Judge 6 vs Ingestion Layer).

        Args:
            request: Comparison request

        Returns:
            Comparison analysis

        """
        if not self.is_available():
            raise ValueError("Gemini AI is not available.")

        prompt = f"""
Compare these two systems:

## System A: {request.system_a_name}
{request.system_a_specs}

## System B: {request.system_b_name}
{request.system_b_specs}

## Comparison Aspects
{", ".join(request.comparison_aspects)}

For each aspect, provide:
1. System A's approach
2. System B's approach
3. Comparative analysis

Then identify:
- Synergies (how they complement each other)
- Conflicts (incompatibilities or redundancies)
- Integration recommendations

Provide structured output with clear sections.
"""

        try:
            response = self.model.generate_content(prompt)
            analysis_text = response.text
        except Exception as e:
            raise ValueError(f"Gemini API error: {e!s}")

        # Parse comparison (simplified)
        comparisons = {}
        for aspect in request.comparison_aspects:
            comparisons[aspect] = {
                "system_a": f"{request.system_a_name} approach",
                "system_b": f"{request.system_b_name} approach",
                "analysis": "Comparative analysis",
            }

        return ComparisonAnalysisResponse(
            analysis_id=str(uuid.uuid4()),
            system_a_name=request.system_a_name,
            system_b_name=request.system_b_name,
            comparisons=comparisons,
            synergies=["Synergy 1", "Synergy 2"],
            conflicts=["Conflict 1"],
            integration_recommendations=["Recommendation 1"],
            overall_assessment=analysis_text[:500],
            created_at=datetime.utcnow(),
        )
