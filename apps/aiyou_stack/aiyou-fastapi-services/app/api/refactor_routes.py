from fastapi import APIRouter, HTTPException, status

from app.models.refactor import AnalyzeRequest, AnalyzeResponse, RefactorRequest, RefactorResponse
from app.services.code_refactorer import CodeRefactorerService

router = APIRouter(prefix="/api/v1/refactor", tags=["Code Refactoring"])
refactorer_service = CodeRefactorerService()


@router.post(
    "/",
    response_model=RefactorResponse,
    summary="Refactor code",
    description="Refactor code to improve quality, readability, performance, or maintainability",
)
async def refactor_code(request: RefactorRequest) -> RefactorResponse:
    """Refactor code based on specified parameters.

    - **code**: The source code to refactor
    - **language**: Programming language of the code
    - **refactor_type**: Type of refactoring (cleanup, readability, performance, etc.)
    - **context**: Optional context about the code
    - **preserve_functionality**: Whether to maintain exact functionality
    """
    try:
        result = await refactorer_service.refactor_code(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Refactoring failed: {e!s}",
        )


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze code quality",
    description="Analyze code for quality issues, metrics, and improvement suggestions",
)
async def analyze_code(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze code without performing refactoring.

    - **code**: The source code to analyze
    - **language**: Programming language of the code

    Returns detailed analysis including:
    - Issues found (with severity and suggestions)
    - Code metrics (complexity, maintainability, etc.)
    - Improvement suggestions
    - Overall quality score
    """
    try:
        result = await refactorer_service.analyze_code(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Analysis failed: {e!s}",
        )


@router.get(
    "/health", summary="Health check", description="Check if the refactoring service is operational",
)
async def health_check():
    """Health check endpoint for the refactoring service."""
    return {"status": "healthy", "service": "code-refactorer", "version": "1.0.0"}
