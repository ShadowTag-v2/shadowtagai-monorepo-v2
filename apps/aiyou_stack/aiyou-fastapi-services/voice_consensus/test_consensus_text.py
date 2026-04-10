#!/usr/bin/env python3
"""
Simple text-based consensus tester (no voice required)
Useful for testing API configuration and consensus logic
"""

import asyncio
import json

from consensus_orchestrator import ConsensusOrchestrator


async def main():
    """Run a simple text query through the consensus system"""

    print("\n" + "=" * 80)
    print("Multi-LLM Consensus Orchestrator - Text Mode")
    print("=" * 80 + "\n")

    # Initialize orchestrator
    orchestrator = ConsensusOrchestrator()

    # Get query from user
    print("Enter your query (or press Enter for default test query):")
    query = input("> ").strip()

    if not query:
        query = """
        What are the key advantages and potential challenges of using
        a multi-model consensus system for AI research compared to
        relying on a single large language model?
        """
        print(f"\nUsing default query:\n{query}\n")

    print("\nProcessing...\n")

    # Execute consensus
    result = await orchestrator.execute_full_consensus(query)

    # Display results
    print("\n" + "=" * 80)
    print("FINAL CONSENSUS SYNTHESIS")
    print("=" * 80 + "\n")
    print(result["final_synthesis"])

    print("\n" + "=" * 80)
    print("EXECUTION METADATA")
    print("=" * 80)

    # Token usage
    layer1_tokens = result["token_usage"]["layer1"]
    layer3_tokens = result["token_usage"]["layer3"]

    total_input = layer1_tokens["input"] + layer3_tokens["input"]
    total_output = layer1_tokens["output"] + layer3_tokens["output"]

    # Add Layer 2 tokens
    for l2_tokens in result["token_usage"]["layer2"]:
        total_input += l2_tokens.get("input", 0)
        total_output += l2_tokens.get("output", 0)

    print("\nModels Used:")
    print("  - Layer 1 (Claude): Initial reasoning")
    print(f"  - Layer 2: {len(result['layer2_responses'])} models")
    for resp in result["layer2_responses"]:
        print(f"    • {resp.model.value}")
    print("  - Layer 3 (Claude): Final synthesis")

    print("\nToken Usage:")
    print(f"  - Input: {total_input:,}")
    print(f"  - Output: {total_output:,}")
    print(f"  - Total: {total_input + total_output:,}")

    if result["peer_reviews"]:
        total_reviews = sum(len(v) for v in result["peer_reviews"].values())
        print(f"\nPeer Reviews: {total_reviews}")

    print("\n" + "=" * 80)

    # Optionally save full result
    save = input("\nSave full result to JSON? [y/N]: ").strip().lower()
    if save == "y":
        filename = "consensus_result.json"

        # Convert ModelResponse objects to dicts for JSON serialization
        serializable_result = {
            "final_synthesis": result["final_synthesis"],
            "layer1_response": {
                "model": result["layer1_response"].model.value,
                "content": result["layer1_response"].content,
                "confidence": result["layer1_response"].confidence,
                "latency": result["layer1_response"].latency,
            },
            "layer2_responses": [
                {
                    "model": r.model.value,
                    "content": r.content,
                    "confidence": r.confidence,
                    "latency": r.latency,
                }
                for r in result["layer2_responses"]
            ],
            "peer_reviews": {
                model.value: [
                    {
                        "reviewer": review.reviewer_model.value,
                        "reviewed": review.reviewed_model.value,
                        "agreement_score": review.agreement_score,
                        "critique": review.critique,
                        "issues": review.identified_issues,
                        "suggestions": review.suggestions,
                    }
                    for review in reviews
                ]
                for model, reviews in result["peer_reviews"].items()
            },
            "token_usage": result["token_usage"],
            "timestamp": result["timestamp"],
        }

        with open(filename, "w") as f:
            json.dump(serializable_result, f, indent=2)

        print(f"\n✓ Saved to {filename}")

    print("\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure your API keys are set:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        print("  export GOOGLE_API_KEY='your-key-here'")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("  export XAI_API_KEY='your-key-here'")
