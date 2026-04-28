# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Prompt Engineering Templates API Routes
Endpoints for R-T-F, T-A-G, B-A-B, C-A-R-E, R-I-S-E templates
"""

from fastapi import APIRouter, HTTPException

from src.models.prompt_templates import (
    BABTemplate,
    CARETemplate,
    PromptTemplateResponse,
    RISETemplate,
    RTFTemplate,
    TAGTemplate,
    TemplateType,
)
from src.services.template_renderer import TemplateRenderer

router = APIRouter()
renderer = TemplateRenderer()


@router.get("/", summary="List all prompt template types")
async def list_prompt_templates():
    """Get a list of all available prompt engineering templates"""
    return {
        "templates": [
            {
                "type": "R-T-F",
                "name": "Role-Task-Format",
                "description": "Simple and direct prompt structure",
                "components": ["role", "task", "format"],
            },
            {
                "type": "T-A-G",
                "name": "Task-Action-Goal",
                "description": "Focused on defining clear objectives and outcomes",
                "components": ["task", "action", "goal"],
            },
            {
                "type": "B-A-B",
                "name": "Before-After-Bridge",
                "description": "Problem-solution focused prompting",
                "components": ["before", "after", "bridge"],
            },
            {
                "type": "C-A-R-E",
                "name": "Context-Action-Result-Example",
                "description": "Comprehensive prompting with context and examples",
                "components": ["context", "action", "result", "example"],
            },
            {
                "type": "R-I-S-E",
                "name": "Role-Input-Steps-Expectation",
                "description": "Detailed step-by-step approach with clear expectations",
                "components": ["role", "input", "steps", "expectation"],
            },
        ],
    }


@router.post("/rtf", response_model=PromptTemplateResponse, summary="Render R-T-F template")
async def render_rtf_template(template: RTFTemplate):
    """Render a Role-Task-Format (R-T-F) prompt template

    Simple and direct prompt structure ideal for straightforward tasks.
    """
    try:
        return renderer.render_rtf(template)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering template: {e!s}") from e


@router.post("/tag", response_model=PromptTemplateResponse, summary="Render T-A-G template")
async def render_tag_template(template: TAGTemplate):
    """Render a Task-Action-Goal (T-A-G) prompt template

    Focused on defining clear objectives and measurable outcomes.
    """
    try:
        return renderer.render_tag(template)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering template: {e!s}") from e


@router.post("/bab", response_model=PromptTemplateResponse, summary="Render B-A-B template")
async def render_bab_template(template: BABTemplate):
    """Render a Before-After-Bridge (B-A-B) prompt template

    Problem-solution focused prompting that clearly defines current state and desired outcome.
    """
    try:
        return renderer.render_bab(template)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering template: {e!s}") from e


@router.post("/care", response_model=PromptTemplateResponse, summary="Render C-A-R-E template")
async def render_care_template(template: CARETemplate):
    """Render a Context-Action-Result-Example (C-A-R-E) prompt template

    Comprehensive prompting with full context and reference examples.
    """
    try:
        return renderer.render_care(template)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering template: {e!s}") from e


@router.post("/rise", response_model=PromptTemplateResponse, summary="Render R-I-S-E template")
async def render_rise_template(template: RISETemplate):
    """Render a Role-Input-Steps-Expectation (R-I-S-E) prompt template

    Detailed step-by-step approach with clear expectations and specific role definition.
    """
    try:
        return renderer.render_rise(template)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering template: {e!s}") from e


@router.get("/examples/{template_type}", summary="Get example for specific template")
async def get_template_example(template_type: TemplateType):
    """Get a pre-filled example for a specific template type"""
    examples = {
        TemplateType.RTF: {
            "role": "Facebook Ad Marketer",
            "task": "Design a compelling Facebook ad campaign to promote a new line of fitness apparel for a sports brand",
            "format": "Create a storyboard outlining the sequence of ad creatives, including ad copy, visuals, and targeting strategy",
        },
        TemplateType.TAG: {
            "task": "Evaluate the performance of team members",
            "action": "Act as a Direct manager and assess the strengths and weaknesses of team members",
            "goal": "Improve team performance so that the average user satisfaction score moves from 6 to 7.5 in the next quarter",
        },
        TemplateType.BAB: {
            "before": "We're nowhere to be seen on SEO rankings",
            "after": "We want to be in top 10 SEO ranking in our niche in 90 days",
            "bridge": "Develop a detailed plan mentioning all the measures we should take also include list of top 20 keywords",
        },
        TemplateType.CARE: {
            "context": "We are launching a new line of sustainable clothing",
            "action": "Can you assist us in creating a targeted advertising campaign that emphasizes our environmental commitment?",
            "result": "Our desired outcome is to drive product awareness and sales",
            "example": "A good example of a similar successful initiative is Patagonia's 'Don't Buy This Jacket' campaign, which highlighted their commitment to sustainability while enhancing their brand image",
        },
        TemplateType.RISE: {
            "role": "Imagine you are a content strategist",
            "input_data": "I've gathered detailed information about our target audience, including their interests & common questions related to our industry",
            "steps": "Provide a Step by Step content strategy plan identifying key topics based on our audience insights, creating an editorial calendar, and drafting engaging content that aligns with our brand message",
            "expectation": "Aim is to increase our blog's monthly visitors by 40% and enhance our brand's position as a thought leader in our industry",
        },
    }

    if template_type not in examples:
        raise HTTPException(
            status_code=404,
            detail=f"No example found for template type: {template_type}",
        )

    return {"template_type": template_type, "example": examples[template_type]}
