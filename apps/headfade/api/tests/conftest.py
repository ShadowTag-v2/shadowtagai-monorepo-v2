"""
HeadFade API — Shared Test Fixtures.

Centralizes mock factories for Firebase, Firestore, and GenAI
to DRY up test setup across test modules. All sys.modules patches
are applied ONCE at conftest-load time, before any test imports.
"""

import sys
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Module-level mock injection — executes once when pytest collects this file.
# CRITICAL: Use direct assignment to override any monorepo conftest leakage.
# ---------------------------------------------------------------------------

# Firebase Admin SDK mocks
_mock_firebase_admin = MagicMock()
_mock_firebase_admin._apps = {"[DEFAULT]": MagicMock()}
_mock_credentials = MagicMock()
_mock_firestore_module = MagicMock()
_mock_firestore_client = MagicMock()
_mock_firestore_module.client.return_value = _mock_firestore_client

sys.modules["firebase_admin"] = _mock_firebase_admin
sys.modules["firebase_admin.credentials"] = _mock_credentials
sys.modules["firebase_admin.firestore"] = _mock_firestore_module

# google.cloud.firestore — required by hdi_telemetry.py
_mock_gc_firestore = MagicMock()
_mock_gc_firestore.Client.return_value = _mock_firestore_client
_mock_gc_firestore.SERVER_TIMESTAMP = "SERVER_TIMESTAMP_SENTINEL"
sys.modules["google.cloud"] = MagicMock()
sys.modules["google.cloud.firestore"] = _mock_gc_firestore

# google.genai — required by arbiter.py
_mock_genai = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = _mock_genai
sys.modules["google.genai.types"] = MagicMock()

# OpenTelemetry — optional production dep, mock for tests
sys.modules["opentelemetry"] = MagicMock()
sys.modules["opentelemetry.api"] = MagicMock()
sys.modules["opentelemetry.sdk"] = MagicMock()
sys.modules["opentelemetry.sdk.trace"] = MagicMock()
sys.modules["opentelemetry.sdk.trace.export"] = MagicMock()
sys.modules["opentelemetry.instrumentation"] = MagicMock()
sys.modules["opentelemetry.instrumentation.fastapi"] = MagicMock()
sys.modules["opentelemetry.exporter"] = MagicMock()
sys.modules["opentelemetry.exporter.cloud_trace"] = MagicMock()
sys.modules["opentelemetry.trace"] = MagicMock()


# ---------------------------------------------------------------------------
# Reusable Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_firestore_db():
    """Fresh MagicMock Firestore client for per-test isolation."""
    db = MagicMock()
    doc = MagicMock()
    db.collection.return_value.document.return_value = doc
    return db, doc


@pytest.fixture
def mock_genai_response():
    """Construct a standard GenAI response with thinking + verdict parts."""

    def _factory(thought_text: str, verdict_text: str):
        mock_part = MagicMock()
        mock_part.thought = True
        mock_part.text = thought_text

        mock_verdict_part = MagicMock()
        mock_verdict_part.thought = False
        mock_verdict_part.text = verdict_text

        mock_content = MagicMock()
        mock_content.parts = [mock_part, mock_verdict_part]

        mock_candidate = MagicMock()
        mock_candidate.content = mock_content

        mock_response = MagicMock()
        mock_response.candidates = [mock_candidate]
        return mock_response

    return _factory


@pytest.fixture
def mock_genai_client(mock_genai_response):
    """Mock GenAI client whose generate_content returns a default response."""
    client = MagicMock()
    default = mock_genai_response(
        "Temporal inconsistencies detected.",
        "VERDICT: AI-generated.",
    )
    client.models.generate_content.return_value = default
    return client
