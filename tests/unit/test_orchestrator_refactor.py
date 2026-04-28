# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""
Tests for the Rich Hickey refactored cor_orchestrator.py submodules.

Validates that the thin orchestrator pattern maintains backward compatibility
and all domain-specific submodules are structurally sound.
"""

import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

PNKLN_ROOT = Path(__file__).resolve().parents[2] / "apps" / "aiyou_stack" / "aiyou-fastapi-services" / "apps"


@pytest.fixture(autouse=True)
def patch_sys_path():
    """Add the pnkln apps directory to sys.path for import resolution."""
    path_str = str(PNKLN_ROOT)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
    if "numpy" not in sys.modules:
        sys.modules["numpy"] = MagicMock()
    yield
    if path_str in sys.path:
        sys.path.remove(path_str)


def _clear_pnkln_cache():
    """Flush cached pnkln modules for clean re-import."""
    for key in list(sys.modules.keys()):
        if key.startswith("pnkln"):
            del sys.modules[key]


class TestCoreSubmoduleExistence:
    """Verify all cor_orchestrator submodules exist and are importable."""

    EXPECTED_MODULES = [
        "pnkln.core.cor_context",
        "pnkln.core.cor_tools",
        "pnkln.core.cor_pipelines",
        "pnkln.core.cor_memory",
    ]

    @pytest.mark.parametrize("module_name", EXPECTED_MODULES)
    def test_submodule_importable(self, module_name):
        """Each refactored core submodule must be importable."""
        _clear_pnkln_cache()
        mod = importlib.import_module(module_name)
        assert mod is not None


class TestThinOrchestratorExports:
    """Verify the thin orchestrator re-exports expected symbols."""

    def test_orchestrator_exports_cor_orchestrator(self):
        """CorOrchestrator must be importable from the thin file."""
        _clear_pnkln_cache()
        from pnkln.core.cor_orchestrator import CorOrchestrator

        assert CorOrchestrator is not None

    def test_orchestrator_exports_pipeline(self):
        """SequentialPipeline must be importable."""
        _clear_pnkln_cache()
        from pnkln.core.cor_orchestrator import SequentialPipeline

        assert SequentialPipeline is not None

    def test_orchestrator_exports_tool_registry(self):
        """ToolRegistry must be importable."""
        _clear_pnkln_cache()
        from pnkln.core.cor_orchestrator import ToolRegistry

        assert ToolRegistry is not None

    def test_orchestrator_exports_memory(self):
        """OrchestratorMemory must be importable."""
        _clear_pnkln_cache()
        from pnkln.core.cor_orchestrator import OrchestratorMemory

        assert OrchestratorMemory is not None


class TestContextSubmodule:
    """Verify cor_context.py exports."""

    def test_execution_context_exists(self):
        """ExecutionContext class must exist."""
        _clear_pnkln_cache()
        from pnkln.core.cor_context import ExecutionContext

        assert ExecutionContext is not None


class TestToolsSubmodule:
    """Verify cor_tools.py exports."""

    def test_tool_registry_exists(self):
        """ToolRegistry class must exist."""
        _clear_pnkln_cache()
        from pnkln.core.cor_tools import ToolRegistry

        assert ToolRegistry is not None

    def test_tool_dataclass_exists(self):
        """Tool dataclass must exist."""
        _clear_pnkln_cache()
        from pnkln.core.cor_tools import Tool

        assert Tool is not None


class TestPipelineSubmodule:
    """Verify cor_pipelines.py exports."""

    def test_sequential_pipeline_exists(self):
        """SequentialPipeline class must exist."""
        _clear_pnkln_cache()
        from pnkln.core.cor_pipelines import SequentialPipeline

        assert SequentialPipeline is not None

    def test_concurrent_executor_exists(self):
        """ConcurrentExecutor class must exist."""
        _clear_pnkln_cache()
        from pnkln.core.cor_pipelines import ConcurrentExecutor

        assert ConcurrentExecutor is not None

    def test_pipeline_stage_exists(self):
        """PipelineStage dataclass must exist."""
        _clear_pnkln_cache()
        from pnkln.core.cor_pipelines import PipelineStage

        assert PipelineStage is not None


class TestMemorySubmodule:
    """Verify cor_memory.py exports."""

    def test_orchestrator_memory_exists(self):
        """OrchestratorMemory class must exist."""
        _clear_pnkln_cache()
        from pnkln.core.cor_memory import OrchestratorMemory

        assert OrchestratorMemory is not None
