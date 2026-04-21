# Copyright 2026 ShadowTag AI. All rights reserved.
"""
Tests for core.ki_engine — all modules.

Covers:
  - Schema: KIMetadata creation, serialization, backward compatibility
  - Decay: Temporal decay curves, recall scoring
  - Activation: Spreading activation, collision detection
  - Budget: Token-budgeted recall, type reservations
  - Closure: Operational closure metrics
  - Events: Event sourcing, append/read/compact
  - Promotion: Belief promotion pipeline
  - FTS: SQLite FTS5 index
  - Migration: Legacy metadata upgrade
"""

import json
import math
import sqlite3
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from core.ki_engine.schema import (
    KIClassification,
    KIMetadata,
    KIRelation,
    KIStatus,
    KIType,
    RelationType,
    generate_ki_id,
)
from core.ki_engine.decay import (
    RankedKI,
    rank_kis,
    recall_score,
    temporal_decay,
)
from core.ki_engine.activation import (
    ActivationResult,
    Collision,
    detect_collisions,
    spread_activation,
)
from core.ki_engine.budget import (
    BudgetResult,
    estimate_tokens,
    token_budget_recall,
)
from core.ki_engine.closure import ClosureResult, compute_closure
from core.ki_engine.events import (
    EventAction,
    KIEvent,
    append_event,
    compact_log,
    count_events,
    read_events,
)
from core.ki_engine.promotion import (
    ConflictResult,
    PromotionResult,
    detect_conflicts,
    promote_beliefs,
)
from core.ki_engine.views import (
    render_constraints,
    render_conflicts,
    render_decisions,
    render_handoff,
    render_index,
)
from core.ki_engine.migration import (
    infer_ki_type,
    migrate_ki_metadata,
)


# ── Fixtures ──────────────────────────────────────────────────────────


def _make_ki(
    name: str = "test-ki",
    ki_type: KIType = KIType.FACT,
    confidence: float = 1.0,
    tags: list[str] | None = None,
    status: KIStatus = KIStatus.ACTIVE,
    age_days: float = 0.0,
    relations: list[KIRelation] | None = None,
) -> KIMetadata:
    """Create a test KI with optional age override."""
    now = datetime.now(UTC)
    updated = (now - timedelta(days=age_days)).isoformat()
    return KIMetadata(
        name=name,
        summary=f"Test summary for {name}",
        created=updated,
        updated=updated,
        tags=tags or [],
        ki_type=ki_type,
        status=status,
        confidence=confidence,
        relations=relations or [],
    )


@pytest.fixture
def tmp_ki_dir(tmp_path: Path) -> Path:
    """Create a temporary KI directory with sample KIs."""
    ki_dir = tmp_path / "knowledge"
    ki_dir.mkdir()

    # Create sample KIs
    for name, ki_type in [
        ("firestore-verdict", KIType.DECISION),
        ("gcp-only-rule", KIType.CONSTRAINT),
        ("supabase-rejected", KIType.BELIEF),
        ("veo-api-reference", KIType.FACT),
    ]:
        ki_path = ki_dir / name
        ki_path.mkdir()
        artifacts = ki_path / "artifacts"
        artifacts.mkdir()

        metadata = KIMetadata(
            name=name,
            summary=f"Summary for {name}",
            tags=["gcp", "architecture"],
            ki_type=ki_type,
            confidence=0.95 if ki_type == KIType.BELIEF else 1.0,
        )
        metadata.save(ki_path / "metadata.json")

        # Create artifact
        (artifacts / "reference.md").write_text(f"# {name}\nContent for {name}\n")

    return ki_dir


# ── Schema Tests ──────────────────────────────────────────────────────


class TestKISchema:
    def test_create_metadata(self):
        ki = _make_ki(name="test", ki_type=KIType.DECISION)
        assert ki.name == "test"
        assert ki.ki_type == KIType.DECISION
        assert ki.status == KIStatus.ACTIVE
        assert ki.confidence == 1.0

    def test_serialization_roundtrip(self):
        ki = _make_ki(
            name="roundtrip",
            ki_type=KIType.CONSTRAINT,
            confidence=0.8,
            tags=["test", "roundtrip"],
        )
        d = ki.to_dict()
        loaded = KIMetadata.from_dict(d)
        assert loaded.name == ki.name
        assert loaded.ki_type == ki.ki_type
        assert loaded.confidence == ki.confidence
        assert loaded.tags == ki.tags

    def test_backward_compatible_load(self):
        """Existing metadata without new fields should load with defaults."""
        legacy = {
            "name": "legacy-ki",
            "summary": "Old format",
            "created": "2026-01-01T00:00:00Z",
            "updated": "2026-01-01T00:00:00Z",
            "references": [],
            "tags": ["old"],
        }
        ki = KIMetadata.from_dict(legacy)
        assert ki.name == "legacy-ki"
        assert ki.ki_type == KIType.FACT  # Default
        assert ki.status == KIStatus.ACTIVE  # Default
        assert ki.confidence == 1.0  # Default
        assert ki.classification == KIClassification.TEAM  # Default

    def test_save_load_file(self, tmp_path: Path):
        ki = _make_ki(name="file-test", tags=["file"])
        path = tmp_path / "metadata.json"
        ki.save(path)
        loaded = KIMetadata.load(path)
        assert loaded.name == "file-test"
        assert loaded.tags == ["file"]

    def test_expired_check(self):
        ki = _make_ki(ki_type=KIType.BELIEF, age_days=60)
        ki.ttl_days = 30
        assert ki.is_expired is True

    def test_not_expired(self):
        ki = _make_ki(ki_type=KIType.FACT, age_days=5)
        ki.ttl_days = None
        assert ki.is_expired is False

    def test_generate_ki_id(self):
        ki_id = generate_ki_id(KIType.DECISION, "Firestore Verdict")
        assert ki_id.startswith("DECI-")
        assert len(ki_id) > 20

    def test_relations(self):
        rel = KIRelation(target_ki="other-ki", relation_type=RelationType.SUPPORTS)
        ki = _make_ki(relations=[rel])
        d = ki.to_dict()
        assert len(d["relations"]) == 1
        assert d["relations"][0]["target_ki"] == "other-ki"


# ── Decay Tests ───────────────────────────────────────────────────────


class TestDecay:
    def test_zero_age_returns_one(self):
        assert temporal_decay(0) == 1.0

    def test_half_life_returns_half(self):
        assert abs(temporal_decay(30, half_life_days=30) - 0.5) < 0.01

    def test_double_half_life(self):
        assert abs(temporal_decay(60, half_life_days=30) - 0.25) < 0.01

    def test_negative_age(self):
        assert temporal_decay(-5) == 1.0

    def test_recall_score_computation(self):
        ki = _make_ki(ki_type=KIType.DECISION, confidence=1.0, age_days=0)
        score = recall_score(ki)
        assert score > 0

    def test_ranking_order(self):
        fresh = _make_ki(name="fresh", ki_type=KIType.DECISION, age_days=0)
        old = _make_ki(name="old", ki_type=KIType.DECISION, age_days=365)
        ranked = rank_kis([old, fresh])
        assert ranked[0].ki.name == "fresh"


# ── Activation Tests ──────────────────────────────────────────────────


class TestActivation:
    def test_basic_activation(self):
        ki1 = _make_ki(name="ki1", tags=["gcp"])
        ki2 = _make_ki(name="ki2", tags=["gcp"])
        result = spread_activation([ki1, ki2], seed_tags={"gcp"})
        assert isinstance(result, ActivationResult)
        assert len(result.activated) >= 2

    def test_collision_detection(self):
        ki1 = _make_ki(name="ki1", tags=["gcp", "cloud", "infra"])
        ki2 = _make_ki(name="ki2", tags=["legal", "privacy", "gdpr"])
        # Both should activate if seeded, and have high dissimilarity
        from core.ki_engine.activation import ActivatedKI

        activated = [
            ActivatedKI(ki=ki1, activation=2.0, base_level=0.5, spread_component=1.5),
            ActivatedKI(ki=ki2, activation=1.8, base_level=0.5, spread_component=1.3),
        ]
        collisions = detect_collisions(activated, dissimilarity_threshold=0.7)
        assert len(collisions) >= 1
        assert collisions[0].dissimilarity >= 0.7

    def test_no_collisions_same_tags(self):
        ki1 = _make_ki(name="ki1", tags=["gcp"])
        ki2 = _make_ki(name="ki2", tags=["gcp"])
        from core.ki_engine.activation import ActivatedKI

        activated = [
            ActivatedKI(ki=ki1, activation=2.0, base_level=0.5, spread_component=1.5),
            ActivatedKI(ki=ki2, activation=1.8, base_level=0.5, spread_component=1.3),
        ]
        collisions = detect_collisions(activated, dissimilarity_threshold=0.7)
        assert len(collisions) == 0


# ── Budget Tests ──────────────────────────────────────────────────────


class TestBudget:
    def test_budget_respects_limit(self):
        kis = [_make_ki(name=f"ki-{i}", tags=["test"]) for i in range(50)]
        result = token_budget_recall(kis, max_tokens=500)
        assert result.total_tokens <= 500

    def test_type_reservation(self):
        kis = [
            _make_ki(name="decision-1", ki_type=KIType.DECISION),
            _make_ki(name="fact-1", ki_type=KIType.FACT),
            _make_ki(name="belief-1", ki_type=KIType.BELIEF, confidence=0.5),
        ]
        result = token_budget_recall(kis, max_tokens=10000)
        names = [r.ki.name for r in result.reserved]
        assert "decision-1" in names  # Decisions get reserved slots

    def test_excludes_expired(self):
        expired = _make_ki(name="expired", ki_type=KIType.BELIEF, age_days=60)
        expired.ttl_days = 30
        active = _make_ki(name="active", ki_type=KIType.FACT)
        result = token_budget_recall([expired, active], max_tokens=10000)
        names = [r.ki.name for r in result.selected]
        assert "expired" not in names
        assert "active" in names


# ── Closure Tests ─────────────────────────────────────────────────────


class TestClosure:
    def test_empty_store(self):
        result = compute_closure([])
        assert result.ki_count == 0
        assert result.phase == "early"
        assert result.closure_index == 0.0

    def test_early_phase(self):
        kis = [_make_ki(name=f"ki-{i}") for i in range(5)]
        result = compute_closure(kis)
        assert result.phase == "early"

    def test_type_composition(self):
        kis = [_make_ki(name=f"fact-{i}", ki_type=KIType.FACT) for i in range(30)]
        result = compute_closure(kis)
        assert result.phase == "type-composition"

    def test_predictions_generated(self):
        kis = [_make_ki(name=f"ki-{i}") for i in range(25)]
        result = compute_closure(kis)
        assert len(result.predictions) > 0


# ── Events Tests ──────────────────────────────────────────────────────


class TestEvents:
    def test_append_and_read(self, tmp_path: Path):
        event = append_event(
            tmp_path,
            EventAction.CREATE,
            "test-ki",
            details={"field": "value"},
        )
        assert event.event_id.startswith("evt-")
        events = read_events(tmp_path)
        assert len(events) == 1
        assert events[0].ki_name == "test-ki"

    def test_filter_by_action(self, tmp_path: Path):
        append_event(tmp_path, EventAction.CREATE, "ki-1")
        append_event(tmp_path, EventAction.UPDATE, "ki-1")
        append_event(tmp_path, EventAction.PROMOTE, "ki-2")
        events = read_events(tmp_path, action_filter=EventAction.PROMOTE)
        assert len(events) == 1
        assert events[0].ki_name == "ki-2"

    def test_compact_log(self, tmp_path: Path):
        for i in range(20):
            append_event(tmp_path, EventAction.UPDATE, "ki-1", details={"i": i})
        assert count_events(tmp_path) == 20
        removed = compact_log(tmp_path, keep_latest_per_ki=5)
        assert removed == 15
        assert count_events(tmp_path) == 5

    def test_event_json_roundtrip(self):
        event = KIEvent(
            event_id="evt-test123",
            timestamp="2026-04-20T00:00:00Z",
            action=EventAction.CREATE,
            ki_name="test-ki",
            details={"key": "value"},
        )
        json_str = event.to_json()
        loaded = KIEvent.from_json(json_str)
        assert loaded.event_id == event.event_id
        assert loaded.ki_name == event.ki_name
        assert loaded.details == event.details


# ── Promotion Tests ───────────────────────────────────────────────────


class TestPromotion:
    def test_promote_high_confidence(self):
        belief = _make_ki(name="high-conf", ki_type=KIType.BELIEF, confidence=0.95)
        result = promote_beliefs([belief], dry_run=True)
        assert "high-conf" in result.promoted

    def test_skip_low_confidence(self):
        belief = _make_ki(name="low-conf", ki_type=KIType.BELIEF, confidence=0.5)
        result = promote_beliefs([belief], dry_run=True)
        assert "low-conf" in result.skipped

    def test_detect_explicit_conflict(self):
        ki1 = _make_ki(
            name="ki1",
            relations=[KIRelation(target_ki="ki2", relation_type=RelationType.CONTRADICTS)],
        )
        ki2 = _make_ki(name="ki2")
        result = detect_conflicts([ki1, ki2])
        assert len(result.detected) >= 1
        assert any("Explicit" in c.reason for c in result.detected)


# ── Views Tests ───────────────────────────────────────────────────────


class TestViews:
    def test_render_index(self):
        kis = [
            _make_ki(name="fact-1", ki_type=KIType.FACT),
            _make_ki(name="decision-1", ki_type=KIType.DECISION),
        ]
        md = render_index(kis)
        assert "# KI Index" in md
        assert "fact-1" in md
        assert "decision-1" in md

    def test_render_handoff(self):
        kis = [
            _make_ki(name="constraint-1", ki_type=KIType.CONSTRAINT),
            _make_ki(name="conflict-1", ki_type=KIType.CONFLICT),
        ]
        md = render_handoff(kis)
        assert "# Session Handoff" in md
        assert "constraint-1" in md


# ── Migration Tests ───────────────────────────────────────────────────


class TestMigration:
    def test_infer_decision(self):
        assert infer_ki_type({"name": "Firestore verdict"}) == KIType.DECISION

    def test_infer_constraint(self):
        assert infer_ki_type({"name": "Must always use GCP"}) == KIType.CONSTRAINT

    def test_infer_fact_default(self):
        assert infer_ki_type({"name": "API reference"}) == KIType.FACT

    def test_migrate_adds_fields(self, tmp_ki_dir: Path):
        # Remove new fields from one KI to simulate legacy
        ki_path = tmp_ki_dir / "veo-api-reference" / "metadata.json"
        with open(ki_path) as f:
            raw = json.load(f)
        del raw["ki_type"]
        del raw["status"]
        del raw["confidence"]
        del raw["classification"]
        with open(ki_path, "w") as f:
            json.dump(raw, f)

        result = migrate_ki_metadata(tmp_ki_dir, dry_run=True)
        assert "veo-api-reference" in result.migrated
        assert "ki_type" in result.upgraded_fields["veo-api-reference"]


# ── FTS Tests ─────────────────────────────────────────────────────────


class TestFTS:
    def test_reindex_and_search(self, tmp_ki_dir: Path):
        from core.ki_engine.fts_index import reindex_all, search_fts, _db_path

        count = reindex_all(tmp_ki_dir)
        assert count >= 4

        conn = sqlite3.connect(str(_db_path(tmp_ki_dir)))
        results = search_fts(conn, "firestore")
        conn.close()
        assert len(results) >= 1
        assert any("firestore" in name for name, _ in results)
