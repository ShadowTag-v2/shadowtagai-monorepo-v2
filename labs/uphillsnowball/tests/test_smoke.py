# labs/uphillsnowball/tests/test_smoke.py
"""Smoke tests to bootstrap pytest discovery (Item 5).

Verifies that core modules import successfully and key classes exist.
"""

from __future__ import annotations


class TestModuleImports:
    """Verify all source modules are importable."""

    def test_watermark_module(self):
        from src.watermark.shadowtag_dct import ShadowTagProcessor
        assert ShadowTagProcessor is not None

    def test_epistemology_module(self):
        from src.intelligence.epistemology_engine import EpistemologicalForensics
        assert EpistemologicalForensics is not None

    def test_ucmj_module(self):
        from src.agents.discipline.ucmj_whiteboard import SwarmWhiteboard
        assert SwarmWhiteboard is not None

    def test_senses_module(self):
        from src.pipelines.senses import RadarSense, PrometheusIngestor
        assert RadarSense is not None
        assert PrometheusIngestor is not None

    def test_activities_module(self):
        from src.activities import j5_draft_opord_and_backbrief
        assert j5_draft_opord_and_backbrief is not None

    def test_governance_module(self):
        import importlib
        mod = importlib.import_module("src.governance.j6_csrmc_cato")
        assert mod is not None

    def test_delivery_module(self):
        from src.delivery import splinter_engine, splinter_io
        assert splinter_engine is not None

    def test_contracts_module(self):
        import importlib
        mod = importlib.import_module("src.contracts.constitution")
        assert mod is not None


class TestSanityChecks:
    """Basic sanity checks."""

    def test_python_version(self):
        import sys
        assert sys.version_info >= (3, 11)

    def test_numpy_available(self):
        import numpy as np
        assert np.__version__
