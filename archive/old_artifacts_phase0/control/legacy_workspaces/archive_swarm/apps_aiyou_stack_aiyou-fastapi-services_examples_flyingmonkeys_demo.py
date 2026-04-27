"""
n-autoresearch/Kosmos/BioAgentss End-to-End Example

Demonstrates full code generation workflow:
1. n-autoresearch/Kosmos/BioAgentss Orchestrator (200 agents)
2. Antigravity Router (cross-model orchestration)
3. MCP Bridge (98% compression)
4. Legal Whiteboard (persistence)
5. California Bar Protocol (task decomposition)
6. Jury Deliberation (3-phase voting)

Author: Gemini 2.0 Flash (Antigravity)
"""

import asyncio
import sys

sys.path.insert(
    0, "/Users/pikeymickey/Documents/Claude Code/Code/Claude Demo/ShadowTag-v2-fastapi-services"
)

from shadowtagai.agents.n-autoresearch/Kosmos/BioAgentss_orchestrator import (
    CodeGenerationTask,
    n-autoresearch/Kosmos/BioAgentssOrchestrator,
)


async def demo_code_generation():
    """
    Demo: Complete code generation workflow with n-autoresearch/Kosmos/BioAgentss
    """
    print("\n" + "=" * 70)
    print("  n-autoresearch/Kosmos/BioAgentsS + ANTIGRAVITY HANDOFF - END-TO-END DEMO")
    print("=" * 70 + "\n")

    # Initialize orchestrator (200 agents)
    print("Step 1: Initializing n-autoresearch/Kosmos/BioAgentss Orchestrator (200 agents)")
    print("-" * 70)

    orchestrator = n-autoresearch/Kosmos/BioAgentssOrchestrator(
        git_repo_path="/Users/pikeymickey/Documents/Claude Code/Code/Claude Demo/ShadowTag-v2-fastapi-services",
        total_agents=200,
    )

    # Initialize agents
    print("\nStep 2: Initializing agent swarm")
    print("-" * 70)
    await orchestrator.initialize_agents()

    # Create code generation task
    print("\nStep 3: Creating code generation task")
    print("-" * 70)

    task = CodeGenerationTask(
        task_id="DEMO_001",
        description="""
        Implement a user authentication middleware for FastAPI that:
        1. Validates JWT tokens from Authorization header
        2. Checks user permissions against a PostgreSQL database
        3. Rate limits requests to 100/min per user
        4. Logs all authentication attempts to CloudWatch
        5. Returns 401 for invalid tokens, 403 for insufficient permissions
        """,
        context={
            "framework": "FastAPI",
            "auth_type": "JWT",
            "database": "PostgreSQL",
            "logging": "CloudWatch",
        },
        confidence=0.85,
        priority=4,
        specialist_required="python",
    )

    print(f"   Task ID: {task.task_id}")
    print(f"   Description: {task.description[:100]}...")
    print(f"   Specialist: {task.specialist_required}")
    print(f"   Priority: {task.priority}/5")

    # Execute with full swarm
    print("\nStep 4: Executing with n-autoresearch/Kosmos/BioAgentss swarm")
    print("-" * 70)

    result = await orchestrator.execute_code_generation(task)

    # Display results
    print("\nStep 5: Results")
    print("-" * 70)
    print(f"   ✅ Task completed: {result['task_id']}")
    print(f"   Decisions made: {len(result['decisions'])}")
    print(f"   Timestamp: {result['timestamp']}")

    # Show agent stats
    print("\nStep 6: Agent Swarm Statistics")
    print("-" * 70)

    from shadowtagai.agents.core.legal_whiteboard import Whiteboard

    stats = Whiteboard.get_swarm_stats()

    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Show Antigravity Router stats
    print("\nStep 7: Antigravity Router Statistics")
    print("-" * 70)

    if hasattr(orchestrator, "antigravity_router"):
        router_stats = orchestrator.antigravity_router.get_stats()

        import json

        print(json.dumps(router_stats, indent=2))

    print("\n" + "=" * 70)
    print("  DEMO COMPLETE - n-autoresearch/Kosmos/BioAgentsS + ANTIGRAVITY OPERATIONAL")
    print("=" * 70 + "\n")


async def demo_judge6_binary():
    """
    Demo: Judge#6 binary decision with MCP compression
    """
    print("\n" + "=" * 70)
    print("  JUDGE#6 BINARY DECISION DEMO (p99≤90ms, $0.0003)")
    print("=" * 70 + "\n")

    from app.mcp_bridge import MCPBridge

    # Initialize MCP Bridge
    mcp = MCPBridge()

    # Large policy context (50KB)
    policy_context = {
        "user_id": "user_67890",
        "request_type": "data_access",
        "gdpr_compliance": {"compliant": True, "data": "..." * 5000},
        "ccpa_requirements": {"compliant": True, "data": "..." * 4000},
        "hipaa_validation": {"compliant": True, "data": "..." * 6000},
        "pii_present": True,
        "sudo_access": False,
        "payment_processing": False,
    }

    print("Step 1: ATP 5-19 Risk Scan")
    print(f"   Input size: {len(str(policy_context)):,} bytes")

    # Compress to 487-byte kernel
    kernel = await mcp.atp_519_scan(policy_context, target_bytes=487)

    print(f"   Kernel size: {len(str(kernel.__dict__)):,} bytes")
    print(f"   Threat level: {kernel.threat_level}/10")
    print(f"   Risk score: {kernel.risk_score}/100")

    # Binary decision
    print("\nStep 2: Judge#6 Binary Decision")

    decision = await mcp.judge_six_binary(kernel, max_latency_ms=35)

    print(f"   Decision: {'APPROVE' if decision.decision else 'DENY'}")
    print(f"   Reasoning: {decision.reasoning}")
    print(f"   Latency: {decision.latency_ms:.1f}ms (SLA: ≤35ms)")
    print(f"   Cost: ${decision.cost_usd:.4f}")
    print(f"   Confidence: {decision.confidence:.0%}")

    # SLA validation
    if decision.latency_ms <= 35:
        print(f"\n   ✅ SLA MET: {decision.latency_ms:.1f}ms ≤ 35ms")
    else:
        print(f"\n   ❌ SLA BREACH: {decision.latency_ms:.1f}ms > 35ms")

    print("\n" + "=" * 70 + "\n")


async def demo_antigravity_routing():
    """
    Demo: Antigravity cross-model routing
    """
    print("\n" + "=" * 70)
    print("  ANTIGRAVITY CROSS-MODEL ROUTING DEMO")
    print("=" * 70 + "\n")

    from app.antigravity_handoff import AntigravityRouter, TaskType

    router = AntigravityRouter()

    # Test different task types
    test_tasks = [
        (TaskType.PRODUCTION_INFERENCE, 5_000, 100),
        (TaskType.DEEP_ANALYSIS, 50_000, 2000),
        (TaskType.JUDGE6_BINARY, 1_000, 35),
        (TaskType.CODE_REFACTORING, 25_000, 3000),
    ]

    for task_type, context_size, sla_ms in test_tasks:
        print(f"\nTask: {task_type.value}")
        print(f"   Context size: {context_size:,} bytes")
        print(f"   SLA target: {sla_ms}ms")

        routing = router.decide_routing(
            task_type=task_type, context_size_bytes=context_size, sla_ms=sla_ms
        )

        print(f"   → Routed to: {routing.model.value}")
        print(f"   → Reasoning: {routing.reasoning}")
        print(f"   → Est. latency: {routing.estimated_latency_ms:.0f}ms")
        print(f"   → Est. cost: ${routing.estimated_cost_usd:.4f}")
        print(f"   → MCP compression: {'YES' if routing.use_mcp_compression else 'NO'}")

    print("\n" + "=" * 70 + "\n")


async def main():
    """Run all demos"""
    # Demo 1: Judge#6 binary (fastest)
    await demo_judge6_binary()

    # Demo 2: Antigravity routing
    await demo_antigravity_routing()

    # Demo 3: Full code generation (requires agent init)
    # Uncomment to run (takes ~30s to initialize 200 agents)
    await demo_code_generation()


if __name__ == "__main__":
    asyncio.run(main())
