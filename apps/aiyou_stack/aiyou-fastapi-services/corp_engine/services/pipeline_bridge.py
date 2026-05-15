"""Pipeline Bridge Service
========================
Bridge between Nightly Intel Pipeline and Corp Engine.
Subscribes to pipeline output topics and routes to tenant processing.
"""

import asyncio
import json
import os
from datetime import datetime

from google.cloud import pubsub_v1


class PipelineBridge:
    """Bridges Nightly Intel Pipeline output to Corp Engine.

    Subscribes to:
    - pnkln-scored-items: Scored intel from pipeline
    - corp-engine-config-changes: Tenant config updates
    - corp-engine-auto-port: Framework update notifications
    """

    def __init__(self):
        self.project_id = os.getenv("PUBSUB_PROJECT", "acquired-jet-478701-b3")
        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()

        # Input subscriptions
        self.subscriptions = {
            "scored_items": "pnkln-scored-items-sub",
            "config_changes": "corp-engine-config-changes-sub",
            "auto_port": "corp-engine-auto-port-sub",
        }

        # Output topic for processed intel
        self.output_topic = self.publisher.topic_path(
            self.project_id,
            "corp-engine-intel-updates-prod",
        )

        self._running = False

    async def start(self):
        """Start all bridge subscriptions"""
        self._running = True

        tasks = [
            self._subscribe_scored_items(),
            self._subscribe_config_changes(),
            self._subscribe_auto_port(),
        ]

        await asyncio.gather(*tasks)

    async def stop(self):
        """Stop all subscriptions"""
        self._running = False

    async def _subscribe_scored_items(self):
        """Subscribe to scored items from Nightly Pipeline"""
        subscription_path = self.subscriber.subscription_path(
            self.project_id,
            self.subscriptions["scored_items"],
        )

        def callback(message):
            asyncio.run(self._handle_scored_item(message))

        try:
            future = self.subscriber.subscribe(subscription_path, callback=callback)
            print(f"Bridge listening on {subscription_path}")
            future.result()
        except Exception as e:
            print(f"Scored items subscription error: {e}")

    async def _subscribe_config_changes(self):
        """Subscribe to tenant config changes"""
        subscription_path = self.subscriber.subscription_path(
            self.project_id,
            self.subscriptions["config_changes"],
        )

        def callback(message):
            asyncio.run(self._handle_config_change(message))

        try:
            future = self.subscriber.subscribe(subscription_path, callback=callback)
            print(f"Bridge listening on {subscription_path}")
            future.result()
        except Exception as e:
            print(f"Config changes subscription error: {e}")

    async def _subscribe_auto_port(self):
        """Subscribe to auto-port framework notifications"""
        subscription_path = self.subscriber.subscription_path(
            self.project_id,
            self.subscriptions["auto_port"],
        )

        def callback(message):
            asyncio.run(self._handle_auto_port(message))

        try:
            future = self.subscriber.subscribe(subscription_path, callback=callback)
            print(f"Bridge listening on {subscription_path}")
            future.result()
        except Exception as e:
            print(f"Auto-port subscription error: {e}")

    async def _handle_scored_item(self, message):
        """Handle scored intel item from pipeline"""
        try:
            data = json.loads(message.data.decode("utf-8"))

            # Filter for Corp Engine relevance
            score = data.get("score", 0)
            if score < 50:
                message.ack()
                return

            # Transform for Corp Engine format
            corp_intel = {
                "id": data.get("id"),
                "source": "nightly-pipeline",
                "type": self._classify_intel_type(data),
                "title": data.get("title"),
                "summary": data.get("summary"),
                "content": data.get("content"),
                "relevance_score": score,
                "categories": data.get("categories", []),
                "tech_keywords": self._extract_tech_keywords(data),
                "pipeline_metadata": {
                    "original_source": data.get("source"),
                    "crawl_timestamp": data.get("crawl_timestamp"),
                    "jr_score": data.get("jr_score"),
                },
                "processed_at": datetime.utcnow().isoformat(),
            }

            # Publish to Corp Engine intel topic
            await self._publish_intel(corp_intel)

            message.ack()

        except Exception as e:
            print(f"Error handling scored item: {e}")
            message.nack()

    async def _handle_config_change(self, message):
        """Handle tenant configuration change"""
        try:
            data = json.loads(message.data.decode("utf-8"))

            tenant_id = data.get("tenant_id")
            change_type = data.get("change_type")

            print(f"Config change for tenant {tenant_id}: {change_type}")

            # Trigger reconfiguration
            if change_type == "profile_update":
                await self._trigger_reconfig(tenant_id, data)

            message.ack()

        except Exception as e:
            print(f"Error handling config change: {e}")
            message.nack()

    async def _handle_auto_port(self, message):
        """Handle auto-port framework notification"""
        try:
            data = json.loads(message.data.decode("utf-8"))

            framework = data.get("framework")
            version = data.get("version")

            print(f"Auto-port notification: {framework} {version}")

            # Notify relevant tenants
            await self._notify_auto_port(framework, version, data)

            message.ack()

        except Exception as e:
            print(f"Error handling auto-port: {e}")
            message.nack()

    def _classify_intel_type(self, data: dict) -> str:
        """Classify intel type from pipeline data"""
        source = data.get("source", "").lower()
        title = data.get("title", "").lower()

        if "security" in title or "vulnerability" in title:
            return "security_alert"
        if "release" in title or "version" in title:
            return "framework_release"
        if "arxiv" in source:
            return "research_paper"
        if any(kw in source for kw in ["github", "npm", "pypi"]):
            return "package_update"
        return "tech_update"

    def _extract_tech_keywords(self, data: dict) -> list[str]:
        """Extract technology keywords from intel data"""
        keywords = set()

        # From categories
        keywords.update(data.get("categories", []))

        # From tags
        keywords.update(data.get("tags", []))

        # Common tech patterns in title/summary
        text = f"{data.get('title', '')} {data.get('summary', '')}".lower()

        tech_patterns = [
            "kubernetes",
            "docker",
            "python",
            "javascript",
            "react",
            "gemini",
            "claude",
            "gpt",
            "llm",
            "transformer",
            "tensorflow",
            "pytorch",
            "langchain",
            "openai",
            "aws",
            "gcp",
            "azure",
            "serverless",
            "microservices",
        ]

        for pattern in tech_patterns:
            if pattern in text:
                keywords.add(pattern)

        return list(keywords)

    async def _publish_intel(self, intel: dict):
        """Publish processed intel to Corp Engine topic"""
        data = json.dumps(intel).encode("utf-8")
        future = self.publisher.publish(self.output_topic, data)
        future.result()

    async def _trigger_reconfig(self, tenant_id: str, data: dict):
        """Trigger tenant reconfiguration"""
        print(f"Triggering reconfig for tenant {tenant_id}")
        # In production, call self-config engine

    async def _notify_auto_port(self, framework: str, version: str, data: dict):
        """Notify tenants about framework update"""
        print(f"Notifying tenants about {framework} {version}")
        # In production, query tenants using this framework


# CLI entry point
if __name__ == "__main__":
    bridge = PipelineBridge()
    asyncio.run(bridge.start())
