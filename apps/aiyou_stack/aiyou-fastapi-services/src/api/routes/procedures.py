"""Structured Problem Solving Process API Routes
Endpoints for Is/Is Not Diagram and 6-step problem solving methodology
"""

from fastapi import APIRouter, HTTPException

from src.models.problem_solving import (
    CorrectiveActionType,
    IsIsNotDiagram,
    ProblemSolvingTechnique,
    StructuredProblemSolvingProcess,
)
from src.services.template_renderer import TemplateRenderer

router = APIRouter()
renderer = TemplateRenderer()


@router.get("/", summary="Get problem-solving process overview")
async def get_procedure_overview():
    """Get an overview of the Structured Problem Solving Process"""
    return {
        "name": "Structured Problem Solving Process",
        "description": "6-step methodology for systematic problem resolution",
        "steps": [
            {
                "step": 1,
                "name": "Describe the Problem",
                "tool": "Is/Is Not Diagram",
                "purpose": "Clarify problem scope and boundaries",
            },
            {
                "step": 2,
                "name": "Identify and Analyze Potential Causes",
                "tools": [
                    "Cause & Effect Diagram (6M)",
                    "Process Flow",
                    "Pareto Analysis",
                    "Control Charts",
                    "Box Plots",
                ],
                "purpose": "Generate hypotheses and analyze existing data",
            },
            {
                "step": 3,
                "name": "Compare Causes to Facts",
                "tools": ["Contradiction Matrix", "Distinctions & Changes"],
                "purpose": "Validate hypotheses against facts from Step 1",
            },
            {
                "step": 4,
                "name": "Identify Root Cause(s)",
                "tools": [
                    "Scatter Diagram",
                    "Multi-Vari Chart",
                    "ANOVA",
                    "Component Swapping",
                    "Characterization Experiments",
                ],
                "purpose": "Collect additional data to confirm root causes",
            },
            {
                "step": 5,
                "name": "Determine Corrective Actions",
                "tools": ["FMEA", "Corrective Action Plan"],
                "types": ["Elimination", "Facilitation", "Mitigation", "Error Proofing"],
                "purpose": "Develop solutions to address root causes",
            },
            {
                "step": 6,
                "name": "Validate, Implement, and Standardize",
                "tools": ["Implementation Plan", "Capability Study", "Sampling Plan"],
                "purpose": "Execute solution and ensure sustained improvement",
            },
        ],
        "available_techniques": [technique.value for technique in ProblemSolvingTechnique],
        "corrective_action_types": [action.value for action in CorrectiveActionType],
    }


@router.post("/is-is-not", summary="Create Is/Is Not diagram")
async def create_is_is_not_diagram(diagram: IsIsNotDiagram):
    """Create and render an Is/Is Not Diagram

    This tool helps clarify the problem by defining what it IS and what it IS NOT
    across four key dimensions: WHAT, WHEN, WHERE, and EXTENT.
    """
    try:
        rendered = renderer.render_is_is_not_diagram(diagram)
        return {"diagram": diagram, "rendered": rendered}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating diagram: {e!s}")


@router.post("/problem-solving", summary="Create structured problem-solving process")
async def create_problem_solving_process(process: StructuredProblemSolvingProcess):
    """Create a complete Structured Problem Solving Process

    Supports all 6 steps of the methodology with integrated tools and techniques.
    """
    try:
        rendered = renderer.render_problem_solving_process(process)
        return {"process": process, "rendered": rendered}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating process: {e!s}")


@router.get("/problem-solving/example", summary="Get example problem-solving process")
async def get_problem_solving_example():
    """Get a pre-filled example of a problem-solving process"""
    return {
        "problem_title": "High defect rate in Product X-500",
        "is_is_not_diagram": {
            "problem_description": "Increased defect rate observed in X-500 production",
            "dimensions": [
                {
                    "dimension": "WHAT",
                    "is_value": "Surface finish defects on X-500 units",
                    "is_not_value": "Dimensional or functional defects",
                    "distinctions": "Only cosmetic surface issues, functionality not affected",
                },
                {
                    "dimension": "WHEN",
                    "is_value": "Started appearing in February 1999",
                    "is_not_value": "Not present in January 1999 or earlier",
                    "distinctions": "Sudden onset in early February",
                },
                {
                    "dimension": "WHERE",
                    "is_value": "Production Line 3 only",
                    "is_not_value": "Not occurring on Lines 1, 2, or 4",
                    "distinctions": "Line 3 uses older polishing equipment",
                },
                {
                    "dimension": "EXTENT",
                    "is_value": "Approximately 15% of units produced",
                    "is_not_value": "Not affecting all units",
                    "distinctions": "Intermittent occurrence, not consistent",
                },
            ],
            "timeline_notes": "Defects started 2/1/99, peaked in mid-February at 20%, currently at 15%",
            "change_points": [
                "New supplier for polishing compound introduced 1/15/99",
                "Maintenance schedule for Line 3 delayed from 1/25/99 to 2/15/99",
                "Temperature fluctuations in facility noted in early February",
            ],
        },
        "potential_causes": [
            "Polishing compound quality variation from new supplier",
            "Equipment calibration drift due to delayed maintenance",
            "Environmental conditions (temperature/humidity) affecting finish",
            "Operator technique differences on Line 3",
            "Material batch variation",
        ],
        "data_analysis_techniques": ["PARETO_ANALYSIS", "PROCESS_CONTROL_CHART", "BOX_PLOTS"],
        "analysis_findings": "Pareto analysis shows 80% of defects occur during second shift. Control charts indicate process capability degradation starting 2/1/99.",
        "root_causes": [
            "Equipment calibration drift on Line 3 polishing station",
            "Interaction between new polishing compound and delayed calibration",
        ],
        "corrective_actions": [
            {
                "action_type": "ELIMINATION",
                "description": "Perform immediate calibration of Line 3 polishing equipment",
                "responsible_party": "Maintenance Team",
                "target_date": "2024-12-20",
                "status": "in_progress",
            },
            {
                "action_type": "ERROR_PROOFING",
                "description": "Install automated calibration monitoring system with alerts",
                "responsible_party": "Engineering Team",
                "target_date": "2024-12-31",
                "status": "planned",
            },
            {
                "action_type": "MITIGATION",
                "description": "Establish weekly calibration verification protocol for all lines",
                "responsible_party": "Quality Team",
                "target_date": "2024-12-22",
                "status": "pending",
            },
        ],
        "implementation_plan": "Phase 1: Immediate calibration (Week 1). Phase 2: Install monitoring (Weeks 2-3). Phase 3: Standardize verification protocol (Week 4).",
        "status": "in_progress",
    }


@router.get("/techniques", summary="List all problem-solving techniques")
async def list_techniques():
    """Get a list of all available problem-solving techniques"""
    return {
        "data_collection_analysis": [
            "Pareto Analysis",
            "Process Control Chart",
            "Box Plots",
            "Checksheet",
            "Multi-Vari Chart",
        ],
        "cause_identification": ["Cause & Effect Diagram (6M)", "Process or Usage Flow"],
        "root_cause_validation": [
            "Scatter Diagram",
            "ANOVA",
            "Contingency Tables",
            "Response Surfaces",
            "Characterization Experiments",
            "Component Swapping Study",
        ],
        "solution_development": [
            "Failure Modes & Effects Analysis (FMEA)",
            "Corrective Action Plan",
        ],
        "implementation_validation": ["Capability Study", "Implementation Plan", "Sampling Plan"],
    }
