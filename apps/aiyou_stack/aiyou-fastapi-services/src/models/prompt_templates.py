"""
Prompt Engineering Template Models
Supports: R-T-F, T-A-G, B-A-B, C-A-R-E, R-I-S-E frameworks
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class TemplateType(StrEnum):
    RTF = "R-T-F"
    TAG = "T-A-G"
    BAB = "B-A-B"
    CARE = "C-A-R-E"
    RISE = "R-I-S-E"


class RTFTemplate(BaseModel):
    """
    R-T-F Template: Role-Task-Format
    Simple and direct prompt structure
    """

    role: str = Field(..., description="The role the AI should act as")
    task: str = Field(..., description="The specific task to complete")
    format: str = Field(..., description="The desired output format")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "Facebook Ad Marketer",
                "task": "Design a compelling Facebook ad campaign to promote a new line of fitness apparel for a sports brand",
                "format": "Create a storyboard outlining the sequence of ad creatives, including ad copy, visuals, and targeting strategy",
            }
        }


class TAGTemplate(BaseModel):
    """
    T-A-G Template: Task-Action-Goal
    Focused on defining clear objectives and outcomes
    """

    task: str = Field(..., description="Define the task to be performed")
    action: str = Field(..., description="State the specific action to take")
    goal: str = Field(..., description="Clarify the desired goal or outcome")

    class Config:
        json_schema_extra = {
            "example": {
                "task": "Evaluate the performance of team members",
                "action": "Act as a Direct manager and assess the strengths and weaknesses of team members",
                "goal": "Improve team performance so that the average user satisfaction score moves from 6 to 7.5 in the next quarter",
            }
        }


class BABTemplate(BaseModel):
    """
    B-A-B Template: Before-After-Bridge
    Problem-solution focused prompting
    """

    before: str = Field(..., description="Explain the current problem state")
    after: str = Field(..., description="State the desired outcome")
    bridge: str = Field(..., description="Ask for the solution/plan to bridge the gap")

    class Config:
        json_schema_extra = {
            "example": {
                "before": "We're nowhere to be seen on SEO rankings",
                "after": "We want to be in top 10 SEO ranking in our niche in 90 days",
                "bridge": "Develop a detailed plan mentioning all the measures we should take also include list of top 20 keywords",
            }
        }


class CARETemplate(BaseModel):
    """
    C-A-R-E Template: Context-Action-Result-Example
    Comprehensive prompting with context and examples
    """

    context: str = Field(..., description="Give the background context")
    action: str = Field(..., description="Describe the action needed")
    result: str = Field(..., description="Clarify the expected result")
    example: str = Field(..., description="Give an example of similar success")

    class Config:
        json_schema_extra = {
            "example": {
                "context": "We are launching a new line of sustainable clothing",
                "action": "Can you assist us in creating a targeted advertising campaign that emphasizes our environmental commitment?",
                "result": "Our desired outcome is to drive product awareness and sales",
                "example": "A good example of a similar successful initiative is Patagonia's 'Don't Buy This Jacket' campaign, which highlighted their commitment to sustainability while enhancing their brand image",
            }
        }


class RISETemplate(BaseModel):
    """
    R-I-S-E Template: Role-Input-Steps-Expectation
    Detailed step-by-step approach with clear expectations
    """

    role: str = Field(..., description="Specify the role")
    input: str = Field(..., alias="input_data", description="Describe the input/data available")
    steps: str = Field(..., description="Ask for step-by-step process")
    expectation: str = Field(..., description="Describe the expected outcome")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "Imagine you are a content strategist",
                "input_data": "I've gathered detailed information about our target audience, including their interests & common questions related to our industry",
                "steps": "Provide a Step by Step content strategy plan identifying key topics based on our audience insights, creating an editorial calendar, and drafting engaging content that aligns with our brand message",
                "expectation": "Aim is to increase our blog's monthly visitors by 40% and enhance our brand's position as a thought leader in our industry",
            }
        }


class PromptTemplateResponse(BaseModel):
    """Response model for rendered prompt templates"""

    template_type: TemplateType
    rendered_prompt: str
    components: dict
    metadata: dict | None = None
