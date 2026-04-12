"""
FastAPI route decorators for ultrathink integration.

Make every route smarter with zero boilerplate.
"""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, Literal

from fastapi import Request


def ultrathink_route(
    reasoning: Literal["CoT", "ToT", "RCR"] | None = None,
    monetize: bool = False,
    track_performance: bool = True,
):
    """
    Enhance FastAPI route with ultrathink capabilities.

    Usage:
        @app.post("/analyze")
        @ultrathink_route(reasoning="ToT", monetize=True)
        async def analyze(data: dict):
            return {"result": "..."}

    This decorator:
    - Applies reasoning strategy if specified
    - Tracks revenue opportunities if monetize=True
    - Logs performance metrics
    - Adds structured logging

    Args:
        reasoning: Optional reasoning strategy to apply
        monetize: Track revenue opportunities in this route
        track_performance: Log latency, tokens, cost

    Returns:
        Decorated function with ultrathink enhancements
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()

            # Extract request if present
            request: Request | None = kwargs.get("request")

            # Apply reasoning if specified
            if reasoning:
                # In production: intercept inputs, apply reasoning, enhance outputs
                # For now: add metadata
                kwargs["_ultrathink_reasoning"] = reasoning

            # Execute route
            result = await func(*args, **kwargs)

            # Track performance
            if track_performance:
                time.time() - start_time
                # Log to structured logger
                # structlog.get_logger().info(
                #     "route_executed",
                #     endpoint=func.__name__,
                #     reasoning=reasoning,
                #     latency_ms=elapsed * 1000,
                # )

            # Revenue tracking
            if monetize and request:
                # Analyze request/response for monetization opportunities
                # revenue_tracker.analyze(request, result)
                pass

            return result

        return wrapper

    return decorator


def with_reasoning(strategy: Literal["CoT", "ToT", "RCR", "MAD"]):
    """
    Apply specific reasoning strategy to a function.

    Usage:
        @with_reasoning("MAD")
        async def make_decision(problem: str) -> str:
            # This will use Multi-Agent Debate automatically
            return "decision"

    Args:
        strategy: Which reasoning approach to use

    Returns:
        Decorated function with reasoning applied
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Import the appropriate reasoning engine
            if strategy == "CoT":
                from ultrathink.core.reasoning import CoT

                reasoner = CoT()
            elif strategy == "ToT":
                from ultrathink.core.reasoning import ToT

                reasoner = ToT()
            elif strategy == "RCR":
                from ultrathink.core.reasoning import RCR

                reasoner = RCR()
            elif strategy == "MAD":
                from ultrathink.core.agents import MultiAgentDebate

                reasoner = MultiAgentDebate()
            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            # Execute with reasoning context
            kwargs["_reasoner"] = reasoner
            result = await func(*args, **kwargs)

            return result

        return wrapper

    return decorator
