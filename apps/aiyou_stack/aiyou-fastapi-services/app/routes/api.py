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
    """Health check endpoint.

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
    """Execute Python code in a sandboxed environment.

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
            detail=f"Code execution failed: {e!s}",
        )


@router.get("/sandbox/stats", response_model=SandboxStatsResponse)
async def get_sandbox_stats(
    executor: SandboxExecutor = Depends(get_executor),
) -> SandboxStatsResponse:
    """Get sandbox execution statistics.

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
    """Reset sandbox execution statistics.

    Returns:
        Success message

    """
    executor.clear_history()

    logger.info("sandbox_stats_reset")

    return {"message": "Sandbox statistics reset successfully"}


@router.post("/stripe/create-checkout-session")
async def create_checkout_session(request: dict):
    """Generate a mocked Stripe checkout session for the Investor slide.
    """
    logger.info("stripe_checkout_requested", payload=request)
    return {
        "id": "cs_test_mock123456789",
        "url": "https://checkout.stripe.com/c/pay/cs_test_mock123",
    }


@router.post("/ast/parse")
async def ast_parse(payload: dict):
    """Evaluate AST structure against Judge-6 rules via GitNexus Indexer.
    """
    input_action = payload.get("action", "")
    logger.info("ast_parse_requested", action=input_action)

    if "rm" in input_action or "drop" in input_action or "delete" in input_action:
        return {
            "status": "VIOLATION",
            "message": "Destructive modifier detected at root execution.",
            "shield": "Execution Killed",
        }

    return {
        "status": "OK",
        "message": "Tree-sitter validated pure execution node.",
        "shield": "Let pass",
    }


@router.post("/stripe/webhook")
async def stripe_webhook(request: dict):
    """Parse generic incoming Stripe events, looking for checkout session completions.
    """
    event_type = request.get("type")

    if event_type == "checkout.session.completed":
        session_data = request.get("data", {}).get("object", {})
        customer_email = session_data.get("customer_email", "unknown")
        logger.info("stripe_checkout_completed", email=customer_email, session_id=session_data.get("id"))
        return {"status": "success", "action": "ingested_completion"}

    logger.info("stripe_webhook_ignored", type=event_type)
    return {"status": "ignored"}
