"""
Unit tests for CodeProvenance and CellLineMapping.

Tests code line provenance tracking for linking findings to source code.

Issue: #62 (GAP-009)
"""

import json
from datetime import datetime

import pytest

from kosmos.execution.provenance import (
    CellLineMapping,
    CodeProvenance,
    build_cell_line_mappings,
    create_provenance_from_notebook,
    get_cell_for_line,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def code_provenance():
    """Sample code provenance for testing."""
    return CodeProvenance(
        notebook_path="artifacts/cycle_1/notebooks/task_5_correlation.ipynb",
        cell_index=3,
        start_line=1,
        end_line=15,
        code_snippet="import pandas as pd\ndf = pd.read_csv('data.csv')\nresult = df.describe()",
        hypothesis_id="hyp_001",
    )


@pytest.fixture
def minimal_provenance():
    """Minimal code provenance with only required fields."""
    return CodeProvenance(
        notebook_path="artifacts/cycle_1/notebooks/task_1_analysis.ipynb",
        cell_index=0,
        start_line=1,
        end_line=None,
        code_snippet="print('Hello')",
    )


@pytest.fixture
def cell_line_mapping():
    """Sample cell-to-line mapping."""
    return CellLineMapping(
        cell_index=2,
        start_line=20,
        end_line=35,
        cell_type="code",
        line_count=16,
        code_hash="abc123def456",
    )


@pytest.fixture
def code_cells():
    """Sample code cells for building mappings."""
    return [
        "import pandas as pd\nimport numpy as np",  # 2 lines
        "df = pd.read_csv('data.csv')\nprint(df.head())",  # 2 lines
        "# Analysis\nresult = df.describe()\nprint(result)\nreturn result",  # 4 lines
    ]


# =============================================================================
# TestCodeProvenance
# =============================================================================


class TestCodeProvenance:
    """Tests for CodeProvenance dataclass."""

    def test_create_provenance_full(self, code_provenance):
        """Test creating CodeProvenance with all fields."""
        assert (
            code_provenance.notebook_path == "artifacts/cycle_1/notebooks/task_5_correlation.ipynb"
        )
        assert code_provenance.cell_index == 3
        assert code_provenance.start_line == 1
        assert code_provenance.end_line == 15
        assert "pandas" in code_provenance.code_snippet
        assert code_provenance.hypothesis_id == "hyp_001"

    def test_create_provenance_minimal(self, minimal_provenance):
        """Test creating CodeProvenance with minimal fields."""
        assert minimal_provenance.notebook_path is not None
        assert minimal_provenance.cell_index == 0
        assert minimal_provenance.start_line == 1
        assert minimal_provenance.end_line is None
        assert minimal_provenance.hypothesis_id is None

    def test_timestamp_auto_set(self, minimal_provenance):
        """Test that timestamp is automatically set."""
        assert minimal_provenance.timestamp is not None
        # Should be a valid ISO format timestamp
        datetime.fromisoformat(minimal_provenance.timestamp)

    def test_code_hash_auto_computed(self, minimal_provenance):
        """Test that code hash is automatically computed."""
        assert minimal_provenance.code_hash is not None
        assert len(minimal_provenance.code_hash) == 16  # Truncated SHA256

    def test_code_snippet_truncation(self):
        """Test that long code snippets are truncated."""
        long_code = "x = 1\n" * 200  # Much longer than 500 chars
        provenance = CodeProvenance(
            notebook_path="test.ipynb",
            cell_index=0,
            start_line=1,
            end_line=200,
            code_snippet=long_code,
        )
        assert len(provenance.code_snippet) <= 503  # 500 + "..."
        assert provenance.code_snippet.endswith("...")

    def test_to_hyperlink_with_line(self, code_provenance):
        """Test hyperlink generation with line number."""
        link = code_provenance.to_hyperlink()
        assert "task_5_correlation.ipynb" in link
        assert "#cell=3" in link
        assert "&line=1" in link

    def test_to_hyperlink_without_line(self, code_provenance):
        """Test hyperlink generation without line number."""
        link = code_provenance.to_hyperlink(include_line=False)
        assert "#cell=3" in link
        assert "line" not in link

    def test_to_markdown_link(self, code_provenance):
        """Test Markdown link generation."""
        md_link = code_provenance.to_markdown_link()
        assert "[task_5_correlation.ipynb]" in md_link
        assert "(" in md_link and ")" in md_link

    def test_to_markdown_link_custom_text(self, code_provenance):
        """Test Markdown link with custom text."""
        md_link = code_provenance.to_markdown_link(text="Analysis Code")
        assert "[Analysis Code]" in md_link

    def test_get_line_range_str_single(self, minimal_provenance):
        """Test line range string for single line."""
        line_str = minimal_provenance.get_line_range_str()
        assert line_str == "line 1"

    def test_get_line_range_str_range(self, code_provenance):
        """Test line range string for line range."""
        line_str = code_provenance.get_line_range_str()
        assert line_str == "lines 1-15"

    def test_get_citation_string(self, code_provenance):
        """Test full citation string."""
        citation = code_provenance.get_citation_string()
        assert "task_5_correlation.ipynb" in citation
        assert "cell 3" in citation
        assert "lines 1-15" in citation


# =============================================================================
# TestCodeProvenanceSerialization
# =============================================================================


class TestCodeProvenanceSerialization:
    """Tests for CodeProvenance serialization."""

    def test_to_dict(self, code_provenance):
        """Test serialization to dictionary."""
        data = code_provenance.to_dict()
        assert isinstance(data, dict)
        assert data["notebook_path"] == code_provenance.notebook_path
        assert data["cell_index"] == code_provenance.cell_index
        assert data["start_line"] == code_provenance.start_line
        assert data["end_line"] == code_provenance.end_line
        assert data["code_snippet"] == code_provenance.code_snippet

    def test_from_dict(self, code_provenance):
        """Test deserialization from dictionary."""
        data = code_provenance.to_dict()
        restored = CodeProvenance.from_dict(data)
        assert restored.notebook_path == code_provenance.notebook_path
        assert restored.cell_index == code_provenance.cell_index
        assert restored.start_line == code_provenance.start_line

    def test_roundtrip_serialization(self, code_provenance):
        """Test serialization roundtrip."""
        data = code_provenance.to_dict()
        restored = CodeProvenance.from_dict(data)
        restored_data = restored.to_dict()
        assert data["notebook_path"] == restored_data["notebook_path"]
        assert data["cell_index"] == restored_data["cell_index"]

    def test_json_serializable(self, code_provenance):
        """Test that to_dict output is JSON serializable."""
        data = code_provenance.to_dict()
        json_str = json.dumps(data)
        assert len(json_str) > 0
        restored_data = json.loads(json_str)
        assert restored_data["cell_index"] == code_provenance.cell_index

    def test_from_dict_missing_optional_fields(self):
        """Test deserialization with missing optional fields."""
        data = {
            "notebook_path": "test.ipynb",
            "cell_index": 0,
            "start_line": 1,
            "end_line": 5,
            "code_snippet": "print(1)",
            # Missing: hypothesis_id, execution_id, timestamp, etc.
        }
        provenance = CodeProvenance.from_dict(data)
        assert provenance.hypothesis_id is None
        assert provenance.execution_id is None

    def test_from_dict_with_all_fields(self, code_provenance):
        """Test deserialization with all fields."""
        data = code_provenance.to_dict()
        restored = CodeProvenance.from_dict(data)
        assert restored.hypothesis_id == code_provenance.hypothesis_id
        assert restored.timestamp == code_provenance.timestamp


# =============================================================================
# TestProvenanceCreation
# =============================================================================


class TestProvenanceCreation:
    """Tests for provenance creation methods."""

    def test_create_from_execution(self):
        """Test creating provenance from execution context."""
        provenance = CodeProvenance.create_from_execution(
            notebook_path="artifacts/cycle_2/notebooks/task_3_analysis.ipynb",
            code="import pandas\ndf = pandas.DataFrame()",
            cell_index=1,
            hypothesis_id="hyp_002",
            cycle=2,
            task_id=3,
            analysis_type="data_analysis",
        )
        assert provenance.notebook_path == "artifacts/cycle_2/notebooks/task_3_analysis.ipynb"
        assert provenance.cell_index == 1
        assert provenance.start_line == 1
        assert provenance.end_line == 2  # 2 lines of code
        assert provenance.hypothesis_id == "hyp_002"
        assert provenance.execution_id == "exec_2_3"

    def test_create_from_execution_single_line(self):
        """Test creating provenance from single line code."""
        provenance = CodeProvenance.create_from_execution(
            notebook_path="test.ipynb",
            code="print('hello')",
            cell_index=0,
        )
        assert provenance.start_line == 1
        assert provenance.end_line is None  # Single line

    def test_create_provenance_from_notebook_function(self):
        """Test convenience function create_provenance_from_notebook."""
        provenance = create_provenance_from_notebook(
            notebook_path="test.ipynb",
            code="x = 1\ny = 2\nz = x + y",
            cell_index=0,
            cycle=1,
            task_id=1,
        )
        assert provenance.notebook_path == "test.ipynb"
        assert provenance.end_line == 3  # 3 lines

    def test_create_from_execution_no_optional_params(self):
        """Test creating provenance without optional parameters."""
        provenance = CodeProvenance.create_from_execution(
            notebook_path="test.ipynb",
            code="x = 1",
            cell_index=0,
        )
        assert provenance.hypothesis_id is None
        assert provenance.execution_id is None
        assert provenance.cycle is None

    def test_create_from_execution_long_code(self):
        """Test that long code is truncated in snippet."""
        long_code = "# Comment\n" * 100  # Long code
        provenance = CodeProvenance.create_from_execution(
            notebook_path="test.ipynb",
            code=long_code,
            cell_index=0,
        )
        assert len(provenance.code_snippet) <= 503


# =============================================================================
# TestCellLineMapping
# =============================================================================


class TestCellLineMapping:
    """Tests for CellLineMapping dataclass."""

    def test_create_mapping(self, cell_line_mapping):
        """Test creating cell line mapping."""
        assert cell_line_mapping.cell_index == 2
        assert cell_line_mapping.start_line == 20
        assert cell_line_mapping.end_line == 35
        assert cell_line_mapping.cell_type == "code"
        assert cell_line_mapping.line_count == 16

    def test_to_dict(self, cell_line_mapping):
        """Test serialization to dictionary."""
        data = cell_line_mapping.to_dict()
        assert data["cell_index"] == 2
        assert data["start_line"] == 20
        assert data["end_line"] == 35

    def test_from_dict(self, cell_line_mapping):
        """Test deserialization from dictionary."""
        data = cell_line_mapping.to_dict()
        restored = CellLineMapping.from_dict(data)
        assert restored.cell_index == cell_line_mapping.cell_index
        assert restored.start_line == cell_line_mapping.start_line

    def test_compute_hash(self):
        """Test code hash computation."""
        code = "import pandas as pd"
        hash1 = CellLineMapping.compute_hash(code)
        hash2 = CellLineMapping.compute_hash(code)
        assert hash1 == hash2
        assert len(hash1) == 16

    def test_compute_hash_different_code(self):
        """Test that different code produces different hashes."""
        hash1 = CellLineMapping.compute_hash("x = 1")
        hash2 = CellLineMapping.compute_hash("x = 2")
        assert hash1 != hash2


# =============================================================================
# TestBuildCellLineMappings
# =============================================================================


class TestBuildCellLineMappings:
    """Tests for build_cell_line_mappings function."""

    def test_build_mappings_from_cells(self, code_cells):
        """Test building mappings from code cells."""
        mappings = build_cell_line_mappings(code_cells)
        assert len(mappings) == 3

        # First cell: lines 1-2
        assert mappings[0].cell_index == 0
        assert mappings[0].start_line == 1
        assert mappings[0].end_line == 2
        assert mappings[0].line_count == 2

        # Second cell: lines 3-4
        assert mappings[1].cell_index == 1
        assert mappings[1].start_line == 3
        assert mappings[1].end_line == 4

        # Third cell: lines 5-8
        assert mappings[2].cell_index == 2
        assert mappings[2].start_line == 5
        assert mappings[2].end_line == 8
        assert mappings[2].line_count == 4

    def test_build_mappings_empty_list(self):
        """Test building mappings from empty list."""
        mappings = build_cell_line_mappings([])
        assert len(mappings) == 0

    def test_build_mappings_single_cell(self):
        """Test building mappings from single cell."""
        mappings = build_cell_line_mappings(["x = 1\ny = 2"])
        assert len(mappings) == 1
        assert mappings[0].start_line == 1
        assert mappings[0].end_line == 2

    def test_build_mappings_custom_offset(self, code_cells):
        """Test building mappings with custom start offset."""
        mappings = build_cell_line_mappings(code_cells, start_offset=10)
        assert mappings[0].start_line == 10
        assert mappings[0].end_line == 11

    def test_mappings_have_code_hash(self, code_cells):
        """Test that mappings include code hashes."""
        mappings = build_cell_line_mappings(code_cells)
        for mapping in mappings:
            assert mapping.code_hash is not None
            assert len(mapping.code_hash) == 16


# =============================================================================
# TestGetCellForLine
# =============================================================================


class TestGetCellForLine:
    """Tests for get_cell_for_line function."""

    def test_get_cell_for_line_found(self, code_cells):
        """Test finding cell for a line number."""
        mappings = build_cell_line_mappings(code_cells)

        # Line 1 is in cell 0
        cell = get_cell_for_line(mappings, 1)
        assert cell is not None
        assert cell.cell_index == 0

        # Line 5 is in cell 2
        cell = get_cell_for_line(mappings, 5)
        assert cell is not None
        assert cell.cell_index == 2

    def test_get_cell_for_line_boundary(self, code_cells):
        """Test finding cell at boundary."""
        mappings = build_cell_line_mappings(code_cells)

        # Line 2 is the last line of cell 0
        cell = get_cell_for_line(mappings, 2)
        assert cell.cell_index == 0

        # Line 3 is the first line of cell 1
        cell = get_cell_for_line(mappings, 3)
        assert cell.cell_index == 1

    def test_get_cell_for_line_not_found(self, code_cells):
        """Test line number not found."""
        mappings = build_cell_line_mappings(code_cells)

        # Line 100 is beyond all cells
        cell = get_cell_for_line(mappings, 100)
        assert cell is None

        # Line 0 is before all cells
        cell = get_cell_for_line(mappings, 0)
        assert cell is None

    def test_get_cell_for_line_empty_mappings(self):
        """Test with empty mappings."""
        cell = get_cell_for_line([], 1)
        assert cell is None


# =============================================================================
# TestEdgeCases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_code_snippet(self):
        """Test provenance with empty code snippet."""
        provenance = CodeProvenance(
            notebook_path="test.ipynb",
            cell_index=0,
            start_line=1,
            end_line=1,
            code_snippet="",
        )
        assert provenance.code_snippet == ""
        # Should still have timestamp and hash
        assert provenance.timestamp is not None

    def test_special_characters_in_path(self):
        """Test provenance with special characters in path."""
        provenance = CodeProvenance(
            notebook_path="artifacts/cycle_1/notebooks/task_5_correlation (copy).ipynb",
            cell_index=0,
            start_line=1,
            end_line=1,
            code_snippet="x = 1",
        )
        assert "(copy)" in provenance.notebook_path

    def test_unicode_in_code_snippet(self):
        """Test provenance with unicode in code snippet."""
        provenance = CodeProvenance(
            notebook_path="test.ipynb",
            cell_index=0,
            start_line=1,
            end_line=1,
            code_snippet="# 日本語コメント\nprint('Hello')",
        )
        assert "日本語" in provenance.code_snippet

    def test_very_long_path(self):
        """Test provenance with very long path."""
        long_path = "artifacts/" + "nested/" * 50 + "test.ipynb"
        provenance = CodeProvenance(
            notebook_path=long_path,
            cell_index=0,
            start_line=1,
            end_line=1,
            code_snippet="x = 1",
        )
        assert provenance.notebook_path == long_path

    def test_zero_cell_index(self):
        """Test provenance with cell index 0."""
        provenance = CodeProvenance(
            notebook_path="test.ipynb",
            cell_index=0,
            start_line=1,
            end_line=5,
            code_snippet="x = 1",
        )
        assert provenance.cell_index == 0
        assert "#cell=0" in provenance.to_hyperlink()

    def test_large_line_numbers(self):
        """Test provenance with large line numbers."""
        provenance = CodeProvenance(
            notebook_path="test.ipynb",
            cell_index=50,
            start_line=10000,
            end_line=10050,
            code_snippet="x = 1",
        )
        assert provenance.start_line == 10000
        assert "&line=10000" in provenance.to_hyperlink()

    def test_negative_values_not_validated(self):
        """Test that negative values are not validated (caller responsibility)."""
        # Note: We don't validate negative values - that's the caller's responsibility
        provenance = CodeProvenance(
            notebook_path="test.ipynb",
            cell_index=-1,
            start_line=-1,
            end_line=-1,
            code_snippet="x = 1",
        )
        assert provenance.cell_index == -1


# =============================================================================
# TestIntegrationWithFinding
# =============================================================================


class TestIntegrationWithFinding:
    """Tests for integration with Finding dataclass."""

    def test_provenance_dict_in_finding(self, code_provenance):
        """Test using provenance dict in Finding-like structure."""
        finding_dict = {
            "finding_id": "f001",
            "cycle": 1,
            "task_id": 5,
            "summary": "Test finding",
            "statistics": {"p_value": 0.01},
            "code_provenance": code_provenance.to_dict(),
        }

        # Verify the provenance is properly structured
        prov = finding_dict["code_provenance"]
        assert prov["notebook_path"] == code_provenance.notebook_path
        assert prov["cell_index"] == code_provenance.cell_index

    def test_reconstruct_provenance_from_finding(self, code_provenance):
        """Test reconstructing provenance from finding dict."""
        finding_dict = {
            "finding_id": "f001",
            "code_provenance": code_provenance.to_dict(),
        }

        prov_data = finding_dict["code_provenance"]
        restored = CodeProvenance.from_dict(prov_data)
        assert restored.notebook_path == code_provenance.notebook_path

    def test_hyperlink_from_finding_provenance(self, code_provenance):
        """Test generating hyperlink from finding's provenance."""
        prov_dict = code_provenance.to_dict()

        # Simulate what report generation does
        hyperlink = f"{prov_dict['notebook_path']}#cell={prov_dict['cell_index']}&line={prov_dict['start_line']}"
        assert "task_5_correlation.ipynb" in hyperlink
        assert "#cell=3" in hyperlink
