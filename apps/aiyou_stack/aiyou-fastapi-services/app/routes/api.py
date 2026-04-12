"""API endpoints for code execution and health checks."""

import structlog
from fastapi import APIRouter, Depends, HTTPException

from app.config import AppSettings, get_settings
from app.models.schemas import (
    CodeExecutionRequest,
    CodeExecutionResponse,
    HealthResponse,
    SandboxStatsResponse,
)
from app.security.sandbox import SandboxExecutor

logger = structlog.get_logger()

router = APIRouter()

# Global executor instance (in production, consider dependency injection)
_executor: SandboxExecutor = None


def get_executor(settings: AppSettings = Depends(get_settings)) -> SandboxExecutor:
    """Get or create sandbox executor instance."""
    global _executor
    if _executor is None:
        _executor = SandboxExecutor(settings.sandbox)
    return _executor


@router.get("/health", response_model=HealthResponse)
async def health_check(
    settings: AppSettings = Depends(get_settings),
) -> HealthResponse:
    """
    Health check endpoint.

    Returns service health status and configuration information.
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        sandbox_enabled=settings.sandbox.enabled,
    )


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    executor: SandboxExecutor = Depends(get_executor),
    settings: AppSettings = Depends(get_settings),
) -> CodeExecutionResponse:
    """
    Execute Python code in a sandboxed environment.

    This endpoint provides secure code execution with the following protections:
    - RestrictedPython for safe code compilation
    - Resource limits (CPU, memory, execution time)
    - Blocked dangerous built-ins (eval, exec, etc.)
    - Whitelisted modules only
    - Process isolation

    Args:
        request: Code execution request containing code and optional timeout

    Returns:
        CodeExecutionResponse with execution results and metrics

    Raises:
        HTTPException: If sandboxing is disabled or execution fails critically
    """
    if not settings.sandbox.enabled:
        logger.error("code_execution_rejected", reason="sandbox_disabled")
        raise HTTPException(
            status_code=503,
            detail="Code execution is disabled (sandbox not enabled)",
        )

    logger.info(
        "code_execution_requested",
        code_length=len(request.code),
        timeout=request.timeout,
    )

    try:
        result = await executor.execute_async(
            code=request.code,
            timeout=request.timeout,
        )

        logger.info(
            "code_execution_completed",
            success=result.success,
            execution_time=result.execution_time,
            memory_used_mb=result.memory_used_mb,
        )

        return CodeExecutionResponse(
            success=result.success,
            output=result.output,
            error=result.error,
            execution_time=result.execution_time,
            memory_used_mb=result.memory_used_mb,
            cpu_percent=result.cpu_percent,
        )

    except Exception as e:
        logger.error(
            "code_execution_error",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Code execution failed: {str(e)}",
        )


@router.get("/sandbox/stats", response_model=SandboxStatsResponse)
async def get_sandbox_stats(
    executor: SandboxExecutor = Depends(get_executor),
) -> SandboxStatsResponse:
    """
    Get sandbox execution statistics.

    Returns:
        SandboxStatsResponse with execution history statistics
    """
    stats = executor.get_execution_stats()

    logger.info("sandbox_stats_requested", stats=stats)

    return SandboxStatsResponse(**stats)


@router.post("/sandbox/reset-stats")
async def reset_sandbox_stats(
    executor: SandboxExecutor = Depends(get_executor),
) -> dict:
    """
    Reset sandbox execution statistics.

    Returns:
        Success message
    """
    executor.clear_history()

    logger.info("sandbox_stats_reset")

    return {"message": "Sandbox statistics reset successfully"}
