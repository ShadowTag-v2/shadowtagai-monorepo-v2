"""PNKLN Integration Tests - Test all four pillars working together"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.core import FunctionTool, GeminiFunctionCaller
from src.pnkln import CorOrchestrator, JudgeSix, SemanticMemory, ShadowTag


def simple_function(x: int) -> int:
    """Simple test function."""
    return x * 2


@pytest.fixture
def full_stack():
    """Create full PNKLN stack for testing."""
    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")

    # Create components
    tools = [
        FunctionTool(
            name="simple_function",
            description="Double a number",
            function=simple_function,
            parameters={"x": {"type": "integer"}},
        ),
    ]

    caller = GeminiFunctionCaller(model_name="gemini-3.1-flash-lite-preview", tools=tools)

    judge = JudgeSix(
        caller=caller,
        mission_statement="Perform mathematical operations",
        purpose_threshold=0.3,
    )

    shadowtag = ShadowTag()
    ns = SemanticMemory()

    cor = CorOrchestrator(function_caller=caller, judge=judge, shadowtag=shadowtag, memory=ns)

    return {"cor": cor, "judge": judge, "shadowtag": shadowtag, "ns": ns}


def test_cor_orchestration(full_stack):
    """Test Cor orchestration of all components."""
    cor = full_stack["cor"]

    result = cor.execute("Double the number 5")
    assert result is not None

    # Check metrics
    metrics = cor.get_metrics()
    assert metrics["total_executions"] == 1
    assert metrics["average_latency_ms"] > 0


def test_shadowtag_watermarking(full_stack):
    """Test ShadowTag watermarking."""
    shadowtag = full_stack["shadowtag"]

    content = "Test content"
    watermarked = shadowtag.watermark(content, {"test": "metadata"})

    # Content should be unchanged (watermark stored separately)
    assert watermarked == content

    # Watermark should be stored
    assert len(shadowtag.watermarks) > 0

    # Watermark should be verifiable
    wm = shadowtag.watermarks[-1]
    assert shadowtag.verify(wm)


def test_ns_memory_storage_and_retrieval(full_stack):
    """Test NS memory storage and retrieval."""
    ns = full_stack["ns"]

    # Store memories
    ns.store("Python is a programming language", {"topic": "programming"})
    ns.store("JavaScript is used for web development", {"topic": "web"})

    # Retrieve
    results = ns.retrieve("Tell me about programming languages", top_k=2)

    assert len(results) > 0
    assert "memory" in results[0]
    assert "similarity" in results[0]


def test_full_stack_integration(full_stack):
    """Test complete integration of all PNKLN components."""
    cor = full_stack["cor"]
    judge = full_stack["judge"]
    shadowtag = full_stack["shadowtag"]
    ns = full_stack["ns"]

    # Store some context in NS
    ns.store("We are testing mathematical operations", {"context": "test"})

    # Execute through Cor
    result = cor.execute("Double the number 7")

    # Verify all components were engaged
    assert result is not None  # Cor executed
    assert len(judge.audit_log) > 0  # Judge validated
    assert len(shadowtag.watermarks) > 0  # ShadowTag watermarked
    assert ns.get_stats()["total_memories"] > 0  # NS has memories

    print("\nIntegration Test Results:")
    print(f"  Cor Executions: {cor.get_metrics()['total_executions']}")
    print(f"  Judge Validations: {len(judge.audit_log)}")
    print(f"  ShadowTag Watermarks: {len(shadowtag.watermarks)}")
    print(f"  NS Memories: {ns.get_stats()['total_memories']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
