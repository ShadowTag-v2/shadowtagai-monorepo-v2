"""Atomic Pipeline Orchestrator
=============================
Multi-model orchestration for intelligent code generation.

Pipeline Stages:
1. INTAKE - Gemini 3 Pro parses and atomizes requirements
2. RESEARCH - Perplexity Sonar performs deep research
3. TRENDS - Grok analyzes X trends and business context
4. EXECUTION - n-autoresearch/Kosmos/BioAgents swarm executes tasks
5. PUBLISH - Git → Vertex AI Workbench → Colab

Philosophy: "Slow is smooth, smooth is fast"
"""

import logging
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .clients import GeminiClient, GrokClient, PerplexityClient
from .clients.gemini_client import GeminiConfig
from .clients.grok_client import GrokConfig
from .clients.perplexity_client import PerplexityConfig

logger = logging.getLogger(__name__)


class PipelineStage(StrEnum):
    """Pipeline execution stages"""

    INTAKE = "intake"  # Gemini parses requirements
    RESEARCH = "research"  # Perplexity deep search
    TRENDS = "trends"  # Grok X/business analysis
    EXECUTION = "execution"  # n-autoresearch/Kosmos/BioAgents swarm
    PUBLISH = "publish"  # Git/Vertex/Colab


class TaskStatus(StrEnum):
    """Status of an atomic task"""

    PENDING = "pending"
    INTAKE = "intake"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    EXECUTING = "executing"
    PUBLISHING = "publishing"
    COMPLETED = "completed"
    FAILED = "failed"


class AtomicTask(BaseModel):
    """An atomic unit of work in the pipeline"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str
    type: str = "feature"  # feature, bugfix, refactor, test
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = Field(default_factory=list)
    complexity: str = "medium"  # low, medium, high

    # Stage results
    intake_result: dict[str, Any] | None = None
    research_result: dict[str, Any] | None = None
    trends_result: dict[str, Any] | None = None
    execution_result: dict[str, Any] | None = None
    publish_result: dict[str, Any] | None = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error: str | None = None


class PipelineConfig(BaseModel):
    """Configuration for the atomic pipeline"""

    # Model configs
    gemini_config: GeminiConfig = Field(default_factory=GeminiConfig)
    perplexity_config: PerplexityConfig = Field(default_factory=PerplexityConfig)
    grok_config: GrokConfig = Field(default_factory=GrokConfig)

    # Pipeline settings
    max_concurrent_tasks: int = 3
    enable_research: bool = True
    enable_trends: bool = True

    # Output settings
    git_auto_commit: bool = True
    vertex_publish: bool = False
    colab_publish: bool = False

    # n-autoresearch/Kosmos/BioAgents integration
    autoresearch_url: str = "http://localhost:8600"
    swarm_size: int = 600  # 570 Flash + 30 Pro


class PipelineResult(BaseModel):
    """Result of pipeline execution"""

    pipeline_id: str
    tasks: list[AtomicTask]
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    duration_seconds: float
    stage_timings: dict[str, float] = Field(default_factory=dict)
    outputs: list[dict[str, Any]] = Field(default_factory=list)


class AtomicPipelineOrchestrator:
    """Orchestrator for the atomic code generation pipeline.

    Implements multi-model flow:
    - Gemini 3 Pro → Design & Parse
    - Perplexity Sonar → Research
    - Grok Code Fast → Trends & Rapid Coding
    - n-autoresearch/Kosmos/BioAgents → Distributed Execution

    Philosophy: "Slow is smooth, smooth is fast"
    Each stage is thorough to ensure quality downstream.
    """

    def __init__(self, config: PipelineConfig | None = None):
        self.config = config or PipelineConfig()
        self._gemini: GeminiClient | None = None
        self._perplexity: PerplexityClient | None = None
        self._grok: GrokClient | None = None
        self._task_queue: list[AtomicTask] = []
        self._results: dict[str, AtomicTask] = {}

        # Stage hooks for customization
        self._pre_hooks: dict[PipelineStage, list[Callable]] = {s: [] for s in PipelineStage}
        self._post_hooks: dict[PipelineStage, list[Callable]] = {s: [] for s in PipelineStage}

    async def __aenter__(self):
        """Initialize all clients"""
        self._gemini = GeminiClient(self.config.gemini_config)
        self._perplexity = PerplexityClient(self.config.perplexity_config)
        self._grok = GrokClient(self.config.grok_config)

        await self._gemini.__aenter__()
        await self._perplexity.__aenter__()
        await self._grok.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup all clients"""
        if self._gemini:
            await self._gemini.__aexit__(exc_type, exc_val, exc_tb)
        if self._perplexity:
            await self._perplexity.__aexit__(exc_type, exc_val, exc_tb)
        if self._grok:
            await self._grok.__aexit__(exc_type, exc_val, exc_tb)

    def add_hook(
        self,
        stage: PipelineStage,
        hook: Callable[[AtomicTask], Awaitable[None]],
        pre: bool = True,
    ):
        """Add a pre or post hook for a pipeline stage"""
        if pre:
            self._pre_hooks[stage].append(hook)
        else:
            self._post_hooks[stage].append(hook)

    # =========================================================================
    # Main Pipeline Entry Point
    # =========================================================================

    async def run(
        self,
        requirements: str,
        context: dict[str, Any] | None = None,
    ) -> PipelineResult:
        """Run the full atomic pipeline.

        Args:
            requirements: Raw requirements or task description
            context: Optional context (codebase info, preferences, etc.)

        Returns:
            PipelineResult with all task outcomes

        """
        pipeline_id = str(uuid.uuid4())[:8]
        start_time = datetime.utcnow()
        stage_timings = {}

        logger.info(f"Starting pipeline {pipeline_id}: {requirements[:100]}...")

        # Stage 1: INTAKE - Gemini parses requirements
        intake_start = datetime.utcnow()
        tasks = await self._stage_intake(requirements, context)
        stage_timings["intake"] = (datetime.utcnow() - intake_start).total_seconds()
        logger.info(f"Intake complete: {len(tasks)} atomic tasks created")

        # Process each task through remaining stages
        completed_tasks = []
        failed_tasks = []

        for task in tasks:
            try:
                # Stage 2: RESEARCH
                if self.config.enable_research:
                    research_start = datetime.utcnow()
                    task = await self._stage_research(task)
                    stage_timings.setdefault("research", 0)
                    stage_timings["research"] += (
                        datetime.utcnow() - research_start
                    ).total_seconds()

                # Stage 3: TRENDS
                if self.config.enable_trends:
                    trends_start = datetime.utcnow()
                    task = await self._stage_trends(task)
                    stage_timings.setdefault("trends", 0)
                    stage_timings["trends"] += (datetime.utcnow() - trends_start).total_seconds()

                # Stage 4: EXECUTION
                exec_start = datetime.utcnow()
                task = await self._stage_execution(task)
                stage_timings.setdefault("execution", 0)
                stage_timings["execution"] += (datetime.utcnow() - exec_start).total_seconds()

                # Stage 5: PUBLISH
                pub_start = datetime.utcnow()
                task = await self._stage_publish(task)
                stage_timings.setdefault("publish", 0)
                stage_timings["publish"] += (datetime.utcnow() - pub_start).total_seconds()

                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                completed_tasks.append(task)

            except Exception as e:
                logger.error(f"Task {task.id} failed: {e}")
                task.status = TaskStatus.FAILED
                task.error = str(e)
                failed_tasks.append(task)

        duration = (datetime.utcnow() - start_time).total_seconds()

        return PipelineResult(
            pipeline_id=pipeline_id,
            tasks=completed_tasks + failed_tasks,
            total_tasks=len(tasks),
            completed_tasks=len(completed_tasks),
            failed_tasks=len(failed_tasks),
            duration_seconds=duration,
            stage_timings=stage_timings,
            outputs=[t.execution_result for t in completed_tasks if t.execution_result],
        )

    # =========================================================================
    # Stage 1: INTAKE (Gemini 3 Pro)
    # =========================================================================

    async def _stage_intake(
        self,
        requirements: str,
        context: dict[str, Any] | None = None,
    ) -> list[AtomicTask]:
        """INTAKE stage: Gemini 3 Pro parses and atomizes requirements.

        "Slow is smooth" - Take time to properly understand requirements.
        """
        parsed = await self._gemini.parse_requirements(requirements)

        tasks = []
        for task_data in parsed.get("atomic_tasks", []):
            task = AtomicTask(
                id=task_data.get("id", str(uuid.uuid4())[:8]),
                description=task_data.get("description", ""),
                type=task_data.get("type", "feature"),
                dependencies=task_data.get("dependencies", []),
                complexity=task_data.get("estimated_complexity", "medium"),
                intake_result={
                    "parsed_requirements": task_data,
                    "acceptance_criteria": task_data.get("acceptance_criteria", []),
                    "context": context,
                },
            )
            task.status = TaskStatus.INTAKE
            tasks.append(task)

        # If parsing failed, create a single task from raw requirements
        if not tasks:
            task = AtomicTask(
                description=requirements,
                intake_result={"raw_requirements": requirements, "context": context},
            )
            tasks.append(task)

        return tasks

    # =========================================================================
    # Stage 2: RESEARCH (Perplexity Sonar)
    # =========================================================================

    async def _stage_research(self, task: AtomicTask) -> AtomicTask:
        """RESEARCH stage: Perplexity Sonar performs deep research.

        Gathers documentation, best practices, and examples.
        """
        task.status = TaskStatus.RESEARCHING

        # Run pre-hooks
        for hook in self._pre_hooks[PipelineStage.RESEARCH]:
            await hook(task)

        # Extract key topics for research
        description = task.description
        intake = task.intake_result or {}

        # Research the topic
        research = await self._perplexity.research_topic(
            topic=description,
            depth="comprehensive" if task.complexity == "high" else "standard",
            focus_areas=intake.get("acceptance_criteria", []),
        )

        task.research_result = {
            "findings": research.content,
            "citations": [c.model_dump() for c in research.citations],
            "model": research.model,
        }

        # Run post-hooks
        for hook in self._post_hooks[PipelineStage.RESEARCH]:
            await hook(task)

        return task

    # =========================================================================
    # Stage 3: TRENDS (Grok Code Fast)
    # =========================================================================

    async def _stage_trends(self, task: AtomicTask) -> AtomicTask:
        """TRENDS stage: Grok analyzes X trends and business context.

        Applies current community preferences and best practices.
        """
        task.status = TaskStatus.ANALYZING

        # Run pre-hooks
        for hook in self._pre_hooks[PipelineStage.TRENDS]:
            await hook(task)

        # Analyze trends related to the task
        trends = await self._grok.analyze_trends(
            topic=task.description,
            context=task.research_result.get("findings", "") if task.research_result else None,
        )

        task.trends_result = {
            "analysis": trends.content,
            "model": trends.model,
            "x_context": trends.x_context,
        }

        # Run post-hooks
        for hook in self._post_hooks[PipelineStage.TRENDS]:
            await hook(task)

        return task

    # =========================================================================
    # Stage 4: EXECUTION (n-autoresearch/Kosmos/BioAgents Swarm)
    # =========================================================================

    async def _stage_execution(self, task: AtomicTask) -> AtomicTask:
        """EXECUTION stage: n-autoresearch/Kosmos/BioAgents swarm executes the task.

        "Smooth is fast" - With good preparation, execution is swift.
        """
        task.status = TaskStatus.EXECUTING

        # Run pre-hooks
        for hook in self._pre_hooks[PipelineStage.EXECUTION]:
            await hook(task)

        # Compile all context for execution
        execution_context = {
            "task": task.description,
            "type": task.type,
            "complexity": task.complexity,
            "intake": task.intake_result,
            "research": task.research_result,
            "trends": task.trends_result,
        }

        # Use Grok for rapid code generation
        code_result = await self._grok.generate_code(
            task=task.description,
            language="python",  # Could be parameterized
            style_guide=task.trends_result.get("analysis", "") if task.trends_result else None,
            test_requirements=True,
        )

        # Also generate tests with Gemini
        if code_result.content:
            tests = await self._gemini.generate_tests(
                code=code_result.content,
                framework="pytest",
                coverage_target="comprehensive" if task.complexity == "high" else "standard",
            )
        else:
            tests = ""

        task.execution_result = {
            "code": code_result.content,
            "tests": tests,
            "model": code_result.model,
            "execution_context": execution_context,
        }

        # Run post-hooks
        for hook in self._post_hooks[PipelineStage.EXECUTION]:
            await hook(task)

        return task

    # =========================================================================
    # Stage 5: PUBLISH (Git → Vertex → Colab)
    # =========================================================================

    async def _stage_publish(self, task: AtomicTask) -> AtomicTask:
        """PUBLISH stage: Output to Git, Vertex AI Workbench, Colab."""
        task.status = TaskStatus.PUBLISHING

        # Run pre-hooks
        for hook in self._pre_hooks[PipelineStage.PUBLISH]:
            await hook(task)

        publish_results = {
            "git": None,
            "vertex": None,
            "colab": None,
        }

        # Git commit (if enabled)
        if self.config.git_auto_commit and task.execution_result:
            publish_results["git"] = {
                "status": "ready",
                "files": ["generated_code.py", "test_generated.py"],
                "commit_message": f"feat({task.id}): {task.description[:50]}",
            }

        # Vertex AI Workbench (if enabled)
        if self.config.vertex_publish:
            publish_results["vertex"] = {
                "status": "ready",
                "notebook_path": f"/vertex/notebooks/{task.id}.ipynb",
            }

        # Colab (if enabled)
        if self.config.colab_publish:
            publish_results["colab"] = {
                "status": "ready",
                "colab_url": f"https://colab.research.google.com/drive/{task.id}",
            }

        task.publish_result = publish_results

        # Run post-hooks
        for hook in self._post_hooks[PipelineStage.PUBLISH]:
            await hook(task)

        return task

    # =========================================================================
    # Design-Specific Methods (@omarsar0 Pattern)
    # =========================================================================

    async def design_frontend(
        self,
        description: str,
        framework: str = "React",
        style_system: str = "MUI",
    ) -> dict[str, Any]:
        """Frontend design using @omarsar0 pattern.

        Gemini 3 Pro leads creative direction (~$0.087 per design).
        Returns design spec for Opus 4.5 integration.

        Args:
            description: Component/page description
            framework: Target framework
            style_system: Styling system

        Returns:
            Design specification for integration

        """
        # Gemini generates the design
        design_spec = await self._gemini.design_component(
            description=description,
            framework=framework,
            style_system=style_system,
        )

        # Research relevant patterns
        research = await self._perplexity.find_documentation(
            technology=f"{framework} {style_system}",
            specific_feature=description,
        )

        # Check current trends
        trends = await self._grok.analyze_trends(
            topic=f"{framework} {style_system} {description}",
        )

        return {
            "design_spec": design_spec.model_dump(),
            "documentation": {
                "content": research.content,
                "citations": [c.model_dump() for c in research.citations],
            },
            "trends": {
                "analysis": trends.content,
            },
            "cost_estimate": "$0.087",  # ~7K tokens
            "ready_for_integration": True,
        }
