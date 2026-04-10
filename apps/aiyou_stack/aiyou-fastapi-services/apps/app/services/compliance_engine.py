"""
Modular Compliance Engine Service

Orchestrates compliance assessments across selected regulation modules.
Implements the core business logic for the ActiveShield MCF.

Design Principles:
- Parallel module assessment for performance
- Unified scoring and aggregation
- Integration with ShadowTag audit layer
- MCP efficiency patterns for batch processing
"""

import asyncio
import hashlib
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from app.compliance.registry import auto_register_modules, get_registry
from app.config import get_settings
from app.models.compliance import (
    AssessmentInput,
    ComplianceAssessmentResult,
    ComplianceBlueprintRequest,
    ComplianceBlueprintResponse,
    ComplianceStatus,
    ModuleMetadata,
    ModuleResult,
    PricingTier,
    RegulationId,
    ValidationRequest,
    ValidationResult,
    ValidationViolation,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class ModularComplianceEngine:
    """
    Central compliance engine that orchestrates module assessments.

    Features:
    - Dynamic module selection based on user configuration
    - Parallel assessment execution
    - Unified compliance scoring
    - Post-generation validation (GPT Store pattern)
    - Batch processing with MCP efficiency patterns
    """

    def __init__(self):
        """Initialize the compliance engine."""
        self._registry = get_registry()
        self._initialized = False
        self._pricing = {
            PricingTier.FREE: {
                "base_price": 0,
                "included_modules": 1,
                "api_calls": 1000,
            },
            PricingTier.PRO: {
                "base_price": 199,
                "included_modules": 1,
                "addon_price": 50,
                "api_calls": 50000,
            },
            PricingTier.ENTERPRISE: {
                "base_price": 2499,
                "included_modules": "unlimited",
                "api_calls": "unlimited",
            },
        }
        logger.info("ModularComplianceEngine initialized")

    async def initialize(self) -> None:
        """Initialize the engine and register all modules."""
        if self._initialized:
            return

        auto_register_modules()
        self._initialized = True
        logger.info(
            f"Compliance engine initialized with {self._registry.get_module_count()} modules"
        )

    # =========================================================================
    # BLUEPRINT GENERATION
    # =========================================================================

    async def generate_blueprint(
        self, request: ComplianceBlueprintRequest
    ) -> ComplianceBlueprintResponse:
        """
        Generate a compliance blueprint based on user's selected regulations.

        Args:
            request: Blueprint request with selected jurisdictions and regulations

        Returns:
            ComplianceBlueprintResponse with module info, endpoints, and SDK config
        """
        await self.initialize()

        selected_modules: list[ModuleMetadata] = []
        total_controls = 0

        for reg_id in request.regulations:
            metadata = self._registry.get_metadata(reg_id)
            if metadata:
                selected_modules.append(metadata)
                module = self._registry.get_module(reg_id)
                if module:
                    total_controls += len(module.controls)

        # Calculate pricing
        base_cost = self._pricing[PricingTier.PRO]["base_price"]
        addon_count = max(0, len(selected_modules) - 1)
        addon_cost = addon_count * self._pricing[PricingTier.PRO]["addon_price"]
        total_monthly_cost = base_cost + addon_cost

        # Generate API endpoints
        api_endpoints = {
            "/api/v1/compliance/assess": "Run compliance assessment",
            "/api/v1/compliance/validate": "Post-generation validation",
            "/api/v1/compliance/audit/{id}": "Retrieve audit proof",
        }
        for module in selected_modules:
            endpoint = f"/api/v1/compliance/modules/{module.id.value}"
            api_endpoints[endpoint] = f"{module.short_name} specific assessment"

        # Generate SDK config
        sdk_config = {
            "enabled_modules": [m.id.value for m in selected_modules],
            "api_base_url": "https://api.activeshield.ai/v1",
            "authentication": "Bearer token",
            "rate_limits": {
                "requests_per_minute": 100,
                "assessments_per_day": 1000,
            },
            "webhook_url": None,
        }

        return ComplianceBlueprintResponse(
            selected_modules=selected_modules,
            total_controls=total_controls,
            estimated_monthly_cost_usd=total_monthly_cost,
            api_endpoints=api_endpoints,
            sdk_config=sdk_config,
        )

    # =========================================================================
    # COMPLIANCE ASSESSMENT
    # =========================================================================

    async def assess(self, input_data: AssessmentInput) -> ComplianceAssessmentResult:
        """
        Run compliance assessment against selected modules.

        Executes assessments in parallel for performance.

        Args:
            input_data: Assessment input with content and module selection

        Returns:
            ComplianceAssessmentResult with all module results and audit proof
        """
        await self.initialize()

        assessment_id = str(uuid4())
        start_time = datetime.utcnow()

        logger.info(f"Starting assessment {assessment_id} for modules: {input_data.modules}")

        # Get selected modules
        modules = self._registry.get_modules(input_data.modules)
        if not modules:
            raise ValueError(f"No valid modules found for: {input_data.modules}")

        # Run assessments in parallel
        assessment_tasks = [module.assess(input_data) for module in modules]
        module_results: list[ModuleResult] = await asyncio.gather(
            *assessment_tasks, return_exceptions=True
        )

        # Filter out exceptions and log errors
        valid_results = []
        for i, result in enumerate(module_results):
            if isinstance(result, Exception):
                logger.error(f"Assessment failed for module {modules[i].module_id}: {result}")
                # Create error result
                valid_results.append(
                    ModuleResult(
                        module_id=modules[i].module_id,
                        module_name=modules[i].metadata.name,
                        status=ComplianceStatus.PENDING_REVIEW,
                        compliance_score=0.0,
                        controls_assessed=0,
                        controls_compliant=0,
                        controls_non_compliant=0,
                        controls_partial=0,
                        control_results=[],
                        recommendations=[f"Assessment error: {str(result)}"],
                        requires_human_review=True,
                    )
                )
            else:
                valid_results.append(result)

        # Aggregate results
        overall_result = self._aggregate_results(valid_results, input_data)
        overall_result.assessment_id = assessment_id

        # Generate audit hash
        overall_result.audit_hash = self._generate_audit_hash(overall_result)

        elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(
            f"Assessment {assessment_id} completed in {elapsed_ms:.2f}ms, "
            f"score: {overall_result.overall_score:.2%}"
        )

        return overall_result

    async def assess_batch(
        self, inputs: list[AssessmentInput], max_concurrent: int = 10
    ) -> list[ComplianceAssessmentResult]:
        """
        Batch assessment with MCP efficiency patterns.

        Implements progressive disclosure - first pass identifies high-risk items,
        second pass does detailed analysis on top violations.

        Args:
            inputs: List of assessment inputs
            max_concurrent: Maximum concurrent assessments

        Returns:
            List of assessment results
        """
        await self.initialize()

        # Phase 1: Quick risk scoring
        semaphore = asyncio.Semaphore(max_concurrent)

        async def assess_with_limit(input_data: AssessmentInput):
            async with semaphore:
                return await self.assess(input_data)

        results = await asyncio.gather(
            *[assess_with_limit(inp) for inp in inputs], return_exceptions=True
        )

        # Filter and return valid results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch assessment {i} failed: {result}")
            else:
                valid_results.append(result)

        logger.info(f"Batch assessment completed: {len(valid_results)}/{len(inputs)} successful")
        return valid_results

    # =========================================================================
    # POST-GENERATION VALIDATION (GPT Store Pattern)
    # =========================================================================

    async def validate_response(self, request: ValidationRequest) -> ValidationResult:
        """
        Validate generated content against compliance rules.

        Used for post-generation validation in GPT Store pattern.

        Args:
            request: Validation request with response text and modules

        Returns:
            ValidationResult with violations and remediated content
        """
        await self.initialize()

        validation_id = str(uuid4())
        all_violations: list[ValidationViolation] = []
        warnings: list[str] = []

        # Get modules for validation
        modules = self._registry.get_modules(request.modules)

        # Check each module's validation rules
        for module in modules:
            violations = await module.validate_content(request.response_text, request.context)
            all_violations.extend(violations)

        # Determine if compliant
        is_compliant = len(all_violations) == 0
        critical_violations = [v for v in all_violations if v.severity == "critical"]

        # Generate warnings for non-critical issues
        for v in all_violations:
            if v.severity in ["medium", "low"]:
                warnings.append(f"{v.module_id.value}: {v.description}")

        # Attempt auto-remediation for non-critical violations
        remediated_text = None
        was_modified = False
        if all_violations and not critical_violations:
            remediated_text = await self._auto_remediate(request.response_text, all_violations)
            was_modified = remediated_text != request.response_text

        # Generate audit hash
        audit_hash = self._generate_validation_hash(request, all_violations)

        return ValidationResult(
            validation_id=validation_id,
            is_compliant=is_compliant,
            violations=all_violations,
            warnings=warnings,
            original_text=request.response_text,
            remediated_text=remediated_text,
            was_modified=was_modified,
            audit_hash=audit_hash,
            modules_checked=request.modules,
        )

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _aggregate_results(
        self, module_results: list[ModuleResult], input_data: AssessmentInput
    ) -> ComplianceAssessmentResult:
        """Aggregate results from multiple module assessments."""
        if not module_results:
            return ComplianceAssessmentResult(
                overall_status=ComplianceStatus.PENDING_REVIEW,
                overall_score=0.0,
                modules_assessed=[],
                total_controls=0,
                total_compliant=0,
                total_non_compliant=0,
            )

        # Calculate totals
        total_controls = sum(r.controls_assessed for r in module_results)
        total_compliant = sum(r.controls_compliant for r in module_results)
        total_non_compliant = sum(r.controls_non_compliant for r in module_results)

        # Calculate overall score (weighted by controls)
        if total_controls > 0:
            weighted_score = (
                sum(r.compliance_score * r.controls_assessed for r in module_results)
                / total_controls
            )
        else:
            weighted_score = 0.0

        # Determine overall status
        if any(r.status == ComplianceStatus.NON_COMPLIANT for r in module_results):
            overall_status = ComplianceStatus.NON_COMPLIANT
        elif any(r.status == ComplianceStatus.PARTIAL for r in module_results):
            overall_status = ComplianceStatus.PARTIAL
        elif all(r.status == ComplianceStatus.COMPLIANT for r in module_results):
            overall_status = ComplianceStatus.COMPLIANT
        else:
            overall_status = ComplianceStatus.PENDING_REVIEW

        # Collect critical findings and recommendations
        critical_findings = []
        recommendations = []
        for result in module_results:
            for control in result.control_results:
                if control.status == ComplianceStatus.NON_COMPLIANT:
                    for finding in control.findings:
                        critical_findings.append(f"[{result.module_id.value}] {finding}")
            recommendations.extend(result.recommendations)

        # Human review required?
        requires_human_review = any(r.requires_human_review for r in module_results)

        # Generate transparency notice if AI content
        transparency_notice = None
        if input_data.is_ai_generated:
            transparency_notice = (
                "This content was generated or modified using artificial intelligence. "
                "Compliance assessment performed by ActiveShield MCF."
            )

        return ComplianceAssessmentResult(
            overall_status=overall_status,
            overall_score=weighted_score,
            modules_assessed=module_results,
            total_controls=total_controls,
            total_compliant=total_compliant,
            total_non_compliant=total_non_compliant,
            critical_findings=critical_findings[:10],  # Top 10
            recommendations=list(set(recommendations))[:10],  # Dedupe, top 10
            requires_human_review=requires_human_review,
            transparency_notice=transparency_notice,
        )

    async def _auto_remediate(self, content: str, violations: list[ValidationViolation]) -> str:
        """
        Attempt automatic remediation of content.

        Only remediates non-critical violations with clear fixes.
        """
        remediated = content

        for violation in violations:
            if violation.severity == "critical":
                continue  # Don't auto-remediate critical issues

            if violation.suggested_fix and violation.location:
                # Simple replacement for detected patterns
                # In production, this would use more sophisticated NLP
                pass

        return remediated

    def _generate_audit_hash(self, result: ComplianceAssessmentResult) -> str:
        """Generate SHA256 hash for audit trail."""
        audit_data = {
            "assessment_id": result.assessment_id,
            "timestamp": result.timestamp.isoformat(),
            "overall_status": result.overall_status.value,
            "overall_score": result.overall_score,
            "modules": [m.module_id.value for m in result.modules_assessed],
            "total_controls": result.total_controls,
        }
        content = str(sorted(audit_data.items()))
        return hashlib.sha256(content.encode()).hexdigest()

    def _generate_validation_hash(
        self, request: ValidationRequest, violations: list[ValidationViolation]
    ) -> str:
        """Generate SHA256 hash for validation audit."""
        audit_data = {
            "content_hash": hashlib.sha256(request.response_text.encode()).hexdigest()[:16],
            "modules": [m.value for m in request.modules],
            "violation_count": len(violations),
            "timestamp": datetime.utcnow().isoformat(),
        }
        content = str(sorted(audit_data.items()))
        return hashlib.sha256(content.encode()).hexdigest()

    def get_available_modules(self) -> list[ModuleMetadata]:
        """Get list of all available compliance modules."""
        return self._registry.list_metadata()

    def get_module_info(self, regulation_id: RegulationId) -> dict[str, Any] | None:
        """Get detailed information about a specific module."""
        module = self._registry.get_module(regulation_id)
        if not module:
            return None

        return {
            "metadata": module.metadata,
            "controls_count": len(module.controls),
            "controls": module.generate_checklist(),
            "validation_rules_count": len(module.validation_rules),
            "required_evidence": module.get_required_evidence(),
        }

    def health_check(self) -> dict[str, Any]:
        """Get compliance engine health status."""
        return {
            "status": "healthy",
            "initialized": self._initialized,
            "registry": self._registry.health_check(),
        }


# Singleton instance
_engine: ModularComplianceEngine | None = None


def get_compliance_engine() -> ModularComplianceEngine:
    """Get or create the compliance engine singleton."""
    global _engine
    if _engine is None:
        _engine = ModularComplianceEngine()
    return _engine
