"""Performance monitoring API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.performance import PerformanceReport
from app.services.bottleneck_detector import BottleneckDetector
from app.services.caching import cache
from app.services.optimizer import PerformanceOptimizer

router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("/report", response_model=PerformanceReport)
async def get_performance_report(
    hours: int = Query(default=24, ge=1, le=168), session: AsyncSession = Depends(get_session),
):
    """Get comprehensive performance report

    Returns:
    - Total requests
    - Average response time
    - Slowest endpoints
    - Top bottlenecks
    - Optimization suggestions
    - Cache hit rate

    """
    detector = BottleneckDetector(session)
    optimizer = PerformanceOptimizer(session)

    # Get slow endpoints
    slow_endpoints = await detector.analyze_slow_endpoints(hours)

    # Get top bottlenecks
    bottlenecks = await detector.find_top_bottlenecks(limit=5)

    # Get optimization report
    opt_report = await optimizer.get_optimization_report()

    # Get cache statistics
    cache_stats = await cache.get_stats()

    # Calculate totals
    total_requests = sum(ep["request_count"] for ep in slow_endpoints)
    avg_response_time = (
        sum(ep["avg_duration"] * ep["request_count"] for ep in slow_endpoints) / total_requests
        if total_requests > 0
        else 0
    )

    return PerformanceReport(
        total_requests=total_requests,
        avg_response_time=round(avg_response_time, 4),
        slowest_endpoints=slow_endpoints[:10],
        top_bottlenecks=bottlenecks,
        optimization_suggestions=[
            {
                "id": i,
                "endpoint": s["endpoint"],
                "suggestion_type": s["type"],
                "description": s["description"],
                "impact": s["impact"],
                "implementation": s["implementation"],
                "created_at": "now",
                "applied": False,
            }
            for i, s in enumerate(opt_report["top_suggestions"])
        ],
        cache_hit_rate=cache_stats["hit_rate"],
        time_period=f"{hours} hours",
    )


@router.get("/bottlenecks")
async def get_bottlenecks(
    limit: int = Query(default=10, ge=1, le=100),
    endpoint: str | None = None,
    severity: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    """Get detected bottlenecks

    Find the exact lines of code making your app slow
    """
    detector = BottleneckDetector(session)
    bottlenecks = await detector.find_top_bottlenecks(limit, endpoint, severity)

    return {
        "count": len(bottlenecks),
        "bottlenecks": bottlenecks,
    }


@router.get("/bottlenecks/{bottleneck_id}/fix")
async def get_bottleneck_fix(bottleneck_id: int, session: AsyncSession = Depends(get_session)):
    """Get specific fix suggestions for a bottleneck

    Returns actionable code examples and optimization strategies
    """
    detector = BottleneckDetector(session)
    fix_suggestions = await detector.generate_fix_suggestions(bottleneck_id)

    if "error" in fix_suggestions:
        raise HTTPException(status_code=404, detail=fix_suggestions["error"])

    return fix_suggestions


@router.get("/slow-endpoints")
async def get_slow_endpoints(
    hours: int = Query(default=24, ge=1, le=168), session: AsyncSession = Depends(get_session),
):
    """Analyze slowest endpoints

    Returns detailed statistics and bottleneck information
    """
    detector = BottleneckDetector(session)
    slow_endpoints = await detector.analyze_slow_endpoints(hours)

    return {
        "count": len(slow_endpoints),
        "time_window_hours": hours,
        "endpoints": slow_endpoints,
    }


@router.get("/trends/{endpoint:path}")
async def get_endpoint_trends(
    endpoint: str,
    hours: int = Query(default=24, ge=1, le=168),
    session: AsyncSession = Depends(get_session),
):
    """Get performance trends for a specific endpoint

    Shows how performance changes over time
    """
    detector = BottleneckDetector(session)
    trends = await detector.get_performance_trends(f"/{endpoint}", hours)

    if "error" in trends:
        raise HTTPException(status_code=404, detail=trends["error"])

    return trends


@router.get("/n-plus-one")
async def detect_n_plus_one(session: AsyncSession = Depends(get_session)):
    """Detect N+1 query problems

    Identifies potential database performance issues
    """
    detector = BottleneckDetector(session)
    issues = await detector.detect_n_plus_one_queries()

    return {
        "count": len(issues),
        "issues": issues,
    }


@router.get("/memory-leaks")
async def detect_memory_leaks(
    hours: int = Query(default=24, ge=1, le=168), session: AsyncSession = Depends(get_session),
):
    """Detect potential memory leaks

    Finds endpoints with increasing memory usage
    """
    detector = BottleneckDetector(session)
    leaks = await detector.find_memory_leaks(hours)

    return {
        "count": len(leaks),
        "time_window_hours": hours,
        "potential_leaks": leaks,
    }


@router.get("/optimization-suggestions")
async def get_optimization_suggestions(session: AsyncSession = Depends(get_session)):
    """Get all optimization suggestions

    AI-generated recommendations to make your app faster
    """
    optimizer = PerformanceOptimizer(session)
    report = await optimizer.get_optimization_report()

    return report


@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics

    Returns cache hit/miss rates and suggestions
    """
    stats = await cache.get_stats()
    suggestions = cache.get_cache_suggestions()

    return {
        "stats": stats,
        "suggestions": suggestions,
    }


@router.post("/cache/clear")
async def clear_cache():
    """Clear all cache

    Warning: This will reset all cached data
    """
    success = await cache.clear()

    if success:
        return {"message": "Cache cleared successfully"}
    raise HTTPException(status_code=500, detail="Failed to clear cache")


@router.get("/summary")
async def get_performance_summary(session: AsyncSession = Depends(get_session)):
    """Get quick performance summary

    The 5 most important things to fix right now
    """
    detector = BottleneckDetector(session)
    optimizer = PerformanceOptimizer(session)

    # Get top 5 critical bottlenecks
    bottlenecks = await detector.find_top_bottlenecks(limit=5, severity="critical")

    # Get high-impact optimization suggestions
    opt_report = await optimizer.get_optimization_report()
    high_impact_suggestions = opt_report["top_suggestions"][:5]

    return {
        "title": "🔥 Performance Summary: Fix These 5 Things Now",
        "critical_bottlenecks": [
            {
                "location": f"{b.file_path}:{b.line_number}" if b.file_path else "unknown",
                "function": b.function_name,
                "impact": f"{b.percentage:.1f}% of request time",
                "severity": b.severity,
            }
            for b in bottlenecks
        ],
        "top_optimizations": high_impact_suggestions,
        "cache_stats": await cache.get_stats(),
    }
