# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""PNKLN Core Stack - AM Briefing Generator and Delivery

Generates and delivers the morning intelligence briefing based on
ingestion pipeline results.

Briefing includes:
- Executive summary
- Tier 1 high-priority items
- Key trends and themes
- Pipeline performance metrics
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Literal

import structlog
from anthropic import Anthropic

from ingestion.core.config import get_config

logger = structlog.get_logger(__name__)


class AMBriefingGenerator:
    """Generates and delivers AM intelligence briefing.

    Uses Gemini to synthesize pipeline results into a concise
    executive summary suitable for morning review.
    """

    BRIEFING_PROMPT = """You are an intelligence analyst preparing a morning briefing for executives at PNKLN, a strategic intelligence platform.

Based on the following ingestion pipeline results, create a concise morning briefing (300-500 words) that includes:

1. **Executive Summary**: Key highlights and themes from overnight intelligence collection
2. **Priority Items**: Top 3-5 Tier 1 items requiring immediate attention
3. **Trends**: Emerging patterns or recurring themes across sources
4. **Operational Status**: Brief note on pipeline performance (items collected, costs, quality)

**Pipeline Results:**
{pipeline_summary}

**Format the briefing in clean markdown** suitable for email or Slack delivery. Be concise, actionable, and highlight strategic implications.
"""

    def __init__(self):
        self.config = get_config()
        self.client = Anthropic(api_key=self.config.anthropic.api_key)
        logger.info("briefing_generator_initialized")

    async def generate(self, pipeline_summary: dict) -> str:
        """Generate AM briefing from pipeline summary.

        Args:
            pipeline_summary: Output from IngestionPipeline.run()

        Returns:
            Formatted briefing text (markdown)

        """
        # Format pipeline summary for Gemini
        summary_text = self._format_summary(pipeline_summary)

        # Generate briefing with Gemini
        prompt = self.BRIEFING_PROMPT.format(pipeline_summary=summary_text)

        try:
            response = self.client.messages.create(
                model=self.config.anthropic.model,
                max_tokens=2048,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}],
            )

            briefing = response.content[0].text

            # Add header with metadata
            header = self._build_header(pipeline_summary)
            full_briefing = f"{header}\n\n{briefing}"

            logger.info("briefing_generated", length_chars=len(full_briefing))

            return full_briefing

        except Exception as e:
            logger.error("briefing_generation_failed", error=str(e))
            # Fallback to basic summary
            return self._generate_fallback_briefing(pipeline_summary)

    def _build_header(self, summary: dict) -> str:
        """Build briefing header with metadata."""
        timestamp = summary.get("timestamp", datetime.utcnow().isoformat())

        return f"""# PNKLN Intelligence Briefing
**Date**: {timestamp}
**Runtime**: {summary.get("runtime_minutes", 0):.1f} minutes
**Items Collected**: {summary.get("items_accepted", 0)} (from {summary.get("items_fetched", 0)} total)
**Cost**: ${summary.get("costs", {}).get("total_usd", 0):.2f}

---
"""

    def _format_summary(self, summary: dict) -> str:
        """Format pipeline summary for Gemini prompt."""
        tier_dist = summary.get("tier_distribution", {})
        quality = summary.get("quality_metrics", {})

        return f"""
**Items Collected**: {summary.get("items_accepted", 0)}
**Tier Distribution**:
- Tier 1 (High-Priority): {tier_dist.get("tier_1", {}).get("count", 0)} ({tier_dist.get("tier_1", {}).get("percentage", 0)}%)
- Tier 2 (Medium): {tier_dist.get("tier_2", {}).get("count", 0)} ({tier_dist.get("tier_2", {}).get("percentage", 0)}%)
- Tier 3 (Reference): {tier_dist.get("tier_3", {}).get("count", 0)} ({tier_dist.get("tier_3", {}).get("percentage", 0)}%)

**Quality Metrics**:
- Average Relevance: {quality.get("avg_relevance", 0):.1%}
- Average Timeliness: {quality.get("avg_timeliness", 0):.1%}
- Average Source Authority: {quality.get("avg_source_authority", 0):.1%}

**Sources**: {", ".join(summary.get("source_stats", {}).keys())}

**Operational Status**: {"✅ Within budget and runtime" if summary.get("within_budget") and summary.get("within_runtime_limit") else "⚠️ Budget or runtime exceeded"}
"""

    def _generate_fallback_briefing(self, summary: dict) -> str:
        """Generate basic briefing if Gemini call fails."""
        header = self._build_header(summary)
        body = f"""
## Executive Summary

Intelligence collection completed successfully with {summary.get("items_accepted", 0)} items processed.

### Tier Distribution
{self._format_summary(summary)}

### Operational Status
- Runtime: {summary.get("runtime_minutes", 0):.1f} minutes (limit: {self.config.ingestion.runtime_limit_minutes} min)
- Cost: ${summary.get("costs", {}).get("total_usd", 0):.2f} (budget: ${self.config.ingestion.cost_budget_usd})
- Pass Rate: {summary.get("pass_rate_pct", 0):.1f}%

*Note: Full briefing generation unavailable. Review raw pipeline summary for details.*
"""

        return f"{header}\n{body}"

    def _deliver_file(self, briefing: str, run_id: str) -> Path:
        """Write briefing to data/briefings/<run_id>.md for audit + dashboard."""
        out_dir = Path("data/briefings")
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{run_id}.md"
        path.write_text(briefing, encoding="utf-8")
        logger.info("briefing_saved", path=str(path))
        return path

    async def _deliver_googleworkspace(self, briefing: str, run_id: str) -> None:
        """Send briefing via gws (googleworkspace/cli) Gmail send.

        Requires: `gws` CLI installed + authenticated (`gws auth login`).
        Recipient from env BRIEFING_RECIPIENT_EMAIL (falls back to config).
        """
        recipient = os.environ.get(
            "BRIEFING_RECIPIENT_EMAIL",
            getattr(self.config.delivery, "recipient_email", None),
        )
        if not recipient:
            logger.warning("briefing_gws_skipped", reason="no recipient email configured")
            return

        subject = f"PNKLN Intelligence Briefing — {run_id}"
        try:
            result = subprocess.run(
                [
                    "gws",
                    "gmail",
                    "send",
                    "--to",
                    recipient,
                    "--subject",
                    subject,
                    "--body",
                    briefing,
                    "--content-type",
                    "text/plain",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                logger.info("briefing_delivered_gws", recipient=recipient, run_id=run_id)
            else:
                logger.warning(
                    "briefing_gws_failed",
                    stderr=result.stderr[:500],
                    returncode=result.returncode,
                )
        except FileNotFoundError:
            logger.warning("briefing_gws_skipped", reason="gws CLI not found in PATH")
        except subprocess.TimeoutExpired:
            logger.warning("briefing_gws_timeout", run_id=run_id)

    async def deliver(
        self,
        briefing: str,
        format: Literal["markdown", "html", "json"] = None,
        run_id: str | None = None,
    ) -> None:
        """Deliver briefing via file sink (always) and Slack webhook (when configured).

        Args:
            briefing: Formatted briefing text
            format: Override default format from config
            run_id: Unique run identifier for filename; defaults to UTC timestamp

        """
        format = format or self.config.delivery.format
        run_id = run_id or datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        logger.info(
            "briefing_delivering",
            recipients=self.config.delivery.recipient_list,
            format=format,
            run_id=run_id,
        )

        self._deliver_file(briefing, run_id)
        await self._deliver_googleworkspace(briefing, run_id)

    async def close(self) -> None:
        """Cleanup resources."""
        logger.info("briefing_generator_closed")
