"""
Performance profiling middleware
Automatically profiles every request and stores metrics
"""

import asyncio
import cProfile
import io
import pstats
import time
import traceback
from collections.abc import Callable
from typing import Any

import psutil
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.database import async_session_maker
from app.models.performance import Bottleneck, PerformanceMetric


class PerformanceProfilingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that profiles every request and identifies bottlenecks
    """

    def __init__(self, app):
        super().__init__(app)
        self.process = psutil.Process()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Profile the request and store metrics"""

        if not settings.ENABLE_PROFILING:
            return await call_next(request)

        # Start timing
        start_time = time.time()

        # Get initial resource usage
        try:
            initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            initial_cpu = self.process.cpu_percent()
        except Exception:
            initial_memory = None
            initial_cpu = None

        # Profile the request if enabled
        profiler = None
        profile_data = None

        if settings.PROFILING_SAMPLE_RATE >= 1.0 or (
            settings.PROFILING_SAMPLE_RATE > 0
            and time.time() % (1 / settings.PROFILING_SAMPLE_RATE) < 1
        ):
            profiler = cProfile.Profile()
            profiler.enable()

        # Execute the request
        error = None
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            raise
        finally:
            # Stop profiling
            if profiler:
                profiler.disable()
                profile_data = self._extract_profile_data(profiler)

            # Calculate metrics
            duration = time.time() - start_time

            try:
                final_memory = self.process.memory_info().rss / 1024 / 1024
                memory_usage = final_memory - (initial_memory or final_memory)
                cpu_usage = self.process.cpu_percent()
            except Exception:
                memory_usage = None
                cpu_usage = None

            # Store metrics asynchronously
            asyncio.create_task(
                self._store_metrics(
                    request=request,
                    duration=duration,
                    status_code=status_code,
                    memory_usage=memory_usage,
                    cpu_usage=cpu_usage,
                    error=error,
                    profile_data=profile_data,
                )
            )

        # Add performance headers to response
        response.headers["X-Response-Time"] = f"{duration:.4f}s"
        if memory_usage:
            response.headers["X-Memory-Usage"] = f"{memory_usage:.2f}MB"

        return response

    def _extract_profile_data(self, profiler: cProfile.Profile) -> dict[str, Any]:
        """Extract useful data from profiler"""
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats("cumulative")

        # Get top 10 functions by cumulative time
        top_functions = []
        for func, (cc, _nc, tt, ct, _callers) in list(stats.stats.items())[:10]:
            filename, line, func_name = func
            top_functions.append(
                {
                    "file": filename,
                    "line": line,
                    "function": func_name,
                    "cumulative_time": ct,
                    "total_time": tt,
                    "calls": cc,
                }
            )

        return {"top_functions": top_functions}

    async def _store_metrics(
        self,
        request: Request,
        duration: float,
        status_code: int,
        memory_usage: float,
        cpu_usage: float,
        error: str,
        profile_data: dict[str, Any],
    ):
        """Store performance metrics to database"""
        try:
            async with async_session_maker() as session:
                # Store main metric
                metric = PerformanceMetric(
                    endpoint=str(request.url.path),
                    method=request.method,
                    duration=duration,
                    status_code=status_code,
                    memory_usage=memory_usage,
                    cpu_usage=cpu_usage,
                    query_params=dict(request.query_params),
                    error=error,
                )
                session.add(metric)

                # Store bottlenecks if we have profile data
                if profile_data and duration >= settings.BOTTLENECK_THRESHOLD:
                    await self._store_bottlenecks(session, request.url.path, profile_data, duration)

                await session.commit()
        except Exception as e:
            print(f"Error storing metrics: {e}")

    async def _store_bottlenecks(
        self, session, endpoint: str, profile_data: dict[str, Any], total_duration: float
    ):
        """Store detected bottlenecks"""
        for func_data in profile_data.get("top_functions", [])[:5]:
            # Calculate severity based on time percentage
            percentage = (func_data["cumulative_time"] / total_duration) * 100

            if percentage < 5:
                severity = "low"
            elif percentage < 15:
                severity = "medium"
            elif percentage < 30:
                severity = "high"
            else:
                severity = "critical"

            bottleneck = Bottleneck(
                endpoint=endpoint,
                line_number=func_data["line"],
                file_path=func_data["file"],
                function_name=func_data["function"],
                duration=func_data["cumulative_time"],
                call_count=func_data["calls"],
                percentage=percentage,
                severity=severity,
            )
            session.add(bottleneck)
