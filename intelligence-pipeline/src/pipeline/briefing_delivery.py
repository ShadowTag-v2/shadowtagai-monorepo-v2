# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
PNKLN Intelligence Pipeline - Briefing Delivery

Delivers morning briefings to CEO and team:
- Tier 1: Detailed executive briefing via email
- Tier 2: Summary of auto-actions taken
- Tier 3: Count only, archived
"""

import os
import json
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

from ..models.intelligence_item import IntelligenceItem, IntelligenceTier

logger = logging.getLogger(__name__)


class BriefingDelivery:
    """
    Briefing delivery handler
    """

    def __init__(self):
        """Initialize briefing delivery"""
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.ceo_email = os.getenv("CEO_EMAIL", "ceo@pnkln.ai")

        logger.info("BriefingDelivery initialized")

    async def deliver_briefing(self, items: list[IntelligenceItem]):
        """
        Deliver morning briefing

        Args:
            items: List of processed intelligence items
        """
        logger.info("=== Delivering Morning Briefing ===")
        start_time = datetime.now()

        # Separate by tier
        tier1_items = [item for item in items if item.tier == IntelligenceTier.TIER_1]
        tier2_items = [item for item in items if item.tier == IntelligenceTier.TIER_2]
        tier3_items = [item for item in items if item.tier == IntelligenceTier.TIER_3]

        # Generate briefing
        briefing_html = self._generate_briefing_html(tier1_items, tier2_items, tier3_items)
        briefing_text = self._generate_briefing_text(tier1_items, tier2_items, tier3_items)

        # Send email
        if self.smtp_user and self.smtp_password:
            await self._send_email(briefing_html, briefing_text)
        else:
            logger.warning("SMTP credentials not configured, skipping email delivery")
            # Save to file instead
            self._save_briefing_to_file(briefing_html)

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✓ Briefing delivered in {duration:.1f}s")

    def _generate_briefing_html(
        self, tier1_items: list[IntelligenceItem], tier2_items: list[IntelligenceItem], tier3_items: list[IntelligenceItem]
    ) -> str:
        """Generate HTML briefing"""
        date_str = datetime.now().strftime("%B %d, %Y")

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; }}
        .tier {{ margin: 20px 0; padding: 20px; border-left: 4px solid #3498db; }}
        .tier1 {{ border-color: #e74c3c; background: #fef5f5; }}
        .tier2 {{ border-color: #f39c12; background: #fef9f5; }}
        .tier3 {{ border-color: #95a5a6; background: #f5f5f5; }}
        .item {{ margin: 15px 0; padding: 15px; background: white; border-radius: 5px; }}
        .score {{ font-weight: bold; color: #e74c3c; }}
        .meta {{ color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 PNKLN Intelligence Briefing</h1>
        <p>{date_str}</p>
    </div>

    <div class="tier tier1">
        <h2>🚨 Tier 1: Executive Action Required ({len(tier1_items)} items)</h2>
        {"".join([self._format_tier1_item_html(item) for item in tier1_items])}
        {self._format_no_items_message(tier1_items, "No critical items today")}
    </div>

    <div class="tier tier2">
        <h2>⚙️ Tier 2: Auto-Actions Taken ({len(tier2_items)} items)</h2>
        {"".join([self._format_tier2_item_html(item) for item in tier2_items])}
        {self._format_no_items_message(tier2_items, "No medium-priority items today")}
    </div>

    <div class="tier tier3">
        <h2>📦 Tier 3: Archived ({len(tier3_items)} items)</h2>
        <p>Low-priority items archived for future reference.</p>
    </div>

    <div style="margin-top: 40px; padding: 20px; background: #ecf0f1; border-radius: 5px;">
        <p><strong>Pipeline Stats:</strong></p>
        <ul>
            <li>Total Items: {len(tier1_items) + len(tier2_items) + len(tier3_items)}</li>
            <li>Critical (Tier 1): {len(tier1_items)}</li>
            <li>Medium (Tier 2): {len(tier2_items)}</li>
            <li>Low (Tier 3): {len(tier3_items)}</li>
        </ul>
    </div>
</body>
</html>
"""
        return html

    def _format_tier1_item_html(self, item: IntelligenceItem) -> str:
        """Format Tier 1 item for HTML"""
        return f"""
        <div class="item">
            <h3>{item.title}</h3>
            <p class="meta">
                Source: {item.source.value} |
                Score: <span class="score">{item.jr_score:.2f}</span> |
                Published: {item.published_date.strftime("%Y-%m-%d")}
            </p>
            <p><strong>Executive Summary:</strong><br>{item.cor_synthesis}</p>
            <p><strong>Recommended Actions:</strong></p>
            <ul>
                {"".join([f"<li>{action}</li>" for action in item.action_items])}
            </ul>
            <p><a href="{item.url}">View Source</a></p>
        </div>
        """

    def _format_tier2_item_html(self, item: IntelligenceItem) -> str:
        """Format Tier 2 item for HTML"""
        return f"""
        <div class="item">
            <h4>{item.title}</h4>
            <p class="meta">Score: {item.jr_score:.2f} | {item.source.value}</p>
            <p><strong>Actions Taken:</strong> {", ".join(item.action_items) if item.action_items else "None"}</p>
            <p><a href="{item.url}">View Source</a></p>
        </div>
        """

    def _format_no_items_message(self, items: list, message: str) -> str:
        """Format no items message"""
        return f"<p><em>{message}</em></p>" if not items else ""

    def _generate_briefing_text(
        self, tier1_items: list[IntelligenceItem], tier2_items: list[IntelligenceItem], tier3_items: list[IntelligenceItem]
    ) -> str:
        """Generate plain text briefing"""
        date_str = datetime.now().strftime("%B %d, %Y")

        text = f"""
PNKLN Intelligence Briefing - {date_str}
{"=" * 60}

TIER 1: EXECUTIVE ACTION REQUIRED ({len(tier1_items)} items)
{"-" * 60}
"""

        for item in tier1_items:
            text += f"""
Title: {item.title}
Source: {item.source.value} | Score: {item.jr_score:.2f}
Published: {item.published_date.strftime("%Y-%m-%d")}

Executive Summary:
{item.cor_synthesis}

Recommended Actions:
{chr(10).join([f"  - {action}" for action in item.action_items])}

URL: {item.url}

{"-" * 60}
"""

        if not tier1_items:
            text += "No critical items today.\n\n"

        text += f"""
TIER 2: AUTO-ACTIONS TAKEN ({len(tier2_items)} items)
{"-" * 60}
"""

        for item in tier2_items:
            text += f"""
{item.title}
  Score: {item.jr_score:.2f} | {item.source.value}
  Actions: {", ".join(item.action_items) if item.action_items else "None"}
  URL: {item.url}

"""

        if not tier2_items:
            text += "No medium-priority items today.\n\n"

        text += f"""
TIER 3: ARCHIVED ({len(tier3_items)} items)
{"-" * 60}
Low-priority items archived for future reference.

PIPELINE STATS:
  Total Items: {len(tier1_items) + len(tier2_items) + len(tier3_items)}
  Critical (Tier 1): {len(tier1_items)}
  Medium (Tier 2): {len(tier2_items)}
  Low (Tier 3): {len(tier3_items)}
"""

        return text

    async def _send_email(self, html: str, text: str):
        """Send email briefing"""
        logger.info(f"📧 Sending briefing email to {self.ceo_email}")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"PNKLN Intelligence Briefing - {datetime.now().strftime('%Y-%m-%d')}"
        msg["From"] = self.smtp_user
        msg["To"] = self.ceo_email

        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info("✓ Email sent successfully")

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            self._save_briefing_to_file(html)

    def _save_briefing_to_file(self, html: str):
        """Save briefing to file as fallback"""
        output_file = f"/tmp/briefing_{datetime.now().strftime('%Y%m%d')}.html"
        with open(output_file, "w") as f:
            f.write(html)
        logger.info(f"✓ Briefing saved to {output_file}")


async def main():
    """
    Main briefing delivery entry point
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Load processed items
    input_file = "/tmp/intelligence_items_processed.json"
    with open(input_file) as f:
        items_data = json.load(f)

    items = [IntelligenceItem.from_dict(item_data) for item_data in items_data]

    # Deliver briefing
    delivery = BriefingDelivery()
    await delivery.deliver_briefing(items)

    print("✓ Briefing delivered")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
