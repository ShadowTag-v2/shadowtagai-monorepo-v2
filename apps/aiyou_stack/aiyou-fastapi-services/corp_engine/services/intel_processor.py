"""
Intel Processor Service
========================
Consumes intel from Nightly Pipeline via Pub/Sub.
Personalizes for each tenant based on AI config.
Triggers ShadowTag watermarking on all outputs.
"""

import asyncio
import json
import os
from datetime import datetime

from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.subscriber.message import Message


class IntelProcessor:
    """
    Processes intel items from Nightly Pipeline for Corp Engine tenants.

    Flow:
    1. Subscribe to pipeline output topic
    2. For each intel item:
       - Match to relevant tenants by industry/tech_stack
       - Generate personalized recommendations
       - Apply ShadowTag signature
       - Store in tenant's intel_feeds
       - Trigger real-time alerts for high-relevance items
    """

    def __init__(self):
        self.project_id = os.getenv("PUBSUB_PROJECT", "acquired-jet-478701-b3")
        self.subscription_id = os.getenv("PUBSUB_SUBSCRIPTION", "intel-processor-prod")
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            self.project_id, self.subscription_id
        )
        self._running = False

    async def start(self):
        """Start consuming intel messages"""
        self._running = True

        def callback(message: Message):
            asyncio.run(self._process_message(message))

        streaming_pull_future = self.subscriber.subscribe(self.subscription_path, callback=callback)

        print(f"Intel Processor listening on {self.subscription_path}")

        try:
            streaming_pull_future.result()
        except Exception as e:
            streaming_pull_future.cancel()
            print(f"Intel Processor error: {e}")

    async def stop(self):
        """Stop the processor"""
        self._running = False

    async def _process_message(self, message: Message):
        """Process a single intel message"""
        try:
            data = json.loads(message.data.decode("utf-8"))

            # Extract intel metadata
            intel_item = {
                "id": data.get("id"),
                "type": data.get("type", "tech_update"),
                "source": data.get("source"),
                "title": data.get("title"),
                "summary": data.get("summary"),
                "content": data.get("content"),
                "score": data.get("relevance_score", 50),
                "categories": data.get("categories", []),
                "tech_keywords": data.get("tech_keywords", []),
                "created_at": datetime.utcnow().isoformat(),
            }

            # Find matching tenants
            matching_tenants = await self._find_matching_tenants(intel_item)

            # Process for each tenant
            for tenant in matching_tenants:
                await self._process_for_tenant(tenant, intel_item)

            message.ack()

        except Exception as e:
            print(f"Error processing message: {e}")
            message.nack()

    async def _find_matching_tenants(self, intel_item: dict) -> list[dict]:
        """Find tenants that should receive this intel based on their profile"""
        # In production, query from database
        # Match by:
        # - industry alignment
        # - tech_stack overlap
        # - regulatory keywords

        # Placeholder - return empty for now
        return []

    async def _process_for_tenant(self, tenant: dict, intel_item: dict):
        """Process intel item for a specific tenant"""

        # 1. Calculate tenant-specific relevance
        relevance = await self._calculate_relevance(tenant, intel_item)

        # 2. Generate personalized recommendations
        recommendations = await self._generate_recommendations(tenant, intel_item)

        # 3. Apply ShadowTag signature
        signature = await self._apply_shadowtag(intel_item)

        # 4. Create tenant intel feed entry
        feed_entry = {
            "tenant_id": tenant["id"],
            "intel_id": intel_item["id"],
            "type": intel_item["type"],
            "title": intel_item["title"],
            "summary": intel_item["summary"],
            "relevance_score": relevance,
            "recommendations": recommendations,
            "shadowtag_signature": signature,
            "is_read": False,
            "is_actioned": False,
            "created_at": datetime.utcnow().isoformat(),
        }

        # 5. Store in database (placeholder)
        await self._store_feed_entry(feed_entry)

        # 6. Trigger alert if high relevance
        if relevance >= 90:
            await self._trigger_alert(tenant, feed_entry)

    async def _calculate_relevance(self, tenant: dict, intel_item: dict) -> int:
        """Calculate relevance score for tenant"""
        base_score = intel_item.get("score", 50)

        # Boost for industry match
        tenant_industry = tenant.get("industry", "")
        if tenant_industry in intel_item.get("categories", []):
            base_score += 20

        # Boost for tech stack overlap
        tenant_tech = set(tenant.get("tech_stack", []))
        intel_tech = set(intel_item.get("tech_keywords", []))
        overlap = len(tenant_tech & intel_tech)
        base_score += overlap * 5

        return min(100, base_score)

    async def _generate_recommendations(self, tenant: dict, intel_item: dict) -> list[str]:
        """Generate personalized recommendations for tenant"""
        recommendations = []

        intel_type = intel_item.get("type", "")

        if intel_type == "tech_update":
            recommendations.append(f"Review {intel_item['title']} for potential integration")
        elif intel_type == "framework_release":
            recommendations.append("Evaluate new framework for compatibility with your stack")
        elif intel_type == "security_alert":
            recommendations.append("URGENT: Review security implications for your deployment")

        return recommendations

    async def _apply_shadowtag(self, intel_item: dict) -> str:
        """Apply ShadowTag C2PA signature to intel item"""
        # In production, use actual ShadowTag signing
        content_hash = hash(json.dumps(intel_item, sort_keys=True))
        return f"c2pa:ed25519:{abs(content_hash):016x}"

    async def _store_feed_entry(self, entry: dict):
        """Store intel feed entry in database"""
        # In production, insert into Cloud SQL
        print(f"Storing intel feed entry for tenant {entry['tenant_id']}")

    async def _trigger_alert(self, tenant: dict, entry: dict):
        """Trigger real-time alert for high-relevance intel"""
        print(f"ALERT: High-relevance intel for tenant {tenant['id']}: {entry['title']}")
        # In production, send to Slack/email/webhook


# CLI entry point for standalone processor
if __name__ == "__main__":
    processor = IntelProcessor()
    asyncio.run(processor.start())
