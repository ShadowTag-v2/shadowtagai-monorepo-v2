# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Demonstration of Gemini Ingestion Layer with visualizations and resilience.

Shows:
1. Visualization generation (ASCII, Mermaid)
2. Circuit breaker protection
3. Cost spike detection
4. Retry logic
5. Complete briefing with charts
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from src.ingestion import (  # noqa: E402
    DEFAULT_SOURCES,
    BriefingGenerator,
    BriefingVisualizer,
    CircuitBreaker,
    CircuitBreakerConfig,
    CostSpikeDetector,
    RetryHandler,
    SourceManager,
    TierClassifier,
)


async def demo_visualizations():
    """Demonstrate visualization generation."""
    print("\n" + "=" * 60)
    print("DEMO 1: Visualizations")
    print("=" * 60)

    # ASCII visualizer
    ascii_viz = BriefingVisualizer(output_format="ascii")

    print("\n### Tier Distribution (ASCII)")
    chart = ascii_viz.generate_tier_distribution_chart(
        tier1_count=150,
        tier2_count=300,
        tier3_count=250,
    )
    print(chart)

    print("\n### Source Coverage (ASCII)")
    source_stats = {
        "YouTube": 120,
        "Twitter": 180,
        "News": 150,
        "Reddit": 80,
        "Academic": 170,
    }
    chart = ascii_viz.generate_source_coverage_chart(source_stats)
    print(chart)

    # Mermaid visualizer
    mermaid_viz = BriefingVisualizer(output_format="mermaid")

    print("\n### Tier Distribution (Mermaid)")
    chart = mermaid_viz.generate_tier_distribution_chart(
        tier1_count=150,
        tier2_count=300,
        tier3_count=250,
    )
    print(chart)

    print("\n### Cost Breakdown (Mermaid)")
    cost_data = {
        "API Costs": 25.50,
        "Compute": 22.10,
        "Storage": 8.20,
        "Network": 2.52,
    }
    chart = mermaid_viz.generate_cost_breakdown(cost_data)
    print(chart)


async def demo_circuit_breaker():
    """Demonstrate circuit breaker."""
    print("\n" + "=" * 60)
    print("DEMO 2: Circuit Breaker")
    print("=" * 60)

    config = CircuitBreakerConfig(
        failure_threshold=3,
        timeout_seconds=5,
    )

    cb = CircuitBreaker("test-source", config)

    # Simulated function that fails
    call_count = 0

    async def flaky_function():
        nonlocal call_count
        call_count += 1

        if call_count <= 3:
            raise Exception(f"Simulated failure #{call_count}")
        return f"Success on call #{call_count}"

    # Try calls until circuit opens
    for i in range(10):
        try:
            result = await cb.call(flaky_function)
            print(f"✓ Call {i + 1}: {result}")
        except Exception as e:
            print(f"✗ Call {i + 1}: {e}")

        # Show circuit state
        stats = cb.get_stats()
        print(f"   State: {stats['state']}, Failures: {stats['failure_count']}")

        await asyncio.sleep(0.5)


async def demo_cost_spike_detection():
    """Demonstrate cost spike detection."""
    print("\n" + "=" * 60)
    print("DEMO 3: Cost Spike Detection")
    print("=" * 60)

    detector = CostSpikeDetector(
        budget=77.0,
        alert_threshold=0.75,
        critical_threshold=0.90,
    )

    # Simulate cost accumulation
    costs = [
        (10.0, "API calls"),
        (15.0, "Compute"),
        (8.0, "Storage"),
        (20.0, "API calls"),
        (15.0, "Compute"),
        (10.0, "Network"),
    ]

    for amount, category in costs:
        detector.record_cost(amount, category)

        stats = detector.get_stats()
        print(f"\nRecorded ${amount:.2f} ({category})")
        print(f"  Total: ${stats['current_cost']:.2f}")
        print(f"  Budget: ${stats['budget']:.2f}")
        print(f"  Utilization: {stats['utilization_percent']:.1f}%")
        print(f"  Status: {stats['status']}")
        print(f"  Throttle: {'ACTIVE' if stats['throttle_active'] else 'OFF'}")

        if detector.alerts:
            latest_alert = detector.alerts[-1]
            print(f"  ⚠️ {latest_alert.message}")


async def demo_retry_handler():
    """Demonstrate retry logic with exponential backoff."""
    print("\n" + "=" * 60)
    print("DEMO 4: Retry Handler")
    print("=" * 60)

    retry = RetryHandler(
        max_retries=3,
        base_delay=0.5,
        jitter=True,
    )

    call_count = 0

    async def eventually_succeeds():
        nonlocal call_count
        call_count += 1

        if call_count < 3:
            raise Exception(f"Failure #{call_count}")
        return f"Success on attempt #{call_count}"

    try:
        result = await retry.execute(eventually_succeeds)
        print(f"\n✓ Final result: {result}")
    except Exception as e:
        print(f"\n✗ All retries exhausted: {e}")


async def demo_full_pipeline():
    """Demonstrate complete pipeline with all features."""
    print("\n" + "=" * 60)
    print("DEMO 5: Full Pipeline with Visualizations")
    print("=" * 60)

    # Setup components
    source_manager = SourceManager(sources=DEFAULT_SOURCES[:3])  # Use first 3 sources
    tier_classifier = TierClassifier()
    briefing_gen = BriefingGenerator(
        enable_visualizations=True,
        visualization_format="ascii",  # Use ASCII for terminal demo
    )

    print("\n### Collecting from sources...")
    collected = await source_manager.collect_all(max_items_per_source=20)

    # Flatten items
    all_items = []
    for _source_name, items in collected.items():
        all_items.extend(items)

    print(f"✓ Collected {len(all_items)} items from {len(collected)} sources")

    print("\n### Classifying items...")
    classified = tier_classifier.classify_batch(all_items)

    tier_dist = tier_classifier.get_tier_distribution()
    print(f"✓ Tier 1: {tier_dist['tier_1']['count']} ({tier_dist['tier_1']['percentage']:.1f}%)")
    print(f"✓ Tier 2: {tier_dist['tier_2']['count']} ({tier_dist['tier_2']['percentage']:.1f}%)")
    print(f"✓ Tier 3: {tier_dist['tier_3']['count']} ({tier_dist['tier_3']['percentage']:.1f}%)")

    print("\n### Generating briefing with visualizations...")
    briefing = await briefing_gen.generate_briefing(
        classified_items=classified,
        source_stats=source_manager.get_coverage_stats(),
        compliance_stats={
            "total_checks": 100,
            "allowed": 96,
            "blocked_by_robots_txt": 2,
            "blocked_by_rate_limit": 2,
            "robots_txt_fetches": 6,
        },
    )

    print("\n" + "=" * 60)
    print("DAILY BRIEFING (with visualizations)")
    print("=" * 60)
    print(briefing.to_markdown(include_visualizations=True))


async def main():
    """Run all demos."""
    await demo_visualizations()
    await demo_circuit_breaker()
    await demo_cost_spike_detection()
    await demo_retry_handler()
    await demo_full_pipeline()

    print("\n" + "=" * 60)
    print("✅ All demos complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
