"""
Ethical Compliance Monitoring for PNKLN Ingestion Layer
Ensures crawling respects robots.txt, rate limits, and transparency requirements
"""
from sqlalchemy import select, func, and_, desc, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ingestion import EthicalCompliance
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse
import aiohttp
import asyncio


class EthicalComplianceMonitor:
    """
    Monitors and enforces ethical crawling practices
    - robots.txt compliance
    - Rate limiting
    - Transparency (user agent, contact info)
    - Terms of service adherence
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_agent = "PNKLNBot/1.0 (+https://pnkln.ai/bot; Intelligence Collection)"
        self.rate_limits = {
            'default': 1.0,  # 1 request per second default
            'youtube': 2.0,  # 2 seconds between requests
            'twitter': 1.5,
            'news': 0.5,
        }
        self.last_request_times = {}

    async def check_robots_txt(self, url: str) -> dict[str, Any]:
        """
        Check if URL is allowed by robots.txt

        Returns:
            - is_compliant: bool
            - details: str (explanation)
            - allowed: bool
        """
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

            async with aiohttp.ClientSession() as client:
                async with client.get(
                    robots_url,
                    headers={'User-Agent': self.user_agent},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        robots_content = await response.text()

                        # Simple robots.txt parsing (production should use robotparser)
                        is_allowed = self._parse_robots_txt(
                            robots_content,
                            parsed.path
                        )

                        # Store compliance check
                        await self._store_compliance_check(
                            url,
                            'robots_txt',
                            is_allowed,
                            f"robots.txt check: {'allowed' if is_allowed else 'disallowed'}"
                        )

                        return {
                            'is_compliant': is_allowed,
                            'details': f"Checked {robots_url}",
                            'allowed': is_allowed,
                        }
                    else:
                        # No robots.txt found - assume allowed
                        return {
                            'is_compliant': True,
                            'details': 'No robots.txt found - assuming allowed',
                            'allowed': True,
                        }

        except Exception as e:
            # On error, assume allowed but log it
            await self._store_compliance_check(
                url,
                'robots_txt',
                True,
                f"Error checking robots.txt: {str(e)}"
            )
            return {
                'is_compliant': True,
                'details': f"Error: {str(e)} - assuming allowed",
                'allowed': True,
            }

    def _parse_robots_txt(self, content: str, path: str) -> bool:
        """
        Simple robots.txt parser
        Production should use urllib.robotparser
        """
        lines = content.split('\n')
        user_agent_match = False

        for line in lines:
            line = line.strip()

            if line.lower().startswith('user-agent:'):
                agent = line.split(':', 1)[1].strip()
                user_agent_match = (agent == '*' or 'pnkln' in agent.lower())

            if user_agent_match and line.lower().startswith('disallow:'):
                disallowed = line.split(':', 1)[1].strip()
                if disallowed and path.startswith(disallowed):
                    return False

        return True

    async def check_rate_limit(
        self,
        source_type: str,
        source_identifier: str
    ) -> dict[str, Any]:
        """
        Check if we're respecting rate limits for this source

        Args:
            source_type: 'youtube', 'twitter', 'news', etc.
            source_identifier: Unique source ID

        Returns:
            - is_compliant: bool
            - wait_seconds: float (time to wait)
            - details: str
        """
        limit_key = f"{source_type}:{source_identifier}"
        current_time = datetime.utcnow()

        # Get rate limit for this source type
        rate_limit_seconds = self.rate_limits.get(source_type, 1.0)

        if limit_key in self.last_request_times:
            last_request = self.last_request_times[limit_key]
            elapsed = (current_time - last_request).total_seconds()

            if elapsed < rate_limit_seconds:
                # Too soon - not compliant
                wait_time = rate_limit_seconds - elapsed

                await self._store_compliance_check(
                    limit_key,
                    'rate_limit',
                    False,
                    f"Rate limit violated: {elapsed:.2f}s < {rate_limit_seconds}s"
                )

                return {
                    'is_compliant': False,
                    'wait_seconds': wait_time,
                    'details': f'Please wait {wait_time:.2f}s before next request',
                }

        # Update last request time
        self.last_request_times[limit_key] = current_time

        return {
            'is_compliant': True,
            'wait_seconds': 0.0,
            'details': 'Rate limit OK',
        }

    async def check_transparency(self) -> dict[str, Any]:
        """
        Verify our bot identifies itself properly

        Returns:
            - is_compliant: bool
            - user_agent: str
            - contact_info: str
        """
        # Check if user agent includes contact info
        has_contact = 'pnkln.ai' in self.user_agent.lower()
        has_bot_identifier = 'bot' in self.user_agent.lower()

        is_compliant = has_contact and has_bot_identifier

        return {
            'is_compliant': is_compliant,
            'user_agent': self.user_agent,
            'contact_info': 'https://pnkln.ai/bot' if has_contact else 'MISSING',
            'details': 'Transparent user agent' if is_compliant else 'User agent needs improvement',
        }

    async def get_compliance_score(
        self,
        hours: int = 24
    ) -> dict[str, Any]:
        """
        Calculate overall ethical compliance score

        Returns score based on recent compliance checks
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Get recent compliance checks
        query = (
            select(
                EthicalCompliance.check_type,
                func.count(EthicalCompliance.id).label('total'),
                func.sum(
                    func.cast(EthicalCompliance.is_compliant, Integer)
                ).label('compliant'),
                func.sum(EthicalCompliance.violations).label('violations'),
            )
            .where(EthicalCompliance.checked_at >= cutoff_time)
            .group_by(EthicalCompliance.check_type)
        )

        result = await self.session.execute(query)
        rows = result.all()

        scores_by_type = {}
        total_checks = 0
        total_compliant = 0
        total_violations = 0

        for row in rows:
            check_type = row.check_type
            total = row.total
            compliant = row.compliant or 0
            violations = row.violations or 0

            score = (compliant / total * 100) if total > 0 else 100

            scores_by_type[check_type] = {
                'score': round(score, 2),
                'total_checks': total,
                'compliant': compliant,
                'violations': violations,
            }

            total_checks += total
            total_compliant += compliant
            total_violations += violations

        overall_score = (
            (total_compliant / total_checks * 100)
            if total_checks > 0 else 100
        )

        return {
            'overall_score': round(overall_score, 2),
            'total_checks': total_checks,
            'total_compliant': total_compliant,
            'total_violations': total_violations,
            'by_check_type': scores_by_type,
            'time_period_hours': hours,
            'status': self._get_compliance_status(overall_score),
        }

    def _get_compliance_status(self, score: float) -> str:
        """Get status based on compliance score"""
        if score >= 95:
            return 'excellent'
        elif score >= 85:
            return 'good'
        elif score >= 70:
            return 'acceptable'
        elif score >= 50:
            return 'poor'
        else:
            return 'critical'

    async def _store_compliance_check(
        self,
        source: str,
        check_type: str,
        is_compliant: bool,
        details: str
    ):
        """Store compliance check in database"""
        try:
            check = EthicalCompliance(
                source_url=source,
                check_type=check_type,
                is_compliant=is_compliant,
                details=details,
                violations=0 if is_compliant else 1,
            )
            self.session.add(check)
            await self.session.commit()
        except Exception as e:
            print(f"Error storing compliance check: {e}")

    async def get_violations(
        self,
        hours: int = 24,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        Get recent ethical violations

        Returns list of violations for review
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        query = (
            select(EthicalCompliance)
            .where(
                and_(
                    EthicalCompliance.checked_at >= cutoff_time,
                    not EthicalCompliance.is_compliant
                )
            )
            .order_by(desc(EthicalCompliance.checked_at))
            .limit(limit)
        )

        result = await self.session.execute(query)
        violations = result.scalars().all()

        return [
            {
                'source': v.source_url,
                'check_type': v.check_type,
                'details': v.details,
                'timestamp': v.checked_at.isoformat(),
            }
            for v in violations
        ]

    async def generate_compliance_report(self) -> dict[str, Any]:
        """
        Generate comprehensive ethical compliance report

        Includes:
        - Overall compliance score
        - Violations by type
        - Recommendations
        - Status
        """
        # Get 24-hour compliance score
        score_data = await self.get_compliance_score(24)

        # Get recent violations
        violations = await self.get_violations(24, 10)

        # Generate recommendations
        recommendations = []

        if score_data['overall_score'] < 95:
            recommendations.append({
                'priority': 'high',
                'issue': f"Compliance score is {score_data['overall_score']}%",
                'recommendation': 'Review and fix recent violations',
            })

        if score_data.get('total_violations', 0) > 10:
            recommendations.append({
                'priority': 'medium',
                'issue': f"{score_data['total_violations']} violations in 24h",
                'recommendation': 'Implement stricter rate limiting',
            })

        # Check robots.txt compliance
        robots_score = score_data['by_check_type'].get('robots_txt', {}).get('score', 100)
        if robots_score < 90:
            recommendations.append({
                'priority': 'critical',
                'issue': 'robots.txt violations detected',
                'recommendation': 'Immediately stop crawling disallowed paths',
            })

        return {
            'compliance_score': score_data,
            'recent_violations': violations,
            'recommendations': recommendations,
            'user_agent': self.user_agent,
            'rate_limits': self.rate_limits,
            'status': score_data['status'],
        }
