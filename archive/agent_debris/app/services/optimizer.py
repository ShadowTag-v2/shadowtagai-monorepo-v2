"""
Performance optimization recommendations engine
Automatically suggests and applies optimizations
"""

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.performance import (
    PerformanceMetric,
    Bottleneck,
    OptimizationSuggestion,
)
from app.core.config import settings
from datetime import datetime, timedelta
from typing import Any
from app.services.bottleneck_detector import BottleneckDetector


class PerformanceOptimizer:
    """
    Analyzes performance data and generates actionable optimization suggestions
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.detector = BottleneckDetector(session)

    async def generate_all_suggestions(self) -> list[dict[str, Any]]:
        """
        Generate all optimization suggestions based on current performance data
        """
        suggestions = []

        # Check for caching opportunities
        caching_suggestions = await self._suggest_caching()
        suggestions.extend(caching_suggestions)

        # Check for database optimizations
        db_suggestions = await self._suggest_database_optimizations()
        suggestions.extend(db_suggestions)

        # Check for async opportunities
        async_suggestions = await self._suggest_async_improvements()
        suggestions.extend(async_suggestions)

        # Check for code-level optimizations
        code_suggestions = await self._suggest_code_optimizations()
        suggestions.extend(code_suggestions)

        # Store suggestions in database
        for suggestion in suggestions:
            await self._store_suggestion(suggestion)

        return suggestions

    async def _suggest_caching(self) -> list[dict[str, Any]]:
        """
        Identify endpoints that would benefit from caching
        """
        suggestions = []
        cutoff_time = datetime.utcnow() - timedelta(hours=1)

        # Find endpoints with many identical requests
        query = (
            select(
                PerformanceMetric.endpoint,
                PerformanceMetric.method,
                func.count(PerformanceMetric.id).label("count"),
                func.avg(PerformanceMetric.duration).label("avg_duration"),
            )
            .where(PerformanceMetric.timestamp >= cutoff_time)
            .group_by(PerformanceMetric.endpoint, PerformanceMetric.method)
            .having(func.count(PerformanceMetric.id) > settings.CACHE_SUGGESTION_THRESHOLD)
            .order_by(desc("count"))
        )

        result = await self.session.execute(query)
        rows = result.all()

        for row in rows:
            potential_savings = row.avg_duration * row.count * 0.9  # 90% reduction

            suggestions.append(
                {
                    "endpoint": row.endpoint,
                    "type": "caching",
                    "impact": "high" if potential_savings > 10 else "medium",
                    "description": f"Cache responses for {row.endpoint} - called {row.count} times in last hour",
                    "implementation": f"""
# Add caching decorator to your endpoint:
from app.services.caching import cache_response

@cache_response('{row.endpoint.replace("/", "_")}', ttl=300)
async def your_endpoint():
    # Your existing code
    pass
                """,
                    "metrics": {
                        "current_calls": row.count,
                        "avg_duration": round(row.avg_duration, 4),
                        "potential_savings_seconds": round(potential_savings, 2),
                    },
                }
            )

        return suggestions

    async def _suggest_database_optimizations(self) -> list[dict[str, Any]]:
        """
        Suggest database-related optimizations
        """
        suggestions = []

        # Find N+1 query problems
        n_plus_one = await self.detector.detect_n_plus_one_queries()

        for issue in n_plus_one:
            suggestions.append(
                {
                    "endpoint": issue["endpoint"],
                    "type": "database",
                    "impact": "high",
                    "description": issue["issue"],
                    "implementation": """
# Fix N+1 queries with eager loading:
from sqlalchemy.orm import selectinload, joinedload

# Before (N+1 query):
users = await session.execute(select(User))
for user in users:
    posts = await session.execute(select(Post).where(Post.user_id == user.id))

# After (single query):
stmt = select(User).options(selectinload(User.posts))
users = await session.execute(stmt)
                """,
                    "metrics": {
                        "call_count": issue["call_count"],
                        "total_time": issue["total_time"],
                    },
                }
            )

        # Find slow queries
        slow_db_queries = await self._find_slow_database_queries()
        suggestions.extend(slow_db_queries)

        return suggestions

    async def _find_slow_database_queries(self) -> list[dict[str, Any]]:
        """Find slow database queries that need optimization"""
        suggestions = []

        query = (
            select(Bottleneck)
            .where(
                and_(
                    Bottleneck.duration > 0.1,  # > 100ms
                    (Bottleneck.function_name.like("%query%") | Bottleneck.function_name.like("%execute%")),
                )
            )
            .order_by(desc(Bottleneck.duration))
            .limit(5)
        )

        result = await self.session.execute(query)
        slow_queries = result.scalars().all()

        for query in slow_queries:
            suggestions.append(
                {
                    "endpoint": query.endpoint,
                    "type": "database",
                    "impact": "high" if query.duration > 0.5 else "medium",
                    "description": f"Slow database query in {query.function_name}",
                    "implementation": """
# Optimization strategies:

1. Add database indexes:
   CREATE INDEX idx_column_name ON table_name(column_name);

2. Use query optimization:
   - Select only needed columns
   - Add proper WHERE clauses
   - Use EXPLAIN to analyze query plan

3. Consider caching query results:
   @cache_response('query_result', ttl=300)
   async def get_data():
       return await db.execute(query)
                """,
                    "metrics": {
                        "duration": round(query.duration, 4),
                        "percentage": round(query.percentage, 2),
                    },
                }
            )

        return suggestions

    async def _suggest_async_improvements(self) -> list[dict[str, Any]]:
        """
        Suggest where async/await can improve performance
        """
        suggestions = []

        # Find bottlenecks with I/O operations
        query = (
            select(Bottleneck)
            .where(
                and_(
                    Bottleneck.duration > 0.05,
                    (
                        Bottleneck.function_name.like("%request%")
                        | Bottleneck.function_name.like("%read%")
                        | Bottleneck.function_name.like("%write%")
                        | Bottleneck.function_name.like("%fetch%")
                    ),
                )
            )
            .order_by(desc(Bottleneck.duration))
            .limit(5)
        )

        result = await self.session.execute(query)
        io_bottlenecks = result.scalars().all()

        for bottleneck in io_bottlenecks:
            if bottleneck.call_count > 1:
                suggestions.append(
                    {
                        "endpoint": bottleneck.endpoint,
                        "type": "async",
                        "impact": "high",
                        "description": f"Parallelize I/O operations in {bottleneck.function_name}",
                        "implementation": """
# Before (sequential - slow):
results = []
for item in items:
    result = await fetch_data(item)
    results.append(result)

# After (parallel - fast):
import asyncio
results = await asyncio.gather(*[fetch_data(item) for item in items])

# This can reduce execution time from N*T to T
# where N is number of items and T is time per operation
                    """,
                        "metrics": {
                            "call_count": bottleneck.call_count,
                            "total_time": round(bottleneck.duration, 4),
                            "potential_speedup": f"{bottleneck.call_count}x",
                        },
                    }
                )

        return suggestions

    async def _suggest_code_optimizations(self) -> list[dict[str, Any]]:
        """
        Suggest general code-level optimizations
        """
        suggestions = []

        # Find CPU-intensive bottlenecks
        query = select(Bottleneck).where(Bottleneck.percentage > 20).order_by(desc(Bottleneck.percentage)).limit(5)

        result = await self.session.execute(query)
        cpu_bottlenecks = result.scalars().all()

        for bottleneck in cpu_bottlenecks:
            suggestions.append(
                {
                    "endpoint": bottleneck.endpoint,
                    "type": "code_optimization",
                    "impact": "high" if bottleneck.percentage > 40 else "medium",
                    "description": f"{bottleneck.function_name} takes {bottleneck.percentage:.1f}% of request time",
                    "implementation": """
# Optimization strategies:

1. Use memoization/caching:
   from functools import lru_cache

   @lru_cache(maxsize=128)
   def expensive_function(arg):
       # computation
       return result

2. Move to background task if possible:
   from fastapi import BackgroundTasks

   @app.post("/process")
   async def process(background_tasks: BackgroundTasks):
       background_tasks.add_task(expensive_function)
       return {"status": "processing"}

3. Optimize algorithms:
   - Use appropriate data structures (set vs list)
   - Avoid nested loops where possible
   - Use generators for large datasets
                """,
                    "metrics": {
                        "percentage": round(bottleneck.percentage, 2),
                        "duration": round(bottleneck.duration, 4),
                    },
                }
            )

        return suggestions

    async def _store_suggestion(self, suggestion: dict[str, Any]):
        """Store suggestion in database"""
        try:
            opt_suggestion = OptimizationSuggestion(
                endpoint=suggestion["endpoint"],
                suggestion_type=suggestion["type"],
                description=suggestion["description"],
                impact=suggestion["impact"],
                implementation=suggestion["implementation"],
            )
            self.session.add(opt_suggestion)
            await self.session.commit()
        except Exception as e:
            print(f"Error storing suggestion: {e}")

    async def get_optimization_report(self) -> dict[str, Any]:
        """
        Generate a comprehensive optimization report
        """
        suggestions = await self.generate_all_suggestions()

        # Group by impact
        high_impact = [s for s in suggestions if s["impact"] == "high"]
        medium_impact = [s for s in suggestions if s["impact"] == "medium"]
        low_impact = [s for s in suggestions if s["impact"] == "low"]

        # Calculate potential improvements
        total_potential_savings = sum(s.get("metrics", {}).get("potential_savings_seconds", 0) for s in suggestions)

        return {
            "total_suggestions": len(suggestions),
            "by_impact": {
                "high": len(high_impact),
                "medium": len(medium_impact),
                "low": len(low_impact),
            },
            "by_type": {
                "caching": len([s for s in suggestions if s["type"] == "caching"]),
                "database": len([s for s in suggestions if s["type"] == "database"]),
                "async": len([s for s in suggestions if s["type"] == "async"]),
                "code": len([s for s in suggestions if s["type"] == "code_optimization"]),
            },
            "potential_savings_seconds": round(total_potential_savings, 2),
            "top_suggestions": high_impact[:5],
            "all_suggestions": suggestions,
        }
