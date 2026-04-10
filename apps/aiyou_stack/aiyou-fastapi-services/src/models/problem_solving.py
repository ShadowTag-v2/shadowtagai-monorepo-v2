"""
Structured Problem Solving Process Models
Based on Is/Is Not Diagram methodology
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class DimensionType(StrEnum):
    WHAT = "WHAT"
    WHEN = "WHEN"
    WHERE = "WHERE"
    EXTENT = "EXTENT"


class IsIsNotDimension(BaseModel):
    """A single dimension in the Is/Is Not analysis"""

    dimension: DimensionType
    is_value: str = Field(..., description="What the problem IS")
    is_not_value: str = Field(..., description="What the problem IS NOT")
    distinctions: str | None = Field(None, description="Key distinctions between IS and IS NOT")


class IsIsNotDiagram(BaseModel):
    """
    Is/Is Not Diagram for problem definition
    Clarifies the scope and boundaries of a problem
    """

    problem_description: str = Field(..., description="Brief description of the problem")
    dimensions: list[IsIsNotDimension] = Field(..., description="IS/IS NOT dimensions")
    timeline_notes: str | None = Field(None, description="Timeline or chronological context")
    change_points: list[str] | None = Field(None, description="Identified change points")

    class Config:
        json_schema_extra = {
            "example": {
                "problem_description": "Product quality defects in manufacturing line",
                "dimensions": [
                    {
                        "dimension": "WHAT",
                        "is_value": "Defects in model X-500 units",
                        "is_not_value": "Defects in other product models",
                        "distinctions": "Issue specific to X-500 design",
                    },
                    {
                        "dimension": "WHERE",
                        "is_value": "Production line 3",
                        "is_not_value": "Production lines 1, 2, or 4",
                        "distinctions": "Line 3 has older equipment",
                    },
                ],
                "timeline_notes": "Started appearing in February 1999",
                "change_points": [
                    "New supplier introduced in January 1999",
                    "Equipment maintenance delayed",
                ],
            }
        }


class ProblemSolvingTechnique(StrEnum):
    PARETO_ANALYSIS = "Pareto Analysis"
    CAUSE_EFFECT_DIAGRAM = "Cause & Effect Diagram (6M)"
    PROCESS_CONTROL_CHART = "Process Control Chart"
    SCATTER_DIAGRAM = "Scatter Diagram"
    BOX_PLOTS = "Box Plots"
    MULTI_VARI_CHART = "Multi-Vari Chart"
    CAPABILITY_STUDY = "Capability Study"
    ANOVA = "ANOVA"
    CONTINGENCY_TABLES = "Contingency Tables"
    RESPONSE_SURFACES = "Response Surfaces"
    COMPONENT_SWAPPING = "Component Swapping Study"
    FMEA = "Failure Modes & Effects Analysis"


class CorrectiveActionType(StrEnum):
    ELIMINATION = "Elimination"
    FACILITATION = "Facilitation"
    MITIGATION = "Mitigation"
    ERROR_PROOFING = "Error Proofing/Flagging"


class CorrectiveAction(BaseModel):
    """A specific corrective action with implementation details"""

    action_type: CorrectiveActionType
    description: str
    responsible_party: str | None = None
    target_date: str | None = None
    status: str | None = "pending"


class ProblemSolvingStep(BaseModel):
    """A single step in the structured problem-solving process"""

    step_number: int
    step_name: str
    description: str
    techniques: list[ProblemSolvingTechnique]
    outputs: list[str] | None = None
    completed: bool = False


class StructuredProblemSolvingProcess(BaseModel):
    """
    Complete Structured Problem Solving Process
    6-step methodology with integrated tools and techniques
    """

    problem_id: str | None = None
    problem_title: str = Field(..., description="Title of the problem being solved")

    # Step 1: Problem Description
    is_is_not_diagram: IsIsNotDiagram

    # Step 2a: Potential Causes
    potential_causes: list[str] = Field(
        default_factory=list, description="Identified potential causes"
    )

    # Step 2b: Data Analysis
    data_analysis_techniques: list[ProblemSolvingTechnique] = Field(
        default_factory=list, description="Techniques used for data analysis"
    )
    analysis_findings: str | None = None

    # Step 3: Compare Causes to Facts
    cause_fact_comparison: dict[str, str] | None = None

    # Step 4: Root Cause Analysis
    root_causes: list[str] = Field(default_factory=list)
    validation_data: str | None = None

    # Step 5: Corrective Actions
    corrective_actions: list[CorrectiveAction] = Field(default_factory=list)

    # Step 6: Validation & Implementation
    implementation_plan: str | None = None
    validation_results: str | None = None
    standardization_notes: str | None = None

    # Metadata
    created_at: datetime | None = None
    updated_at: datetime | None = None
    owner: str | None = None
    status: str = "in_progress"

    class Config:
        json_schema_extra = {
            "example": {
                "problem_title": "High defect rate in Product X-500",
                "is_is_not_diagram": {
                    "problem_description": "Increased defect rate observed in X-500 production",
                    "dimensions": [
                        {
                            "dimension": "WHAT",
                            "is_value": "Surface finish defects",
                            "is_not_value": "Dimensional or functional defects",
                        }
                    ],
                },
                "potential_causes": [
                    "Material quality variation",
                    "Equipment calibration drift",
                    "Operator training gap",
                ],
                "root_causes": ["Equipment calibration drift on Line 3"],
                "corrective_actions": [
                    {
                        "action_type": "ERROR_PROOFING",
                        "description": "Install automated calibration monitoring system",
                        "responsible_party": "Maintenance Team",
                        "target_date": "2024-12-31",
                    }
                ],
            }
        }
