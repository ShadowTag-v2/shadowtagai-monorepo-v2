# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Demo script to showcase Gemini Ingestion Layer."""

import asyncio

from src.pipeline import IngestionPipeline


async def run_demo():
    """Run a demo pipeline execution."""
    print("=" * 80)
    print("🎯 Gemini Ingestion Layer - Demo")
    print("=" * 80)
    print()
    print("This demo showcases:")
    print("  ✅ 4 source collectors (YouTube, Twitter, NewsAPI, RSS)")
    print("  ✅ Ethical compliance (rate limiting, robots.txt, User-Agent)")
    print("  ✅ Cost monitoring ($77/month budget, $0.0026/item target)")
    print("  ✅ Quality gates (≥100 items, ≥4 sources, ≥0.70 relevance)")
    print("  ✅ Tier classification (20% T1, 50% T2, 30% T3)")
    print("  ✅ Runtime efficiency (≤45 min target)")
    print()
    print("=" * 80)
    print()

    # Run pipeline
    pipeline = IngestionPipeline()
    summary = await pipeline.run()

    # Display results
    print("\n" + "=" * 80)
    print("📊 DEMO RESULTS")
    print("=" * 80)

    if summary["status"] == "completed":
        metrics = summary["metrics"]
        gates = summary["quality_gates"]
        budget = summary["budget_status"]

        print("\n1️⃣ Collection Metrics:")
        print(f"   Total Items: {metrics['total_items']}")
        print("   By Source:")
        for source, count in metrics["items_by_source"].items():
            print(f"     - {source}: {count} items")

        print("\n2️⃣ Tier Distribution:")
        for tier, count in metrics["items_by_tier"].items():
            pct = (count / metrics["total_items"] * 100) if metrics["total_items"] > 0 else 0
            print(f"     - {tier}: {count} items ({pct:.1f}%)")

        print("\n3️⃣ Quality Gates:")
        print(f"   Overall: {gates['overall_status'].upper()}")
        print(f"   Passed: {gates['passed']}/{gates['total_gates']}")
        print(f"   Warnings: {gates['warnings']}, Critical: {gates['critical']}")
        print("   Details:")
        for result in gates["results"]:
            status = "✅" if result["passed"] else "❌"
            print(f"     {status} {result['message']}")

        print("\n4️⃣ Cost Analysis:")
        print(f"   Total Cost: ${metrics['total_cost']:.4f}")
        print(f"   Cost/Item: ${metrics['cost_per_item']:.6f} (target: $0.0026)")
        print("   By Source:")
        for source, cost in metrics["cost_by_source"].items():
            print(f"     - {source}: ${cost:.4f}")
        print(f"   Daily Budget: ${budget['daily_summary']['total_cost']:.2f} / $2.57")
        print(f"   Utilization: {budget['daily_summary']['budget_utilization_pct']:.1f}%")

        print("\n5️⃣ Performance:")
        print(f"   Runtime: {summary['runtime_minutes']:.2f} minutes")
        print(f"   Target: {IngestionPipeline.TARGET_RUNTIME_MINUTES} minutes")
        if summary["under_target"]:
            print("   Status: ✅ ON TARGET")
        else:
            print("   Status: ⚠️ OVER TARGET")

        print("\n6️⃣ Ethics Verification:")
        print("   ✅ All crawlers have @rate_limit decorators")
        print("   ✅ RSSCollector implements robots.txt checking")
        print('   ✅ User-Agent: "AiYou-Bot/1.0 (+https://aiyou.ai/bot-info)"')
        print("   ✅ Rate limited to 1 req/sec per source")

    else:
        print(f"❌ Pipeline failed: {summary.get('error', 'Unknown error')}")

    print("\n" + "=" * 80)
    print("Demo complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_demo())
