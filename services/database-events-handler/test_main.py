"""
test_main.py — Tests for database-events-handler

Covers:
  - CDC event extraction from Pub/Sub envelopes
  - Routing logic (BigQuery, Healing, Payment, FinOps)
  - Rate limiter / circuit breaker
  - HTTP handler status codes
"""

from __future__ import annotations

import base64
import json
import time
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

import main


# ─── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
  """Clear the in-memory rate limiter between tests."""
  main._event_counts.clear()
  yield
  main._event_counts.clear()


def _make_pubsub_envelope(event: dict) -> dict:
  """Create a Pub/Sub push envelope wrapping a CDC event."""
  encoded = base64.b64encode(json.dumps(event).encode("utf-8")).decode("utf-8")
  return {"message": {"data": encoded}}


def _make_cdc_event(
  table: str = "users",
  change_type: str = "INSERT",
  keys: dict | None = None,
  new_values: dict | None = None,
) -> dict:
  """Create a standard CDC event."""
  return {
    "changeType": change_type,
    "tableName": table,
    "commitTimestamp": datetime.now(tz=UTC).isoformat(),
    "keys": keys or {"id": "test_001"},
    "newValues": new_values or {"name": "Test User"},
    "oldValues": {},
  }


# ─── Event Extraction ─────────────────────────────────────────────────────────


class TestExtractCDCEvent:
  """Tests for _extract_cdc_event."""

  def test_extracts_from_pubsub_envelope(self):
    event = _make_cdc_event(table="users")
    envelope = _make_pubsub_envelope(event)
    result = main._extract_cdc_event(envelope)
    assert result["tableName"] == "users"
    assert result["changeType"] == "INSERT"

  def test_returns_raw_event_if_no_message(self):
    raw = {"tableName": "sessions", "changeType": "UPDATE"}
    result = main._extract_cdc_event(raw)
    assert result["tableName"] == "sessions"

  def test_handles_empty_data(self):
    envelope = {"message": {"data": ""}}
    result = main._extract_cdc_event(envelope)
    assert result == {"message": {"data": ""}}

  def test_handles_missing_data_key(self):
    envelope = {"message": {}}
    result = main._extract_cdc_event(envelope)
    assert result == {"message": {}}


# ─── Rate Limiter ──────────────────────────────────────────────────────────────


class TestRateLimiter:
  """Tests for _check_rate_limit."""

  def test_allows_under_limit(self):
    assert main._check_rate_limit("users") is True

  def test_allows_up_to_max(self):
    for _ in range(main.MAX_EVENTS_PER_MINUTE):
      assert main._check_rate_limit("users") is True

  def test_blocks_over_limit(self):
    for _ in range(main.MAX_EVENTS_PER_MINUTE):
      main._check_rate_limit("users")
    assert main._check_rate_limit("users") is False

  def test_independent_per_table(self):
    for _ in range(main.MAX_EVENTS_PER_MINUTE):
      main._check_rate_limit("users")
    # Different table should still be under limit
    assert main._check_rate_limit("sessions") is True

  def test_window_expiry(self):
    """Events older than 60s should be pruned."""
    main._event_counts["users"] = [time.time() - 120]  # 2 minutes ago
    assert main._check_rate_limit("users") is True
    # Old entry pruned, only the new one remains
    assert len(main._event_counts["users"]) == 1


# ─── Routing Logic ─────────────────────────────────────────────────────────────


class TestRoutingLogic:
  """Tests for individual routing functions."""

  def test_bigquery_routing_inserts_row(self):
    bq_client = MagicMock()
    bq_client.insert_rows_json.return_value = []
    event = _make_cdc_event(table="users")
    main._route_to_bigquery(event, bq_client)
    bq_client.insert_rows_json.assert_called_once()

  def test_bigquery_routing_logs_errors(self):
    bq_client = MagicMock()
    bq_client.insert_rows_json.return_value = [{"error": "test"}]
    event = _make_cdc_event(table="users")
    main._route_to_bigquery(event, bq_client)
    # Should not raise, just log

  def test_healing_routes_schema_critical_tables(self):
    publisher = MagicMock()
    publisher.topic_path.return_value = "projects/test/topics/schema-healing-requests"
    future = MagicMock()
    future.result.return_value = "msg-id-123"
    publisher.publish.return_value = future

    event = _make_cdc_event(table="users")
    main._route_to_healing(event, publisher)
    publisher.publish.assert_called_once()

  def test_healing_skips_non_critical_tables(self):
    publisher = MagicMock()
    event = _make_cdc_event(table="audit_logs")
    main._route_to_healing(event, publisher)
    publisher.publish.assert_not_called()

  def test_payment_routes_transaction_tables(self):
    publisher = MagicMock()
    publisher.topic_path.return_value = "projects/test/topics/payment-reconciliation"
    future = MagicMock()
    future.result.return_value = "msg-id-456"
    publisher.publish.return_value = future

    event = _make_cdc_event(table="transactions", change_type="INSERT")
    main._route_payment_event(event, publisher)
    publisher.publish.assert_called_once()

  def test_payment_skips_deletes(self):
    publisher = MagicMock()
    event = _make_cdc_event(table="transactions", change_type="DELETE")
    main._route_payment_event(event, publisher)
    publisher.publish.assert_not_called()

  def test_payment_skips_non_payment_tables(self):
    publisher = MagicMock()
    event = _make_cdc_event(table="users", change_type="INSERT")
    main._route_payment_event(event, publisher)
    publisher.publish.assert_not_called()

  def test_finops_emits_check(self):
    publisher = MagicMock()
    publisher.topic_path.return_value = "projects/test/topics/finops-checks"
    future = MagicMock()
    future.result.return_value = "msg-id-789"
    publisher.publish.return_value = future

    event = _make_cdc_event(table="users")
    main._check_finops(event, publisher)
    publisher.publish.assert_called_once()


# ─── HTTP Handler ──────────────────────────────────────────────────────────────


class TestHTTPHandler:
  """Tests for the handle_cdc_event HTTP function."""

  @patch("main.pubsub_v1.PublisherClient")
  @patch("main.bigquery.Client")
  def test_returns_200_on_success(self, mock_bq_cls, mock_pub_cls):
    mock_bq = MagicMock()
    mock_bq.insert_rows_json.return_value = []
    mock_bq_cls.return_value = mock_bq

    mock_pub = MagicMock()
    future = MagicMock()
    future.result.return_value = "msg-id"
    mock_pub.publish.return_value = future
    mock_pub.topic_path.return_value = "projects/test/topics/test"
    mock_pub_cls.return_value = mock_pub

    request = MagicMock()
    event = _make_cdc_event(table="users")
    request.get_json.return_value = _make_pubsub_envelope(event)

    response, status = main.handle_cdc_event(request)
    assert status == 200
    body = json.loads(response)
    assert body["status"] == "processed"
    assert body["table"] == "users"

  def test_returns_400_on_empty_body(self):
    request = MagicMock()
    request.get_json.return_value = None
    response, status = main.handle_cdc_event(request)
    assert status == 400

  @patch("main.pubsub_v1.PublisherClient")
  @patch("main.bigquery.Client")
  def test_returns_429_on_rate_limit(self, mock_bq_cls, mock_pub_cls):
    # Exhaust the rate limit
    for _ in range(main.MAX_EVENTS_PER_MINUTE + 1):
      main._check_rate_limit("users")

    request = MagicMock()
    event = _make_cdc_event(table="users")
    request.get_json.return_value = _make_pubsub_envelope(event)

    response, status = main.handle_cdc_event(request)
    assert status == 429
    body = json.loads(response)
    assert body["status"] == "rate_limited"


# ─── Standalone Test Runner ───────────────────────────────────────────────────


class TestStandaloneMode:
  """Tests for the _run_test function."""

  def test_run_test_completes(self, capsys):
    main._run_test()
    captured = capsys.readouterr()
    assert "Test passed" in captured.out
    assert "BigQuery" in captured.out
