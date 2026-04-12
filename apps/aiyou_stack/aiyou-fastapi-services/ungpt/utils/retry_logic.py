"""
Retry Logic with Exponential Backoff

Used across all UnGPT layers for resilient API calls.
"""

import asyncio
import random
from collections.abc import Callable
from functools import wraps
from typing import TypeVar

T = TypeVar("T")


class RetryExhausted(Exception):
    """All retry attempts exhausted"""

    pass


async def with_retry(
    func: Callable[..., T],
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    **kwargs,
) -> T:
    """
    Execute async function with exponential backoff retry.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
        exponential_base: Base for exponential calculation
        jitter: Add random jitter to delay
        **kwargs: Keyword arguments for func

    Returns:
        Result from successful function call

    Raises:
        RetryExhausted: If all retries fail
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            # Call the function
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        except Exception as e:
            last_exception = e

            if attempt == max_retries:
                # Final attempt failed
                break

            # Calculate delay
            delay = min(base_delay * (exponential_base**attempt), max_delay)

            # Add jitter
            if jitter:
                delay = delay * (0.5 + random.random())

            # Log retry
            print(f"  Retry {attempt + 1}/{max_retries}: {type(e).__name__} - waiting {delay:.1f}s")

            await asyncio.sleep(delay)

    raise RetryExhausted(f"All {max_retries} retries exhausted. Last error: {last_exception}")


def retry_decorator(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
    """
    Decorator version of retry logic.

    Usage:
        @retry_decorator(max_retries=3)
        async def my_api_call():
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await with_retry(
                func,
                *args,
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                **kwargs,
            )

        return wrapper

    return decorator
