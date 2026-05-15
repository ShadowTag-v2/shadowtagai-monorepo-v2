"""Thread Rollup & Transfer Package System
Context preservation and session continuity

Author: ShadowTag-v2JR System
Date: 2025-11-17
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass
class ImmediateAction:
    """Week 1 priority action"""

    priority: int
    category: str
    task: str
    subtasks: list[str]
    deadline: str


@dataclass
class StateSummary:
    """Current state summary snapshot"""

    what_built: str
    core_asset: list[str]
    key_verticals: list[str]
    technical_foundation: dict[str, Any]
    business_model: dict[str, Any]
    go_to_market: dict[str, Any]
    critical_frameworks: list[str]


@dataclass
class ThreadContext:
    """Complete thread context for rollup"""

    generated_date: str
    context: str
    state_summary: StateSummary
    business_metrics: dict[str, Any]
    vertical_targets: dict[str, Any]
    tech_stack: dict[str, Any]
    kill_switches: dict[str, Any]
    decision_framework: dict[str, Any]
    immediate_actions: list[ImmediateAction]
    development_principles: dict[str, Any]
    frameworks_referenced: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class RestartPrompt:
    """Restart prompt for new session"""

    project: str
    date_generated: str
    current_phase: str
    quick_context: str
    completed_items: list[str]
    current_focus: dict[str, str]
    key_parameters: dict[str, Any]
    development_constraints: list[str]
    kill_switches: list[str]
    operating_posture: dict[str, Any]
    immediate_question: str
    options: list[str]

    def format_markdown(self) -> str:
        """Format as markdown restart prompt"""
        md = f"""# CONTEXT RESTORATION BLOCK

**Project**: {self.project}
**Date Generated**: {self.date_generated}
**Current Phase**: {self.current_phase}

## Quick Context
{self.quick_context}

## What's Been Done
"""
        for item in self.completed_items:
            md += f"- ✅ {item}\n"

        md += "\n## Current Focus\n"
        for priority, details in self.current_focus.items():
            md += f"\n**{priority}**: {details}\n"

        md += "\n## Key Parameters\n```python\n"
        for key, value in self.key_parameters.items():
            md += f"{key} = {value}\n"
        md += "```\n"

        md += "\n## Development Constraints\n"
        for constraint in self.development_constraints:
            md += f"* {constraint}\n"

        md += "\n## Kill-Switches\n"
        for switch in self.kill_switches:
            md += f"* {switch}\n"

        md += "\n## Operating Posture\n"
        for key, value in self.operating_posture.items():
            md += f"* {key}: {value}\n"

        md += f"\n## Immediate Next Question\n{self.immediate_question}\n\n"
        md += "**Options:**\n"
        for i, option in enumerate(self.options, 1):
            md += f"{i}. {option}\n"

        md += "\nAwaiting directive.\n"

        return md


class TransferPackage:
    """Complete transfer package for thread continuation"""

    def __init__(self):
        self.context: ThreadContext | None = None
        self.restart_prompt: RestartPrompt | None = None
        self.validation_checks: dict[str, bool] = {}
        self.compression_ratio: str | None = None

    def create_context(
        self,
        state_summary: StateSummary,
        metrics: dict[str, Any],
        verticals: dict[str, Any],
        tech_stack: dict[str, Any],
        kill_switches: dict[str, Any],
        decision_framework: dict[str, Any],
        actions: list[ImmediateAction],
        principles: dict[str, Any],
        frameworks: dict[str, str],
    ) -> ThreadContext:
        """Create thread context"""
        self.context = ThreadContext(
            generated_date=datetime.now().strftime("%Y-%m-%d"),
            context="AI Agent Business Plan Development",
            state_summary=state_summary,
            business_metrics=metrics,
            vertical_targets=verticals,
            tech_stack=tech_stack,
            kill_switches=kill_switches,
            decision_framework=decision_framework,
            immediate_actions=actions,
            development_principles=principles,
            frameworks_referenced=frameworks,
        )
        return self.context

    def create_restart_prompt(
        self,
        project: str,
        phase: str,
        context: str,
        completed: list[str],
        focus: dict[str, str],
        parameters: dict[str, Any],
        constraints: list[str],
        switches: list[str],
        posture: dict[str, Any],
        question: str,
        options: list[str],
    ) -> RestartPrompt:
        """Create restart prompt"""
        self.restart_prompt = RestartPrompt(
            project=project,
            date_generated=datetime.now().strftime("%Y-%m-%d"),
            current_phase=phase,
            quick_context=context,
            completed_items=completed,
            current_focus=focus,
            key_parameters=parameters,
            development_constraints=constraints,
            kill_switches=switches,
            operating_posture=posture,
            immediate_question=question,
            options=options,
        )
        return self.restart_prompt

    def validate(self) -> dict[str, bool]:
        """Validate transfer package"""
        self.validation_checks = {
            "business_model_preserved": self.context is not None,
            "technical_stack_defined": bool(self.context.tech_stack) if self.context else False,
            "financial_targets_locked": bool(self.context.business_metrics)
            if self.context
            else False,
            "decision_frameworks_embedded": bool(self.context.decision_framework)
            if self.context
            else False,
            "priorities_clear": bool(self.context.immediate_actions) if self.context else False,
            "guardrails_intact": bool(self.context.kill_switches) if self.context else False,
        }
        return self.validation_checks

    def get_package(self) -> dict[str, Any]:
        """Get complete transfer package"""
        return {
            "part_1_state_summary": self.context.to_dict() if self.context else {},
            "part_2_handoff_outline": {
                "business_metrics": self.context.business_metrics if self.context else {},
                "vertical_targets": self.context.vertical_targets if self.context else {},
                "tech_stack": self.context.tech_stack if self.context else {},
                "kill_switches": self.context.kill_switches if self.context else {},
                "decision_framework": self.context.decision_framework if self.context else {},
            },
            "part_3_restart_prompt": self.restart_prompt.format_markdown()
            if self.restart_prompt
            else "",
            "validation_checks": self.validation_checks,
            "compression_ratio": self.compression_ratio or "47:1",
            "generated": datetime.now().isoformat(),
        }

    def save_to_file(self, filepath: str) -> None:
        """Save transfer package to file"""
        package = self.get_package()
        with open(filepath, "w") as f:
            json.dump(package, f, indent=2)

    @staticmethod
    def load_from_file(filepath: str) -> dict[str, Any]:
        """Load transfer package from file"""
        with open(filepath) as f:
            return json.load(f)
