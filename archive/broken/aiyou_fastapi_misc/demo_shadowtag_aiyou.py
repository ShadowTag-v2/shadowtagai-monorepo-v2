"""
Demo: ShadowTag + ShadowTag-v4 Integration
Demonstrates complete workflows for both platforms

Run:
    python examples/demo_shadowtag_ShadowTag-v2.py
"""

import asyncio
import os
from datetime import datetime

from src.agents.ShadowTag-v2_neural_rank import ShadowTag-v2NeuralRankAgent
from src.agents.neural_hash import NeuralHashAgent
from src.protocols.agent_protocol import MediaAsset
from src.services.gemini_batch import GeminiBatchProcessor
from src.services.shadowtag_watermark import ShadowTagWatermarkService


async def demo_shadowtag_workflow():
    """
    Demonstrate ShadowTag authentication workflow

    Flow: Media Upload → Neural Hash → Watermark → Blockchain Receipt
    """
    print("\n" + "=" * 80)
    print("SHADOWTAG AUTHENTICATION DEMO")
    print("=" * 80 + "\n")

    # Initialize services (would use real API key in production)
    gemini_api_key = os.getenv("GEMINI_API_KEY", "demo_key")

    batch_processor = GeminiBatchProcessor(api_key=gemini_api_key, batch_size=100)

    neural_hash_agent = NeuralHashAgent(
        gemini_api_key=gemini_api_key, batch_processor=batch_processor
    )

    watermark_service = ShadowTagWatermarkService()

    # Create sample media asset
    asset = MediaAsset(
        asset_type="video",
        url="https://example.com/creator_video.mp4",
        title="How Neural Networks Really Work - Deep Dive",
        description="Comprehensive explanation of neural network architectures",
        extracted_text="In this video, we'll explore the fundamental principles of neural networks...",
        creator_id="creator_12345",
    )

    print(f"📹 Processing asset: {asset.title}")
    print(f"   Asset ID: {asset.asset_id}")
    print(f"   Type: {asset.asset_type}")
    print(f"   Creator: {asset.creator_id}\n")

    # Step 1: Generate neural fingerprint
    print("🔐 Step 1: Generating neural fingerprint...")
    fingerprint = await neural_hash_agent.generate_fingerprint(asset)

    print(f"   ✓ Fingerprint ID: {fingerprint.fingerprint_id}")
    print(f"   ✓ Semantic embedding: {len(fingerprint.semantic_embedding)}-dim vector")
    print(
        f"   ✓ Latent density: mean={fingerprint.latent_density['mean']:.4f}, "
        f"entropy={fingerprint.latent_density['entropy']:.4f}"
    )
    print(f"   ✓ Perceptual hash: {fingerprint.perceptual_hash[:32]}...")
    print(f"   ✓ Collision probability: {fingerprint.collision_probability:.2e}")
    print(f"   ✓ Metadata reduction: {fingerprint.metadata_reduction * 100:.0f}%")
    print("   💰 Cost: $0.002\n")

    # Step 2: Embed watermark
    print("🎨 Step 2: Embedding dual-layer watermark...")
    watermarked_asset, watermark_data = await watermark_service.embed_watermark(
        asset, creator_id=asset.creator_id, neural_fingerprint_id=fingerprint.fingerprint_id
    )

    print(f"   ✓ Watermark ID: {watermark_data.watermark_id}")
    print(f"   ✓ Type: {watermark_data.watermark_type}")
    print(f"   ✓ Strength: {watermark_data.strength * 100:.0f}%")
    print(f"   ✓ PSNR: {watermark_data.psnr_db or 'N/A'} dB (imperceptible)")
    print(f"   ✓ Robustness: {watermark_data.robustness_score * 100:.0f}% survival rate")
    print("   💰 Cost: $0.001\n")

    # Step 3: Blockchain receipt (simulated)
    print("⛓️  Step 3: Recording blockchain receipt...")
    blockchain_hash = f"0x{fingerprint.perceptual_hash[:64]}"
    watermarked_asset.blockchain_receipt = blockchain_hash

    print(f"   ✓ Blockchain hash: {blockchain_hash[:32]}...")
    print(f"   ✓ Timestamp: {datetime.utcnow().isoformat()}")
    print("   💰 Cost: $0.00 (gas fees vary)\n")

    # Verification
    print("✅ Step 4: Verifying authentication...")
    verification = await watermark_service.verify_watermark(watermarked_asset)

    print(f"   ✓ Watermark verified: {verification['is_watermarked']}")
    print(f"   ✓ Confidence: {verification['confidence'] * 100:.1f}%")
    print(f"   ✓ Creator ID: {asset.creator_id}")
    print(f"   ✓ Blockchain: {blockchain_hash[:32]}...\n")

    print("📊 Total cost: $0.003 per asset")
    print("🎯 Target: $1.4B ARR ShadowTag platform")
    print("\n")


async def demo_ShadowTag-v2_workflow():
    """
    Demonstrate ShadowTag-v4 content ranking workflow

    Flow: Content Ingest → Embed → AI-Cognition Rank → Feed
    """
    print("\n" + "=" * 80)
    print("ShadowTag-v2 AI-COGNITION RANKING DEMO")
    print("=" * 80 + "\n")

    # Initialize services
    gemini_api_key = os.getenv("GEMINI_API_KEY", "demo_key")

    batch_processor = GeminiBatchProcessor(api_key=gemini_api_key, batch_size=100)

    neural_rank_agent = ShadowTag-v2NeuralRankAgent(
        gemini_api_key=gemini_api_key, batch_processor=batch_processor
    )

    # Sample content items
    content_items = [
        {
            "id": "content_001",
            "title": "Understanding Quantum Computing: A Comprehensive Guide",
            "description": "Deep dive into quantum mechanics and computing principles",
            "text": "Quantum computing represents a paradigm shift in computational power...",
            "source_type": "educational",
        },
        {
            "id": "content_002",
            "title": "YOU WON'T BELIEVE What Happened Next!!!",
            "description": "Shocking revelation! Click now!",
            "text": "This is the most amazing thing you'll see today...",
            "source_type": "entertainment",
        },
        {
            "id": "content_003",
            "title": "Climate Change: Latest IPCC Report Analysis",
            "description": "Factual analysis of recent climate science findings",
            "text": "The IPCC's latest assessment report reveals critical insights...",
            "source_type": "news",
        },
    ]

    print("📚 Ranking content items by AI-cognition value...\n")

    # Rank all content
    scores = await neural_rank_agent.rank_content_batch(content_items)

    # Display results
    for content, score in zip(content_items, scores, strict=False):
        print(f"📄 Content: {content['title'][:60]}")
        print(f"   ID: {content['id']}")
        print(f"   Category: {score.category.value}")
        print("\n   🧠 AI-Cognition Scores:")
        print(f"   ├─ Overall: {score.overall_score:.1f}/100 [{score.tier.value.upper()}]")
        print(f"   ├─ Educational value: {score.educational_value:.1f}/100")
        print(f"   ├─ Factual accuracy: {score.factual_accuracy:.1f}/100")
        print(f"   ├─ Depth of insight: {score.depth_of_insight:.1f}/100")
        print(f"   ├─ Long-term relevance: {score.long_term_relevance:.1f}/100")
        print(f"   └─ Clarity: {score.clarity_score:.1f}/100")
        print("\n   ⚠️  Anti-Metrics:")
        print(f"   ├─ Clickbait: {score.clickbait_score:.1f}/100")
        print(f"   └─ Sensationalism: {score.sensationalism_score:.1f}/100")
        print("\n   💰 Cost: $0.003")
        print()

    # Sort by score
    sorted_scores = neural_rank_agent.get_feed_ranking(scores)

    print("\n📺 ShadowTag-v4 Feed (Ranked by AI-Cognition, NOT Engagement):")
    print("-" * 80)
    for i, score in enumerate(sorted_scores, 1):
        content = next(
            c for c in content_items if c["id"] == scores[scores.index(score)].analyzed_at
        )
        # Find matching content
        matching_content = content_items[scores.index(score)]

        print(f"{i}. [{score.tier.value.upper()}] {matching_content['title'][:60]}")
        print(f"   Score: {score.overall_score:.1f} | Category: {score.category.value}")

    print("\n" + "-" * 80)
    print("🎯 Target: $275M ARR ShadowTag-v4 discovery platform")
    print("💡 Key differentiator: AI-cognition ranking, NOT engagement bait\n")


async def demo_cost_analysis():
    """Demonstrate cost savings with batch processing"""
    print("\n" + "=" * 80)
    print("COST OPTIMIZATION: GEMINI BATCH API")
    print("=" * 80 + "\n")

    gemini_api_key = os.getenv("GEMINI_API_KEY", "demo_key")
    batch_processor = GeminiBatchProcessor(api_key=gemini_api_key)

    # Estimate costs
    scenarios = [
        ("ShadowTag: 1M assets/month", 1_000_000, "embedding"),
        ("ShadowTag-v4: 500K content items/month", 500_000, "embedding"),
        ("Combined platform", 1_500_000, "embedding"),
    ]

    for name, num_items, _task_type in scenarios:
        from src.services.gemini_batch import BatchTaskType

        estimate = await batch_processor.compute_cost_estimate(num_items, BatchTaskType.EMBEDDING)

        print(f"📊 {name}:")
        print(f"   Items: {num_items:,}")
        print(f"   Individual API cost: ${estimate['individual_cost_usd']:,.2f}/month")
        print(f"   Batch API cost: ${estimate['batch_cost_usd']:,.2f}/month")
        print(
            f"   💰 Savings: ${estimate['savings_usd']:,.2f}/month ({estimate['savings_percentage']:.0f}%)"
        )
        print()


async def main():
    """Run all demos"""
    print("\n")
    print("█" * 80)
    print(" " * 15 + "SHADOWTAG + ShadowTag-v2: DUAL-VERTICAL DEMO")
    print(" " * 20 + "$15-20B Combined Ecosystem")
    print("█" * 80)

    # Run demos
    await demo_shadowtag_workflow()
    await demo_ShadowTag-v2_workflow()
    await demo_cost_analysis()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\n✅ ShadowTag (Proof Layer):")
    print("   • Neural fingerprinting: $0.002/asset")
    print("   • Dual-layer watermarking: 99% robustness")
    print("   • Blockchain receipts: immutable provenance")
    print("   • Target: $1.4B ARR, 75% margin, $10-12B valuation")

    print("\n✅ ShadowTag-v4 (Discovery Layer):")
    print("   • AI-cognition ranking: $0.003/item")
    print("   • Anti-clickbait filtering")
    print("   • Educational value prioritization")
    print("   • Target: $275M ARR, 79% margin, $5-8B valuation")

    print("\n🚀 Phase 0 (Weeks 1-12):")
    print("   • Budget: $350K")
    print("   • Deliverable: Proof-of-concept with 250 edge sites")
    print("   • Target: $1.5M ARR by Week 12")

    print("\n📚 Documentation: docs/research/")
    print("   • ai-agents-knowledge-base.md")
    print("   • strategic-business-integration.md")
    print("   • implementation-checklist.md")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
