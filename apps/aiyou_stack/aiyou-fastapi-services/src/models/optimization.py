"""Doing Less Better Results - Life/Work Optimization Framework
8 key areas for focused improvement
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class AreaType(StrEnum):
    RELATIONSHIPS = "Relationships"
    PERSONAL_GOALS = "Personal Goals"
    HEALTH_FITNESS = "Health & Fitness"
    LEARNING = "Learning"
    WORK_TASKS = "Work Tasks"
    ENERGY = "Energy"
    MONEY = "Money"
    MENTAL_CLARITY = "Mental Clarity"


class LifeArea(BaseModel):
    """A specific life area with optimization strategies"""

    area: AreaType
    current_state: str | None = Field(None, description="Current situation in this area")
    strategies: list[str] = Field(..., description="Specific strategies to implement")
    action_items: list[str] = Field(default_factory=list, description="Concrete action items")
    priority_level: int | None = Field(None, ge=1, le=10, description="Priority from 1-10")
    notes: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "area": "HEALTH_FITNESS",
                "current_state": "Inconsistent exercise routine, 1-2 times per month",
                "strategies": [
                    "Consistency beats intensity",
                    "Aim for 3 x 30-minute sessions a week",
                    "Focus on activities you enjoy for long-term success",
                ],
                "action_items": [
                    "Schedule 3 x 30-min workout slots in calendar",
                    "Choose enjoyable activities: swimming, hiking, cycling",
                    "Track consistency in habit tracker",
                ],
                "priority_level": 8,
            },
        }


class OptimizationStrategy(BaseModel):
    """Complete optimization strategy across all 8 areas"""

    name: str = Field(..., description="Name of this optimization plan")
    description: str | None = Field(None, description="Overall description and goals")

    # All 8 areas
    relationships: LifeArea | None = None
    personal_goals: LifeArea | None = None
    health_fitness: LifeArea | None = None
    learning: LifeArea | None = None
    work_tasks: LifeArea | None = None
    energy: LifeArea | None = None
    money: LifeArea | None = None
    mental_clarity: LifeArea | None = None

    focus_areas: list[AreaType] = Field(
        ..., description="Primary areas of focus (2-3 recommended)", max_length=3,
    )
    timeline: str | None = Field(None, description="Timeline for this optimization period")
    success_metrics: list[str] | None = Field(None, description="How to measure success")


class DoingLessBetterResults(BaseModel):
    """Complete Doing Less Better Results Framework
    Focuses on doing less but achieving better outcomes
    """

    strategy: OptimizationStrategy

    # Pre-filled framework defaults for each area
    framework_defaults: dict = Field(
        default={
            "RELATIONSHIPS": {
                "strategies": [
                    "Focus on the five people who inspire and energise you",
                    "Step back from connections that drain your energy",
                ],
            },
            "PERSONAL_GOALS": {
                "strategies": [
                    "Choose one or two goals that truly matter",
                    "Break them into small, actionable steps",
                ],
            },
            "HEALTH_FITNESS": {
                "strategies": [
                    "Consistency beats intensity",
                    "Aim for 3 x 30-minute sessions a week",
                    "Focus on activities you enjoy for long-term success",
                ],
            },
            "LEARNING": {
                "strategies": [
                    "Commit to learning one skill that aligns with your biggest goal",
                    "Decide the outcome you want and stick with it until you see results",
                ],
            },
            "WORK_TASKS": {
                "strategies": [
                    "Prioritize the three tasks that create the most value",
                    "Delegate or eliminate what doesn't move the needle",
                ],
            },
            "ENERGY": {
                "strategies": [
                    "Protect your time & energy by saying 'no' to things you don't want to do",
                    "Channel your energy into high impact tasks",
                ],
            },
            "MONEY": {
                "strategies": [
                    "Track your spending and cut three unnecessary expenses",
                    "Redirect savings to investments or experiences with long-term value",
                ],
            },
            "MENTAL_CLARITY": {
                "strategies": [
                    "Start your day with journaling or a quiet moment",
                    "Keep your workspace simple and organized to minimize distractions",
                ],
            },
        },
    )

    class Config:
        json_schema_extra = {
            "example": {
                "strategy": {
                    "name": "Q1 2024 Focus Plan",
                    "description": "Simplified approach focusing on health, learning, and work productivity",
                    "focus_areas": ["HEALTH_FITNESS", "LEARNING", "WORK_TASKS"],
                    "timeline": "January - March 2024",
                    "health_fitness": {
                        "area": "HEALTH_FITNESS",
                        "current_state": "Sporadic exercise",
                        "strategies": [
                            "Consistency beats intensity",
                            "3 x 30-minute sessions weekly",
                        ],
                        "action_items": [
                            "Monday/Wednesday/Friday: 30-min morning walks",
                            "Track in Habitica app",
                        ],
                        "priority_level": 9,
                    },
                },
            },
        }
