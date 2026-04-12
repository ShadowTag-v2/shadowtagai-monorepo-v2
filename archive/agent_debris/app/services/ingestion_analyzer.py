"""
Ingestion Layer Analysis for PNKLN Core Stack™
Monitors GKE CronJob batch processing, quality gates, and cost efficiency
"""
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ingestion import (
    IngestionJob,
    SourceMetric,
    CostTracking,
    BriefingDelivery,
    QualityGates,
    IngestionReport,
)
from app.services.source_coverage import SourceCoverageAnalyzer
from app.services.ethical_compliance import EthicalComplianceMonitor
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import calendar


class IngestionAnalyzer:
    """
    Analyzes ingestion layer performance for PNKLN Core Stack™

    Focuses on:
    - Runtime efficiency (~45 min/night target)
    - Quality gates (items, sources, costs, scores)
    - Cost tracking (~$77/month operational)
    - AM briefing delivery effectiveness
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.coverage_analyzer = SourceCoverageAnalyzer(session)
        self.compliance_monitor = EthicalComplianceMonitor(session)
        self.quality_gates = QualityGates()

    async def analyze_runtime_efficiency(
        self,
        days: int = 7
    ) -> dict[str, Any]:
        """
        Analyze nightly batch job runtime efficiency
        Target: ~45 minutes per night

        Returns runtime statistics and optimization suggestions
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)

        query = (
            select(
                IngestionJob.job_name,
                func.avg(IngestionJob.runtime_minutes).label('avg_runtime'),
                func.min(IngestionJob.runtime_minutes).label('min_runtime'),
                func.max(IngestionJob.runtime_minutes).label('max_runtime'),
                func.count(IngestionJob.id).label('run_count'),
                func.sum(IngestionJob.items_collected).label('total_items'),
                func.sum(IngestionJob.errors).label('total_errors'),
            )
            .where(
                and_(
                    IngestionJob.started_at >= cutoff_time,
                    IngestionJob.completed_at.isnot(None)
                )
            )
            .group_by(IngestionJob.job_name)
        )

        result = await self.session.execute(query)
        rows = result.all()

        jobs_analysis = []
        total_runtime = 0
        total_runs = 0

        for row in rows:
            avg_runtime = row.avg_runtime or 0
            total_runtime += avg_runtime * row.run_count
            total_runs += row.run_count

            # Check if meeting target
            target = self.quality_gates.runtime_threshold_minutes
            meets_target = avg_runtime <= target

            efficiency_percentage = (target / avg_runtime * 100) if avg_runtime > 0 else 0

            jobs_analysis.append({
                'job_name': row.job_name,
                'avg_runtime_minutes': round(avg_runtime, 2),
                'min_runtime_minutes': round(row.min_runtime or 0, 2),
                'max_runtime_minutes': round(row.max_runtime or 0, 2),
                'run_count': row.run_count,
                'total_items': row.total_items or 0,
                'total_errors': row.total_errors or 0,
                'meets_target': meets_target,
                'efficiency_percentage': round(efficiency_percentage, 2),
                'variance': round((row.max_runtime or 0) - (row.min_runtime or 0), 2),
            })

        overall_avg = (total_runtime / total_runs) if total_runs > 0 else 0

        return {
            'target_runtime_minutes': self.quality_gates.runtime_threshold_minutes,
            'actual_avg_runtime_minutes': round(overall_avg, 2),
            'meets_target': overall_avg <= self.quality_gates.runtime_threshold_minutes,
            'total_runs_analyzed': total_runs,
            'time_period_days': days,
            'jobs': jobs_analysis,
            'optimization_suggestions': self._generate_runtime_optimizations(
                jobs_analysis,
                overall_avg
            ),
        }

    def _generate_runtime_optimizations(
        self,
        jobs: list[dict[str, Any]],
        overall_avg: float
    ) -> list[dict[str, Any]]:
        """Generate optimization suggestions based on runtime analysis"""
        suggestions = []

        target = self.quality_gates.runtime_threshold_minutes

        # Check if exceeding target
        if overall_avg > target:
            overage = overall_avg - target
            suggestions.append({
                'priority': 'high',
                'issue': f'Average runtime {overall_avg:.1f} min exceeds target {target:.1f} min',
                'suggestion': 'Consider parallelizing slow jobs in GKE',
                'potential_savings_minutes': round(overage, 2),
            })

        # Find slowest jobs
        slow_jobs = [j for j in jobs if j['avg_runtime_minutes'] > target]
        for job in slow_jobs[:3]:  # Top 3 slowest
            suggestions.append({
                'priority': 'medium',
                'issue': f"{job['job_name']} takes {job['avg_runtime_minutes']:.1f} min",
                'suggestion': 'Optimize this job or split into parallel containers',
                'job_name': job['job_name'],
            })

        # Check for high variance (unstable runtimes)
        high_variance = [j for j in jobs if j.get('variance', 0) > 15]
        if high_variance:
            suggestions.append({
                'priority': 'low',
                'issue': f"{len(high_variance)} jobs have high runtime variance",
                'suggestion': 'Investigate resource contention or external API latency',
            })

        return suggestions

    async def check_quality_gates(
        self,
        hours: int = 24
    ) -> dict[str, Any]:
        """
        Check if ingestion meets quality gates

        Gates:
        - Daily items threshold (e.g., ≥1000 items/day)
        - Source diversity threshold (e.g., ≥5 unique sources)
        - Cost per item threshold (e.g., ≤$0.10/item)
        - Average quality score threshold (e.g., ≥70)
        - Tier 1 percentage threshold (e.g., ≥20%)
        - Ethical compliance threshold (e.g., ≥95%)
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Gate 1: Daily items
        items_query = (
            select(func.sum(IngestionJob.items_collected))
            .where(IngestionJob.started_at >= cutoff_time)
        )
        result = await self.session.execute(items_query)
        total_items = result.scalar() or 0
        daily_items = int(total_items * (24 / hours))

        # Gate 2: Source diversity
        coverage = await self.coverage_analyzer.analyze_coverage(hours)
        source_diversity = coverage.total_sources

        # Gate 3: Cost per item
        cost_query = (
            select(func.sum(SourceMetric.cost))
            .where(SourceMetric.timestamp >= cutoff_time)
        )
        result = await self.session.execute(cost_query)
        total_cost = result.scalar() or 0
        cost_per_item = (total_cost / total_items) if total_items > 0 else 0

        # Gate 4: Average quality scores
        quality_query = (
            select(
                func.avg(SourceMetric.relevance_score).label('avg_relevance'),
                func.avg(SourceMetric.timeliness_score).label('avg_timeliness'),
                func.avg(SourceMetric.completeness_score).label('avg_completeness'),
            )
            .where(SourceMetric.timestamp >= cutoff_time)
        )
        result = await self.session.execute(quality_query)
        quality_row = result.one()

        avg_score = (
            (quality_row.avg_relevance or 0) +
            (quality_row.avg_timeliness or 0) +
            (quality_row.avg_completeness or 0)
        ) / 3

        # Gate 5: Tier 1 percentage
        tier_dist = await self.coverage_analyzer.get_tier_distribution(hours)
        tier_1_percentage = tier_dist['percentages']['tier_1']

        # Gate 6: Ethical compliance
        compliance = await self.compliance_monitor.get_compliance_score(hours)
        ethical_score = compliance['overall_score']

        # Evaluate gates
        gates = {
            'daily_items': {
                'value': daily_items,
                'threshold': self.quality_gates.daily_items_threshold,
                'passed': daily_items >= self.quality_gates.daily_items_threshold,
                'status': 'PASS' if daily_items >= self.quality_gates.daily_items_threshold else 'FAIL',
            },
            'source_diversity': {
                'value': source_diversity,
                'threshold': self.quality_gates.source_diversity_threshold,
                'passed': source_diversity >= self.quality_gates.source_diversity_threshold,
                'status': 'PASS' if source_diversity >= self.quality_gates.source_diversity_threshold else 'FAIL',
            },
            'cost_per_item': {
                'value': round(cost_per_item, 4),
                'threshold': self.quality_gates.cost_per_item_threshold,
                'passed': cost_per_item <= self.quality_gates.cost_per_item_threshold,
                'status': 'PASS' if cost_per_item <= self.quality_gates.cost_per_item_threshold else 'FAIL',
            },
            'average_score': {
                'value': round(avg_score, 2),
                'threshold': self.quality_gates.average_score_threshold,
                'passed': avg_score >= self.quality_gates.average_score_threshold,
                'status': 'PASS' if avg_score >= self.quality_gates.average_score_threshold else 'FAIL',
            },
            'tier_1_percentage': {
                'value': tier_1_percentage,
                'threshold': self.quality_gates.tier_1_percentage_threshold,
                'passed': tier_1_percentage >= self.quality_gates.tier_1_percentage_threshold,
                'status': 'PASS' if tier_1_percentage >= self.quality_gates.tier_1_percentage_threshold else 'FAIL',
            },
            'ethical_compliance': {
                'value': ethical_score,
                'threshold': self.quality_gates.ethical_compliance_threshold,
                'passed': ethical_score >= self.quality_gates.ethical_compliance_threshold,
                'status': 'PASS' if ethical_score >= self.quality_gates.ethical_compliance_threshold else 'FAIL',
            },
        }

        # Overall status
        all_passed = all(gate['passed'] for gate in gates.values())

        return {
            'overall_status': 'PASS' if all_passed else 'FAIL',
            'gates': gates,
            'passed_count': sum(1 for gate in gates.values() if gate['passed']),
            'total_gates': len(gates),
            'time_period_hours': hours,
        }

    async def track_monthly_costs(
        self,
        month: str | None = None
    ) -> dict[str, Any]:
        """
        Track monthly operational costs
        Target: ~$77/month

        Args:
            month: YYYY-MM format (defaults to current month)
        """
        if not month:
            now = datetime.utcnow()
            month = f"{now.year}-{now.month:02d}"

        query = select(CostTracking).where(CostTracking.month == month)
        result = await self.session.execute(query)
        cost_record = result.scalar_one_or_none()

        if not cost_record:
            # No data for this month yet
            return {
                'month': month,
                'total_cost': 0.0,
                'budget': 77.0,
                'remaining_budget': 77.0,
                'cost_breakdown': {},
                'items_collected': 0,
                'cost_per_item': 0.0,
                'status': 'no_data',
            }

        remaining = cost_record.budget - cost_record.total_cost
        utilization = (cost_record.total_cost / cost_record.budget * 100) if cost_record.budget > 0 else 0

        return {
            'month': month,
            'total_cost': round(cost_record.total_cost, 2),
            'budget': cost_record.budget,
            'remaining_budget': round(remaining, 2),
            'budget_utilization': round(utilization, 2),
            'cost_breakdown': {
                'api_costs': round(cost_record.api_costs, 2),
                'compute_costs': round(cost_record.compute_costs, 2),
                'storage_costs': round(cost_record.storage_costs, 2),
                'network_costs': round(cost_record.network_costs, 2),
            },
            'items_collected': cost_record.items_collected,
            'cost_per_item': round(cost_record.cost_per_item, 4),
            'status': self._get_budget_status(utilization),
            'projection': self._project_monthly_cost(cost_record),
        }

    def _get_budget_status(self, utilization: float) -> str:
        """Get budget status based on utilization"""
        if utilization < 75:
            return 'healthy'
        elif utilization < 90:
            return 'warning'
        elif utilization < 100:
            return 'critical'
        else:
            return 'over_budget'

    def _project_monthly_cost(self, cost_record: CostTracking) -> dict[str, Any]:
        """Project end-of-month cost based on current spending"""
        now = datetime.utcnow()
        year, month = map(int, cost_record.month.split('-'))
        days_in_month = calendar.monthrange(year, month)[1]
        day_of_month = now.day if now.month == month else days_in_month

        daily_rate = cost_record.total_cost / day_of_month if day_of_month > 0 else 0
        projected_total = daily_rate * days_in_month

        return {
            'current_day': day_of_month,
            'days_in_month': days_in_month,
            'daily_rate': round(daily_rate, 2),
            'projected_total': round(projected_total, 2),
            'projected_overage': round(max(0, projected_total - cost_record.budget), 2),
        }

    async def analyze_briefing_delivery(
        self,
        days: int = 7
    ) -> dict[str, Any]:
        """
        Analyze AM briefing delivery effectiveness

        Returns:
        - On-time delivery rate
        - Average delay
        - Effectiveness scores
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)

        query = (
            select(BriefingDelivery)
            .where(BriefingDelivery.delivery_date >= cutoff_time)
            .order_by(desc(BriefingDelivery.delivery_date))
        )

        result = await self.session.execute(query)
        deliveries = result.scalars().all()

        if not deliveries:
            return {
                'total_deliveries': 0,
                'on_time_rate': 0,
                'status': 'no_data',
            }

        total = len(deliveries)
        on_time = sum(1 for d in deliveries if d.delivery_delay_minutes <= 5)
        avg_delay = sum(d.delivery_delay_minutes for d in deliveries) / total
        avg_effectiveness = sum(
            d.effectiveness_score for d in deliveries if d.effectiveness_score
        ) / len([d for d in deliveries if d.effectiveness_score]) if deliveries else 0

        return {
            'total_deliveries': total,
            'on_time_deliveries': on_time,
            'on_time_rate': round((on_time / total * 100) if total > 0 else 0, 2),
            'avg_delay_minutes': round(avg_delay, 2),
            'avg_effectiveness_score': round(avg_effectiveness, 2),
            'time_period_days': days,
            'status': 'excellent' if on_time / total >= 0.95 else 'good' if on_time / total >= 0.85 else 'needs_improvement',
        }

    async def generate_ingestion_report(
        self,
        hours: int = 24
    ) -> IngestionReport:
        """
        Generate comprehensive ingestion layer report

        Includes all key metrics for PNKLN Core Stack™
        """
        # Runtime efficiency
        runtime = await self.analyze_runtime_efficiency(7)

        # Items per day
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        items_query = select(func.sum(IngestionJob.items_collected)).where(
            IngestionJob.started_at >= cutoff_time
        )
        result = await self.session.execute(items_query)
        total_items = result.scalar() or 0
        items_per_day = int(total_items * (24 / hours))

        # Source coverage
        coverage_report = await self.coverage_analyzer.get_coverage_report()

        # Cost metrics
        current_month = datetime.utcnow().strftime("%Y-%m")
        cost_data = await self.track_monthly_costs(current_month)

        # Quality gates
        gates = await self.check_quality_gates(hours)

        # Tier distribution
        tier_dist = coverage_report['tier_distribution']

        # Ethical compliance
        compliance = await self.compliance_monitor.generate_compliance_report()

        # Briefing delivery
        briefing = await self.analyze_briefing_delivery(7)

        # Optimization suggestions
        optimizations = []
        optimizations.extend(runtime.get('optimization_suggestions', []))

        if coverage_report['coverage_gaps']:
            optimizations.append({
                'type': 'coverage',
                'priority': 'medium',
                'suggestion': f"{len(coverage_report['coverage_gaps'])} source coverage gaps detected",
                'details': coverage_report['coverage_gaps'][:3],
            })

        if not gates['overall_status'] == 'PASS':
            failed_gates = [name for name, gate in gates['gates'].items() if not gate['passed']]
            optimizations.append({
                'type': 'quality_gates',
                'priority': 'high',
                'suggestion': f"Quality gates failing: {', '.join(failed_gates)}",
            })

        return IngestionReport(
            runtime_efficiency=runtime,
            items_per_day=items_per_day,
            sources_coverage=coverage_report['coverage'],
            cost_metrics=cost_data,
            quality_gates=gates,
            tier_distribution=tier_dist,
            ethical_compliance=compliance,
            briefing_delivery=briefing,
            optimization_suggestions=optimizations,
        )
