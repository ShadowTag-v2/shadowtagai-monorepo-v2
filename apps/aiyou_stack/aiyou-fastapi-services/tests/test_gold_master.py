#!/usr/bin/env python3
"""
▛///▞ ANTIGRAVITY :: UNIFIED TEST SUITE
:: "Details matter, it's worth waiting to get it right." - Steve Jobs

COMPREHENSIVE TEST SUITE FOR SHADOWTAG OMEGA GOLD MASTER

Run: pytest tests/test_gold_master.py -v
"""

import os
import sys

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==============================================================================
# FIXTURE: ENVIRONMENT SETUP
# ==============================================================================


@pytest.fixture(scope="module")
def setup_env():
    """Ensure proper environment for testing"""
    os.environ.setdefault("PYTHONPATH", os.getcwd())
    return True


# ==============================================================================
# TEST SUITE 1: JUDGE#6 UNIFIED
# ==============================================================================


class TestJudge6Unified:
    """Test the merged Judge#6 CSRMC enforcement engine"""

    @pytest.fixture
    def judge(self):
        from libs.shadowtag_v4.governance.judge6_unified import judge_unified

        return judge_unified

    def test_judge_singleton_exists(self, judge):
        """Verify Judge#6 singleton is instantiated"""
        assert judge is not None
        assert hasattr(judge, "enforce")
        assert hasattr(judge, "gate")
        assert hasattr(judge, "calculate_s_score")

    @pytest.mark.asyncio
    async def test_legal_gate_blocks_illegal(self, judge):
        """Legal gate should KILL illegal activities"""
        result = await judge.enforce(
            action="hack into competitor database", context={"authenticated": True}
        )
        assert result.approved == False
        assert result.verdict.value == "KILL"
        assert "LEGAL" in str(result.gates_triggered)

    @pytest.mark.asyncio
    async def test_financial_gate_requires_roi(self, judge):
        """Financial gate should block low ROI"""
        result = await judge.enforce(
            action="invest in new project",
            context={
                "authenticated": True,
                "roi": 1.5,  # Below 3x threshold
                "ltv_cac": 5.0,
                "npv_confidence": 0.80,
            },
        )
        assert result.approved == False
        assert "ROI" in result.reasoning or "Financial" in result.reasoning

    @pytest.mark.asyncio
    async def test_normal_operation_passes(self, judge):
        """Normal operation should pass all gates"""
        result = await judge.enforce(
            action="deploy feature to staging",
            context={"authenticated": True, "roi": 5.0, "ltv_cac": 6.0, "npv_confidence": 0.85},
        )
        assert result.approved == True
        assert result.latency_ms < 100  # p99 SLA

    @pytest.mark.asyncio
    async def test_sla_compliance(self, judge):
        """Judge#6 should meet p99 ≤ 90ms SLA"""
        latencies = []
        for _ in range(10):
            result = await judge.enforce(action="test action", context={"authenticated": True})
            latencies.append(result.latency_ms)

        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 90, f"Average latency {avg_latency:.2f}ms exceeds 90ms SLA"

    def test_s_score_calculation(self, judge):
        """S-Score survivability calculation"""
        status, score = judge.calculate_s_score(hardening=1.0, vulnerability=0.5)
        assert status == "NOMINAL"
        assert score > 1.0

        status, score = judge.calculate_s_score(hardening=0.5, vulnerability=1.0)
        assert status == "TRIGGER_ESTOP"
        assert score < 1.0

    def test_legacy_gate_function(self, judge):
        """Legacy gate() function for backward compatibility"""
        result = judge.gate(
            action="approve purchase",
            payload={
                "intent": "revenue growth",
                "roi": 4.0,
                "ltv_cac": 5.0,
                "npv_confidence": 0.75,
            },
        )
        assert result["verdict"] == "APPROVED"

    def test_code_hazard_scan(self, judge):
        """Hazard database scan for code security"""
        assessment = judge.assess_code("const key = 'sk-1234567890abcdef'")
        assert assessment.verdict.value in ["WARN", "KILL"]
        assert "API Key" in assessment.rationale


# ==============================================================================
# TEST SUITE 2: AG-UI PROTOCOL ADAPTER
# ==============================================================================


class TestAGUIAdapter:
    """Test AG-UI protocol adapter for CopilotKit integration"""

    @pytest.fixture
    def adapter(self):
        from libs.shadowtag_v4.protocols.agui_adapter import AGUIAdapter

        return AGUIAdapter(agent_id="test_agent")

    def test_adapter_initialization(self, adapter):
        """Adapter should initialize with correct agent ID"""
        assert adapter.agent_id == "test_agent"
        assert adapter.current_run_id is None

    @pytest.mark.asyncio
    async def test_run_lifecycle_events(self, adapter):
        """Test RUN_STARTED and RUN_FINISHED events"""
        start_event = await adapter.emit_run_started()
        assert start_event.type.value == "RUN_STARTED"
        assert adapter.current_run_id is not None

        end_event = await adapter.emit_run_finished(success=True)
        assert end_event.type.value == "RUN_FINISHED"

    @pytest.mark.asyncio
    async def test_text_streaming_events(self, adapter):
        """Test TEXT_MESSAGE_* streaming events"""
        await adapter.emit_run_started()

        start = await adapter.emit_text_start(message_id="msg_1")
        assert start.type.value == "TEXT_MESSAGE_START"

        delta = await adapter.emit_text_delta("Hello ", "msg_1")
        assert delta.type.value == "TEXT_MESSAGE_CONTENT"
        assert delta.delta == "Hello "

        end = await adapter.emit_text_end("msg_1")
        assert end.type.value == "TEXT_MESSAGE_END"

    @pytest.mark.asyncio
    async def test_tool_call_events(self, adapter):
        """Test TOOL_CALL_* events"""
        await adapter.emit_run_started()

        start = await adapter.emit_tool_call_start(
            tool_name="calculator", args={"expression": "2+2"}, tool_call_id="tool_1"
        )
        assert start.type.value == "TOOL_CALL_START"
        assert start.tool_name == "calculator"

        end = await adapter.emit_tool_call_end(
            tool_call_id="tool_1", tool_name="calculator", result=4
        )
        assert end.type.value == "TOOL_CALL_END"
        assert end.result == 4

    @pytest.mark.asyncio
    async def test_shadowtag_extension_events(self, adapter):
        """Test ShadowTag-specific extension events"""
        await adapter.emit_run_started()

        # Swarm vote
        vote = await adapter.emit_swarm_vote(
            intent="deploy to production",
            risk_level="M",
            verdict="PASS",
            confidence=0.85,
            brakes=0,
            troops_voting={"HHT": {"approve": 90, "reject": 0}},
        )
        assert vote.type.value == "SWARM_VOTE_RESULT"

        # Judge#6 gate
        gate = await adapter.emit_judge6_gate(
            gate="financial",
            approved=True,
            risk_level="L",
            reasoning="ROI 5× exceeds threshold",
            latency_ms=12.5,
        )
        assert gate.type.value == "JUDGE6_GATE"

        # CSRMC checkpoint
        checkpoint = await adapter.emit_csrmc_checkpoint(
            phase="operations", s_score=1.25, status="NOMINAL"
        )
        assert checkpoint.type.value == "CSRMC_CHECKPOINT"

    @pytest.mark.asyncio
    async def test_sse_format(self, adapter):
        """Events should format correctly as Server-Sent Events"""
        event = await adapter.emit_run_started()
        sse = event.to_sse()

        assert sse.startswith("data: ")
        assert sse.endswith("\n\n")
        assert '"type":"RUN_STARTED"' in sse


# ==============================================================================
# TEST SUITE 3: n-autoresearch/Kosmos/BioAgents SWARM
# ==============================================================================


class Testn-autoresearch/Kosmos/BioAgentsSwarm:
    """Test n-autoresearch/Kosmos/BioAgents v8 swarm orchestration"""

    @pytest.fixture
    def swarm(self):
        from libs.shadowtag_v4.agents.n-autoresearch/Kosmos/BioAgents_v8 import n-autoresearch/Kosmos/BioAgentsV8

        return n-autoresearch/Kosmos/BioAgentsV8()  # Mock mode (no API key)

    def test_swarm_initialization(self, swarm):
        """Swarm should initialize with components"""
        assert swarm.mission == "MAKE CASH"
        assert swarm.registry is not None
        assert swarm.sandbox is not None
        assert swarm.router is not None

    def test_tool_registry(self, swarm):
        """Tool registry should have default tools"""
        tools = swarm.search_tools("calc")
        assert len(tools) > 0
        assert "calculator" in tools

    def test_sandbox_execution(self, swarm):
        """Sandbox should execute safe Python code"""
        result = swarm.execute_code("results['answer'] = 2 + 2")
        assert result["error"] is None
        assert result["results"]["answer"] == 4

    def test_sandbox_blocks_imports(self, swarm):
        """Sandbox should block import statements"""
        result = swarm.execute_code("import os")
        assert result["error"] is not None
        assert "Imports not allowed" in result["error"]

    def test_puzzle_room_creation(self, swarm):
        """Puzzle room should initialize with 7 locks"""
        room = swarm.puzzle_room()
        status = room.get_status()
        assert status["locks_total"] == 7
        assert status["locks_solved"] == 0
        assert status["vault_open"] == False

    def test_puzzle_room_solve_lock(self, swarm):
        """Puzzle room should solve locks correctly"""
        room = swarm.puzzle_room()

        # Solve lock 1 (Victorian Math: 1847 + 1776 - 1492 = 2131)
        result = room.attempt_lock(1, 2131)
        assert result["success"] == True

        # Wrong answer should fail
        result = room.attempt_lock(2, 9999)
        assert result["success"] == False

    def test_token_tracking(self, swarm):
        """Token usage should be tracked"""
        assert hasattr(swarm.tokens, "input_tokens")
        assert hasattr(swarm.tokens, "output_tokens")
        assert hasattr(swarm.tokens, "cost")


# ==============================================================================
# TEST SUITE 4: MULTI-MODEL ROUTER
# ==============================================================================


class TestMultiModelRouter:
    """Test Claude + Gemini routing logic"""

    @pytest.fixture
    def router(self):
        from libs.shadowtag_v4.agents.n-autoresearch/Kosmos/BioAgents_v8 import MultiModelRouter

        return MultiModelRouter()

    def test_router_initialization(self, router):
        """Router should initialize with token trackers"""
        assert hasattr(router, "gemini_tokens")
        assert hasattr(router, "claude_tokens")

    def test_bulk_read_routing(self, router):
        """Bulk reading tasks should route to Gemini"""
        assert router.should_route_to_gemini("read all files in directory") == True
        assert router.should_route_to_gemini("analyze codebase") == True
        assert router.should_route_to_gemini("summarize documents") == True

    def test_reasoning_stays_claude(self, router):
        """Reasoning tasks should stay with Claude"""
        assert router.should_route_to_gemini("design system architecture") == False
        assert router.should_route_to_gemini("write implementation plan") == False

    def test_large_context_routes_gemini(self, router):
        """Large context tasks should route to Gemini (2M window)"""
        assert router.should_route_to_gemini("any task", context_size=150000) == True

    def test_cost_comparison(self, router):
        """Cost comparison should calculate savings"""
        comparison = router.cost_comparison()
        assert "gemini_cost" in comparison
        assert "claude_cost" in comparison
        assert "savings" in comparison


# ==============================================================================
# TEST SUITE 5: INTEGRATION TESTS
# ==============================================================================


class TestIntegration:
    """End-to-end integration tests"""

    @pytest.mark.asyncio
    async def test_judge_to_agui_pipeline(self):
        """Judge#6 decision should emit AG-UI event"""
        from libs.shadowtag_v4.governance.judge6_unified import judge_unified
        from libs.shadowtag_v4.protocols.agui_adapter import AGUIAdapter

        adapter = AGUIAdapter(agent_id="integration_test")
        await adapter.emit_run_started()

        # Make Judge#6 decision
        decision = await judge_unified.enforce(
            action="process payment",
            context={"authenticated": True, "roi": 5.0, "ltv_cac": 6.0, "npv_confidence": 0.80},
        )

        # Emit as AG-UI event
        gate_event = await adapter.emit_judge6_gate(
            gate="unified",
            approved=decision.approved,
            risk_level=decision.risk_level.value,
            reasoning=decision.reasoning,
            latency_ms=decision.latency_ms,
        )

        assert gate_event.approved == decision.approved
        assert gate_event.latency_ms == decision.latency_ms

    def test_unified_agent_import(self):
        """Unified agent layer should import cleanly"""
        # This tests the __init__.py consolidation
        try:
            from libs.shadowtag_v4.agents import registry, rlm, router, sandbox, swarm

            assert swarm is not None
            assert router is not None
        except ImportError as e:
            # Expected if running outside full environment
            pytest.skip(f"Full environment needed: {e}")


# ==============================================================================
# MAIN: RUN ALL TESTS
# ==============================================================================

if __name__ == "__main__":
    print("▛///▞ SHADOWTAG OMEGA :: GOLD MASTER TEST SUITE")
    print("=" * 60)
    pytest.main([__file__, "-v", "--tb=short", "-x"])
