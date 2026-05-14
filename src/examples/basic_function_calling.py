# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Basic Gemini Function Calling Example

Demonstrates the simplest migration from AutoGen to native Gemini.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.core import GeminiFunctionCaller, FunctionTool


# Define your tools as Python functions
def research_topic(query: str) -> dict:
    """Research a topic and return findings."""
    print(f"🔍 Researching: {query}")
    return {
        "query": query,
        "findings": f"Research results for: {query}",
        "sources": ["academic.paper.com", "research.institute.edu"],
        "key_insights": ["Key insight #1 about the topic", "Key insight #2 about the topic", "Key insight #3 about the topic"],
    }


def analyze_data(data: dict) -> dict:
    """Analyze research data and extract insights."""
    print(f"📊 Analyzing data: {data.get('query', 'unknown')}")
    return {
        "insights": ["Pattern A detected in research", "Correlation B found between factors", "Trend C emerging in the field"],
        "confidence": 0.85,
        "methodology": "Statistical analysis with cross-validation",
    }


def write_report(analysis: dict) -> str:
    """Write a final report based on analysis."""
    insights = analysis.get("insights", [])
    print(f"📝 Writing report with {len(insights)} insights")

    report = f"""
# Research Report

## Executive Summary
Based on comprehensive analysis, we identified {len(insights)} key insights.

## Key Findings
"""
    for i, insight in enumerate(insights, 1):
        report += f"{i}. {insight}\n"

    report += f"\n## Confidence Level\n{analysis.get('confidence', 0) * 100:.1f}%\n"

    return report


def main():
    """Run basic function calling example."""
    print("=" * 60)
    print("BASIC GEMINI FUNCTION CALLING EXAMPLE")
    print("AutoGen Replacement Demo")
    print("=" * 60)
    print()

    # Check for API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not set")
        print("Get your free key from: https://aistudio.google.com/app/apikey")
        print("Then run: export GOOGLE_API_KEY='your-key-here'")
        return

    # Define tools
    tools = [
        FunctionTool(
            name="research_topic",
            description="Research a topic and return findings",
            function=research_topic,
            parameters={"query": {"type": "string", "description": "The topic to research"}},
        ),
        FunctionTool(
            name="analyze_data",
            description="Analyze research data and extract insights",
            function=analyze_data,
            parameters={"data": {"type": "object", "description": "The research data to analyze"}},
        ),
        FunctionTool(
            name="write_report",
            description="Write final report based on analysis",
            function=write_report,
            parameters={"analysis": {"type": "object", "description": "The analysis results"}},
        ),
    ]

    # Create function caller
    print("🚀 Initializing Gemini Function Caller...")
    caller = GeminiFunctionCaller(
        model_name="gemini-2.0-flash-exp",
        tools=tools,
        system_instruction="""You are a research assistant. When given a topic to research:
1. First call research_topic to gather information
2. Then call analyze_data to extract insights
3. Finally call write_report to create a comprehensive report""",
    )
    print("✅ Initialized\n")

    # Execute
    prompt = "Research quantum computing, analyze the findings, and write a comprehensive report"
    print(f"📋 Task: {prompt}\n")
    print("⏱️  Executing...\n")

    try:
        result = caller.execute(prompt)

        print("\n" + "=" * 60)
        print("RESULT")
        print("=" * 60)
        print(result)
        print()

        # Show metrics
        metrics = caller.get_metrics()
        print("=" * 60)
        print("PERFORMANCE METRICS")
        print("=" * 60)
        print(f"Total Latency: {metrics['total_latency_ms']:.2f}ms")
        print(f"Function Calls: {metrics['function_calls']}")
        print(f"Function Execution Time: {metrics['total_function_time_ms']:.2f}ms")
        print(f"Gemini Overhead: {metrics['gemini_overhead_ms']:.2f}ms")
        print(f"Meets p99≤90ms SLA: {'✅ YES' if metrics['meets_p99_sla'] else '❌ NO'}")
        print()

        print("Function Call Timeline:")
        for fc in metrics["function_execution_times"]:
            print(f"  • {fc['name']}: {fc['time_ms']:.2f}ms")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
