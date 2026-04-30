import sys
from unittest.mock import MagicMock, patch

# Mock google.cloud.bigquery BEFORE importing tower_edge to avoid pyarrow dependency issues in test env
mock_bq_module = MagicMock()
sys.modules["google.cloud"] = MagicMock()
sys.modules["google.cloud.bigquery"] = mock_bq_module


import pytest  # noqa: E402

from src.pnkln.verticals.tower_edge import ConnectionType, Telemetry, TowerNode  # noqa: E402


@pytest.fixture
def mock_bq():
    return mock_bq_module.Client.return_value


@pytest.fixture
def node(mock_bq):
    return TowerNode(node_id="TEST-NODE-01", location_code="US-TEST-001", hardware_spec="MOCK-HW")


def test_initialization(node):
    assert node.node_id == "TEST-NODE-01"
    assert node.current_connection == ConnectionType.FIBER
    # node._bq_client should be the mock return value
    assert node._bq_client is not None


def test_heartbeat_normal(node):
    # Mock sensors to return normal values
    with patch.object(node, "_read_hardware_sensors") as mock_sensors:
        mock_sensors.return_value = Telemetry(
            latency_ms=20.0,
            jitter_ms=2.0,
            gpu_temp_c=40.0,
            power_draw_w=500.0,
            active_inferences=1,
        )

        t = node.heartbeat()

        assert t.latency_ms == 20.0
        # Should verify BQ insert called
        node._bq_client.insert_rows_json.assert_called_once()


def test_failover_trigger(node):
    # Mock high latency
    with patch.object(node, "_read_hardware_sensors") as mock_sensors:
        mock_sensors.return_value = Telemetry(
            latency_ms=150.0,  # > 100ms trigger
            jitter_ms=5.0,
            gpu_temp_c=40.0,
            power_draw_w=500.0,
            active_inferences=1,
        )

        # Fiber connection
        node.current_connection = ConnectionType.FIBER

        node.heartbeat()

        # access log to verify? Or check state change if mock jitter was good
        # In code, _evaluate_failover uses a hardcoded mock jitter=20.0 < 25.0
        # So it SHOULD switch to STARLINK
        assert node.current_connection == ConnectionType.STARLINK


def test_revenue_calculation(node):
    # 1 GB data mock
    data = b"x" * (1024 * 1024 * 1024)

    # Mock Orchestrator to avoid real execution/import issues
    node._brain.execute = MagicMock(return_value="mock_result")

    # Default RateCard: $0.05/GB offload + $0.002/inference
    # Cost should be 0.05 + 0.002 = 0.052

    node.process_workload("job-123", data)

    # Verify Ledger watermark called with revenue
    # _ledger is real instance, so we check formatted state
    assert len(node._ledger.watermarks) > 0
    last_wm = node._ledger.watermarks[-1]
    metadata = last_wm.metadata

    assert metadata["revenue_usd"] == pytest.approx(0.052)
    assert metadata["event_type"] == "EDGE_INFERENCE"
