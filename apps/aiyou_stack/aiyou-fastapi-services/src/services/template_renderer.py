# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Template Rendering Service
Converts template models into formatted prompts and documents
"""

from src.models.optimization import DoingLessBetterResults
from src.models.problem_solving import IsIsNotDiagram, StructuredProblemSolvingProcess
from src.models.prompt_templates import (
    BABTemplate,
    CARETemplate,
    PromptTemplateResponse,
    RISETemplate,
    RTFTemplate,
    TAGTemplate,
    TemplateType,
)


class TemplateRenderer:
    """Renders various template types into formatted prompts and documents"""

    @staticmethod
    def render_rtf(template: RTFTemplate) -> PromptTemplateResponse:
        """Render R-T-F template"""
        prompt = f"""Act as a {template.role}

Task: {template.task}

Output Format: {template.format}"""

        return PromptTemplateResponse(
            template_type=TemplateType.RTF,
            rendered_prompt=prompt,
            components={"role": template.role, "task": template.task, "format": template.format},
            metadata={"framework": "R-T-F: Role-Task-Format"},
        )

    @staticmethod
    def render_tag(template: TAGTemplate) -> PromptTemplateResponse:
        """Render T-A-G template"""
        prompt = f"""Task Definition:
{template.task}

Action Required:
{template.action}

Goal:
{template.goal}"""

        return PromptTemplateResponse(
            template_type=TemplateType.TAG,
            rendered_prompt=prompt,
            components={"task": template.task, "action": template.action, "goal": template.goal},
            metadata={"framework": "T-A-G: Task-Action-Goal"},
        )

    @staticmethod
    def render_bab(template: BABTemplate) -> PromptTemplateResponse:
        """Render B-A-B template"""
        prompt = f"""Current Situation (BEFORE):
{template.before}

Desired Outcome (AFTER):
{template.after}

Solution Required (BRIDGE):
{template.bridge}"""

        return PromptTemplateResponse(
            template_type=TemplateType.BAB,
            rendered_prompt=prompt,
            components={
                "before": template.before,
                "after": template.after,
                "bridge": template.bridge,
            },
            metadata={"framework": "B-A-B: Before-After-Bridge"},
        )

    @staticmethod
    def render_care(template: CARETemplate) -> PromptTemplateResponse:
        """Render C-A-R-E template"""
        prompt = f"""Context:
{template.context}

Action Requested:
{template.action}

Expected Result:
{template.result}

Reference Example:
{template.example}"""

        return PromptTemplateResponse(
            template_type=TemplateType.CARE,
            rendered_prompt=prompt,
            components={
                "context": template.context,
                "action": template.action,
                "result": template.result,
                "example": template.example,
            },
            metadata={"framework": "C-A-R-E: Context-Action-Result-Example"},
        )

    @staticmethod
    def render_rise(template: RISETemplate) -> PromptTemplateResponse:
        """Render R-I-S-E template"""
        prompt = f"""Role:
{template.role}

Available Input/Data:
{template.input}

Step-by-Step Approach:
{template.steps}

Expected Outcome:
{template.expectation}"""

        return PromptTemplateResponse(
            template_type=TemplateType.RISE,
            rendered_prompt=prompt,
            components={
                "role": template.role,
                "input": template.input,
                "steps": template.steps,
                "expectation": template.expectation,
            },
            metadata={"framework": "R-I-S-E: Role-Input-Steps-Expectation"},
        )

    @staticmethod
    def render_is_is_not_diagram(diagram: IsIsNotDiagram) -> str:
        """Render Is/Is Not Diagram as formatted text"""
        output = f"""IS / IS NOT ANALYSIS
{"=" * 80}

Problem Description: {diagram.problem_description}

"""

        # Dimensions table
        output += f"{'Dimension':<15} {'IS':<30} {'IS NOT':<30}\n"
        output += f"{'-' * 80}\n"

        for dim in diagram.dimensions:
            output += f"{dim.dimension.value:<15} {dim.is_value:<30} {dim.is_not_value:<30}\n"
            if dim.distinctions:
                output += f"{'Distinctions:':<15} {dim.distinctions}\n"
            output += "\n"

        if diagram.timeline_notes:
            output += f"\nTimeline Notes:\n{diagram.timeline_notes}\n"

        if diagram.change_points:
            output += "\nIdentified Change Points:\n"
            for i, point in enumerate(diagram.change_points, 1):
                output += f"  {i}. {point}\n"

        return output

    @staticmethod
    def render_problem_solving_process(process: StructuredProblemSolvingProcess) -> str:
        """Render complete Structured Problem Solving Process"""
        output = f"""STRUCTURED PROBLEM SOLVING PROCESS
{"=" * 80}

Problem: {process.problem_title}
Status: {process.status.upper()}

"""

        # Step 1: Is/Is Not Diagram
        output += "STEP 1: DESCRIBE THE PROBLEM\n"
        output += "-" * 80 + "\n\n"
        output += TemplateRenderer.render_is_is_not_diagram(process.is_is_not_diagram)
        output += "\n\n"

        # Step 2a: Potential Causes
        output += "STEP 2A: IDENTIFY POTENTIAL CAUSES\n"
        output += "-" * 80 + "\n"
        if process.potential_causes:
            for i, cause in enumerate(process.potential_causes, 1):
                output += f"  {i}. {cause}\n"
        else:
            output += "  (No causes identified yet)\n"
        output += "\n"

        # Step 2b: Data Analysis
        output += "STEP 2B: COLLECT, ORGANIZE, AND ANALYZE DATA\n"
        output += "-" * 80 + "\n"
        if process.data_analysis_techniques:
            output += "Techniques Used:\n"
            for technique in process.data_analysis_techniques:
                output += f"  • {technique.value}\n"
        if process.analysis_findings:
            output += f"\nFindings:\n{process.analysis_findings}\n"
        output += "\n"

        # Step 3: Compare Causes to Facts
        output += "STEP 3: COMPARE CAUSES TO THE FACTS\n"
        output += "-" * 80 + "\n"
        if process.cause_fact_comparison:
            for cause, fact in process.cause_fact_comparison.items():
                output += f"  Cause: {cause}\n"
                output += f"  Fact: {fact}\n\n"
        output += "\n"

        # Step 4: Root Causes
        output += "STEP 4: IDENTIFY ROOT CAUSE(S)\n"
        output += "-" * 80 + "\n"
        if process.root_causes:
            for i, cause in enumerate(process.root_causes, 1):
                output += f"  {i}. {cause}\n"
        if process.validation_data:
            output += f"\nValidation Data:\n{process.validation_data}\n"
        output += "\n"

        # Step 5: Corrective Actions
        output += "STEP 5: DETERMINE CORRECTIVE ACTIONS\n"
        output += "-" * 80 + "\n"
        if process.corrective_actions:
            for i, action in enumerate(process.corrective_actions, 1):
                output += f"  {i}. [{action.action_type.value}] {action.description}\n"
                if action.responsible_party:
                    output += f"     Responsible: {action.responsible_party}\n"
                if action.target_date:
                    output += f"     Target Date: {action.target_date}\n"
                output += f"     Status: {action.status}\n\n"
        output += "\n"

        # Step 6: Validation & Implementation
        output += "STEP 6: VALIDATE, IMPLEMENT, AND STANDARDIZE\n"
        output += "-" * 80 + "\n"
        if process.implementation_plan:
            output += f"Implementation Plan:\n{process.implementation_plan}\n\n"
        if process.validation_results:
            output += f"Validation Results:\n{process.validation_results}\n\n"
        if process.standardization_notes:
            output += f"Standardization:\n{process.standardization_notes}\n"

        return output

    @staticmethod
    def render_optimization_strategy(optimization: DoingLessBetterResults) -> str:
        """Render Doing Less Better Results framework"""
        strategy = optimization.strategy

        output = f"""DOING LESS, BETTER RESULTS
{"=" * 80}

Strategy: {strategy.name}
"""

        if strategy.description:
            output += f"\n{strategy.description}\n"

        output += f"\nFocus Areas: {', '.join([area.value for area in strategy.focus_areas])}\n"

        if strategy.timeline:
            output += f"Timeline: {strategy.timeline}\n"

        output += "\n" + "=" * 80 + "\n\n"

        # Render each area
        areas = [
            ("1. RELATIONSHIPS", strategy.relationships),
            ("2. PERSONAL GOALS", strategy.personal_goals),
            ("3. HEALTH & FITNESS", strategy.health_fitness),
            ("4. LEARNING", strategy.learning),
            ("5. WORK TASKS", strategy.work_tasks),
            ("6. ENERGY", strategy.energy),
            ("7. MONEY", strategy.money),
            ("8. MENTAL CLARITY", strategy.mental_clarity),
        ]

        for title, area in areas:
            if area:
                output += f"{title}\n"
                output += "-" * 80 + "\n"

                if area.current_state:
                    output += f"Current State: {area.current_state}\n\n"

                output += "Strategies:\n"
                for strat in area.strategies:
                    output += f"  • {strat}\n"

                if area.action_items:
                    output += "\nAction Items:\n"
                    for item in area.action_items:
                        output += f"  ☐ {item}\n"

                if area.priority_level:
                    output += f"\nPriority Level: {area.priority_level}/10\n"

                if area.notes:
                    output += f"\nNotes: {area.notes}\n"

                output += "\n"

        if strategy.success_metrics:
            output += "SUCCESS METRICS\n"
            output += "-" * 80 + "\n"
            for metric in strategy.success_metrics:
                output += f"  • {metric}\n"

        return output
