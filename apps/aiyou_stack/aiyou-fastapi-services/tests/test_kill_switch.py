"""Tests for KillSwitch"""

import pytest

from pnkln_file_search.monitoring.kill_switch import KillSwitch, KillSwitchState
from pnkln_file_search.monitoring.metrics import MetricsCollector


@pytest.fixture
def metrics_collector():
    """Create metrics collector"""
    return MetricsCollector(window_size=100)


def test_kill_switch_initialization(metrics_collector):
    """Test kill switch initialization"""
    kill_switch = KillSwitch(metrics_collector)

    assert kill_switch.state == KillSwitchState.ACTIVE
    assert kill_switch.violation_count == 0


def test_kill_switch_healthy_check(metrics_collector):
    """Test health check with no violations"""
    kill_switch = KillSwitch(metrics_collector)

    # Add some healthy metrics
    for _ in range(10):
        metrics_collector.record_file_search_latency(200)  # 200ms < threshold

    health = kill_switch.check_health()

    assert health["healthy"] is True
    assert len(health["violations"]) == 0
    assert health["state"] == KillSwitchState.ACTIVE.value


def test_kill_switch_latency_violation(metrics_collector):
    """Test health check with latency violations"""
    kill_switch = KillSwitch(metrics_collector)

    # Add metrics that exceed threshold
    for _ in range(100):
        metrics_collector.record_file_search_latency(1500)  # 1500ms > 1000ms threshold

    health = kill_switch.check_health()

    assert health["healthy"] is False
    assert len(health["violations"]) > 0
    assert health["violations"][0]["type"] == "latency"


def test_kill_switch_degradation(metrics_collector):
    """Test kill switch degradation"""
    kill_switch = KillSwitch(metrics_collector)

    # Trigger one violation
    for _ in range(100):
        metrics_collector.record_file_search_latency(1500)

    kill_switch.check_health()

    assert kill_switch.state == KillSwitchState.DEGRADED


def test_kill_switch_disable(metrics_collector):
    """Test kill switch disable after multiple violations"""
    kill_switch = KillSwitch(metrics_collector)

    # Add metrics that exceed threshold
    for _ in range(100):
        metrics_collector.record_file_search_latency(1500)

    # Trigger multiple violations
    for _ in range(3):
        kill_switch.check_health()

    assert kill_switch.state == KillSwitchState.DISABLED
    assert not kill_switch.is_enabled()


def test_kill_switch_recovery(metrics_collector):
    """Test kill switch recovery"""
    kill_switch = KillSwitch(metrics_collector)

    # Trigger degradation
    for _ in range(100):
        metrics_collector.record_file_search_latency(1500)
    kill_switch.check_health()

    assert kill_switch.state == KillSwitchState.DEGRADED

    # Add healthy metrics
    metrics_collector.file_search_latencies.clear()
    for _ in range(100):
        metrics_collector.record_file_search_latency(200)

    kill_switch.check_health()

    assert kill_switch.state == KillSwitchState.ACTIVE
    assert kill_switch.violation_count == 0


def test_kill_switch_force_disable(metrics_collector):
    """Test manual force disable"""
    kill_switch = KillSwitch(metrics_collector)

    kill_switch.force_disable()

    assert kill_switch.state == KillSwitchState.DISABLED
    assert not kill_switch.is_enabled()


def test_kill_switch_force_enable(metrics_collector):
    """Test manual force enable"""
    kill_switch = KillSwitch(metrics_collector)

    kill_switch.force_disable()
    assert kill_switch.state == KillSwitchState.DISABLED

    kill_switch.force_enable()
    assert kill_switch.state == KillSwitchState.ACTIVE
    assert kill_switch.is_enabled()
