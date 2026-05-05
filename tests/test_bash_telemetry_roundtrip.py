# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Telemetry Roundtrip Integration Tests.

Verifies the contract between BashTelemetryTracker (classifier-side)
and EventCatalog (telemetry-side) for bash security events.

Tests validate:
1. BashTelemetryTracker emits correct event types and data shapes.
2. EventCatalog factory methods produce TelemetryEvent with matching fields.
3. Field-level contract alignment between the two systems.
4. Round-trip: tracker writes → reader parses → catalog validates.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from packages.agnt_bash_classifier.classifier import BashSecurityClassifier
from packages.agnt_bash_classifier.security_checks import BashSecurityCheckId
from packages.agnt_bash_classifier.telemetry import BashTelemetryTracker
from packages.telemetry.catalog import EventCatalog


class TestTelemetryRoundtrip:
    """Verify EventCatalog ↔ BashTelemetryTracker contract alignment."""

    def test_block_event_field_contract(self, tmp_path: Path) -> None:
        """Tracker's check_failed event fields must match EventCatalog's factory."""
        log = str(tmp_path / "roundtrip.jsonl")
        tracker = BashTelemetryTracker(log_path=log)
        clf = BashSecurityClassifier(telemetry=tracker)

        # Trigger a known block
        result = clf.classify("echo `whoami`")
        assert not result.allowed

        # Read back the tracker's output
        with open(log) as f:
            events = [json.loads(line) for line in f if line.strip()]
        assert len(events) == 1
        tracker_event = events[0]

        # Verify tracker event type
        assert tracker_event["event_type"] == "tengu_bash_security_check_failed"

        # Verify tracker data shape
        data = tracker_event["data"]
        assert "check_id" in data
        assert "check_name" in data
        assert "command" in data
        assert "message" in data

        # Build equivalent EventCatalog event
        command_hash = hashlib.sha256("echo `whoami`"[:200].encode()).hexdigest()[:16]
        catalog_event = EventCatalog.bash_security_check_failed(
            check_id=data["check_id"],
            check_name=data["check_name"],
            command_hash=command_hash,
            message=data["message"],
        )

        # Verify catalog event matches
        assert catalog_event.event == "agnt_bash_security_check_failed"
        assert catalog_event.success is False
        assert catalog_event.error_message == data["message"]
        assert catalog_event.properties["check_id"] == data["check_id"]
        assert catalog_event.properties["check_name"] == data["check_name"]

    def test_pass_event_field_contract(self, tmp_path: Path) -> None:
        """Tracker's validated event fields must match EventCatalog's factory."""
        log = str(tmp_path / "roundtrip.jsonl")
        tracker = BashTelemetryTracker(log_path=log)
        clf = BashSecurityClassifier(telemetry=tracker)

        # Trigger a pass
        result = clf.classify("ls -la")
        assert result.allowed

        with open(log) as f:
            events = [json.loads(line) for line in f if line.strip()]
        assert len(events) == 1
        tracker_event = events[0]

        # Verify tracker event type
        assert tracker_event["event_type"] == "tengu_bash_security_validated"

        data = tracker_event["data"]
        assert data["checks_passed"] == 23
        assert data["duration_ms"] >= 0.0

        # Build equivalent EventCatalog event
        command_hash = hashlib.sha256("ls -la"[:200].encode()).hexdigest()[:16]
        catalog_event = EventCatalog.bash_security_validated(
            command_hash=command_hash,
            checks_passed=data["checks_passed"],
            duration_ms=data["duration_ms"],
        )

        assert catalog_event.event == "agnt_bash_security_validated"
        assert catalog_event.properties["checks_passed"] == 23
        assert catalog_event.duration_ms == data["duration_ms"]

    def test_event_type_mapping(self) -> None:
        """Tracker event names must map to EventCatalog event names."""
        # This documents the naming contract
        mapping = {
            "tengu_bash_security_check_failed": "agnt_bash_security_check_failed",
            "tengu_bash_security_validated": "agnt_bash_security_validated",
        }
        for tracker_name, catalog_name in mapping.items():
            # Verify catalog factory exists
            if tracker_name == "tengu_bash_security_check_failed":
                ev = EventCatalog.bash_security_check_failed()
                assert ev.event == catalog_name
            elif tracker_name == "tengu_bash_security_validated":
                ev = EventCatalog.bash_security_validated()
                assert ev.event == catalog_name

    def test_tracker_creates_log_directory(self, tmp_path: Path) -> None:
        """Tracker must create intermediate directories for the log file."""
        deep_path = str(tmp_path / "a" / "b" / "c" / "test.jsonl")
        tracker = BashTelemetryTracker(log_path=deep_path)
        clf = BashSecurityClassifier(telemetry=tracker)
        clf.classify("pwd")
        assert os.path.exists(deep_path)

    def test_multiple_events_append_correctly(self, tmp_path: Path) -> None:
        """Multiple classify calls must append events, not overwrite."""
        log = str(tmp_path / "multi.jsonl")
        tracker = BashTelemetryTracker(log_path=log)
        clf = BashSecurityClassifier(telemetry=tracker)

        clf.classify("ls -la")            # pass
        clf.classify("echo `whoami`")      # block
        clf.classify("pwd")               # pass
        clf.classify("echo $(id)")         # block

        with open(log) as f:
            events = [json.loads(line) for line in f if line.strip()]
        assert len(events) == 4

        # Verify event type sequence
        types = [e["event_type"] for e in events]
        assert types == [
            "tengu_bash_security_validated",
            "tengu_bash_security_check_failed",
            "tengu_bash_security_validated",
            "tengu_bash_security_check_failed",
        ]

    def test_check_id_enum_roundtrip(self, tmp_path: Path) -> None:
        """Check ID must survive serialization/deserialization roundtrip."""
        log = str(tmp_path / "enum.jsonl")
        tracker = BashTelemetryTracker(log_path=log)
        clf = BashSecurityClassifier(telemetry=tracker)

        # Trigger backtick block (check 5: SHELL_METACHARACTERS)
        clf.classify("echo `id`")

        with open(log) as f:
            events = [json.loads(line) for line in f if line.strip()]
        data = events[0]["data"]

        # Verify int conversion roundtrip
        check_id_int = data["check_id"]
        recovered = BashSecurityCheckId(check_id_int)
        assert recovered == BashSecurityCheckId.SHELL_METACHARACTERS
        assert recovered.name == data["check_name"]

    def test_command_truncation_200_chars(self, tmp_path: Path) -> None:
        """Commands longer than 200 chars must be truncated in telemetry."""
        log = str(tmp_path / "truncate.jsonl")
        tracker = BashTelemetryTracker(log_path=log)
        clf = BashSecurityClassifier(telemetry=tracker)

        long_cmd = "echo " + "a" * 300
        clf.classify(long_cmd)

        with open(log) as f:
            events = [json.loads(line) for line in f if line.strip()]
        # The classifier truncates to command[:200] before passing to tracker
        assert len(events[0]["data"]["command"]) <= 200

    def test_timestamp_present_and_numeric(self, tmp_path: Path) -> None:
        """Every tracker event must have a numeric timestamp."""
        log = str(tmp_path / "ts.jsonl")
        tracker = BashTelemetryTracker(log_path=log)
        clf = BashSecurityClassifier(telemetry=tracker)

        clf.classify("date")

        with open(log) as f:
            events = [json.loads(line) for line in f if line.strip()]
        assert isinstance(events[0]["timestamp"], float)
        assert events[0]["timestamp"] > 0
