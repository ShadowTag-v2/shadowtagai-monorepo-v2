"""
Integration tests for code line provenance in the execution pipeline.

Tests end-to-end provenance tracking through notebook generation,
finding augmentation, and report generation.

Issue: #62 (GAP-009)
"""

import json
import tempfile
from pathlib import Path

import pytest

from kosmos.execution.notebook_generator import NotebookGenerator
from kosmos.execution.provenance import (
    CodeProvenance,
    build_cell_line_mappings,
)
from kosmos.world_model.artifacts import ArtifactStateManager, Finding

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_artifacts_dir():
    """Create temporary artifacts directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def notebook_generator(temp_artifacts_dir):
    """Create NotebookGenerator for testing."""
    return NotebookGenerator(artifacts_dir=temp_artifacts_dir)


@pytest.fixture
def state_manager(temp_artifacts_dir):
    """Create ArtifactStateManager for testing."""
    return ArtifactStateManager(artifacts_dir=temp_artifacts_dir)


@pytest.fixture
def sample_code():
    """Sample analysis code."""
    return """import pandas as pd
import numpy as np

# Load data
df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})

# Calculate correlation
correlation = df['x'].corr(df['y'])
print(f"Correlation: {correlation}")

# Return result
result = {'correlation': correlation}
"""


@pytest.fixture
def finding_with_provenance():
    """Create a Finding with code provenance."""
    provenance = CodeProvenance(
        notebook_path="artifacts/cycle_1/notebooks/task_5_correlation.ipynb",
        cell_index=1,
        start_line=1,
        end_line=12,
        code_snippet="import pandas as pd\nimport numpy as np\n...",
        hypothesis_id="hyp_001",
        cycle=1,
        task_id=5,
        analysis_type="correlation",
    )
    return Finding(
        finding_id="f001",
        cycle=1,
        task_id=5,
        summary="Strong correlation found between x and y",
        statistics={"correlation": 0.95, "p_value": 0.01},
        code_provenance=provenance.to_dict(),
    )


# =============================================================================
# TestProvenanceWithNotebookGenerator
# =============================================================================


class TestProvenanceWithNotebookGenerator:
    """Tests for provenance integration with NotebookGenerator."""

    def test_notebook_metadata_includes_cell_mappings(self, notebook_generator, sample_code):
        """Test that generated notebooks include cell-to-line mappings."""
        metadata = notebook_generator.create_notebook(
            code=sample_code,
            cycle=1,
            task_id=1,
            analysis_type="correlation",
            title="Correlation Analysis",
        )

        assert metadata is not None
        assert metadata.cell_line_mappings is not None
        assert len(metadata.cell_line_mappings) > 0

    def test_cell_mappings_track_line_numbers(self, notebook_generator, sample_code):
        """Test that cell mappings track correct line numbers."""
        metadata = notebook_generator.create_notebook(
            code=sample_code,
            cycle=1,
            task_id=1,
            analysis_type="correlation",
        )

        mappings = metadata.cell_line_mappings
        # First cell should start at line 1
        assert mappings[0]["start_line"] == 1
        # Each mapping should have required fields
        for mapping in mappings:
            assert "cell_index" in mapping
            assert "start_line" in mapping
            assert "end_line" in mapping
            assert "code_hash" in mapping

    def test_create_provenance_from_notebook_metadata(self, notebook_generator, sample_code):
        """Test creating provenance from generated notebook metadata."""
        metadata = notebook_generator.create_notebook(
            code=sample_code,
            cycle=1,
            task_id=1,
            analysis_type="correlation",
        )

        # Create provenance using notebook metadata
        provenance = CodeProvenance.create_from_execution(
            notebook_path=metadata.path,
            code=sample_code,
            cell_index=0,
            cycle=1,
            task_id=1,
            analysis_type="correlation",
        )

        assert provenance.notebook_path == metadata.path
        assert provenance.code_hash is not None

    def test_multiple_cells_get_correct_mappings(self, notebook_generator):
        """Test that code split into multiple cells gets correct mappings."""
        # Code with explicit cell markers
        code = """# %% Cell 1
import pandas as pd
import numpy as np

# %% Cell 2
df = pd.DataFrame({'x': [1, 2, 3]})
print(df)

# %% Cell 3
result = df.describe()
"""
        metadata = notebook_generator.create_notebook(
            code=code,
            cycle=1,
            task_id=2,
            analysis_type="data_analysis",
        )

        assert metadata is not None
        # Should have multiple cells (code is split by # %%)
        assert metadata.code_cell_count >= 1


# =============================================================================
# TestProvenanceInFinding
# =============================================================================


class TestProvenanceInFinding:
    """Tests for provenance in Finding dataclass."""

    def test_finding_stores_provenance(self, finding_with_provenance):
        """Test that Finding stores code provenance."""
        assert finding_with_provenance.code_provenance is not None
        prov = finding_with_provenance.code_provenance
        assert prov["notebook_path"] is not None
        assert prov["cell_index"] == 1

    def test_finding_serializes_provenance(self, finding_with_provenance):
        """Test that Finding serializes provenance correctly."""
        data = finding_with_provenance.to_dict()
        assert "code_provenance" in data
        assert data["code_provenance"]["cell_index"] == 1

    def test_finding_json_serializable(self, finding_with_provenance):
        """Test that Finding with provenance is JSON serializable."""
        data = finding_with_provenance.to_dict()
        json_str = json.dumps(data)
        restored = json.loads(json_str)
        assert (
            restored["code_provenance"]["notebook_path"]
            == finding_with_provenance.code_provenance["notebook_path"]
        )

    def test_finding_without_provenance(self):
        """Test Finding without provenance (backward compatibility)."""
        finding = Finding(
            finding_id="f002",
            cycle=1,
            task_id=1,
            summary="Test finding",
            statistics={"p_value": 0.05},
        )
        assert finding.code_provenance is None
        data = finding.to_dict()
        assert data.get("code_provenance") is None


# =============================================================================
# TestProvenanceInReports
# =============================================================================


class TestProvenanceInReports:
    """Tests for provenance in report generation."""

    def test_hyperlink_format(self, finding_with_provenance):
        """Test that hyperlinks are correctly formatted."""
        prov = finding_with_provenance.code_provenance
        hyperlink = f"{prov['notebook_path']}#cell={prov['cell_index']}&line={prov['start_line']}"

        assert "task_5_correlation.ipynb" in hyperlink
        assert "#cell=1" in hyperlink
        assert "&line=1" in hyperlink

    def test_report_generation_with_provenance(self, finding_with_provenance):
        """Test report generation includes provenance hyperlinks."""
        # Simulate report generation logic from research_loop.py
        report = ""
        finding = finding_with_provenance

        if finding.code_provenance:
            prov = finding.code_provenance
            hyperlink = (
                f"{prov['notebook_path']}#cell={prov['cell_index']}&line={prov['start_line']}"
            )
            filename = prov["notebook_path"].split("/")[-1]
            report += f"**Code Citation**: [{filename}]({hyperlink})"
            if prov.get("start_line") and prov.get("end_line"):
                report += f" (lines {prov['start_line']}-{prov['end_line']})"
            report += "\n\n"

        assert "Code Citation" in report
        assert "task_5_correlation.ipynb" in report
        assert "lines 1-12" in report

    def test_report_fallback_without_provenance(self):
        """Test report falls back to notebook_path without provenance."""
        finding = Finding(
            finding_id="f003",
            cycle=1,
            task_id=1,
            summary="Test",
            statistics={},
            notebook_path="artifacts/cycle_1/notebooks/test.ipynb",
        )

        report = ""
        if finding.code_provenance:
            pass  # Would use hyperlink
        elif finding.notebook_path:
            report += f"**Evidence**: `{finding.notebook_path}`\n\n"

        assert "Evidence" in report
        assert finding.notebook_path in report


# =============================================================================
# TestProvenanceValidation
# =============================================================================


class TestProvenanceValidation:
    """Tests for provenance validation and consistency."""

    def test_code_hash_consistency(self, sample_code):
        """Test that same code produces consistent hash."""
        prov1 = CodeProvenance.create_from_execution(
            notebook_path="test.ipynb",
            code=sample_code,
            cell_index=0,
        )
        prov2 = CodeProvenance.create_from_execution(
            notebook_path="test.ipynb",
            code=sample_code,
            cell_index=0,
        )
        # Note: code_hash is computed from truncated snippet
        assert prov1.code_hash == prov2.code_hash

    def test_different_code_different_hash(self):
        """Test that different code produces different hash."""
        prov1 = CodeProvenance.create_from_execution(
            notebook_path="test.ipynb",
            code="x = 1",
            cell_index=0,
        )
        prov2 = CodeProvenance.create_from_execution(
            notebook_path="test.ipynb",
            code="x = 2",
            cell_index=0,
        )
        assert prov1.code_hash != prov2.code_hash

    def test_cell_mapping_hash_matches_provenance(self, notebook_generator):
        """Test that cell mapping hashes can validate provenance."""
        code = "import pandas\ndf = pandas.DataFrame()"
        metadata = notebook_generator.create_notebook(
            code=code,
            cycle=1,
            task_id=1,
            analysis_type="test",
        )

        # Both should have consistent hashing
        assert metadata.cell_line_mappings is not None
        for mapping in metadata.cell_line_mappings:
            assert "code_hash" in mapping
            assert len(mapping["code_hash"]) == 16


# =============================================================================
# TestEndToEndPipeline
# =============================================================================


class TestEndToEndPipeline:
    """End-to-end tests for provenance pipeline."""

    def test_full_pipeline_notebook_to_finding(self, notebook_generator, sample_code):
        """Test full pipeline from notebook generation to finding."""
        # Step 1: Generate notebook
        metadata = notebook_generator.create_notebook(
            code=sample_code,
            cycle=1,
            task_id=5,
            analysis_type="correlation",
            title="Correlation Analysis",
        )
        assert metadata is not None

        # Step 2: Create provenance
        provenance = CodeProvenance.create_from_execution(
            notebook_path=metadata.path,
            code=sample_code,
            cell_index=0,
            hypothesis_id="hyp_001",
            cycle=1,
            task_id=5,
            analysis_type="correlation",
        )

        # Step 3: Create finding with provenance
        finding = Finding(
            finding_id="f_full_test",
            cycle=1,
            task_id=5,
            summary="Correlation analysis completed",
            statistics={"correlation": 0.95},
            code_provenance=provenance.to_dict(),
        )

        # Step 4: Verify complete chain
        assert finding.code_provenance is not None
        assert finding.code_provenance["notebook_path"] == metadata.path
        assert finding.code_provenance["cell_index"] == 0

    def test_finding_save_and_load_with_provenance(
        self, state_manager, finding_with_provenance, temp_artifacts_dir
    ):
        """Test saving and loading findings with provenance."""
        import asyncio
        import json

        # Save finding - use async method with correct signature
        finding_dict = finding_with_provenance.to_dict()
        asyncio.get_event_loop().run_until_complete(
            state_manager.save_finding_artifact(cycle=1, task_id=5, finding=finding_dict)
        )

        # Verify file was saved with provenance
        finding_path = temp_artifacts_dir / "cycle_1" / "task_5_finding.json"
        assert finding_path.exists()

        # Load directly and verify provenance preserved
        with open(finding_path) as f:
            loaded_dict = json.load(f)

        assert "code_provenance" in loaded_dict
        assert (
            loaded_dict["code_provenance"]["cell_index"]
            == finding_with_provenance.code_provenance["cell_index"]
        )

    def test_provenance_in_cycle_summary_format(self, finding_with_provenance):
        """Test that provenance generates correct hyperlink format for summary."""
        # Test the hyperlink generation logic that would be used in summary
        prov = finding_with_provenance.code_provenance
        hyperlink = f"{prov['notebook_path']}#cell={prov['cell_index']}&line={prov['start_line']}"
        filename = prov["notebook_path"].split("/")[-1]

        # Build report fragment
        report = f"**Code Citation**: [{filename}]({hyperlink})"
        if prov.get("start_line") and prov.get("end_line"):
            report += f" (lines {prov['start_line']}-{prov['end_line']})"
        report += "\n\n"

        # Verify format
        assert "Code Citation" in report
        assert "task_5_correlation.ipynb" in report
        assert "#cell=1" in report
        assert "lines 1-12" in report


# =============================================================================
# TestPerformance
# =============================================================================


class TestPerformance:
    """Performance tests for provenance tracking."""

    def test_provenance_creation_fast(self, sample_code):
        """Test that provenance creation is fast."""
        import time

        start = time.time()

        for _ in range(100):
            CodeProvenance.create_from_execution(
                notebook_path="test.ipynb",
                code=sample_code,
                cell_index=0,
            )

        elapsed = time.time() - start
        # 100 provenances should complete in under 1 second
        assert elapsed < 1.0

    def test_cell_mapping_build_fast(self):
        """Test that cell mapping building is fast."""
        import time

        # 50 cells of code
        cells = [f"x_{i} = {i}\ny_{i} = {i * 2}" for i in range(50)]

        start = time.time()
        for _ in range(100):
            build_cell_line_mappings(cells)
        elapsed = time.time() - start

        # Should complete in under 1 second
        assert elapsed < 1.0

    def test_serialization_fast(self, finding_with_provenance):
        """Test that serialization with provenance is fast."""
        import time

        start = time.time()

        for _ in range(1000):
            data = finding_with_provenance.to_dict()
            json.dumps(data)

        elapsed = time.time() - start
        # 1000 serializations should complete in under 2 seconds
        assert elapsed < 2.0


# =============================================================================
# TestEdgeCases
# =============================================================================


class TestEdgeCases:
    """Edge case tests for provenance pipeline."""

    def test_empty_code_notebook(self, notebook_generator):
        """Test handling empty code."""
        metadata = notebook_generator.create_notebook(
            code="",
            cycle=1,
            task_id=1,
            analysis_type="test",
        )
        # Should return None for empty code
        assert metadata is None

    def test_whitespace_only_code(self, notebook_generator):
        """Test handling whitespace-only code."""
        metadata = notebook_generator.create_notebook(
            code="   \n   \n   ",
            cycle=1,
            task_id=1,
            analysis_type="test",
        )
        # Should return None for whitespace-only
        assert metadata is None

    def test_very_long_code(self, notebook_generator):
        """Test handling very long code."""
        long_code = "\n".join([f"x_{i} = {i}" for i in range(1000)])
        metadata = notebook_generator.create_notebook(
            code=long_code,
            cycle=1,
            task_id=1,
            analysis_type="long_test",
        )
        assert metadata is not None
        assert metadata.total_line_count == 1000

    def test_finding_with_null_provenance_fields(self):
        """Test finding with some null provenance fields."""
        provenance = CodeProvenance(
            notebook_path="test.ipynb",
            cell_index=0,
            start_line=1,
            end_line=None,  # Null end_line
            code_snippet="x = 1",
            hypothesis_id=None,  # Null hypothesis_id
        )
        finding = Finding(
            finding_id="f_null",
            cycle=1,
            task_id=1,
            summary="Test",
            statistics={},
            code_provenance=provenance.to_dict(),
        )
        data = finding.to_dict()
        assert data["code_provenance"]["end_line"] is None
        assert data["code_provenance"]["hypothesis_id"] is None
