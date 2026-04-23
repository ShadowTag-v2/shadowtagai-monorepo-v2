"""Optimization and General Template API Routes
Endpoints for Doing Less Better Results and other templates
"""

from fastapi import APIRouter, HTTPException

from src.models.optimization import AreaType, DoingLessBetterResults
from src.services.template_renderer import TemplateRenderer

router = APIRouter()
renderer = TemplateRenderer()


@router.get("/", summary="List all available templates")
async def list_templates():
    """Get a list of all available template types"""
    return {
        "templates": [
            {
                "category": "Prompt Engineering",
                "endpoint": "/api/prompts",
                "templates": ["R-T-F", "T-A-G", "B-A-B", "C-A-R-E", "R-I-S-E"],
                "description": "Structured prompt engineering frameworks for AI interactions",
            },
            {
                "category": "Problem Solving",
                "endpoint": "/api/procedures",
                "templates": ["Is/Is Not Diagram", "6-Step Problem Solving Process"],
                "description": "Systematic problem-solving methodologies",
            },
            {
                "category": "Optimization",
                "endpoint": "/api/templates/optimization",
                "templates": ["Doing Less Better Results"],
                "description": "Life and work optimization frameworks",
            },
        ],
    }


@router.post("/optimization", summary="Create optimization strategy")
async def create_optimization_strategy(optimization: DoingLessBetterResults):
    """Create a Doing Less Better Results optimization strategy

    Focus on 2-3 key areas and implement targeted strategies for better outcomes.
    """
    try:
        rendered = renderer.render_optimization_strategy(optimization)
        return {
            "strategy": optimization.strategy,
            "rendered": rendered,
            "framework": "Doing Less Better Results",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating strategy: {e!s}") from e


@router.get("/optimization/framework", summary="Get optimization framework overview")
async def get_optimization_framework():
    """Get the complete Doing Less Better Results framework with default strategies"""
    return {
        "name": "Doing Less Better Results",
        "description": "Focus on doing less but achieving better outcomes across 8 key life areas",
        "principle": "Consistency and focus beat scattered effort",
        "areas": [
            {
                "area": "RELATIONSHIPS",
                "default_strategies": [
                    "Focus on the five people who inspire and energise you",
                    "Step back from connections that drain your energy",
                ],
            },
            {
                "area": "PERSONAL_GOALS",
                "default_strategies": [
                    "Choose one or two goals that truly matter",
                    "Break them into small, actionable steps",
                ],
            },
            {
                "area": "HEALTH_FITNESS",
                "default_strategies": [
                    "Consistency beats intensity",
                    "Aim for 3 x 30-minute sessions a week",
                    "Focus on activities you enjoy for long-term success",
                ],
            },
            {
                "area": "LEARNING",
                "default_strategies": [
                    "Commit to learning one skill that aligns with your biggest goal",
                    "Decide the outcome you want and stick with it until you see results",
                ],
            },
            {
                "area": "WORK_TASKS",
                "default_strategies": [
                    "Prioritize the three tasks that create the most value",
                    "Delegate or eliminate what doesn't move the needle",
                ],
            },
            {
                "area": "ENERGY",
                "default_strategies": [
                    "Protect your time & energy by saying 'no' to things you don't want to do",
                    "Channel your energy into high impact tasks",
                ],
            },
            {
                "area": "MONEY",
                "default_strategies": [
                    "Track your spending and cut three unnecessary expenses",
                    "Redirect savings to investments or experiences with long-term value",
                ],
            },
            {
                "area": "MENTAL_CLARITY",
                "default_strategies": [
                    "Start your day with journaling or a quiet moment",
                    "Keep your workspace simple and organized to minimize distractions",
                ],
            },
        ],
        "recommended_focus": "Choose 2-3 areas to focus on for maximum impact",
    }


@router.get("/optimization/example", summary="Get example optimization strategy")
async def get_optimization_example():
    """Get a pre-filled example of an optimization strategy"""
    return {
        "strategy": {
            "name": "Q1 2024 Focus Plan",
            "description": "Simplified approach focusing on health, learning, and work productivity",
            "focus_areas": ["HEALTH_FITNESS", "LEARNING", "WORK_TASKS"],
            "timeline": "January - March 2024",
            "health_fitness": {
                "area": "HEALTH_FITNESS",
                "current_state": "Sporadic exercise, 1-2 times per month",
                "strategies": [
                    "Consistency beats intensity",
                    "Aim for 3 x 30-minute sessions a week",
                    "Focus on activities you enjoy for long-term success",
                ],
                "action_items": [
                    "Schedule Monday/Wednesday/Friday 7am workout blocks",
                    "Join local swimming pool (enjoyable activity)",
                    "Track consistency in Habitica app",
                    "Start with 20-min sessions, build to 30-min",
                ],
                "priority_level": 9,
                "notes": "Swimming chosen because I enjoyed it in college",
            },
            "learning": {
                "area": "LEARNING",
                "current_state": "Trying to learn Python, React, and Spanish simultaneously",
                "strategies": [
                    "Commit to learning one skill that aligns with your biggest goal",
                    "Decide the outcome you want and stick with it until you see results",
                ],
                "action_items": [
                    "Focus ONLY on Python (most relevant to career goals)",
                    "Pause React and Spanish learning",
                    "Complete 'Python for Data Science' course by March 31",
                    "Build one real project using Python",
                    "30 minutes daily, every weekday morning",
                ],
                "priority_level": 8,
                "notes": "Dropping other skills to focus. Can revisit in Q2.",
            },
            "work_tasks": {
                "area": "WORK_TASKS",
                "current_state": "Overwhelmed with 15+ ongoing projects, difficulty prioritizing",
                "strategies": [
                    "Prioritize the three tasks that create the most value",
                    "Delegate or eliminate what doesn't move the needle",
                ],
                "action_items": [
                    "Identify top 3 high-impact projects: API redesign, customer dashboard, team automation",
                    "Delegate 5 low-impact projects to team members",
                    "Eliminate 7 projects that no longer align with goals",
                    "Weekly review every Monday to maintain focus",
                    "Block 2-hour deep work sessions daily for top 3 only",
                ],
                "priority_level": 10,
                "notes": "This is the biggest bottleneck. Saying no is critical.",
            },
            "success_metrics": [
                "Health: Achieve 10+ workout sessions per month for 3 consecutive months",
                "Learning: Complete Python course + deploy 1 real project",
                "Work: Ship all 3 priority projects by March 31",
                "Overall: Feel less overwhelmed, more energized by end of Q1",
            ],
        },
    }


@router.get("/areas", summary="List all life areas")
async def list_life_areas():
    """Get a list of all 8 life areas in the optimization framework"""
    return {
        "areas": [area.value for area in AreaType],
        "total": 8,
        "recommended_focus": "2-3 areas at a time",
    }
