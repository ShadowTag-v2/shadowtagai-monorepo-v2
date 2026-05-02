"""
Unit tests for ShadowTag-v2JR Core Framework
Testing PRISM, Business Plan, Framework, and Context modules

Author: ShadowTag-v2JR System
Date: 2025-11-17
"""

import pytest
from src.core import (
    PicoTrace,
    PrismKernel,
    ValueLock,
    PrismRuntime,
    VerticalType,
    BusinessMetrics,
    VerticalPortfolio,
    KillSwitchGates,
    RiskProbability,
    RiskSeverity,
    RiskLevel,
    OperatingFramework,
    TransferPackage,
    StateSummary,
    ImmediateAction,
)


class TestPrismKernel:
    """Test PRISM kernel functionality"""

    def test_pico_trace_validation(self):
        """Test PiCO trace validation"""
        trace = PicoTrace(
            bind_input={"data": "test"}, direct_flow={"flow": "active"}, carry_motion={"motion": "forward"}, project_output={"output": "result"}
        )
        assert trace.validate() is True

    def test_value_lock_initialization(self):
        """Test ValueLock initialization and validation"""
        lock = ValueLock()
        assert lock.operating_mode == "strict"
        assert lock.iq_baseline == 160
        assert lock.validate_posture() is True
        assert len(lock.pillars) == 4
        assert len(lock.research_deltas) == 8

    def test_prism_runtime_initialization(self):
        """Test PRISM runtime initialization"""
        runtime = PrismRuntime()
        trace = PicoTrace(bind_input={"x": 1}, direct_flow={"y": 2}, carry_motion={"z": 3}, project_output={"result": 4})
        kernel = PrismKernel(
            position_sequence=["pos1"],
            role_disciplines=["role1"],
            intent_targets=["intent1"],
            structure_pipeline=["struct1"],
            modality_modes=["mode1"],
        )

        assert runtime.initialize(trace, kernel) is True
        status = runtime.get_status()
        assert status["initialized"] is True
        assert status["posture_valid"] is True

    def test_prism_flow_execution(self):
        """Test PiCO flow execution"""
        runtime = PrismRuntime()
        trace = PicoTrace(bind_input={"a": 1}, direct_flow={"b": 2}, carry_motion={"c": 3}, project_output={"d": 4})
        kernel = PrismKernel(position_sequence=["p"], role_disciplines=["r"], intent_targets=["i"], structure_pipeline=["s"], modality_modes=["m"])

        runtime.initialize(trace, kernel)
        output = runtime.execute_flow()

        assert "a" in output
        assert "b" in output
        assert "c" in output
        assert "d" in output


class TestBusinessPlan:
    """Test business plan functionality"""

    def test_business_metrics(self):
        """Test business metrics defaults"""
        metrics = BusinessMetrics()
        assert metrics.monthly_recurring_revenue == 120_000
        assert metrics.customer_count == 50
        assert metrics.ltv_cac_ratio == 4.0
        assert metrics.gross_margin == 0.75

    def test_vertical_portfolio(self):
        """Test vertical portfolio calculations"""
        portfolio = VerticalPortfolio()

        total_mrr = portfolio.total_mrr()
        assert total_mrr == 74_900  # Sum of all MRR contributions

        total_customers = portfolio.total_customers()
        assert total_customers == 50

        priority = portfolio.get_priority_order()
        assert priority[0] == VerticalType.SALES_AUTOMATION

    def test_vertical_annual_value(self):
        """Test vertical annual value calculation"""
        portfolio = VerticalPortfolio()
        sales_vertical = portfolio.verticals[VerticalType.SALES_AUTOMATION]

        # (1500 * 12 * 15) + (5000 * 15) = 270,000 + 75,000 = 345,000
        assert sales_vertical.annual_value == 345_000

    def test_kill_switch_gates(self):
        """Test kill-switch evaluation"""
        gates = KillSwitchGates()

        # Month 3 - should trigger
        triggered = gates.check_gates(month=3, mrr=8_000, pilots=3)
        assert len(triggered) > 0

        # Month 3 - should pass
        triggered = gates.check_gates(month=3, mrr=12_000, pilots=6)
        assert len(triggered) == 0

        # Month 12 - should trigger
        triggered = gates.check_gates(month=12, mrr=80_000, ltv_cac=3.5)
        assert len(triggered) > 0


class TestOperatingFramework:
    """Test operating framework functionality"""

    def test_risk_assessment_matrix(self):
        """Test risk assessment matrix"""
        framework = OperatingFramework()

        # Extremely high risk
        risk = framework.risk_matrix.assess(RiskProbability.A_FREQUENT, RiskSeverity.I_CATASTROPHIC)
        assert risk == RiskLevel.EH_EXTREMELY_HIGH

        # Low risk
        risk = framework.risk_matrix.assess(RiskProbability.E_UNLIKELY, RiskSeverity.IV_NEGLIGIBLE)
        assert risk == RiskLevel.L_LOW

    def test_action_gates(self):
        """Test action gate determination"""
        framework = OperatingFramework()

        gate = framework.risk_matrix.get_action_gate(RiskLevel.EH_EXTREMELY_HIGH)
        assert gate == "BLOCK (non-negotiable)"

        gate = framework.risk_matrix.get_action_gate(RiskLevel.L_LOW)
        assert gate == "ALLOW"

    def test_decision_validation(self):
        """Test decision protocol validation"""
        framework = OperatingFramework()

        # Should approve low-risk aligned action
        result = framework.assess_action(
            action="Deploy new feature",
            probability=RiskProbability.D_SELDOM,
            severity=RiskSeverity.III_MODERATE,
            mission_aligned=True,
            doctrine_compliant=True,
        )

        assert result["approved"] is True
        assert result["risk_level"] == "L"

        # Should block misaligned action
        result = framework.assess_action(
            action="Deploy vulnerable code",
            probability=RiskProbability.A_FREQUENT,
            severity=RiskSeverity.I_CATASTROPHIC,
            mission_aligned=False,
            doctrine_compliant=False,
        )

        assert result["approved"] is False

    def test_code_validation(self):
        """Test code constraint validation"""
        framework = OperatingFramework()

        # Valid code
        result = framework.validate_code(function_lines=15, test_coverage=0.85)
        assert result["function_length_valid"] is True
        assert result["test_coverage_valid"] is True

        # Invalid code
        result = framework.validate_code(function_lines=25, test_coverage=0.60)
        assert result["function_length_valid"] is False
        assert result["test_coverage_valid"] is False

    def test_development_constraints(self):
        """Test development constraints"""
        framework = OperatingFramework()

        assert framework.constraints.max_function_length == 20
        assert framework.constraints.test_coverage_min == 0.80
        assert len(framework.constraints.shipping_philosophy) == 4
        assert len(framework.constraints.guardrails) == 3


class TestContextManagement:
    """Test context and rollup functionality"""

    def test_transfer_package_creation(self):
        """Test transfer package creation"""
        package = TransferPackage()

        state = StateSummary(
            what_built="AI Agent Business Plan",
            core_asset=["Business plan", "Tech architecture"],
            key_verticals=["Sales", "Content"],
            technical_foundation={"stack": "Python"},
            business_model={"type": "SaaS"},
            go_to_market={"phase": "Week 1"},
            critical_frameworks=["ATP 5-19"],
        )

        action = ImmediateAction(
            priority=1, category="revenue", task="Build Sales Agent MVP", subtasks=["Setup", "Integrate", "Deploy"], deadline="Week 1"
        )

        context = package.create_context(
            state_summary=state,
            metrics={"mrr": 120_000},
            verticals={},
            tech_stack={},
            kill_switches={},
            decision_framework={},
            actions=[action],
            principles={},
            frameworks={},
        )

        assert context is not None
        assert context.state_summary.what_built == "AI Agent Business Plan"

    def test_restart_prompt_formatting(self):
        """Test restart prompt markdown formatting"""
        package = TransferPackage()

        prompt = package.create_restart_prompt(
            project="AI Agent Business Plan",
            phase="Week 1",
            context="Building SaaS platform",
            completed=["Business plan", "Architecture"],
            focus={"Priority 1": "Build MVP"},
            parameters={"mrr_target": 120_000},
            constraints=["Functions ≤20 lines"],
            switches=["Month 3: <$10K MRR"],
            posture={"mode": "strict"},
            question="What's next?",
            options=["Build", "Deploy", "Test"],
        )

        markdown = prompt.format_markdown()
        assert "# CONTEXT RESTORATION BLOCK" in markdown
        assert "AI Agent Business Plan" in markdown
        assert "Week 1" in markdown

    def test_package_validation(self):
        """Test transfer package validation"""
        package = TransferPackage()

        state = StateSummary(
            what_built="Test", core_asset=[], key_verticals=[], technical_foundation={}, business_model={}, go_to_market={}, critical_frameworks=[]
        )

        package.create_context(
            state_summary=state,
            metrics={"test": 1},
            verticals={},
            tech_stack={"python": "3.11"},
            kill_switches={},
            decision_framework={},
            actions=[],
            principles={},
            frameworks={},
        )

        validation = package.validate()
        assert validation["business_model_preserved"] is True
        assert validation["technical_stack_defined"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
