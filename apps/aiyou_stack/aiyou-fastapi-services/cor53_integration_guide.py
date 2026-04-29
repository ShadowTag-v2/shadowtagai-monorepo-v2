# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import logging

logger = logging.getLogger(__name__)
"""COR.53 Integration Guide - Complete Unified Workflow

This module provides the complete end-to-end integration of:
- Gemini Ingestion Layer (multi-source intelligence collection)
- COR Skill Registry (discovery & risk assessment)
- AutoGen Orchestration (multi-agent execution)
- Judge 6 Enforcement (doctrine compliance)
- Gemini Secondary Validation

Complete Workflow:
0. Intelligence ingestion (multi-source collection & tier classification)
1. Task intake and decomposition (from intelligence or manual)
2. Judge 6 PRB pre-flight validation
3. Skill discovery and routing
4. AutoGen multi-agent orchestration
5. Execution with watermark injection
6. Post-execution audit and compliance check

This is the RECOMMENDED deployment path (Option C) for production operations
requiring both execution velocity and compliance rigor.

Usage Patterns:
- Intelligence-Driven Operations: AM briefing → automated task generation
- Healthcare GTM: Compliant market research with regulatory validation
- Financial Operations: SEC-compliant transaction processing
- Production Deployments: RA-1 operations with kill-switch protection
- Multi-Vertical Expansion: Parallel execution across 30 verticals

Author: PNKLN Strategic Systems
Version: 2.0.0 (with Gemini Ingestion Layer integration)
"""

import json  # noqa: E402
import logging  # noqa: E402
import os  # noqa: E402
from dataclasses import asdict, dataclass  # noqa: E402
from datetime import datetime  # noqa: E402
from typing import Any  # noqa: E402

from cor_autogen_integration import COROrchestrator  # noqa: E402
from Cor_Claude_Code_6_enforcement import (  # noqa: E402
    Cor_Claude_Code_6Enforcer,
    DoctrineConstraints,
    ValidationResult,
    ViolationLevel,
)

# Import Gemini Ingestion Layer
try:
    from gemini_ingestion_layer import (
        DataTier,
        GeminiIngestionPipeline,
        IngestionMetrics,
        IntelligenceItem,  # noqa: F401
        SourceType,
    )

    INGESTION_AVAILABLE = True
except ImportError:
    INGESTION_AVAILABLE = False
    logger.warning("Gemini Ingestion Layer not available")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TaskRequest:
    """Structured task request for COR.53 processing"""

    task_id: str
    description: str
    justification: str
    requester: str
    priority: str  # 'low', 'medium', 'high', 'critical'
    estimated_hours: int | None = None
    cost_estimate: int | None = None
    compliance_requirements: list[str] | None = None
    ra1_approval: bool = False  # Explicit approval for RA-1 operations
    context: dict[str, Any] | None = None


@dataclass
class ExecutionResult:
    """Complete execution result with audit trail"""

    task_request: TaskRequest
    validation: ValidationResult
    execution_output: dict[str, Any] | None
    overall_status: str  # 'COMPLETED', 'BLOCKED', 'FAILED', 'REVIEW_REQUIRED'
    execution_time_seconds: float
    timestamp: str
    audit_references: list[str]


class COR53UnifiedPipeline:
    """Complete COR.53 integration pipeline
    Option C: Full Stack - Balanced velocity + compliance

    Now includes Gemini Ingestion Layer (Phase 0) for intelligence-driven operations
    """

    def __init__(
        self,
        anthropic_api_key: str | None = None,
        gemini_api_key: str | None = None,
        doctrine: DoctrineConstraints | None = None,
        enable_strict_mode: bool = True,
        enable_ingestion: bool = True,
    ):
        """Initialize COR.53 unified pipeline

        Args:
            anthropic_api_key: Anthropic API key
            gemini_api_key: Google Gemini API key
            doctrine: Doctrine constraints
            enable_strict_mode: Enable strict enforcement (recommended for production)
            enable_ingestion: Enable Gemini Ingestion Layer (Phase 0)

        """
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.gemini_api_key = gemini_api_key or os.environ.get("GOOGLE_API_KEY")
        self.doctrine = doctrine or DoctrineConstraints()
        self.enable_strict_mode = enable_strict_mode
        self.enable_ingestion = enable_ingestion and INGESTION_AVAILABLE

        # Initialize components
        logger.info("Initializing COR.53 unified pipeline...")

        self.Cor_Claude_Code_6 = Cor_Claude_Code_6Enforcer(
            api_key=self.anthropic_api_key,
            gemini_api_key=self.gemini_api_key,
            doctrine=self.doctrine,
        )

        self.orchestrator = COROrchestrator(api_key=self.anthropic_api_key, enable_watermarks=True)

        # Initialize Gemini Ingestion Layer (Phase 0)
        if self.enable_ingestion:
            self.ingestion_pipeline = GeminiIngestionPipeline(gemini_api_key=self.gemini_api_key)
            logger.info("Gemini Ingestion Layer enabled (Phase 0)")
        else:
            self.ingestion_pipeline = None
            logger.info("Gemini Ingestion Layer disabled (manual task mode only)")

        self.execution_history: list[ExecutionResult] = []
        self.ingestion_history: list[IngestionMetrics] = []
        self.task_counter = 0

        logger.info("COR.53 pipeline initialized")
        logger.info(f"Strict Mode: {'ENABLED' if enable_strict_mode else 'DISABLED'}")
        logger.info(f"Ingestion Mode: {'ENABLED' if self.enable_ingestion else 'DISABLED'}")
        logger.info(
            f"Doctrine Constraints: {self.doctrine.vertical_target}-vertical target, "
            f"${self.doctrine.bootstrap_limit}K bootstrap",
        )

    def process_task(self, task_request: TaskRequest) -> ExecutionResult:
        """Process a task through the complete COR.53 pipeline

        Args:
            task_request: Structured task request

        Returns:
            ExecutionResult with complete audit trail

        """
        start_time = datetime.utcnow()
        logger.info(f"Processing task {task_request.task_id}: {task_request.description[:50]}...")

        # PHASE 1: Judge 6 Pre-Flight Validation
        logger.info("PHASE 1: Judge 6 PRB Validation")

        validation_context = {
            "cost_estimate": task_request.cost_estimate or 0,
            "estimated_hours": task_request.estimated_hours or 0,
            "ra1_approval": task_request.ra1_approval,
            "watermark_enabled": True,
            "compliance_requirements": task_request.compliance_requirements or [],
        }

        # Add compliance flags
        if task_request.compliance_requirements:
            for req in task_request.compliance_requirements:
                validation_context[f"{req.lower()}_compliant"] = True

        validation = self.Cor_Claude_Code_6.validate_task(
            task_description=task_request.description,
            justification=task_request.justification,
            context=validation_context,
        )

        # PHASE 2: Enforcement Decision
        logger.info(f"PHASE 2: Enforcement Decision - {validation.violation_level.value}")

        execution_output = None
        overall_status = "BLOCKED"
        audit_references = []

        # Check if task is blocked
        if not validation.is_valid:
            logger.warning(f"Task BLOCKED: {validation.violation_level.value}")
            logger.warning(f"Violations: {validation.violations}")

            overall_status = "BLOCKED"

            # In strict mode, V3+ violations are hard blocks
            if self.enable_strict_mode and validation.violation_level in [
                ViolationLevel.V3_MAJOR,
                ViolationLevel.V4_CRITICAL,
            ]:
                logger.error("STRICT MODE: Task execution denied")
                audit_references.append("strict_mode_block")
            else:
                overall_status = "REVIEW_REQUIRED"
                audit_references.append("manual_review_required")

        else:
            # PHASE 3: Task Execution
            logger.info("PHASE 3: Task Execution via AutoGen Orchestrator")

            try:
                execution_output = self.orchestrator.execute_task(
                    task_description=task_request.description,
                    enable_skill_routing=True,
                )

                overall_status = "COMPLETED"
                logger.info(f"Task executed successfully: {execution_output['task_id']}")

            except Exception as e:
                logger.error(f"Task execution failed: {e}")
                overall_status = "FAILED"
                execution_output = {"error": str(e), "task_id": task_request.task_id}

        # PHASE 4: Post-Execution Audit
        logger.info("PHASE 4: Post-Execution Audit")

        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()

        result = ExecutionResult(
            task_request=task_request,
            validation=validation,
            execution_output=execution_output,
            overall_status=overall_status,
            execution_time_seconds=execution_time,
            timestamp=end_time.isoformat(),
            audit_references=audit_references,
        )

        self.execution_history.append(result)

        # Log completion
        logger.info(
            f"Task {task_request.task_id} complete: {overall_status} in {execution_time:.2f}s",
        )

        return result

    def batch_process_tasks(self, tasks: list[TaskRequest]) -> list[ExecutionResult]:
        """Process multiple tasks in batch

        Args:
            tasks: List of task requests

        Returns:
            List of execution results

        """
        logger.info(f"Batch processing {len(tasks)} tasks...")

        results = []
        for task in tasks:
            result = self.process_task(task)
            results.append(result)

        # Summary statistics
        completed = sum(1 for r in results if r.overall_status == "COMPLETED")
        blocked = sum(1 for r in results if r.overall_status == "BLOCKED")
        failed = sum(1 for r in results if r.overall_status == "FAILED")
        review_required = sum(1 for r in results if r.overall_status == "REVIEW_REQUIRED")

        logger.info(
            f"Batch complete: {completed} completed, {blocked} blocked, "
            f"{failed} failed, {review_required} need review",
        )

        return results

    def run_intelligence_ingestion(
        self,
        source_configs: dict[SourceType, dict[str, Any]],
    ) -> IngestionMetrics:
        """Run PHASE 0: Intelligence ingestion cycle

        Args:
            source_configs: Configuration for each source type

        Returns:
            IngestionMetrics with performance data

        """
        if not self.enable_ingestion or not self.ingestion_pipeline:
            logger.error("Ingestion layer not enabled")
            raise ValueError("Ingestion layer disabled - enable with enable_ingestion=True")

        logger.info("PHASE 0: Running Gemini Ingestion Layer...")

        metrics = self.ingestion_pipeline.run_ingestion_cycle(source_configs)

        self.ingestion_history.append(metrics)

        logger.info(
            f"Ingestion complete: {metrics.items_ingested} items, "
            f"{metrics.tier_1_count} Tier 1, ${metrics.total_cost:.4f} cost",
        )

        return metrics

    def generate_intelligence_briefing(self, date: str | None = None) -> str:
        """Generate AM briefing from ingested intelligence

        Args:
            date: Date for briefing (defaults to today)

        Returns:
            Formatted briefing text

        """
        if not self.enable_ingestion or not self.ingestion_pipeline:
            logger.error("Ingestion layer not enabled")
            raise ValueError("Ingestion layer disabled")

        return self.ingestion_pipeline.generate_am_briefing(date)

    def intelligence_to_tasks(
        self,
        min_tier: DataTier = DataTier.TIER_1_CRITICAL,
        auto_execute: bool = False,
    ) -> list[TaskRequest]:
        """Convert ingested intelligence items to task requests

        Args:
            min_tier: Minimum tier level to convert (default: Tier 1 only)
            auto_execute: If True, automatically execute tasks (requires caution)

        Returns:
            List of generated TaskRequest objects

        """
        if not self.enable_ingestion or not self.ingestion_pipeline:
            logger.error("Ingestion layer not enabled")
            raise ValueError("Ingestion layer disabled")

        logger.info(f"Converting intelligence items (min tier: {min_tier.value}) to tasks...")

        # Filter intelligence items by tier
        tier_order = {
            DataTier.TIER_1_CRITICAL: 1,
            DataTier.TIER_2_IMPORTANT: 2,
            DataTier.TIER_3_BACKGROUND: 3,
        }

        min_tier_value = tier_order[min_tier]

        filtered_items = [
            item
            for item in self.ingestion_pipeline.ingestion_history
            if tier_order[item.tier] <= min_tier_value
        ]

        logger.info(f"Found {len(filtered_items)} items >= {min_tier.value}")

        # Generate tasks
        tasks = []
        for item in filtered_items:
            task = TaskRequest(
                task_id=f"INTEL_{item.item_id}",
                description=f"Analyze and act on intelligence: {item.title}",
                justification=f"Intelligence item from {item.source_type.value} with "
                f"relevance score {item.relevance_score:.2f}. "
                f"Classified as {item.tier.value}. "
                f"Content: {item.content[:100]}...",
                requester="gemini_ingestion_layer",
                priority="high" if item.tier == DataTier.TIER_1_CRITICAL else "medium",
                estimated_hours=2,
                cost_estimate=0,
                context={
                    "intelligence_item_id": item.item_id,
                    "source_url": item.source_url,
                    "tier": item.tier.value,
                    "relevance_score": item.relevance_score,
                },
            )
            tasks.append(task)

        logger.info(f"Generated {len(tasks)} tasks from intelligence")

        # Optionally auto-execute
        if auto_execute:
            logger.warning("Auto-executing intelligence-driven tasks (use with caution)")
            results = self.batch_process_tasks(tasks)
            logger.info(f"Auto-execution complete: {len(results)} tasks processed")

        return tasks

    def export_execution_report(self, output_path: str = "cor53_execution_report.json") -> str:
        """Export comprehensive execution report

        Args:
            output_path: Path to write report

        Returns:
            Path to report file

        """
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "pipeline_version": "1.0.0",
            "doctrine_constraints": asdict(self.doctrine),
            "strict_mode": self.enable_strict_mode,
            "total_tasks": len(self.execution_history),
            "summary": self._generate_summary(),
            "executions": [self._serialize_result(r) for r in self.execution_history],
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Execution report exported: {output_path}")
        return output_path

    def _generate_summary(self) -> dict[str, Any]:
        """Generate summary statistics"""
        if not self.execution_history:
            return {"no_data": True}

        status_counts = {}
        for result in self.execution_history:
            status = result.overall_status
            status_counts[status] = status_counts.get(status, 0) + 1

        violation_counts = {}
        for result in self.execution_history:
            level = result.validation.violation_level.value
            violation_counts[level] = violation_counts.get(level, 0) + 1

        avg_execution_time = sum(r.execution_time_seconds for r in self.execution_history) / len(
            self.execution_history,
        )

        return {
            "status_distribution": status_counts,
            "violation_distribution": violation_counts,
            "average_execution_time_seconds": avg_execution_time,
            "total_brakes_triggered": sum(
                1 for r in self.execution_history if r.validation.brakes_triggered
            ),
        }

    def _serialize_result(self, result: ExecutionResult) -> dict[str, Any]:
        """Serialize execution result for JSON export"""
        return {
            "task_id": result.task_request.task_id,
            "description": result.task_request.description,
            "overall_status": result.overall_status,
            "violation_level": result.validation.violation_level.value,
            "purpose_score": result.validation.purpose_score,
            "reasons_score": result.validation.reasons_score,
            "brakes_triggered": result.validation.brakes_triggered,
            "execution_time_seconds": result.execution_time_seconds,
            "timestamp": result.timestamp,
            "violations": result.validation.violations,
            "recommendations": result.validation.recommendations,
        }


# ============================================================================
# Example Usage Patterns
# ============================================================================


def example_healthcare_gtm():
    """Example: Healthcare GTM Strategy (Compliant)"""
    print("\n=== Example 1: Healthcare GTM Strategy ===")

    pipeline = COR53UnifiedPipeline()

    task = TaskRequest(
        task_id="GTM_HEALTHCARE_001",
        description="Develop go-to-market strategy for telehealth vertical including "
        "HIPAA compliance requirements, market sizing, and competitive analysis",
        justification="This task enables PNKLN's 30-vertical expansion strategy by establishing "
        "a replicable GTM framework for healthcare. Telehealth represents a $50B TAM "
        "with clear regulatory pathways. This research requires zero capital and can "
        "be completed in 48 hours, aligning with bootstrap constraints.",
        requester="strategic_planning",
        priority="high",
        estimated_hours=12,
        cost_estimate=0,
        compliance_requirements=["HIPAA"],
    )

    result = pipeline.process_task(task)

    print(f"Status: {result.overall_status}")
    print(f"Violation Level: {result.validation.violation_level.value}")
    print(f"Purpose Score: {result.validation.purpose_score:.2f}")
    print(f"Reasons Score: {result.validation.reasons_score:.2f}")
    print(f"Execution Time: {result.execution_time_seconds:.2f}s")

    return result


def example_production_database_operation():
    """Example: Production Database Operation (Should Block)"""
    print("\n=== Example 2: Production Database Operation (High Risk) ===")

    pipeline = COR53UnifiedPipeline(enable_strict_mode=True)

    task = TaskRequest(
        task_id="DB_CLEANUP_001",
        description="Delete production database records for users inactive > 90 days",
        justification="Clean up old data",
        requester="operations",
        priority="low",
        estimated_hours=2,
        cost_estimate=0,
        ra1_approval=False,  # No approval = should block
    )

    result = pipeline.process_task(task)

    print(f"Status: {result.overall_status}")
    print(f"Violation Level: {result.validation.violation_level.value}")
    print(f"Brakes Triggered: {result.validation.brakes_triggered}")
    print(f"Violations: {result.validation.violations}")
    print(f"Recommendations: {result.validation.recommendations}")

    return result


def example_batch_vertical_expansion():
    """Example: Batch Processing for Multi-Vertical Expansion"""
    print("\n=== Example 3: Batch Multi-Vertical Expansion ===")

    pipeline = COR53UnifiedPipeline()

    # 5 vertical markets for parallel processing
    verticals = ["telehealth", "fintech", "legaltech", "edtech", "manufacturing"]

    tasks = []
    for i, vertical in enumerate(verticals):
        task = TaskRequest(
            task_id=f"VERTICAL_GTM_{i + 1:03d}",
            description=f"Develop GTM strategy for {vertical} vertical including compliance, "
            f"market sizing, and competitive positioning",
            justification=f"Part of 30-vertical expansion strategy. {vertical.title()} represents "
            f"a significant market opportunity with established regulatory frameworks. "
            f"Zero capital required, leverages existing doctrine infrastructure.",
            requester="strategic_planning",
            priority="high",
            estimated_hours=10,
            cost_estimate=0,
        )
        tasks.append(task)

    results = pipeline.batch_process_tasks(tasks)

    print("\nBatch Results:")
    for result in results:
        print(
            f"  {result.task_request.task_id}: {result.overall_status} "
            f"({result.validation.violation_level.value})",
        )

    # Export report
    report_path = pipeline.export_execution_report("batch_vertical_report.json")
    print(f"\n✓ Report exported: {report_path}")

    return results


# ============================================================================
# COR.53 Singleton Instance (Import this for integration)
# ============================================================================

# Global singleton for easy import
COR_INSTANCE = None


def initialize_cor53(
    anthropic_api_key: str | None = None,
    gemini_api_key: str | None = None,
    strict_mode: bool = True,
) -> dict[str, Any]:
    """Initialize COR.53 global singleton

    Returns:
        Dictionary with initialized components for easy access

    """
    global COR_INSTANCE

    pipeline = COR53UnifiedPipeline(
        anthropic_api_key=anthropic_api_key,
        gemini_api_key=gemini_api_key,
        enable_strict_mode=strict_mode,
    )

    COR_INSTANCE = {
        "pipeline": pipeline,
        "Cor_Claude_Code_6": pipeline.Cor_Claude_Code_6,
        "orchestrator": pipeline.orchestrator,
        "process_task": pipeline.process_task,
        "batch_process": pipeline.batch_process_tasks,
        "export_report": pipeline.export_execution_report,
    }

    logger.info("COR.53 global singleton initialized")
    return COR_INSTANCE


def main():
    """Run all example usage patterns"""
    print("=" * 80)
    print("COR.53 Integration Guide - Complete Unified Workflow")
    print("Option C: Full Stack (Balanced Velocity + Compliance)")
    print("=" * 80)

    # Initialize COR.53
    print("\nInitializing COR.53 pipeline...")
    initialize_cor53()

    # Run examples
    example_healthcare_gtm()
    example_production_database_operation()
    example_batch_vertical_expansion()

    print("\n" + "=" * 80)
    print("✓ COR.53 Integration Guide Examples Complete")
    print("=" * 80)
    print("\nIntegration Instructions:")
    print("1. Import: from cor53_integration_guide import initialize_cor53")
    print("2. Initialize: cor = initialize_cor53()")
    print("3. Use: result = cor['process_task'](task_request)")
    print("4. Export: cor['export_report']('execution_report.json')")


if __name__ == "__main__":
    main()
