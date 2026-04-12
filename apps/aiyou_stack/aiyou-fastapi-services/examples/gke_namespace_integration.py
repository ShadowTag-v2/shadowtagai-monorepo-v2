#!/usr/bin/env python3
"""
GKE 4-Namespace Integration Example

This example demonstrates how services in different GKE namespaces
interact with the PNKLN Core Stack™:

1. pnkln-ingestion: Calls external APIs, crawlers
2. pnkln-validation: Called by ingestion, calls processing
3. pnkln-processing: Called by validation, calls delivery
4. pnkln-delivery: Called by processing, delivers briefings

Simulates the "called by services in 4 namespaces" architecture.
"""

import asyncio

import httpx


class NamespaceService:
    """Base class for namespace services"""

    def __init__(self, namespace: str, api_base: str = "http://localhost:8000"):
        self.namespace = namespace
        self.api_base = api_base
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        await self.client.aclose()

    def log(self, message: str):
        print(f"[{self.namespace}] {message}")


class IngestionNamespace(NamespaceService):
    """Ingestion namespace - collects data from sources"""

    def __init__(self):
        super().__init__("pnkln-ingestion")

    async def run_cron_job(self):
        """Simulate nightly CronJob execution"""
        self.log("Starting nightly ingestion CronJob...")

        # Run ingestion
        response = await self.client.post(
            f"{self.api_base}/api/v1/ingestion/run", json={"sources": None}
        )
        data = response.json()

        self.log(f"Ingested {data['metrics']['items_ingested']} items")
        self.log(f"Runtime: {data['metrics']['runtime_minutes']:.2f} min")

        # Check ethical compliance
        compliance = await self.client.get(f"{self.api_base}/api/v1/ingestion/compliance")
        compliance_data = compliance.json()

        self.log(f"Compliance score: {compliance_data['compliance_score']:.2%}")

        return data["metrics"]


class ValidationNamespace(NamespaceService):
    """Validation namespace - validates ingested content"""

    def __init__(self):
        super().__init__("pnkln-validation")

    async def validate_items(self, item_count: int):
        """Called by ingestion namespace to validate items"""
        self.log(f"Received {item_count} items for validation...")

        # Get validation metrics
        response = await self.client.get(f"{self.api_base}/api/v1/validation/metrics")
        metrics = response.json()

        self.log(f"Validated {metrics['items_validated']} items")
        self.log(f"Approved: {metrics['approved_count']}, Rejected: {metrics['rejected_count']}")
        self.log(f"Avg confidence: {metrics['average_confidence']:.2%}")

        # Check performance gates
        gates = await self.client.get(f"{self.api_base}/api/v1/validation/gates")
        gates_data = gates.json()

        self.log(f"FP threshold: {gates_data['fp_rate_threshold']:.2%}")
        self.log(f"FN threshold: {gates_data['fn_rate_threshold']:.2%}")

        return metrics


class ProcessingNamespace(NamespaceService):
    """Processing namespace - enriches and classifies data"""

    def __init__(self):
        super().__init__("pnkln-processing")

    async def process_validated_items(self, validated_count: int):
        """Called by validation namespace to process items"""
        self.log(f"Processing {validated_count} validated items...")

        # Simulate tier classification
        self.log("Running tier classification...")
        await asyncio.sleep(0.5)  # Simulate processing

        # Get quality metrics
        response = await self.client.get(f"{self.api_base}/api/v1/metrics/quality")
        quality = response.json()

        self.log(f"Tier 1 items: {quality['tier_1_count']}")
        self.log(f"Tier 2 items: {quality['tier_2_count']}")
        self.log(f"Tier 3 items: {quality['tier_3_count']}")
        self.log(f"Avg relevance: {quality['average_relevance_score']:.2%}")

        return quality


class DeliveryNamespace(NamespaceService):
    """Delivery namespace - generates and delivers briefings"""

    def __init__(self):
        super().__init__("pnkln-delivery")

    async def generate_briefing(self):
        """Called by processing namespace to generate briefing"""
        self.log("Generating AM briefing...")

        # Get briefing
        response = await self.client.get(f"{self.api_base}/api/v1/pnkln/briefing/latest")
        briefing = response.json()

        self.log(f"Briefing generated with {briefing['new_items_count']} items")
        self.log(f"Tier 1 highlights: {len(briefing['tier_1_highlights'])}")
        self.log(f"Format: {briefing['format']}")

        # Simulate delivery
        self.log(f"Delivering briefing at {briefing.get('delivery_time', 'scheduled time')}...")
        await asyncio.sleep(0.3)

        self.log("Briefing delivered successfully!")

        return briefing


async def simulate_namespace_flow():
    """Simulate complete flow through all 4 namespaces"""

    print("=" * 80)
    print("PNKLN Core Stack™ - 4-Namespace Integration Simulation")
    print("=" * 80)
    print()

    # Initialize namespace services
    ingestion_ns = IngestionNamespace()
    validation_ns = ValidationNamespace()
    processing_ns = ProcessingNamespace()
    delivery_ns = DeliveryNamespace()

    try:
        # Step 1: Ingestion namespace runs CronJob
        print("Step 1: Ingestion Namespace (Nightly CronJob)")
        print("-" * 80)
        ingestion_metrics = await ingestion_ns.run_cron_job()
        print()

        # Step 2: Validation namespace called by ingestion
        print("Step 2: Validation Namespace (Called by Ingestion)")
        print("-" * 80)
        validation_metrics = await validation_ns.validate_items(ingestion_metrics["items_ingested"])
        print()

        # Step 3: Processing namespace called by validation
        print("Step 3: Processing Namespace (Called by Validation)")
        print("-" * 80)
        quality_metrics = await processing_ns.process_validated_items(
            validation_metrics["approved_count"]
        )
        print()

        # Step 4: Delivery namespace called by processing
        print("Step 4: Delivery Namespace (Called by Processing)")
        print("-" * 80)
        briefing = await delivery_ns.generate_briefing()
        print()

        # Summary
        print("=" * 80)
        print("Namespace Flow Complete - Summary")
        print("=" * 80)
        print(f"Ingested: {ingestion_metrics['items_ingested']} items")
        print(f"Validated: {validation_metrics['approved_count']} approved")
        print(f"Processed: {quality_metrics['tier_1_count']} Tier 1 items")
        print(f"Delivered: Briefing with {briefing['new_items_count']} items")
        print()

        # Check overall stack health
        print("Checking overall stack health...")
        response = await ingestion_ns.client.get(f"{ingestion_ns.api_base}/api/v1/pnkln/status")
        status = response.json()

        print(f"Stack Status: {status['summary']}")
        print()

    finally:
        # Clean up
        await ingestion_ns.close()
        await validation_ns.close()
        await processing_ns.close()
        await delivery_ns.close()


if __name__ == "__main__":
    print("\nSimulating PNKLN 4-Namespace Architecture")
    print("Ensure API is running at http://localhost:8000\n")

    asyncio.run(simulate_namespace_flow())
