"""
Ingestion Layer API endpoints for PNKLN Core Stack™
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.ingestion_analyzer import IngestionAnalyzer
from app.services.source_coverage import SourceCoverageAnalyzer
from app.services.ethical_compliance import EthicalComplianceMonitor
from app.models.ingestion import IngestionReport
from typing import Optional

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.get("/report", response_model=IngestionReport)
async def get_ingestion_report(
    hours: int = Query(default=24, ge=1, le=168),
    session: AsyncSession = Depends(get_session)
):
    """
    Get comprehensive ingestion layer report for PNKLN Core Stack™

    Returns:
    - Runtime efficiency (~45 min/night target)
    - Items collected per day
    - Multi-source coverage (YouTube, Twitter, News, etc.)
    - Cost metrics (~$77/month operational)
    - Quality gates (items, sources, costs, scores)
    - Tier distribution (Tier 1/2/3)
    - Ethical compliance (robots.txt, rate limiting)
    - AM briefing delivery effectiveness
    - Optimization suggestions
    """
    analyzer = IngestionAnalyzer(session)
    return await analyzer.generate_ingestion_report(hours)


@router.get("/runtime-efficiency")
async def get_runtime_efficiency(
    days: int = Query(default=7, ge=1, le=30),
    session: AsyncSession = Depends(get_session)
):
    """
    Analyze nightly batch job runtime efficiency

    Target: ~45 minutes per night (GKE CronJob)

    Returns detailed runtime statistics and optimization suggestions
    """
    analyzer = IngestionAnalyzer(session)
    return await analyzer.analyze_runtime_efficiency(days)


@router.get("/quality-gates")
async def check_quality_gates(
    hours: int = Query(default=24, ge=1, le=168),
    session: AsyncSession = Depends(get_session)
):
    """
    Check if ingestion meets quality gates

    Gates:
    - Daily items ≥ threshold
    - Source diversity ≥ threshold
    - Cost per item ≤ threshold
    - Average quality score ≥ threshold
    - Tier 1 percentage ≥ threshold
    - Ethical compliance ≥ threshold

    Returns PASS/FAIL status for each gate
    """
    analyzer = IngestionAnalyzer(session)
    return await analyzer.check_quality_gates(hours)


@router.get("/source-coverage")
async def get_source_coverage(
    hours: int = Query(default=24, ge=1, le=168),
    session: AsyncSession = Depends(get_session)
):
    """
    Analyze multi-source coverage

    Tracks: YouTube, Twitter, News, RSS, Web, API, Podcast, Research

    Returns coverage breakdown and diversity score
    """
    analyzer = SourceCoverageAnalyzer(session)
    return await analyzer.get_coverage_report()


@router.get("/source-coverage/gaps")
async def get_coverage_gaps(
    hours: int = Query(default=24, ge=1, le=168),
    session: AsyncSession = Depends(get_session)
):
    """
    Identify source coverage gaps

    Returns recommendations for improving source diversity
    """
    analyzer = SourceCoverageAnalyzer(session)
    return await analyzer.identify_gaps(hours)


@router.get("/source-coverage/{source_type}")
async def get_source_quality(
    source_type: str,
    hours: int = Query(default=24, ge=1, le=168),
    session: AsyncSession = Depends(get_session)
):
    """
    Get quality metrics for a specific source type

    Returns relevance, timeliness, completeness, and cost metrics
    """
    analyzer = SourceCoverageAnalyzer(session)
    return await analyzer.get_source_quality(source_type, hours)


@router.get("/tier-distribution")
async def get_tier_distribution(
    hours: int = Query(default=24, ge=1, le=168),
    session: AsyncSession = Depends(get_session)
):
    """
    Analyze tier distribution (Tier 1/2/3)

    Shows breakdown of high-value vs. low-value sources
    """
    analyzer = SourceCoverageAnalyzer(session)
    return await analyzer.get_tier_distribution(hours)


@router.get("/ethical-compliance")
async def get_ethical_compliance(
    session: AsyncSession = Depends(get_session)
):
    """
    Get ethical compliance report

    Includes:
    - robots.txt compliance
    - Rate limiting adherence
    - Transparency (user agent)
    - Recent violations
    - Compliance score (0-100)
    """
    monitor = EthicalComplianceMonitor(session)
    return await monitor.generate_compliance_report()


@router.get("/ethical-compliance/score")
async def get_compliance_score(
    hours: int = Query(default=24, ge=1, le=168),
    session: AsyncSession = Depends(get_session)
):
    """
    Get ethical compliance score

    Returns score (0-100) and breakdown by check type
    """
    monitor = EthicalComplianceMonitor(session)
    return await monitor.get_compliance_score(hours)


@router.get("/ethical-compliance/violations")
async def get_violations(
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_session)
):
    """
    Get recent ethical violations

    Returns list of violations for review and remediation
    """
    monitor = EthicalComplianceMonitor(session)
    violations = await monitor.get_violations(hours, limit)

    return {
        'count': len(violations),
        'violations': violations,
        'time_period_hours': hours,
    }


@router.get("/costs/monthly")
async def get_monthly_costs(
    month: str | None = Query(
        default=None,
        description="Month in YYYY-MM format (defaults to current month)"
    ),
    session: AsyncSession = Depends(get_session)
):
    """
    Track monthly operational costs

    Target: ~$77/month

    Returns:
    - Total cost
    - Budget remaining
    - Cost breakdown (API, compute, storage, network)
    - Cost per item
    - Projected end-of-month cost
    """
    analyzer = IngestionAnalyzer(session)
    return await analyzer.track_monthly_costs(month)


@router.get("/briefing-delivery")
async def get_briefing_delivery(
    days: int = Query(default=7, ge=1, le=30),
    session: AsyncSession = Depends(get_session)
):
    """
    Analyze AM briefing delivery effectiveness

    Returns:
    - On-time delivery rate
    - Average delay
    - Effectiveness scores
    - Recipient engagement
    """
    analyzer = IngestionAnalyzer(session)
    return await analyzer.analyze_briefing_delivery(days)


@router.get("/summary")
async def get_ingestion_summary(
    session: AsyncSession = Depends(get_session)
):
    """
    Get quick ingestion layer summary

    The most important metrics at a glance
    """
    analyzer = IngestionAnalyzer(session)

    # Get key metrics
    runtime = await analyzer.analyze_runtime_efficiency(7)
    gates = await analyzer.check_quality_gates(24)
    costs = await analyzer.track_monthly_costs()
    compliance_monitor = EthicalComplianceMonitor(session)
    compliance = await compliance_monitor.get_compliance_score(24)

    return {
        'title': '🔍 PNKLN Ingestion Layer Summary',
        'runtime_efficiency': {
            'target_minutes': 45,
            'actual_minutes': runtime['actual_avg_runtime_minutes'],
            'meets_target': runtime['meets_target'],
            'status': 'OK' if runtime['meets_target'] else 'SLOW',
        },
        'quality_gates': {
            'status': gates['overall_status'],
            'passed': gates['passed_count'],
            'total': gates['total_gates'],
        },
        'monthly_cost': {
            'spent': costs['total_cost'],
            'budget': costs['budget'],
            'remaining': costs['remaining_budget'],
            'status': costs['status'],
        },
        'ethical_compliance': {
            'score': compliance['overall_score'],
            'status': compliance['status'],
        },
        'quick_actions': [
            '1. Check /ingestion/report for full details',
            '2. Review /ingestion/quality-gates for gate status',
            '3. Check /ingestion/source-coverage/gaps for coverage improvements',
            '4. Monitor /ingestion/ethical-compliance for violations',
        ],
    }


@router.post("/check-robots-txt")
async def check_robots_txt(
    url: str = Query(..., description="URL to check against robots.txt"),
    session: AsyncSession = Depends(get_session)
):
    """
    Check if a URL is allowed by robots.txt

    Returns compliance status and details
    """
    monitor = EthicalComplianceMonitor(session)
    result = await monitor.check_robots_txt(url)

    return {
        'url': url,
        'result': result,
    }


@router.post("/check-rate-limit")
async def check_rate_limit(
    source_type: str = Query(..., description="Source type (youtube, twitter, etc.)"),
    source_identifier: str = Query(..., description="Unique source identifier"),
    session: AsyncSession = Depends(get_session)
):
    """
    Check if we're respecting rate limits for a source

    Returns wait time if rate limit would be violated
    """
    monitor = EthicalComplianceMonitor(session)
    result = await monitor.check_rate_limit(source_type, source_identifier)

    return {
        'source_type': source_type,
        'source_identifier': source_identifier,
        'result': result,
    }
