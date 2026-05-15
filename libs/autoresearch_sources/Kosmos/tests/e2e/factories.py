"""
Test factories for creating complex test scenarios.

Provides factory methods for creating test data:
- Hypotheses
- Experiment protocols
- Experiment results
- Research scenarios
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ResearchScenarioFactory:
    """Factory for creating complete research scenarios."""

    @staticmethod
    def create_simple_hypothesis(
        domain: str = "biology",
        research_question: str = "Does X affect Y?",
        hypothesis_id: str | None = None,
        testability_score: float = 0.8,
        novelty_score: float = 0.6,
    ):
        """
        Create a simple testable hypothesis.

        Args:
            domain: Scientific domain
            research_question: Research question being addressed
            hypothesis_id: Optional ID (auto-generated if None)
            testability_score: Testability score (0-1)
            novelty_score: Novelty score (0-1)

        Returns:
            Hypothesis instance
        """
        from kosmos.models.hypothesis import Hypothesis, HypothesisStatus

        return Hypothesis(
            id=hypothesis_id or f"hyp_{uuid.uuid4().hex[:8]}",
            statement=f"X increases Y in {domain} under specific conditions",
            research_question=research_question,
            domain=domain,
            rationale="Based on prior research and theoretical framework",
            status=HypothesisStatus.GENERATED,
            testability_score=testability_score,
            novelty_score=novelty_score,
            confidence_score=0.7,
            priority_score=0.75,
        )

    @staticmethod
    def create_experiment_protocol(hypothesis, num_steps: int = 3, protocol_id: str | None = None):
        """
        Create an experiment protocol for a hypothesis.

        Args:
            hypothesis: Hypothesis to create protocol for
            num_steps: Number of protocol steps
            protocol_id: Optional ID (auto-generated if None)

        Returns:
            ExperimentProtocol instance
        """
        from kosmos.models.experiment import (
            ExperimentProtocol,
            ExperimentType,
            ProtocolStep,
            ResourceRequirements,
            Variable,
            VariableType,
        )

        steps = [
            ProtocolStep(
                step_number=i,
                title=f"Step {i}: {'Setup' if i == 1 else 'Execute' if i == 2 else 'Analyze'}",
                description=f"Execute step {i} of the experiment with proper methodology",
                action=f"action_{i}()",
                expected_duration_minutes=15 * i,
            )
            for i in range(1, num_steps + 1)
        ]

        # Create required variables
        variables = {
            "independent_var": Variable(
                name="independent_var",
                type=VariableType.INDEPENDENT,
                description="Main independent variable being manipulated",
                values=[0, 1, 2],
            ),
            "dependent_var": Variable(
                name="dependent_var",
                type=VariableType.DEPENDENT,
                description="Primary outcome measurement variable",
                measurement_method="direct_measurement",
            ),
        }

        # Create required resource requirements
        resource_requirements = ResourceRequirements(
            compute_hours=1.0, memory_gb=4.0, estimated_cost_usd=1.0, estimated_duration_days=1.0
        )

        return ExperimentProtocol(
            id=protocol_id or f"proto_{uuid.uuid4().hex[:8]}",
            hypothesis_id=hypothesis.id,
            name=f"Test protocol for {hypothesis.id}",
            description="Computational experiment to test hypothesis with proper methodology and controls",
            domain=hypothesis.domain,
            experiment_type=ExperimentType.COMPUTATIONAL,
            objective=f"Test whether {hypothesis.statement}",
            steps=steps,
            variables=variables,
            resource_requirements=resource_requirements,
            rigor_score=0.85,
        )

    @staticmethod
    def create_successful_result(
        protocol,
        p_value: float = 0.01,
        supports_hypothesis: bool = True,
        result_id: str | None = None,
    ):
        """
        Create a successful experiment result.

        Args:
            protocol: Protocol the result is for
            p_value: P-value of the result
            supports_hypothesis: Whether result supports hypothesis
            result_id: Optional ID (auto-generated if None)

        Returns:
            ExperimentResult instance
        """
        import platform
        import sys

        from kosmos.models.result import ExecutionMetadata, ExperimentResult, ResultStatus

        now = datetime.utcnow()
        result_id_val = result_id or f"result_{uuid.uuid4().hex[:8]}"

        # Create required ExecutionMetadata
        metadata = ExecutionMetadata(
            start_time=now,
            end_time=now,
            duration_seconds=1.5,
            python_version=sys.version,
            platform=platform.system(),
            experiment_id=protocol.id,
            protocol_id=protocol.id,
            hypothesis_id=protocol.hypothesis_id,
        )

        return ExperimentResult(
            id=result_id_val,
            experiment_id=protocol.id,
            protocol_id=protocol.id,
            hypothesis_id=protocol.hypothesis_id,
            status=ResultStatus.SUCCESS,
            supports_hypothesis=supports_hypothesis,
            primary_p_value=p_value,
            metadata=metadata,
            interpretation=f"Results {'support' if supports_hypothesis else 'do not support'} the hypothesis",
            summary=f"Experiment completed with p-value={p_value:.4f}",
        )

    @staticmethod
    def create_failed_result(
        protocol, error_message: str = "Execution error", result_id: str | None = None
    ):
        """
        Create a failed experiment result.

        Args:
            protocol: Protocol the result is for
            error_message: Error message
            result_id: Optional ID (auto-generated if None)

        Returns:
            ExperimentResult instance
        """
        import platform
        import sys

        from kosmos.models.result import ExecutionMetadata, ExperimentResult, ResultStatus

        now = datetime.utcnow()
        result_id_val = result_id or f"result_{uuid.uuid4().hex[:8]}"

        # Create required ExecutionMetadata
        metadata = ExecutionMetadata(
            start_time=now,
            end_time=now,
            duration_seconds=0.5,
            python_version=sys.version,
            platform=platform.system(),
            experiment_id=protocol.id,
            protocol_id=protocol.id,
            hypothesis_id=protocol.hypothesis_id,
        )

        return ExperimentResult(
            id=result_id_val,
            experiment_id=protocol.id,
            protocol_id=protocol.id,
            hypothesis_id=protocol.hypothesis_id,
            status=ResultStatus.FAILED,
            supports_hypothesis=None,
            primary_p_value=None,
            metadata=metadata,
            interpretation=f"Experiment failed: {error_message}",
            summary=error_message,
        )

    @staticmethod
    def create_research_plan(
        research_question: str = "Test research question",
        max_iterations: int = 5,
        hypotheses: list | None = None,
    ):
        """
        Create a ResearchPlan with optional hypotheses.

        Args:
            research_question: Research question
            max_iterations: Maximum iterations
            hypotheses: Optional list of hypotheses to add

        Returns:
            ResearchPlan instance
        """
        from kosmos.core.workflow import ResearchPlan

        plan = ResearchPlan(research_question=research_question, max_iterations=max_iterations)

        if hypotheses:
            for hyp in hypotheses:
                plan.add_hypothesis(hyp.id)

        return plan

    @staticmethod
    def create_complete_scenario(
        domain: str = "biology", num_hypotheses: int = 3, num_results_per_hypothesis: int = 1
    ) -> dict[str, Any]:
        """
        Create a complete research scenario with hypotheses, protocols, and results.

        Args:
            domain: Scientific domain
            num_hypotheses: Number of hypotheses to create
            num_results_per_hypothesis: Number of results per hypothesis

        Returns:
            Dict with 'hypotheses', 'protocols', 'results', 'research_plan'
        """
        factory = ResearchScenarioFactory()

        hypotheses = []
        protocols = []
        results = []

        for i in range(num_hypotheses):
            hyp = factory.create_simple_hypothesis(
                domain=domain,
                research_question=f"Research question {i + 1}",
                novelty_score=0.8 - (i * 0.1),  # Decreasing novelty
            )
            hypotheses.append(hyp)

            proto = factory.create_experiment_protocol(hyp)
            protocols.append(proto)

            for j in range(num_results_per_hypothesis):
                # Alternate between supporting and not supporting
                supports = (i + j) % 2 == 0
                result = factory.create_successful_result(
                    proto, p_value=0.01 if supports else 0.15, supports_hypothesis=supports
                )
                results.append(result)

        research_plan = factory.create_research_plan(
            research_question=f"Comprehensive {domain} research",
            max_iterations=10,
            hypotheses=hypotheses,
        )

        return {
            "hypotheses": hypotheses,
            "protocols": protocols,
            "results": results,
            "research_plan": research_plan,
        }


@dataclass
class EntityFactory:
    """Factory for creating World Model entities."""

    @staticmethod
    def create_hypothesis_entity(
        hypothesis_id: str | None = None,
        statement: str = "Test hypothesis",
        domain: str = "biology",
        project: str | None = None,
    ):
        """Create Entity from hypothesis data."""
        from kosmos.world_model.models import Entity

        return Entity(
            id=hypothesis_id or f"hyp_{uuid.uuid4().hex[:8]}",
            type="Hypothesis",
            properties={
                "statement": statement,
                "domain": domain,
                "research_question": "Does X affect Y?",
            },
            confidence=0.8,
            project=project,
            created_by="test_factory",
        )

    @staticmethod
    def create_result_entity(
        result_id: str | None = None,
        hypothesis_id: str = "hyp_001",
        supports_hypothesis: bool = True,
        project: str | None = None,
    ):
        """Create Entity from result data."""
        from kosmos.world_model.models import Entity

        return Entity(
            id=result_id or f"result_{uuid.uuid4().hex[:8]}",
            type="ExperimentResult",
            properties={
                "hypothesis_id": hypothesis_id,
                "supports_hypothesis": supports_hypothesis,
                "status": "SUCCESS",
            },
            confidence=1.0,
            project=project,
            created_by="test_factory",
        )

    @staticmethod
    def create_protocol_entity(
        protocol_id: str | None = None,
        hypothesis_id: str = "hyp_001",
        name: str = "Test Protocol",
        project: str | None = None,
    ):
        """Create Entity from protocol data."""
        from kosmos.world_model.models import Entity

        return Entity(
            id=protocol_id or f"proto_{uuid.uuid4().hex[:8]}",
            type="ExperimentProtocol",
            properties={"name": name, "hypothesis_id": hypothesis_id, "domain": "biology"},
            confidence=0.9,
            project=project,
            created_by="test_factory",
        )


@dataclass
class RelationshipFactory:
    """Factory for creating World Model relationships."""

    @staticmethod
    def create_tests_relationship(source_id: str, target_id: str, iteration: int = 1):
        """Create TESTS relationship (protocol tests hypothesis)."""
        from kosmos.world_model.models import Relationship

        return Relationship(
            source_id=source_id,
            target_id=target_id,
            type="TESTS",
            properties={"iteration": iteration},
            confidence=1.0,
            created_by="test_factory",
        )

    @staticmethod
    def create_supports_relationship(
        source_id: str, target_id: str, p_value: float = 0.01, effect_size: float = 0.8
    ):
        """Create SUPPORTS relationship (result supports hypothesis)."""
        from kosmos.world_model.models import Relationship

        return Relationship(
            source_id=source_id,
            target_id=target_id,
            type="SUPPORTS",
            properties={"p_value": p_value, "effect_size": effect_size},
            confidence=0.95,
            created_by="test_factory",
        )

    @staticmethod
    def create_spawned_by_relationship(source_id: str, target_id: str, generation: int = 1):
        """Create SPAWNED_BY relationship (hypothesis from research question)."""
        from kosmos.world_model.models import Relationship

        return Relationship(
            source_id=source_id,
            target_id=target_id,
            type="SPAWNED_BY",
            properties={"generation": generation},
            confidence=1.0,
            created_by="test_factory",
        )


@dataclass
class APICallFactory:
    """Factory for creating mock API call data."""

    @staticmethod
    def create_api_call(
        input_tokens: int = 1000,
        output_tokens: int = 500,
        model: str = "claude-3-5-sonnet-20241022",
        duration_seconds: float = 1.5,
        success: bool = True,
        timestamp: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Create mock API call record.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name
            duration_seconds: Call duration
            success: Whether call succeeded
            timestamp: Timestamp (defaults to now)

        Returns:
            API call record dict
        """
        return {
            "timestamp": (timestamp or datetime.utcnow()).isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "duration_seconds": duration_seconds,
            "success": success,
        }

    @staticmethod
    def create_expensive_api_call(cost_usd: float = 0.10) -> dict[str, Any]:
        """
        Create API call with specific cost.

        Claude 3.5 Sonnet pricing: $3/M input, $15/M output
        """
        # Calculate tokens to achieve target cost
        # Assume 2:1 input:output ratio
        # cost = (input/1M * 3) + (output/1M * 15)
        # With output = input/2:
        # cost = (input/1M * 3) + (input/2M * 15) = input/1M * (3 + 7.5) = input/1M * 10.5
        # input = cost * 1M / 10.5
        input_tokens = int(cost_usd * 1_000_000 / 10.5)
        output_tokens = input_tokens // 2

        return APICallFactory.create_api_call(
            input_tokens=input_tokens, output_tokens=output_tokens
        )

    @staticmethod
    def create_batch_api_calls(
        count: int = 10, total_cost_usd: float = 0.50
    ) -> list[dict[str, Any]]:
        """
        Create batch of API calls with specific total cost.

        Args:
            count: Number of API calls
            total_cost_usd: Total cost across all calls

        Returns:
            List of API call records
        """
        cost_per_call = total_cost_usd / count
        return [APICallFactory.create_expensive_api_call(cost_per_call) for _ in range(count)]
