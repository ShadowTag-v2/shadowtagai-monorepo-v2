#!/usr/bin/env python3
"""PNKLN Core Stack™ Complete Pipeline Example

This example demonstrates the full end-to-end flow through the PNKLN stack:
1. Gemini Ingestion Layer - Collect data from multiple sources
2. Judge #6 Validation - Validate and filter content
3. Processing - Tier classification and analysis
4. Delivery - Generate AM briefing

Represents the 4-namespace GKE architecture.
"""

import asyncio

import httpx


class PNKLNPipelineDemo:
    """Demonstration of complete PNKLN pipeline"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)

    async def run_complete_pipeline(self):
        """Execute the full PNKLN pipeline"""
        print("=" * 80)
        print("PNKLN Core Stack™ - Complete Pipeline Demonstration")
        print("=" * 80)
        print()

        # Step 1: Check stack health
        print("Step 1: Checking PNKLN stack health...")
        await self.check_stack_health()
        print()

        # Step 2: Run ingestion
        print("Step 2: Running Gemini Ingestion Layer...")
        ingestion_metrics = await self.run_ingestion()
        print()

        # Step 3: Validate ingested items
        print("Step 3: Running Judge #6 validation...")
        validation_metrics = await self.run_validation()
        print()

        # Step 4: Check quality gates
        print("Step 4: Checking quality gates...")
        await self.check_quality_gates()
        print()

        # Step 5: Get compliance report
        print("Step 5: Fetching ethical compliance report...")
        await self.get_compliance_report()
        print()

        # Step 6: Get AM briefing
        print("Step 6: Generating AM briefing...")
        await self.get_briefing()
        print()

        # Step 7: View metrics overview
        print("Step 7: Viewing metrics overview...")
        await self.get_metrics_overview()
        print()

        # Step 8: Check SLA status
        print("Step 8: Checking SLA compliance...")
        await self.check_sla_status()
        print()

        print("=" * 80)
        print("Pipeline execution complete!")
        print("=" * 80)

    async def check_stack_health(self):
        """Check overall stack health"""
        response = await self.client.get(f"{self.base_url}/api/v1/pnkln/status")
        data = response.json()

        print(f"  Overall Status: {data['summary']}")
        print("  Namespaces:")
        for ns_key, ns_data in data["status"].items():
            if ns_key.endswith("_status"):
                ns = ns_data["namespace"]
                healthy = "✓" if ns_data["healthy"] else "✗"
                print(f"    {healthy} {ns}: {ns_data['pod_count']} pods")

    async def run_ingestion(self):
        """Run ingestion pipeline"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/ingestion/run",
            json={"sources": None},  # All sources
        )
        data = response.json()

        metrics = data["metrics"]
        print(f"  Items Ingested: {metrics['items_ingested']}")
        print(f"  Unique Sources: {metrics['unique_sources']}")
        print(f"  Runtime: {metrics['runtime_minutes']:.2f} min")
        print(f"  Avg Cost/Item: ${metrics['average_cost_per_item']:.4f}")
        print(f"  Quality Gate: {'✓ PASSED' if metrics['quality_gate_passed'] else '✗ FAILED'}")

        print("\n  Source Breakdown:")
        print(f"    YouTube: {metrics['youtube_items']}")
        print(f"    Twitter: {metrics['twitter_items']}")
        print(f"    News: {metrics['news_items']}")
        print(f"    RSS: {metrics['rss_items']}")

        print("\n  Tier Distribution:")
        print(f"    Tier 1 (High-value): {metrics['tier_1_count']}")
        print(f"    Tier 2 (Medium-value): {metrics['tier_2_count']}")
        print(f"    Tier 3 (Low-value): {metrics['tier_3_count']}")

        return metrics

    async def run_validation(self):
        """Get validation metrics"""
        response = await self.client.get(f"{self.base_url}/api/v1/validation/metrics")
        metrics = response.json()

        print(f"  Items Validated: {metrics['items_validated']}")
        print(f"  Approved: {metrics['approved_count']}")
        print(f"  Rejected: {metrics['rejected_count']}")
        print(f"  Review Required: {metrics['review_required_count']}")

        print("\n  Performance:")
        print(f"    Avg Latency: {metrics['average_latency_ms']:.2f}ms")
        print(f"    P99 Latency: {metrics['p99_latency_ms']:.2f}ms")
        print(f"    Avg Confidence: {metrics['average_confidence']:.2%}")

        print("\n  Error Rates:")
        print(f"    False Positive: {metrics['false_positive_rate']:.2%}")
        print(f"    False Negative: {metrics['false_negative_rate']:.2%}")

        return metrics

    async def check_quality_gates(self):
        """Check quality gate configuration"""
        response = await self.client.get(f"{self.base_url}/api/v1/ingestion/quality-gates")
        gates = response.json()

        print("  Quality Gate Thresholds:")
        print(f"    Min Daily Items: {gates['min_daily_items']}")
        print(f"    Min Unique Sources: {gates['min_unique_sources']}")
        print(f"    Max Cost/Item: ${gates['max_cost_per_item']}")
        print(f"    Min Relevance Score: {gates['min_relevance_score']:.2%}")

    async def get_compliance_report(self):
        """Get ethical compliance report"""
        response = await self.client.get(f"{self.base_url}/api/v1/ingestion/compliance")
        report = response.json()

        print(f"  Compliance Score: {report['compliance_score']:.2%}")
        print(f"  robots.txt Violations: {report['robots_txt_violations']}")
        print(f"  Rate Limit Violations: {report['rate_limit_violations']}")
        print(f"  Total Requests: {report['total_requests']}")
        print(f"  Flagged Domains: {len(report['flagged_domains'])}")

    async def get_briefing(self):
        """Get AM briefing"""
        response = await self.client.get(f"{self.base_url}/api/v1/pnkln/briefing/latest")
        briefing = response.json()

        print(f"  New Items: {briefing['new_items_count']}")
        print(f"  Tier 1 Highlights: {len(briefing['tier_1_highlights'])}")
        print(
            f"  Quality Gate: {'✓ PASSED' if briefing['quality_gate']['all_gates_passed'] else '✗ FAILED'}",
        )
        print(f"  Delivered: {'Yes' if briefing['delivered'] else 'No'}")

    async def get_metrics_overview(self):
        """Get comprehensive metrics"""
        response = await self.client.get(f"{self.base_url}/api/v1/metrics/overview")
        metrics = response.json()

        print("  Cost Metrics:")
        print(f"    Total: ${metrics['cost']['total_cost']:.2f}")
        print(f"    Budget Utilization: {metrics['cost']['budget_utilization_percent']:.1f}%")

        print("\n  Performance Metrics:")
        print(
            f"    Ingestion Runtime: {metrics['performance']['ingestion_runtime_minutes']:.2f} min",
        )
        print(f"    Validation P99: {metrics['performance']['validation_p99_latency_ms']:.2f}ms")
        print(f"    Delivery Success: {metrics['performance']['delivery_success_rate']:.2%}")

        print("\n  Quality Metrics:")
        print(f"    Total Items: {metrics['quality']['total_items']}")
        print(f"    Avg Relevance: {metrics['quality']['average_relevance_score']:.2%}")
        print(f"    Approval Rate: {metrics['quality']['validation_approval_rate']:.2%}")

    async def check_sla_status(self):
        """Check SLA compliance"""
        response = await self.client.get(f"{self.base_url}/api/v1/metrics/sla-status")
        sla = response.json()

        print(f"  Overall SLA: {'✓ MET' if sla['overall_sla_met'] else '✗ FAILED'}")
        print("\n  Individual Checks:")

        for check_name, check_data in sla["checks"].items():
            status = "✓" if check_data["met"] else "✗"
            print(
                f"    {status} {check_name}: {check_data['actual']} (target: {check_data['target']}) {check_data['unit']}",
            )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


async def main():
    """Run the demo"""
    demo = PNKLNPipelineDemo()

    try:
        await demo.run_complete_pipeline()
    finally:
        await demo.close()


if __name__ == "__main__":
    print("\nStarting PNKLN Core Stack™ Pipeline Demo")
    print("Make sure the API is running at http://localhost:8000\n")

    asyncio.run(main())
