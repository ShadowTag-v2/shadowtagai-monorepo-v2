"""
Bottleneck detection and analysis service
Finds the exact lines making your app slow
"""

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.performance import (
    PerformanceMetric,
    Bottleneck,
    BottleneckResponse,
)
from datetime import datetime, timedelta
from typing import Any


class BottleneckDetector:
    """
    Analyzes performance metrics to find bottlenecks
    and provides specific line-by-line recommendations
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_top_bottlenecks(self, limit: int = 5, endpoint: str = None, severity: str = None) -> list[BottleneckResponse]:
        """
        Find the top bottlenecks in the application

        Returns the specific functions/lines causing slowdowns
        """
        query = select(Bottleneck).order_by(desc(Bottleneck.percentage))

        if endpoint:
            query = query.where(Bottleneck.endpoint == endpoint)

        if severity:
            query = query.where(Bottleneck.severity == severity)

        query = query.limit(limit)

        result = await self.session.execute(query)
        bottlenecks = result.scalars().all()

        return [BottleneckResponse.from_orm(b) for b in bottlenecks]

    async def analyze_slow_endpoints(self, time_window_hours: int = 24) -> list[dict[str, Any]]:
        """
        Analyze which endpoints are slowest

        Returns detailed analysis of slow endpoints with statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)

        # Get average duration per endpoint
        query = (
            select(
                PerformanceMetric.endpoint,
                func.avg(PerformanceMetric.duration).label("avg_duration"),
                func.max(PerformanceMetric.duration).label("max_duration"),
                func.min(PerformanceMetric.duration).label("min_duration"),
                func.count(PerformanceMetric.id).label("request_count"),
            )
            .where(PerformanceMetric.timestamp >= cutoff_time)
            .group_by(PerformanceMetric.endpoint)
            .order_by(desc("avg_duration"))
            .limit(10)
        )

        result = await self.session.execute(query)
        rows = result.all()

        slow_endpoints = []
        for row in rows:
            # Get related bottlenecks for this endpoint
            bottleneck_query = select(Bottleneck).where(Bottleneck.endpoint == row.endpoint).order_by(desc(Bottleneck.percentage)).limit(3)
            bottleneck_result = await self.session.execute(bottleneck_query)
            bottlenecks = bottleneck_result.scalars().all()

            slow_endpoints.append(
                {
                    "endpoint": row.endpoint,
                    "avg_duration": round(row.avg_duration, 4),
                    "max_duration": round(row.max_duration, 4),
                    "min_duration": round(row.min_duration, 4),
                    "request_count": row.request_count,
                    "top_bottlenecks": [
                        {
                            "function": b.function_name,
                            "file": b.file_path,
                            "line": b.line_number,
                            "percentage": round(b.percentage, 2),
                            "severity": b.severity,
                        }
                        for b in bottlenecks
                    ],
                }
            )

        return slow_endpoints

    async def detect_n_plus_one_queries(self) -> list[dict[str, Any]]:
        """
        Detect potential N+1 query problems

        Identifies endpoints with high database call counts
        """
        # Look for bottlenecks with high call counts
        query = (
            select(Bottleneck)
            .where(
                and_(
                    Bottleneck.call_count > 50,
                    Bottleneck.function_name.like("%query%") | Bottleneck.function_name.like("%execute%") | Bottleneck.function_name.like("%fetch%"),
                )
            )
            .order_by(desc(Bottleneck.call_count))
            .limit(10)
        )

        result = await self.session.execute(query)
        potential_issues = result.scalars().all()

        return [
            {
                "endpoint": b.endpoint,
                "function": b.function_name,
                "file": b.file_path,
                "line": b.line_number,
                "call_count": b.call_count,
                "total_time": round(b.duration, 4),
                "issue": "Potential N+1 query - multiple database calls in loop",
                "suggestion": "Consider using eager loading or batch queries",
            }
            for b in potential_issues
        ]

    async def find_memory_leaks(self, time_window_hours: int = 24) -> list[dict[str, Any]]:
        """
        Detect potential memory leaks

        Finds endpoints with increasing memory usage over time
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)

        query = (
            select(
                PerformanceMetric.endpoint,
                func.avg(PerformanceMetric.memory_usage).label("avg_memory"),
                func.max(PerformanceMetric.memory_usage).label("max_memory"),
                func.count(PerformanceMetric.id).label("count"),
            )
            .where(and_(PerformanceMetric.timestamp >= cutoff_time, PerformanceMetric.memory_usage.isnot(None)))
            .group_by(PerformanceMetric.endpoint)
            .having(func.max(PerformanceMetric.memory_usage) > 100)  # > 100MB
            .order_by(desc("max_memory"))
        )

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                "endpoint": row.endpoint,
                "avg_memory_mb": round(row.avg_memory, 2),
                "max_memory_mb": round(row.max_memory, 2),
                "request_count": row.count,
                "severity": "critical" if row.max_memory > 500 else "high",
                "suggestion": "Review memory usage - potential memory leak",
            }
            for row in rows
        ]

    async def get_performance_trends(self, endpoint: str, hours: int = 24) -> dict[str, Any]:
        """
        Get performance trends for a specific endpoint

        Shows how performance changes over time
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        query = (
            select(PerformanceMetric)
            .where(and_(PerformanceMetric.endpoint == endpoint, PerformanceMetric.timestamp >= cutoff_time))
            .order_by(PerformanceMetric.timestamp)
        )

        result = await self.session.execute(query)
        metrics = result.scalars().all()

        if not metrics:
            return {"error": "No data available for this endpoint"}

        # Calculate trends
        durations = [m.duration for m in metrics]
        timestamps = [m.timestamp for m in metrics]

        return {
            "endpoint": endpoint,
            "period_hours": hours,
            "total_requests": len(metrics),
            "avg_duration": round(sum(durations) / len(durations), 4),
            "min_duration": round(min(durations), 4),
            "max_duration": round(max(durations), 4),
            "trend": "improving" if durations[-1] < durations[0] else "degrading",
            "data_points": [
                {
                    "timestamp": ts.isoformat(),
                    "duration": round(d, 4),
                }
                for ts, d in zip(timestamps[-20:], durations[-20:])
            ],
        }

    async def generate_fix_suggestions(self, bottleneck_id: int) -> dict[str, Any]:
        """
        Generate specific code fix suggestions for a bottleneck

        Provides actual code examples and optimization strategies
        """
        query = select(Bottleneck).where(Bottleneck.id == bottleneck_id)
        result = await self.session.execute(query)
        bottleneck = result.scalar_one_or_none()

        if not bottleneck:
            return {"error": "Bottleneck not found"}

        suggestions = []

        # Database-related fixes
        if any(keyword in bottleneck.function_name.lower() for keyword in ["query", "execute", "fetch", "select"]):
            suggestions.append(
                {
                    "type": "database_optimization",
                    "title": "Optimize Database Query",
                    "description": "Add indexes, use eager loading, or cache results",
                    "code_example": """
# Before (slow):
users = await db.query(User).all()
for user in users:
    posts = await db.query(Post).filter(Post.user_id == user.id).all()

# After (fast):
from sqlalchemy.orm import selectinload
users = await db.query(User).options(selectinload(User.posts)).all()
                """,
                    "impact": "high",
                }
            )

        # I/O related fixes
        if any(keyword in bottleneck.function_name.lower() for keyword in ["read", "write", "open", "request", "get", "post"]):
            suggestions.append(
                {
                    "type": "io_optimization",
                    "title": "Optimize I/O Operations",
                    "description": "Use async I/O, batch operations, or caching",
                    "code_example": """
# Before (slow):
results = []
for item in items:
    result = await fetch_data(item)
    results.append(result)

# After (fast):
import asyncio
results = await asyncio.gather(*[fetch_data(item) for item in items])
                """,
                    "impact": "high",
                }
            )

        # CPU-intensive fixes
        if bottleneck.percentage > 30:
            suggestions.append(
                {
                    "type": "cpu_optimization",
                    "title": "Optimize CPU-Intensive Code",
                    "description": "Use caching, memoization, or move to background task",
                    "code_example": """
# Before (slow):
def expensive_computation(data):
    # Heavy processing
    return result

# After (fast):
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(data):
    # Heavy processing
    return result
                """,
                    "impact": "medium",
                }
            )

        # General caching suggestion
        if bottleneck.call_count > 10:
            suggestions.append(
                {
                    "type": "caching",
                    "title": "Add Caching",
                    "description": "Cache the result to avoid repeated expensive operations",
                    "code_example": """
from app.services.caching import cache_response

@cache_response('my_endpoint', ttl=300)
async def my_endpoint(param: str):
    # Expensive operation
    return result
                """,
                    "impact": "high",
                }
            )

        return {
            "bottleneck": {
                "function": bottleneck.function_name,
                "file": bottleneck.file_path,
                "line": bottleneck.line_number,
                "duration": bottleneck.duration,
                "percentage": bottleneck.percentage,
                "severity": bottleneck.severity,
            },
            "suggestions": suggestions,
        }
