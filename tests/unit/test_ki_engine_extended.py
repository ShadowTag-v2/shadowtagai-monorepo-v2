# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
"""Tests for ki_engine extended modules: encryption, FTS5, migration, isolation."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from core.ki_engine.encrypt import (
    decrypt_content,
    encrypt_content,
    is_encrypted,
)
from core.ki_engine.fts_index import (
    init_index,
    index_ki,
    reindex_all,
    search_fts,
)
from core.ki_engine.isolation import (
    IsolationConfig,
    init_isolated,
    list_agent_kis,
    list_shared_kis,
    load_isolation_config,
    resolve_agent_dir,
    save_isolation_config,
    share_ki,
    unshare_ki,
)
from core.ki_engine.migration import (
    infer_ki_type,
    migrate_ki_metadata,
)
from core.ki_engine.schema import (
    KIMetadata,
    KIType,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ki_tmpdir(tmp_path: Path) -> Path:
    """Create a temporary KI directory with sample KIs."""
    ki_dir = tmp_path / "knowledge"
    ki_dir.mkdir()

    # Create a sample KI
    ki1 = ki_dir / "firestore-decision"
    ki1.mkdir()
    (ki1 / "metadata.json").write_text(
        json.dumps(
            {
                "name": "Firestore vs Supabase Decision",
                "summary": "Firestore is the canonical database. Supabase rejected.",
                "createdAt": "2026-04-01T00:00:00Z",
                "updatedAt": "2026-04-15T00:00:00Z",
                "references": [],
                "tags": ["firestore", "database", "architecture"],
            }
        )
    )
    artifacts1 = ki1 / "artifacts"
    artifacts1.mkdir()
    (artifacts1 / "analysis.md").write_text("# Firestore vs Supabase\nFirestore chosen for GCP native integration.")

    # Create another sample KI
    ki2 = ki_dir / "security-constraint"
    ki2.mkdir()
    (ki2 / "metadata.json").write_text(
        json.dumps(
            {
                "name": "Never store secrets in code",
                "summary": "All secrets must use GCP Secret Manager. Never hardcode.",
                "createdAt": "2026-03-01T00:00:00Z",
                "updatedAt": "2026-04-10T00:00:00Z",
                "references": [],
                "tags": ["security", "secrets", "constraint"],
            }
        )
    )

    return ki_dir


# ---------------------------------------------------------------------------
# Encryption Tests
# ---------------------------------------------------------------------------


class TestEncryption:
    """Tests for AES-256-GCM encryption."""

    @pytest.fixture(autouse=True)
    def _set_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MEMORY_ENCRYPTION_KEY", "test-key-for-unit-tests-only")

    def test_encrypt_decrypt_roundtrip(self) -> None:
        """Plaintext → encrypt → decrypt should return original."""
        plaintext = "Attorney-client privilege session transcript."
        encrypted = encrypt_content(plaintext)
        assert encrypted != plaintext
        assert is_encrypted(encrypted)
        assert decrypt_content(encrypted) == plaintext

    def test_encrypted_format(self) -> None:
        """Encrypted output must match ENC:v1:{nonce}:{ciphertext} format."""
        encrypted = encrypt_content("test")
        parts = encrypted.split(":")
        assert len(parts) == 4
        assert parts[0] == "ENC"
        assert parts[1] == "v1"

    def test_is_encrypted_detects_format(self) -> None:
        """is_encrypted should detect ENC:v1: prefix and reject plaintext."""
        assert is_encrypted("ENC:v1:abc:def") is True
        assert is_encrypted("plaintext content") is False
        assert is_encrypted("") is False

    def test_different_encryptions_differ(self) -> None:
        """Two encryptions of same content should produce different ciphertext."""
        content = "same content"
        enc1 = encrypt_content(content)
        enc2 = encrypt_content(content)
        assert enc1 != enc2  # Different nonces

    def test_decrypt_invalid_format_raises(self) -> None:
        """Decrypting invalid format must raise ValueError."""
        with pytest.raises(ValueError, match="Invalid encrypted format"):
            decrypt_content("NOT:ENCRYPTED")

    def test_encrypt_empty_string(self) -> None:
        """Empty string should encrypt and decrypt correctly."""
        encrypted = encrypt_content("")
        assert is_encrypted(encrypted)
        assert decrypt_content(encrypted) == ""


# ---------------------------------------------------------------------------
# FTS5 Index Tests
# ---------------------------------------------------------------------------


class TestFTS5Index:
    """Tests for SQLite FTS5 full-text search index."""

    def test_init_creates_tables(self, tmp_path: Path) -> None:
        """init_index should create ki_meta, ki_fts, and ki_artifacts tables."""
        conn = init_index(tmp_path)
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' OR type='view'").fetchall()
        table_names = {t[0] for t in tables}
        assert "ki_meta" in table_names
        assert "ki_artifacts" in table_names
        conn.close()

    def test_index_and_search(self, tmp_path: Path) -> None:
        """Index a KI and search for it via FTS5."""
        conn = init_index(tmp_path)
        ki = KIMetadata(
            name="test-ki",
            summary="Firestore is the canonical database for this project",
            tags=["firestore", "database"],
            ki_type=KIType.DECISION,
        )
        index_ki(conn, ki, artifact_content="We chose Firestore over Supabase.")

        results = search_fts(conn, "Firestore")
        assert len(results) >= 1
        assert results[0][0] == "test-ki"
        conn.close()

    def test_search_no_results(self, tmp_path: Path) -> None:
        """Search for non-existent term should return empty list."""
        conn = init_index(tmp_path)
        results = search_fts(conn, "nonexistent_xyzzy")
        assert results == []
        conn.close()

    def test_reindex_all(self, ki_tmpdir: Path) -> None:
        """reindex_all should index all KIs from directory."""
        count = reindex_all(ki_tmpdir)
        assert count == 2

        # Verify database exists
        db_path = ki_tmpdir / ".ki-index.db"
        assert db_path.exists()

        # Verify search works
        conn = sqlite3.connect(str(db_path))
        results = conn.execute("SELECT name FROM ki_meta ORDER BY name").fetchall()
        assert len(results) == 2
        conn.close()


# ---------------------------------------------------------------------------
# Migration Tests
# ---------------------------------------------------------------------------


class TestMigration:
    """Tests for KI metadata migration."""

    def test_infer_type_decision(self) -> None:
        """Should infer DECISION type from name containing 'decision'."""
        ki = {"name": "Firestore vs Supabase Decision", "summary": ""}
        assert infer_ki_type(ki) == KIType.DECISION

    def test_infer_type_constraint(self) -> None:
        """Should infer CONSTRAINT type from summary containing 'never'."""
        ki = {"name": "Security Rule", "summary": "never store secrets in code"}
        assert infer_ki_type(ki) == KIType.CONSTRAINT

    def test_infer_type_procedure(self) -> None:
        """Should infer PROCEDURE type from name containing 'how to'."""
        ki = {"name": "How to deploy Cloud Run", "summary": ""}
        assert infer_ki_type(ki) == KIType.PROCEDURE

    def test_infer_type_default_fact(self) -> None:
        """Should default to FACT when no indicators match."""
        ki = {"name": "Generic Item", "summary": "some content"}
        assert infer_ki_type(ki) == KIType.FACT

    def test_dry_run_does_not_modify(self, ki_tmpdir: Path) -> None:
        """Dry run should report changes without writing files."""
        result = migrate_ki_metadata(ki_tmpdir, dry_run=True)
        assert len(result.migrated) == 2
        assert len(result.errors) == 0

        # Verify files unchanged (no ki_type field)
        meta = json.loads((ki_tmpdir / "firestore-decision" / "metadata.json").read_text())
        assert "ki_type" not in meta

    def test_live_migration_adds_fields(self, ki_tmpdir: Path) -> None:
        """Live migration should add ki_type, status, confidence, classification."""
        result = migrate_ki_metadata(ki_tmpdir, dry_run=False)
        assert len(result.migrated) == 2

        meta = json.loads((ki_tmpdir / "firestore-decision" / "metadata.json").read_text())
        assert "ki_type" in meta
        assert "status" in meta
        assert "confidence" in meta
        assert "classification" in meta
        assert meta["ki_type"] == "decision"
        assert meta["status"] == "active"

    def test_migration_idempotent(self, ki_tmpdir: Path) -> None:
        """Running migration twice should skip already-migrated KIs."""
        migrate_ki_metadata(ki_tmpdir, dry_run=False)
        result2 = migrate_ki_metadata(ki_tmpdir, dry_run=False)
        assert len(result2.migrated) == 0
        assert len(result2.skipped) == 2

    def test_migration_nonexistent_dir(self, tmp_path: Path) -> None:
        """Migration on nonexistent dir should return error."""
        result = migrate_ki_metadata(tmp_path / "nonexistent")
        assert len(result.errors) == 1


# ---------------------------------------------------------------------------
# Isolation Tests
# ---------------------------------------------------------------------------


class TestIsolation:
    """Tests for per-agent KI isolation."""

    def test_init_creates_dirs(self, tmp_path: Path) -> None:
        """init_isolated should create agent and shared directories."""
        config = init_isolated(tmp_path, ["antigravity", "claude"])
        assert config.mode == "per-agent"
        assert (tmp_path / "agents" / "antigravity").exists()
        assert (tmp_path / "agents" / "claude").exists()
        assert (tmp_path / "shared").exists()

    def test_config_persistence(self, tmp_path: Path) -> None:
        """Config should persist to JSON and reload."""
        config = IsolationConfig(
            mode="per-agent",
            agents=["antigravity", "claude"],
            default_agent="antigravity",
        )
        save_isolation_config(tmp_path, config)
        loaded = load_isolation_config(tmp_path)
        assert loaded.mode == "per-agent"
        assert loaded.agents == ["antigravity", "claude"]

    def test_resolve_agent_dir_per_agent(self, tmp_path: Path) -> None:
        """In per-agent mode, resolve to agents/{id} subdir."""
        init_isolated(tmp_path, ["antigravity"])
        resolved = resolve_agent_dir(tmp_path, "antigravity")
        assert resolved == tmp_path / "agents" / "antigravity"

    def test_resolve_agent_dir_shared_mode(self, tmp_path: Path) -> None:
        """In shared mode, resolve to root ki_dir."""
        resolved = resolve_agent_dir(tmp_path, "anything")
        assert resolved == tmp_path

    def test_share_and_unshare(self, tmp_path: Path) -> None:
        """share_ki should copy to shared dir, unshare should remove."""
        init_isolated(tmp_path, ["antigravity"])

        # Create a KI in antigravity's store
        ki_dir = tmp_path / "agents" / "antigravity" / "test-ki"
        ki_dir.mkdir(parents=True)
        (ki_dir / "metadata.json").write_text('{"name": "test-ki"}')

        # Share it
        assert share_ki(tmp_path, "antigravity", "test-ki") is True
        assert (tmp_path / "shared" / "test-ki" / "metadata.json").exists()

        # Unshare it
        assert unshare_ki(tmp_path, "test-ki") is True
        assert not (tmp_path / "shared" / "test-ki").exists()

    def test_list_agent_and_shared_kis(self, tmp_path: Path) -> None:
        """Should list KIs in agent store and shared store independently."""
        init_isolated(tmp_path, ["antigravity"])

        # Create agent KIs
        for name in ["ki-a", "ki-b"]:
            d = tmp_path / "agents" / "antigravity" / name
            d.mkdir(parents=True)
            (d / "metadata.json").write_text(f'{{"name": "{name}"}}')

        # Create shared KI
        sd = tmp_path / "shared" / "ki-shared"
        sd.mkdir(parents=True)
        (sd / "metadata.json").write_text('{"name": "ki-shared"}')

        assert list_agent_kis(tmp_path, "antigravity") == ["ki-a", "ki-b"]
        assert list_shared_kis(tmp_path) == ["ki-shared"]
