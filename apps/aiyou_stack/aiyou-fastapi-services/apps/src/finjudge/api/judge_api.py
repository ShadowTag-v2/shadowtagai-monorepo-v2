import logging

from fastapi import APIRouter, BackgroundTasks, Header

from src.finjudge.core.billing import StripeManager
from src.finjudge.core.pure_judge import JudgeRequest, JudgeRuling, PureJudgeEngine
from src.ultrathink.finance.leaks import RevenueLeakDetector

# Setup Logger
logger = logging.getLogger("finjudge.api")
router = APIRouter()

# Initialize Engines
engine = PureJudgeEngine()
revenue_guard = RevenueLeakDetector()
billing = StripeManager()


async def check_revenue_leaks(tokens: int, tier: str):
    """Background task to check for revenue leaks without blocking the response.
    """
    # Simulate looking up revenue from billing system based on tier/tokens
    revenue = 0.0 if tier == "free" else (tokens / 1000) * 0.01  # Mock revenue calc

    log_entry = {"tokens_used": tokens, "revenue_generated": revenue, "tier": tier}

    warning = revenue_guard.analyze_transaction(log_entry)
    if warning:
        logger.warning(
            f"REVENUE LEAK DETECTED: {warning.description} [Severity: {warning.severity}]",
        )


@router.post("/v1/judge", response_model=JudgeRuling)
async def judge_decision(
    request: JudgeRequest,
    background_tasks: BackgroundTasks,
    x_api_key: str | None = Header(None),
):
    """Execute a ruling via the FinJudge Pure Engine.
    Includes Revenue Guard checks in the background.
    """
    # 1. Evaluate
    ruling = await engine.evaluate(request)

    # 2. Estimate Tokens (Mock)
    # In reality, this would count tokens from the LLM response
    estimated_tokens = len(request.intent_nl) // 4 + 500

    # 3. Determine Tier (Real Check)
    sub_status = billing.check_subscription(x_api_key or "")
    tier = "pro" if sub_status.is_active else "free"

    # 4. Trigger Revenue Guard
    background_tasks.add_task(check_revenue_leaks, estimated_tokens, tier)

    return ruling


@router.post("/v1/subscribe")
async def create_subscription(email: str, x_api_key: str = Header(...)):
    """Generate a Stripe Checkout link for upgrading to Pro.
    """
    # Use API key as user ID proxy for now
    checkout_url = billing.create_checkout_session(user_id=x_api_key, email=email)
    return {"checkout_url": checkout_url}
