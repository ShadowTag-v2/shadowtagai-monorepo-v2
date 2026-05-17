# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for packages/cor_google — AG-UI, GCP Substrate, A2A Mesh, Darwinian Gate."""


import pytest

from packages.cor_google.ag_ui import (
    AGUIEvent,
    AGUIEventBus,
    AGUIEventPayload,
    get_event_bus,
)
from packages.cor_google.a2a_mesh import (
    A2AMesh,
    AgentCapability,
    AgentCard,
    TaskStatus,
)
from packages.cor_google.gcp_substrate import GCPSubstrate, SubstrateConfig
from packages.cor_google.darwinian_gate import DarwinianGate, MutationCandidate


# ─── AG-UI Event Protocol ───────────────────────────────────────────


class TestAGUIEventPayload:
    def test_payload_creation(self):
        payload = AGUIEventPayload(
            event_type=AGUIEvent.MEMORY_GATE_LOCKED,
            source_agent="test_agent",
            data={"key": "value"},
        )
        assert payload.event_type == AGUIEvent.MEMORY_GATE_LOCKED
        assert payload.source_agent == "test_agent"
        assert payload.data == {"key": "value"}
        assert payload.event_id  # UUID generated
        assert payload.timestamp_ns > 0

    def test_payload_immutable(self):
        payload = AGUIEventPayload(event_type=AGUIEvent.TRIAD_MUTATION_SPIN)
        with pytest.raises(AttributeError):
            payload.source_agent = "mutated"  # type: ignore[misc]

    def test_to_dict(self):
        payload = AGUIEventPayload(
            event_type=AGUIEvent.JUDGE6_AUDIT_PASS,
            source_agent="judge_6",
            data={"verdict": True},
        )
        d = payload.to_dict()
        assert d["event_type"] == "ag_ui_judge6_audit_pass"
        assert d["source_agent"] == "judge_6"
        assert d["data"]["verdict"] is True


class TestAGUIEventBus:
    def test_subscribe_and_emit(self):
        bus = AGUIEventBus()
        received = []

        def handler(payload: AGUIEventPayload):
            received.append(payload)

        bus.subscribe(AGUIEvent.MEMORY_GATE_LOCKED, handler)
        bus.emit(AGUIEventPayload(event_type=AGUIEvent.MEMORY_GATE_LOCKED))

        assert len(received) == 1
        assert received[0].event_type == AGUIEvent.MEMORY_GATE_LOCKED

    def test_emit_no_subscribers(self):
        bus = AGUIEventBus()
        # Should not raise
        bus.emit(AGUIEventPayload(event_type=AGUIEvent.EPISTEMIC_SYNC))
        assert bus.ledger_size == 1

    def test_ledger_bounded(self):
        bus = AGUIEventBus()
        bus._max_ledger_size = 10
        for _ in range(15):
            bus.emit(AGUIEventPayload(event_type=AGUIEvent.SUBSTRATE_WRITE))
        # After eviction: 15 - 2 (20% of 10) = 13? No — evicts after reaching 10
        # At 10: evicts 2, then appends → 9. Continues...
        assert bus.ledger_size <= 12

    def test_emit_memory_gate(self):
        bus = AGUIEventBus()
        payload = bus.emit_memory_gate({"rule": "no_secrets"})
        assert payload.event_type == AGUIEvent.MEMORY_GATE_LOCKED
        assert payload.data["invariants"]["rule"] == "no_secrets"

    def test_emit_triad_spin(self):
        bus = AGUIEventBus()
        payload = bus.emit_triad_spin("mut_001", 0.80, 0.92)
        assert payload.data["mutation_id"] == "mut_001"
        assert payload.data["delta"] == pytest.approx(0.12)

    def test_emit_judge6_pass(self):
        bus = AGUIEventBus()
        payload = bus.emit_judge6_verdict(True, 0.95, "mut_001")
        assert payload.event_type == AGUIEvent.JUDGE6_AUDIT_PASS

    def test_emit_judge6_fail(self):
        bus = AGUIEventBus()
        payload = bus.emit_judge6_verdict(False, 0.30, "mut_002")
        assert payload.event_type == AGUIEvent.JUDGE6_AUDIT_FAIL

    def test_emit_speed_delta(self):
        bus = AGUIEventBus()
        payload = bus.emit_speed_delta("runner.py", 100.0, 85.0)
        assert payload.data["improvement_pct"] == pytest.approx(15.0)

    def test_get_ledger(self):
        bus = AGUIEventBus()
        bus.emit(AGUIEventPayload(event_type=AGUIEvent.SUBSTRATE_READ))
        bus.emit(AGUIEventPayload(event_type=AGUIEvent.SUBSTRATE_WRITE))
        ledger = bus.get_ledger(last_n=1)
        assert len(ledger) == 1
        assert ledger[0]["event_type"] == "ag_ui_substrate_write"

    def test_handler_exception_non_blocking(self):
        bus = AGUIEventBus()

        def bad_handler(_):
            raise RuntimeError("boom")

        bus.subscribe(AGUIEvent.EPISTEMIC_SYNC, bad_handler)
        # Should not raise
        bus.emit(AGUIEventPayload(event_type=AGUIEvent.EPISTEMIC_SYNC))
        assert bus.ledger_size == 1

    def test_get_event_bus_singleton(self):
        import packages.cor_google.ag_ui as mod
        mod._global_bus = None  # Reset
        bus1 = get_event_bus()
        bus2 = get_event_bus()
        assert bus1 is bus2
        mod._global_bus = None  # Cleanup


# ─── GCP Substrate ───────────────────────────────────────────────────


class TestGCPSubstrate:
    def test_dry_run_write(self):
        config = SubstrateConfig(dry_run=True)
        substrate = GCPSubstrate(config)
        result = substrate.write_event({"event_id": "test_001", "data": {}})
        assert result is True
        assert substrate.stats["write_count"] == 1

    def test_dry_run_config(self):
        config = SubstrateConfig(project_id="test-project", dry_run=True)
        assert config.project_id == "test-project"
        assert config.firestore_collection == "ag_ui_events"
        assert config.bigquery_dataset == "shadowtag_telemetry"

    def test_stats(self):
        config = SubstrateConfig(dry_run=True)
        substrate = GCPSubstrate(config)
        stats = substrate.stats
        assert stats["dry_run"] is True
        assert stats["write_count"] == 0
        assert stats["error_count"] == 0


# ─── A2A Mesh ────────────────────────────────────────────────────────


class TestA2AMesh:
    def test_register_agent(self):
        mesh = A2AMesh()
        card = AgentCard(
            agent_id="vulture_1",
            display_name="Vulture Agent 1",
            capabilities=[AgentCapability.CODE_MUTATION, AgentCapability.LINT_FIX],
        )
        mesh.register_agent(card)
        assert mesh.agent_count == 1

    def test_find_agents_by_capability(self):
        mesh = A2AMesh()
        card = AgentCard(
            agent_id="sec_agent",
            display_name="Security Agent",
            capabilities=[AgentCapability.SECURITY_AUDIT],
        )
        mesh.register_agent(card)
        found = mesh.find_agents(AgentCapability.SECURITY_AUDIT)
        assert len(found) == 1
        assert found[0].agent_id == "sec_agent"

    def test_find_agents_no_match(self):
        mesh = A2AMesh()
        found = mesh.find_agents(AgentCapability.DEPLOYMENT)
        assert len(found) == 0

    def test_dispatch_task(self):
        mesh = A2AMesh()
        mesh.register_agent(AgentCard(
            agent_id="lint_bot",
            display_name="Lint Bot",
            capabilities=[AgentCapability.LINT_FIX],
        ))
        task = mesh.dispatch_task("orchestrator", AgentCapability.LINT_FIX, {"file": "main.py"})
        assert task.status == TaskStatus.PENDING
        assert task.target_agent == "lint_bot"

    def test_dispatch_no_agent(self):
        mesh = A2AMesh()
        task = mesh.dispatch_task("orchestrator", AgentCapability.DEPLOYMENT, {})
        assert task.status == TaskStatus.FAILED
        assert "No agent found" in task.result.get("error", "")

    def test_complete_task(self):
        mesh = A2AMesh()
        mesh.register_agent(AgentCard(
            agent_id="bot",
            display_name="Bot",
            capabilities=[AgentCapability.CODE_MUTATION],
        ))
        task = mesh.dispatch_task("orch", AgentCapability.CODE_MUTATION, {})
        completed = mesh.complete_task(task.task_id, {"lines_changed": 42})
        assert completed is not None
        assert completed.status == TaskStatus.COMPLETED
        assert completed.result["lines_changed"] == 42

    def test_complete_unknown_task(self):
        mesh = A2AMesh()
        result = mesh.complete_task("nonexistent", {})
        assert result is None

    def test_list_agents(self):
        mesh = A2AMesh()
        mesh.register_agent(AgentCard("a1", "Agent 1", [AgentCapability.LINT_FIX]))
        mesh.register_agent(AgentCard("a2", "Agent 2", [AgentCapability.DEPLOYMENT]))
        agents = mesh.list_agents()
        assert len(agents) == 2

    def test_list_tasks_filter(self):
        mesh = A2AMesh()
        mesh.register_agent(AgentCard("bot", "Bot", [AgentCapability.LINT_FIX]))
        t1 = mesh.dispatch_task("orch", AgentCapability.LINT_FIX, {})
        mesh.complete_task(t1.task_id, {})
        mesh.dispatch_task("orch", AgentCapability.LINT_FIX, {})

        completed = mesh.list_tasks(status=TaskStatus.COMPLETED)
        pending = mesh.list_tasks(status=TaskStatus.PENDING)
        assert len(completed) == 1
        assert len(pending) == 1

    def test_agent_card_to_dict(self):
        card = AgentCard("id1", "Test", [AgentCapability.BROWSER_AUTOMATION])
        d = card.to_dict()
        assert d["agent_id"] == "id1"
        assert "browser_automation" in d["capabilities"]


# ─── Darwinian Gate ──────────────────────────────────────────────────


class TestDarwinianGate:
    def test_mutation_accepted(self):
        bus = AGUIEventBus()
        gate = DarwinianGate(bus, fitness_threshold=0.05)
        candidate = MutationCandidate(
            mutation_id="mut_001",
            source_file="main.py",
            description="Optimize loop",
            fitness_before=0.80,
            fitness_after=0.90,
        )
        result = gate.propose_mutation(candidate)
        assert result is True
        assert gate.accepted_count == 1

    def test_mutation_rejected_below_threshold(self):
        bus = AGUIEventBus()
        gate = DarwinianGate(bus, fitness_threshold=0.05)
        candidate = MutationCandidate(
            mutation_id="mut_002",
            source_file="utils.py",
            description="Minor tweak",
            fitness_before=0.80,
            fitness_after=0.82,
        )
        result = gate.propose_mutation(candidate)
        assert result is False
        assert gate.rejected_count == 1

    def test_mutation_rejected_regression(self):
        bus = AGUIEventBus()
        gate = DarwinianGate(bus, fitness_threshold=0.05)
        candidate = MutationCandidate(
            mutation_id="mut_003",
            source_file="core.py",
            description="Bad change",
            fitness_before=0.90,
            fitness_after=0.85,
        )
        result = gate.propose_mutation(candidate)
        assert result is False

    def test_gate_stats(self):
        bus = AGUIEventBus()
        gate = DarwinianGate(bus, fitness_threshold=0.05)
        gate.propose_mutation(MutationCandidate("m1", "a.py", "ok", 0.5, 0.9))
        gate.propose_mutation(MutationCandidate("m2", "b.py", "bad", 0.9, 0.5))
        stats = gate.stats
        assert stats["total_mutations"] == 2
        assert stats["accepted"] == 1
        assert stats["rejected"] == 1
        assert stats["acceptance_rate"] == pytest.approx(0.5)

    def test_events_emitted(self):
        bus = AGUIEventBus()
        events_received = []
        bus.subscribe(AGUIEvent.DARWINIAN_GATE_OPEN, lambda p: events_received.append(p))
        bus.subscribe(AGUIEvent.DARWINIAN_GATE_CLOSED, lambda p: events_received.append(p))

        gate = DarwinianGate(bus, fitness_threshold=0.05)
        gate.propose_mutation(MutationCandidate("m1", "a.py", "good", 0.5, 0.9))
        gate.propose_mutation(MutationCandidate("m2", "b.py", "bad", 0.9, 0.5))

        assert len(events_received) == 2
        assert events_received[0].event_type == AGUIEvent.DARWINIAN_GATE_OPEN
        assert events_received[1].event_type == AGUIEvent.DARWINIAN_GATE_CLOSED

    def test_mutation_candidate_properties(self):
        m = MutationCandidate("m1", "f.py", "test", 0.5, 0.8)
        assert m.fitness_delta == pytest.approx(0.3)
        assert m.is_improvement is True

        m2 = MutationCandidate("m2", "f.py", "test", 0.8, 0.7)
        assert m2.is_improvement is False

    def test_benchmark_speed_delta_emitted(self):
        bus = AGUIEventBus()
        speed_events = []
        bus.subscribe(AGUIEvent.SPEED_DELTA_COMPUTED, lambda p: speed_events.append(p))

        gate = DarwinianGate(bus, fitness_threshold=0.01)
        gate.propose_mutation(MutationCandidate(
            "m1", "a.py", "perf", 0.5, 0.6, benchmark_ms=100.0
        ))

        assert len(speed_events) == 1
        assert speed_events[0].data["before_ms"] == 100.0
