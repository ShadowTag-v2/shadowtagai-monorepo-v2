"""Full PNKLN Stack Example

Demonstrates all four pillars working together:
1. JR Engine - Purpose/Reasons/Brakes validation
2. Cor - Unified execution orchestration
3. ShadowTag - Cryptographic watermarking
4. NS - Semantic memory retrieval
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.core import FunctionTool, GeminiFunctionCaller
from src.pnkln import CorOrchestrator, JudgeSix, SemanticMemory, ShadowTag


# Define tools
def research_topic(query: str) -> dict:
    """Research a topic."""
    return {
        "query": query,
        "findings": f"Comprehensive research about {query}",
        "key_points": [
            "Point 1 about the topic",
            "Point 2 about the topic",
            "Point 3 about the topic",
        ],
    }


def summarize(data: dict) -> str:
    """Summarize research data."""
    query = data.get("query", "unknown")
    points = data.get("key_points", [])
    return f"Summary of {query}: {len(points)} key points identified"


def main():
    """Run full PNKLN stack example."""
    print("=" * 70)
    print("FULL PNKLN STACK DEMONSTRATION")
    print("JR Engine + Cor + ShadowTag + NS")
    print("=" * 70)
    print()

    # Check API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not set")
        print("Get your free key from: https://aistudio.google.com/app/apikey")
        return

    # 1. Initialize NS (Semantic Memory)
    print("1️⃣  Initializing NS (Semantic Memory)...")
    ns = SemanticMemory()

    # Pre-populate with some memories
    ns.store("Quantum computing uses qubits for computation", {"topic": "quantum"})
    ns.store("AI research focuses on neural networks", {"topic": "ai"})
    ns.store("Blockchain provides decentralized consensus", {"topic": "blockchain"})
    print(f"   ✅ Loaded {ns.get_stats()['total_memories']} memories\n")

    # 2. Initialize ShadowTag
    print("2️⃣  Initializing ShadowTag (Watermarking)...")
    shadowtag = ShadowTag()
    print("   ✅ Cryptographic keys generated\n")

    # 3. Create function caller with tools
    print("3️⃣  Creating Gemini Function Caller...")
    tools = [
        FunctionTool(
            name="research_topic",
            description="Research a topic",
            function=research_topic,
            parameters={"query": {"type": "string"}},
        ),
        FunctionTool(
            name="summarize",
            description="Summarize research data",
            function=summarize,
            parameters={"data": {"type": "object"}},
        ),
    ]

    caller = GeminiFunctionCaller(model_name="gemini-2.0-flash-exp", tools=tools)
    print("   ✅ Function caller ready\n")

    # 4. Wrap with Judge #6
    print("4️⃣  Initializing Judge #6 (JR Engine)...")
    judge = JudgeSix(
        caller=caller,
        mission_statement="Research topics and provide summaries",
        purpose_threshold=0.3,
        reasons_threshold=0.5,
        brakes_threshold=0.8,
    )
    print("   ✅ JR validation layer active\n")

    # 5. Create Cor orchestrator
    print("5️⃣  Initializing Cor (Orchestrator)...")
    cor = CorOrchestrator(function_caller=caller, judge=judge, shadowtag=shadowtag, memory=ns)
    print("   ✅ All systems integrated\n")

    # Execute task
    print("=" * 70)
    print("EXECUTING TASK")
    print("=" * 70)

    task = "Research artificial intelligence and summarize the findings"
    print(f"📋 Task: {task}\n")

    # First, retrieve relevant memories
    print("🔍 Retrieving relevant memories from NS...")
    memories = ns.retrieve(task, top_k=2)
    print(f"   Found {len(memories)} relevant memories:")
    for mem in memories:
        print(f"   • {mem['memory']['content']} (similarity: {mem['similarity']:.2f})")
    print()

    # Execute through Cor
    print("⚙️  Executing through Cor orchestrator...\n")
    try:
        result = cor.execute(task)

        print("\n" + "=" * 70)
        print("RESULT")
        print("=" * 70)
        print(result)
        print()

        # Show Cor metrics
        print("=" * 70)
        print("COR ORCHESTRATION METRICS")
        print("=" * 70)
        metrics = cor.get_metrics()
        print(f"Total Executions: {metrics['total_executions']}")
        print(f"Average Latency: {metrics['average_latency_ms']:.2f}ms")
        print(f"P99 Latency: {metrics['p99_latency_ms']:.2f}ms")
        print(f"Meets p99≤90ms SLA: {'✅ YES' if metrics['meets_sla'] else '❌ NO'}")
        print()

        # Show Judge #6 audit log
        print("=" * 70)
        print("JUDGE #6 AUDIT LOG")
        print("=" * 70)
        for validation in judge.audit_log:
            print(f"• {validation.function_name}: {validation.result.value}")
            print(
                f"  Purpose: {validation.purpose_score:.2f} | "
                f"Reasons: {validation.reasons_score:.2f} | "
                f"Brakes: {validation.brakes_score:.2f}",
            )
        print()

        # Show ShadowTag watermarks
        print("=" * 70)
        print("SHADOWTAG WATERMARKS")
        print("=" * 70)
        audit_trail = shadowtag.export_audit_trail()
        print(f"Total Watermarks: {len(audit_trail)}")
        for wm in audit_trail:
            print(f"\n• Content: {wm['content'][:60]}...")
            print(f"  Signature: {wm['signature'][:40]}...")
            print(f"  Merkle Root: {wm['merkle_root'][:40]}...")
            print(f"  Timestamp: {wm['timestamp']}")
        print()

        # Store result in NS for future retrieval
        print("💾 Storing result in NS for future reference...")
        ns.store(result[:200], {"task": task, "type": "result"})
        print(f"   ✅ Stored. Total memories: {ns.get_stats()['total_memories']}\n")

        print("=" * 70)
        print("✅ FULL PNKLN STACK EXECUTION COMPLETE")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
