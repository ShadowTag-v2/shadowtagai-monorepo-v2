"""Tests for the Modular Compliance Engine
"""

import pytest

from app.models.compliance import (
    AssessmentInput,
    ComplianceBlueprintRequest,
    Jurisdiction,
    RegulationId,
    ValidationRequest,
)
from app.services.compliance_engine import get_compliance_engine


@pytest.fixture
def engine():
    """Get compliance engine instance"""
    return get_compliance_engine()


class TestComplianceEngine:
    """Test cases for ModularComplianceEngine"""

    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine):
        """Engine should initialize correctly"""
        await engine.initialize()
        assert engine._initialized is True
        assert engine._registry.get_module_count() > 0

    @pytest.mark.asyncio
    async def test_generate_blueprint(self, engine):
        """Should generate compliance blueprint"""
        request = ComplianceBlueprintRequest(
            jurisdictions=[Jurisdiction.EU, Jurisdiction.US],
            regulations=[RegulationId.EU_AI_ACT, RegulationId.GDPR],
        )

        blueprint = await engine.generate_blueprint(request)

        assert len(blueprint.selected_modules) == 2
        assert blueprint.total_controls > 0
        assert blueprint.estimated_monthly_cost_usd > 0
        assert len(blueprint.api_endpoints) > 0

    @pytest.mark.asyncio
    async def test_assess_single_module(self, engine):
        """Should assess against single module"""
        input_data = AssessmentInput(
            content_type="ai_chatbot",
            is_ai_generated=True,
            modules=[RegulationId.EU_AI_ACT],
            metadata={"ai_disclosure": True},
        )

        result = await engine.assess(input_data)

        assert result.assessment_id is not None
        assert len(result.modules_assessed) == 1
        assert result.modules_assessed[0].module_id == RegulationId.EU_AI_ACT
        assert 0 <= result.overall_score <= 1

    @pytest.mark.asyncio
    async def test_assess_multiple_modules(self, engine):
        """Should assess against multiple modules"""
        input_data = AssessmentInput(
            content_type="ai_chatbot",
            is_ai_generated=True,
            contains_pii=True,
            modules=[RegulationId.EU_AI_ACT, RegulationId.GDPR],
            metadata={
                "ai_disclosure": True,
                "lawful_basis": "consent",
            },
        )

        result = await engine.assess(input_data)

        assert len(result.modules_assessed) == 2
        assert result.total_controls > 0
        assert result.audit_hash is not None

    @pytest.mark.asyncio
    async def test_validate_response_compliant(self, engine):
        """Should validate compliant response"""
        request = ValidationRequest(
            response_text="This is a helpful AI assistant response. I am an AI and cannot provide medical advice.",
            modules=[RegulationId.EU_AI_ACT],
        )

        result = await engine.validate_response(request)

        assert result.validation_id is not None
        assert result.modules_checked == [RegulationId.EU_AI_ACT]

    @pytest.mark.asyncio
    async def test_validate_response_with_violations(self, engine):
        """Should detect violations in response"""
        request = ValidationRequest(
            response_text="Patient John Doe, SSN 123-45-6789, was diagnosed with diabetes.",
            modules=[RegulationId.HIPAA],
        )

        result = await engine.validate_response(request)

        assert len(result.violations) > 0

    @pytest.mark.asyncio
    async def test_batch_assessment(self, engine):
        """Should process batch assessments"""
        inputs = [
            AssessmentInput(
                content_type="ai_chatbot",
                content_id=f"item_{i}",
                modules=[RegulationId.EU_AI_ACT],
            )
            for i in range(5)
        ]

        results = await engine.assess_batch(inputs, max_concurrent=3)

        assert len(results) == 5
        assert all(r.assessment_id is not None for r in results)

    def test_get_available_modules(self, engine):
        """Should list available modules"""
        # Ensure initialized
        import asyncio

        asyncio.get_event_loop().run_until_complete(engine.initialize())

        modules = engine.get_available_modules()

        assert len(modules) >= 5  # At least our 5 built-in modules
        module_ids = [m.id for m in modules]
        assert RegulationId.EU_AI_ACT in module_ids
        assert RegulationId.GDPR in module_ids

    def test_get_module_info(self, engine):
        """Should get detailed module info"""
        import asyncio

        asyncio.get_event_loop().run_until_complete(engine.initialize())

        info = engine.get_module_info(RegulationId.EU_AI_ACT)

        assert info is not None
        assert "metadata" in info
        assert "controls_count" in info
        assert info["controls_count"] > 0

    def test_health_check(self, engine):
        """Health check should return status"""
        health = engine.health_check()

        assert health["status"] == "healthy"
        assert "registry" in health
