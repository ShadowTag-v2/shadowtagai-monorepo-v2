from enum import Enum, StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RefactorType(StrEnum):
    """Types of refactoring operations."""

    CLEANUP = "cleanup"
    READABILITY = "readability"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    BEST_PRACTICES = "best_practices"
    TECHNICAL_DEBT = "technical_debt"
    FULL = "full"


class CodeLanguage(StrEnum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"


class RefactorRequest(BaseModel):
    """Request model for code refactoring."""

    code: str = Field(..., description="The code to refactor")
    language: CodeLanguage = Field(..., description="Programming language of the code")
    refactor_type: RefactorType = Field(
        default=RefactorType.FULL, description="Type of refactoring to perform"
    )
    context: str | None = Field(
        None, description="Additional context about the code (e.g., purpose, constraints)"
    )
    preserve_functionality: bool = Field(
        default=True, description="Ensure refactored code maintains original functionality"
    )


class CodeIssue(BaseModel):
    """Represents a code quality issue."""

    line_number: int | None = None
    severity: str  # "error", "warning", "info"
    category: str
    message: str
    suggestion: str | None = None


class RefactorResponse(BaseModel):
    """Response model for code refactoring."""

    original_code: str
    refactored_code: str
    issues_found: list[CodeIssue]
    improvements: list[str]
    complexity_before: dict[str, Any] | None = None
    complexity_after: dict[str, Any] | None = None
    explanation: str


class AnalyzeRequest(BaseModel):
    """Request model for code analysis only."""

    code: str = Field(..., description="The code to analyze")
    language: CodeLanguage = Field(..., description="Programming language of the code")


class AnalyzeResponse(BaseModel):
    """Response model for code analysis."""

    issues: list[CodeIssue]
    metrics: dict[str, Any]
    suggestions: list[str]
    overall_quality_score: float | None = None
