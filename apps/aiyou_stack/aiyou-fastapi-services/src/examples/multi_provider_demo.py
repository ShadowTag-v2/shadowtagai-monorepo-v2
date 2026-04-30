"""Multi-Provider Demo: Gemini + Anthropic Working Together

This example demonstrates the unified orchestrator routing tasks between
Gemini (for speed/cost) and Anthropic (for reasoning quality).

Performance comparison:
- Simple tasks → Gemini (45-80ms, $0.00)
- Complex reasoning → Anthropic (500-1500ms, superior quality)
- Hybrid workflows → Both working together

Run:
    export GOOGLE_API_KEY='your-gemini-key'
    export ANTHROPIC_API_KEY='your-anthropic-key'
    python src/examples/multi_provider_demo.py
"""

import os
import sys
import time
from typing import Any

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.core.gemini_function_calling import FunctionTool, GeminiFunctionCaller
from src.core.multi_provider import MultiProviderExecutor, Provider
from src.core.unified_orchestrator import TaskComplexity, UnifiedOrchestrator


def print_section(title: str):
    """Print section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def print_result(result: Any, show_trace: bool = False):
    """Pretty print execution result."""
    print(
        f"✓ Result: {result.content[:200]}..."
        if len(result.content) > 200
        else f"✓ Result: {result.content}",
    )
    print("\nMetrics:")
    print(f"  • Complexity: {result.task_complexity.value}")
    print(f"  • Primary Provider: {result.primary_provider.value}")
    if result.secondary_provider:
        print(f"  • Secondary Provider: {result.secondary_provider.value}")
    print(f"  • Latency: {result.total_latency_ms:.2f}ms")
    print(f"  • Cost: ${result.total_cost_usd:.6f}")
    print(f"  • Tokens: {result.total_tokens_input} in / {result.total_tokens_output} out")
    print(f"  • Function Calls: {result.function_calls}")
    print(f"  • LLM Calls: {result.llm_calls}")

    if show_trace and result.execution_trace:
        print("\nExecution Trace:")
        for i, step in enumerate(result.execution_trace, 1):
            print(f"  {i}. {step.get('type', 'unknown')} via {step.get('provider', 'unknown')}")
            if "latency_ms" in step:
                print(f"     Latency: {step['latency_ms']:.2f}ms")
            if "cost_usd" in step:
                print(f"     Cost: ${step['cost_usd']:.6f}")


def demo_simple_tasks(orchestrator: UnifiedOrchestrator):
    """Demo: Simple tasks → Gemini (fast & cheap)."""
    print_section("1. SIMPLE TASKS → Gemini (Fast & Cheap)")

    tasks = [
        "What is 2 + 2?",
        "Calculate 15 * 23",
        "What's the capital of France?",
    ]

    for task in tasks:
        print(f"\nTask: {task}")
        result = orchestrator.execute(task, complexity=TaskComplexity.SIMPLE)
        print_result(result)


def demo_complex_reasoning(orchestrator: UnifiedOrchestrator):
    """Demo: Complex reasoning → Anthropic (superior quality)."""
    print_section("2. COMPLEX REASONING → Anthropic (Superior Quality)")

    tasks = [
        "Explain the philosophical implications of quantum entanglement",
        "Compare and contrast utilitarianism with deontological ethics",
        "Why does general relativity break down at quantum scales?",
    ]

    for task in tasks:
        print(f"\nTask: {task}")
        result = orchestrator.execute(task, complexity=TaskComplexity.COMPLEX)
        print_result(result)


def demo_hybrid_workflow(orchestrator: UnifiedOrchestrator):
    """Demo: Hybrid workflow → Anthropic plans, Gemini executes."""
    print_section("3. HYBRID WORKFLOW → Anthropic Plans, Gemini Executes")

    task = (
        "Research the top 3 AI trends in 2025, analyze their business impact, "
        "and write a concise executive summary"
    )

    print(f"Task: {task}\n")
    result = orchestrator.execute(task, complexity=TaskComplexity.HYBRID)
    print_result(result, show_trace=True)


def demo_auto_routing(orchestrator: UnifiedOrchestrator):
    """Demo: Automatic complexity detection."""
    print_section("4. AUTO-ROUTING → Automatic Complexity Detection")

    tasks = [
        ("What is 5 * 5?", "Should route to SIMPLE → Gemini"),
        ("Explain why the sky is blue", "Should route to COMPLEX → Anthropic"),
        ("Search for papers on AI and summarize findings", "Should route to HYBRID"),
    ]

    for task, expected in tasks:
        print(f"\nTask: {task}")
        print(f"Expected: {expected}")
        result = orchestrator.execute(task)  # Auto-detect complexity
        print_result(result)


def demo_provider_override(orchestrator: UnifiedOrchestrator):
    """Demo: Manual provider selection."""
    print_section("5. PROVIDER OVERRIDE → Manual Selection")

    task = "Explain machine learning"

    # Force Gemini
    print(f"\nTask: {task}")
    print("Forcing Provider: Gemini")
    result = orchestrator.execute(
        task,
        provider=Provider.GEMINI,
        complexity=TaskComplexity.MODERATE,
    )
    print_result(result)

    # Force Anthropic
    print(f"\nTask: {task}")
    print("Forcing Provider: Anthropic")
    result = orchestrator.execute(
        task,
        provider=Provider.ANTHROPIC,
        complexity=TaskComplexity.MODERATE,
    )
    print_result(result)


def demo_with_function_calling(orchestrator: UnifiedOrchestrator):
    """Demo: Function calling with Gemini."""
    print_section("6. FUNCTION CALLING → Gemini with Python Tools")

    # Define example tools
    def get_weather(city: str) -> str:
        """Get weather for a city."""
        # Mock weather API
        weather_data = {
            "San Francisco": "Sunny, 72°F",
            "New York": "Cloudy, 65°F",
            "London": "Rainy, 58°F",
        }
        return weather_data.get(city, "Unknown city")

    def calculate_distance(city1: str, city2: str) -> str:
        """Calculate distance between cities."""
        # Mock distance calculation
        return f"Distance between {city1} and {city2}: ~500 miles"

    # Create function caller with tools
    tools = [
        FunctionTool(
            name="get_weather",
            description="Get current weather for a city",
            function=get_weather,
            parameters={"city": {"type": "string", "description": "City name"}},
        ),
        FunctionTool(
            name="calculate_distance",
            description="Calculate distance between two cities",
            function=calculate_distance,
            parameters={
                "city1": {"type": "string", "description": "First city"},
                "city2": {"type": "string", "description": "Second city"},
            },
        ),
    ]

    function_caller = GeminiFunctionCaller(model_name="gemini-3.1-flash-lite-preview", tools=tools)

    # Create orchestrator with function calling
    orch_with_tools = UnifiedOrchestrator(function_caller=function_caller, enable_auto_routing=True)

    task = "What's the weather in San Francisco and how far is it from New York?"
    print(f"Task: {task}\n")

    result = orch_with_tools.execute(task, complexity=TaskComplexity.SIMPLE)
    print_result(result)


def demo_performance_comparison():
    """Demo: Side-by-side performance comparison."""
    print_section("7. PERFORMANCE COMPARISON → Gemini vs Anthropic")

    executor = MultiProviderExecutor()

    task = "Explain photosynthesis in 2 sentences"

    # Gemini
    print("\nGemini 2.0 Flash:")
    start = time.time()
    gemini_result = executor.execute(task, provider=Provider.GEMINI, max_tokens=200)
    gemini_time = (time.time() - start) * 1000

    print(f"  Result: {gemini_result.content}")
    print(f"  Latency: {gemini_time:.2f}ms")
    print(f"  Cost: ${gemini_result.cost_usd:.6f}")
    print(f"  Tokens: {gemini_result.tokens_output} out")

    # Anthropic
    print("\nAnthropic Claude Sonnet 4.5:")
    start = time.time()
    anthropic_result = executor.execute(task, provider=Provider.ANTHROPIC, max_tokens=200)
    anthropic_time = (time.time() - start) * 1000

    print(f"  Result: {anthropic_result.content}")
    print(f"  Latency: {anthropic_time:.2f}ms")
    print(f"  Cost: ${anthropic_result.cost_usd:.6f}")
    print(f"  Tokens: {anthropic_result.tokens_output} out")

    # Comparison
    print("\nComparison:")
    print(f"  Speed: Gemini is {anthropic_time / gemini_time:.1f}x faster")
    print(
        f"  Cost: Gemini is {anthropic_result.cost_usd / max(gemini_result.cost_usd, 0.000001):.1f}x cheaper",
    )


def demo_metrics(orchestrator: UnifiedOrchestrator):
    """Demo: Aggregated metrics."""
    print_section("8. METRICS → Aggregated Performance Data")

    metrics = orchestrator.get_metrics()

    print(f"Total Executions: {metrics['total_executions']}")
    print(f"Total Cost: ${metrics['total_cost_usd']:.6f}")
    print(f"Average Latency: {metrics['average_latency_ms']:.2f}ms")
    print(f"Total Function Calls: {metrics['total_function_calls']}")
    print(f"Total LLM Calls: {metrics['total_llm_calls']}")

    print("\nProvider Distribution:")
    for provider, count in metrics["provider_distribution"].items():
        percentage = (count / metrics["total_executions"]) * 100
        print(f"  • {provider}: {count} ({percentage:.1f}%)")

    print("\nComplexity Distribution:")
    for complexity, count in metrics["complexity_distribution"].items():
        percentage = (count / metrics["total_executions"]) * 100
        print(f"  • {complexity}: {count} ({percentage:.1f}%)")

    print("\nToken Usage:")
    print(f"  • Input: {metrics['total_tokens_input']:,}")
    print(f"  • Output: {metrics['total_tokens_output']:,}")
    print(f"  • Total: {metrics['total_tokens_input'] + metrics['total_tokens_output']:,}")


def main():
    """Run all demos."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║       MULTI-PROVIDER ORCHESTRATOR DEMO                          ║
║       Gemini + Anthropic Working Together                       ║
║                                                                  ║
║  • Simple tasks → Gemini (12x faster, 70% cheaper)             ║
║  • Complex reasoning → Anthropic (superior quality)             ║
║  • Hybrid workflows → Best of both worlds                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Check API keys
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  GOOGLE_API_KEY not set. Gemini examples will fail.")
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not set. Anthropic examples will fail.")

    if not os.getenv("GOOGLE_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ No API keys found. Please set at least one:")
        print("   export GOOGLE_API_KEY='your-key'")
        print("   export ANTHROPIC_API_KEY='your-key'")
        sys.exit(1)

    # Create orchestrator
    orchestrator = UnifiedOrchestrator(enable_auto_routing=True)

    try:
        # Run demos
        demo_simple_tasks(orchestrator)
        demo_complex_reasoning(orchestrator)
        demo_hybrid_workflow(orchestrator)
        demo_auto_routing(orchestrator)
        demo_provider_override(orchestrator)
        demo_with_function_calling(orchestrator)
        demo_performance_comparison()
        demo_metrics(orchestrator)

        print_section("✓ ALL DEMOS COMPLETED")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
