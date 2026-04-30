"""Test Quality Gates

Aligned with new requirements:
- Items, Sources, Costs, Scores instead of 98% coverage
- 60% confidence threshold for pre-prod
"""

from src.gemini_ingestion_layer.quality.gates import GateStatus, QualityGates


def test_items_volume_pass():
    """Test items volume gate passes with sufficient items"""
    gates = QualityGates(daily_items_target=10000, daily_items_min=8000)

    stats = {
        "items_ingested": 10500,
        "unique_sources": 5,
        "total_cost_usd": 10.0,
        "average_relevance_score": 0.70,
        "items_by_age": [],
        "field_completion_rates": [1.0],
        "runtime_minutes": 40.0,
    }

    result = gates.evaluate(stats)
    volume_gate = next(g for g in result.gates if g.name == "Items Volume")

    assert volume_gate.status == GateStatus.PASS
    assert volume_gate.actual_value == 10500


def test_items_volume_warning():
    """Test items volume gate warns when below target but above minimum"""
    gates = QualityGates(daily_items_target=10000, daily_items_min=8000)

    stats = {
        "items_ingested": 9000,
        "unique_sources": 5,
        "total_cost_usd": 9.0,
        "average_relevance_score": 0.65,
        "items_by_age": [],
        "field_completion_rates": [1.0],
        "runtime_minutes": 40.0,
    }

    result = gates.evaluate(stats)
    volume_gate = next(g for g in result.gates if g.name == "Items Volume")

    assert volume_gate.status == GateStatus.WARN


def test_cost_efficiency_pass():
    """Test cost efficiency gate with target cost"""
    gates = QualityGates(cost_per_item_target=0.001)

    stats = {
        "items_ingested": 10000,
        "unique_sources": 5,
        "total_cost_usd": 8.0,  # $0.0008 per item
        "average_relevance_score": 0.65,
        "items_by_age": [],
        "field_completion_rates": [1.0],
        "runtime_minutes": 40.0,
    }

    result = gates.evaluate(stats)
    cost_gate = next(g for g in result.gates if g.name == "Cost Efficiency")

    assert cost_gate.status == GateStatus.PASS


def test_relevance_score_threshold_60_percent():
    """Test 60% confidence threshold for pre-prod (not 70% like Judge 6)"""
    gates = QualityGates(min_relevance_score=0.60)

    # Just above threshold
    stats_pass = {
        "items_ingested": 10000,
        "unique_sources": 5,
        "total_cost_usd": 10.0,
        "average_relevance_score": 0.62,  # 62% - should pass
        "items_by_age": [],
        "field_completion_rates": [0.9],
        "runtime_minutes": 40.0,
    }

    result_pass = gates.evaluate(stats_pass)
    relevance_gate = next(g for g in result_pass.gates if g.name == "Relevance Score")
    assert relevance_gate.status == GateStatus.PASS

    # Just below threshold
    stats_fail = stats_pass.copy()
    stats_fail["average_relevance_score"] = 0.58  # 58% - should fail

    result_fail = gates.evaluate(stats_fail)
    relevance_gate_fail = next(g for g in result_fail.gates if g.name == "Relevance Score")
    assert relevance_gate_fail.status == GateStatus.FAIL


def test_runtime_efficiency():
    """Test runtime efficiency gate (~45 min target, 60 min max)"""
    gates = QualityGates(target_runtime_minutes=45, max_runtime_minutes=60)

    # Within target
    stats_pass = {
        "items_ingested": 10000,
        "unique_sources": 5,
        "total_cost_usd": 10.0,
        "average_relevance_score": 0.65,
        "items_by_age": [],
        "field_completion_rates": [0.9],
        "runtime_minutes": 42.0,
    }

    result = gates.evaluate(stats_pass)
    runtime_gate = next(g for g in result.gates if g.name == "Runtime Efficiency")
    assert runtime_gate.status == GateStatus.PASS

    # Above target but within max (warning)
    stats_warn = stats_pass.copy()
    stats_warn["runtime_minutes"] = 50.0

    result_warn = gates.evaluate(stats_warn)
    runtime_gate_warn = next(g for g in result_warn.gates if g.name == "Runtime Efficiency")
    assert runtime_gate_warn.status == GateStatus.WARN

    # Exceeds maximum
    stats_fail = stats_pass.copy()
    stats_fail["runtime_minutes"] = 65.0

    result_fail = gates.evaluate(stats_fail)
    runtime_gate_fail = next(g for g in result_fail.gates if g.name == "Runtime Efficiency")
    assert runtime_gate_fail.status == GateStatus.FAIL


def test_source_diversity():
    """Test minimum source diversity requirement"""
    gates = QualityGates(min_source_diversity=5)

    stats_pass = {
        "items_ingested": 10000,
        "unique_sources": 6,  # Above minimum
        "total_cost_usd": 10.0,
        "average_relevance_score": 0.65,
        "items_by_age": [],
        "field_completion_rates": [0.9],
        "runtime_minutes": 40.0,
    }

    result = gates.evaluate(stats_pass)
    diversity_gate = next(g for g in result.gates if g.name == "Source Diversity")
    assert diversity_gate.status == GateStatus.PASS

    # Below minimum
    stats_fail = stats_pass.copy()
    stats_fail["unique_sources"] = 3

    result_fail = gates.evaluate(stats_fail)
    diversity_gate_fail = next(g for g in result_fail.gates if g.name == "Source Diversity")
    assert diversity_gate_fail.status == GateStatus.FAIL
