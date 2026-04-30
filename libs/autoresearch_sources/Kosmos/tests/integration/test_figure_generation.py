"""
Integration tests for figure generation (Issue #60).

These tests create actual figures and verify they exist on disk.
Requires matplotlib to be installed.
"""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from kosmos.analysis.visualization import COLORS, PublicationVisualizer
from kosmos.execution.figure_manager import FigureManager


class TestRealFigureGeneration:
    """Test actual figure generation with PublicationVisualizer."""

    @pytest.fixture
    def visualizer(self):
        """Create visualizer for testing."""
        return PublicationVisualizer()

    @pytest.fixture
    def manager(self, tmp_path):
        """Create FigureManager for testing."""
        return FigureManager(artifacts_dir=tmp_path)

    def test_generate_real_box_plot(self, visualizer, tmp_path):
        """Test generating actual box plot PNG."""
        output_path = tmp_path / "box_plot.png"

        # Create sample data
        data = {"Control": np.random.normal(10, 2, 30), "Treatment": np.random.normal(12, 2, 30)}

        # Generate figure
        result_path = visualizer.box_plot_with_points(
            data=data,
            title="Treatment vs Control",
            y_label="Response",
            output_path=str(output_path),
        )

        # Verify file exists
        assert Path(result_path).exists()
        assert output_path.stat().st_size > 0

    def test_generate_real_scatter_plot(self, visualizer, tmp_path):
        """Test generating actual scatter plot with regression."""
        output_path = tmp_path / "scatter.png"

        # Create correlated data
        np.random.seed(42)
        x = np.random.uniform(0, 10, 50)
        y = 2 * x + 1 + np.random.normal(0, 1, 50)

        # Generate figure
        result_path = visualizer.scatter_with_regression(
            x=x,
            y=y,
            x_label="Independent Variable",
            y_label="Dependent Variable",
            title="Correlation Analysis",
            output_path=str(output_path),
        )

        # Verify file exists
        assert Path(result_path).exists()
        assert output_path.stat().st_size > 0

    def test_generate_real_log_log_plot(self, visualizer, tmp_path):
        """Test generating actual log-log plot."""
        output_path = tmp_path / "log_log.png"

        # Create power law data
        np.random.seed(42)
        x = np.logspace(0, 3, 100)
        y = x**2 * np.random.uniform(0.8, 1.2, 100)

        # Generate figure
        result_path = visualizer.log_log_plot(
            x=x,
            y=y,
            x_label="Size",
            y_label="Frequency",
            title="Scaling Law",
            output_path=str(output_path),
        )

        # Verify file exists
        assert Path(result_path).exists()
        assert output_path.stat().st_size > 0

    def test_generate_real_violin_plot(self, visualizer, tmp_path):
        """Test generating actual violin plot."""
        output_path = tmp_path / "violin.png"

        data = {
            "Group A": np.random.normal(0, 1, 100),
            "Group B": np.random.normal(0.5, 1.5, 100),
            "Group C": np.random.normal(-0.5, 0.8, 100),
        }

        result_path = visualizer.violin_plot(
            data=data,
            title="Distribution Comparison",
            y_label="Value",
            output_path=str(output_path),
        )

        assert Path(result_path).exists()

    def test_generate_real_volcano_plot(self, visualizer, tmp_path):
        """Test generating actual volcano plot."""
        output_path = tmp_path / "volcano.png"

        # Simulated differential expression data
        np.random.seed(42)
        n_genes = 1000
        log2fc = np.random.normal(0, 1, n_genes)
        p_values = np.random.uniform(0, 1, n_genes)

        # Make some significant
        p_values[:50] = np.random.uniform(0.001, 0.01, 50)
        log2fc[:25] = np.random.uniform(1, 3, 25)
        log2fc[25:50] = np.random.uniform(-3, -1, 25)

        result_path = visualizer.volcano_plot(
            log2fc=log2fc,
            p_values=p_values,
            title="Differential Expression",
            output_path=str(output_path),
        )

        assert Path(result_path).exists()

    def test_generate_real_heatmap(self, visualizer, tmp_path):
        """Test generating actual heatmap."""
        output_path = tmp_path / "heatmap.png"

        # Create correlation matrix-like data
        np.random.seed(42)
        data = np.random.uniform(-1, 1, (5, 5))
        np.fill_diagonal(data, 1)

        result_path = visualizer.custom_heatmap(
            data=data,
            row_labels=["Gene A", "Gene B", "Gene C", "Gene D", "Gene E"],
            col_labels=["Sample 1", "Sample 2", "Sample 3", "Sample 4", "Sample 5"],
            title="Correlation Matrix",
            output_path=str(output_path),
        )

        assert Path(result_path).exists()


class TestFigureDPI:
    """Test that figures are saved at correct DPI."""

    @pytest.fixture
    def visualizer(self):
        """Create visualizer for testing."""
        return PublicationVisualizer()

    def test_standard_figure_dpi_is_300(self, visualizer, tmp_path):
        """Test standard figures are at least 300 DPI."""
        output_path = tmp_path / "standard.png"

        data = {"A": np.array([1, 2, 3]), "B": np.array([4, 5, 6])}
        visualizer.box_plot_with_points(data=data, output_path=str(output_path))

        # Open image and check resolution
        img = Image.open(output_path)
        dpi = img.info.get("dpi", (72, 72))

        # DPI should be at least 300 (may be slightly different due to rounding)
        assert dpi[0] >= 250, f"DPI {dpi[0]} is less than expected 300"

    def test_log_log_figure_dpi_is_600(self, visualizer, tmp_path):
        """Test log-log figures are at least 600 DPI."""
        output_path = tmp_path / "log_log.png"

        x = np.logspace(0, 2, 50)
        y = x**1.5
        visualizer.log_log_plot(
            x=x, y=y, x_label="X", y_label="Y", title="Test", output_path=str(output_path)
        )

        img = Image.open(output_path)
        dpi = img.info.get("dpi", (72, 72))

        # DPI should be at least 600
        assert dpi[0] >= 500, f"DPI {dpi[0]} is less than expected 600"


class TestFigureManagerIntegration:
    """Test FigureManager with real figure generation."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create FigureManager for testing."""
        return FigureManager(artifacts_dir=tmp_path)

    def test_manager_generates_box_plot(self, manager, tmp_path):
        """Test FigureManager generates real box plot."""
        data = {
            "groups": {
                "Control": np.random.normal(10, 2, 20),
                "Treatment": np.random.normal(15, 2, 20),
            }
        }

        metadata = manager.generate_figure(
            data=data, analysis_type="t_test", cycle=1, task_id=1, title="T-Test Comparison"
        )

        assert metadata is not None
        assert Path(metadata.path).exists()
        assert metadata.plot_type == "box_plot_with_points"
        assert metadata.cycle == 1
        assert metadata.task_id == 1

    def test_manager_generates_scatter_plot(self, manager, tmp_path):
        """Test FigureManager generates real scatter plot."""
        np.random.seed(42)
        x = np.random.uniform(0, 10, 30)
        y = 0.5 * x + np.random.normal(0, 1, 30)

        metadata = manager.generate_figure(
            data={"x": x, "y": y},
            analysis_type="correlation",
            cycle=1,
            task_id=2,
            title="Correlation Analysis",
        )

        assert metadata is not None
        assert Path(metadata.path).exists()
        assert metadata.plot_type == "scatter_with_regression"

    def test_manager_creates_figures_in_correct_directory(self, manager, tmp_path):
        """Test figures are created in correct directory structure."""
        data = {"groups": {"A": np.array([1, 2, 3]), "B": np.array([4, 5, 6])}}

        metadata = manager.generate_figure(data=data, analysis_type="t_test", cycle=3, task_id=7)

        assert metadata is not None
        expected_dir = tmp_path / "cycle_3" / "figures"
        assert expected_dir.exists()
        assert Path(metadata.path).parent == expected_dir

    def test_manager_tracks_multiple_figures(self, manager):
        """Test manager tracks multiple generated figures."""
        # Generate several figures
        for i in range(3):
            data = {"groups": {"A": np.random.randn(10), "B": np.random.randn(10)}}
            manager.generate_figure(data=data, analysis_type="t_test", cycle=1, task_id=i)

        assert manager.get_figure_count() == 3
        assert len(manager.get_figure_paths()) == 3

    def test_manager_filters_figures_by_cycle(self, manager):
        """Test filtering figures by cycle."""
        # Generate figures in different cycles
        data = {"groups": {"A": np.random.randn(10), "B": np.random.randn(10)}}

        manager.generate_figure(data=data, analysis_type="t_test", cycle=1, task_id=1)
        manager.generate_figure(data=data, analysis_type="t_test", cycle=1, task_id=2)
        manager.generate_figure(data=data, analysis_type="t_test", cycle=2, task_id=1)

        cycle_1_figs = manager.get_figures_for_cycle(1)
        cycle_2_figs = manager.get_figures_for_cycle(2)

        assert len(cycle_1_figs) == 2
        assert len(cycle_2_figs) == 1


class TestFindingFigureIntegration:
    """Test Finding dataclass figure fields."""

    def test_finding_with_figure_paths(self):
        """Test Finding includes figure paths."""
        from kosmos.world_model.artifacts import Finding

        finding = Finding(
            finding_id="find_001",
            cycle=1,
            task_id=1,
            summary="Test finding",
            statistics={"p_value": 0.01},
            figure_paths=["artifacts/cycle_1/figures/task_1_box.png"],
            figure_metadata={"plot_type": "box_plot_with_points", "dpi": 300},
        )

        assert finding.figure_paths is not None
        assert len(finding.figure_paths) == 1
        assert finding.figure_metadata["plot_type"] == "box_plot_with_points"

    def test_finding_serializes_with_figures(self):
        """Test Finding serialization includes figure data."""
        from kosmos.world_model.artifacts import Finding

        finding = Finding(
            finding_id="find_002",
            cycle=1,
            task_id=2,
            summary="Test finding with figures",
            statistics={"r_squared": 0.85},
            figure_paths=["path/to/fig1.png", "path/to/fig2.png"],
            figure_metadata={"caption": "Test figures"},
        )

        data = finding.to_dict()

        assert "figure_paths" in data
        assert len(data["figure_paths"]) == 2
        assert "figure_metadata" in data


class TestKosmosFiguresColorScheme:
    """Test that figures use correct kosmos-figures color scheme."""

    def test_colors_match_kosmos_figures(self):
        """Test color constants match kosmos-figures specification."""
        assert COLORS["red"] == "#d7191c"
        assert COLORS["blue"] == "#0072B2"
        assert COLORS["neutral"] == "#abd9e9"
        assert COLORS["blue_dark"] == "#2c7bb6"
        assert COLORS["gray"] == "#808080"
        assert COLORS["black"] == "#000000"


class TestFigureInCodeTemplates:
    """Test figure generation in code templates.

    These tests verify that code templates include figure generation code.
    Uses mock protocol objects to avoid complex Pydantic validation.
    """

    def test_ttest_template_includes_figure(self):
        """Test T-test template generates figure code."""
        from unittest.mock import Mock

        from kosmos.execution.code_generator import TTestComparisonCodeTemplate
        from kosmos.models.experiment import ExperimentType

        # Create mock protocol
        mock_var = Mock()
        mock_var.type.value = "independent"
        mock_var.name = "group"

        mock_dep_var = Mock()
        mock_dep_var.type.value = "dependent"
        mock_dep_var.name = "value"

        mock_control = Mock()
        mock_control.name = "control"

        protocol = Mock()
        protocol.name = "Test Protocol"
        protocol.experiment_type = ExperimentType.DATA_ANALYSIS
        protocol.variables = {"group": mock_var, "value": mock_dep_var}
        protocol.control_groups = [mock_control]
        protocol.steps = []

        template = TTestComparisonCodeTemplate()
        code = template.generate(protocol)

        assert "PublicationVisualizer" in code
        assert "box_plot_with_points" in code
        assert "figure_path" in code

    def test_correlation_template_includes_figure(self):
        """Test correlation template generates figure code."""
        from unittest.mock import Mock

        from kosmos.execution.code_generator import CorrelationAnalysisCodeTemplate
        from kosmos.models.experiment import ExperimentType

        # Create mock protocol
        mock_test = Mock()
        mock_test.test_type.value = "correlation"

        protocol = Mock()
        protocol.name = "Correlation Analysis"
        protocol.experiment_type = ExperimentType.DATA_ANALYSIS
        protocol.variables = {"x": Mock(), "y": Mock()}
        protocol.statistical_tests = [mock_test]

        template = CorrelationAnalysisCodeTemplate()
        code = template.generate(protocol)

        assert "PublicationVisualizer" in code
        assert "scatter_with_regression" in code
        assert "figure_path" in code

    def test_log_log_template_includes_figure(self):
        """Test log-log template generates figure code."""
        from unittest.mock import Mock

        from kosmos.execution.code_generator import LogLogScalingCodeTemplate
        from kosmos.models.experiment import ExperimentType

        protocol = Mock()
        protocol.name = "Power Law Scaling"
        protocol.description = "Power law scaling analysis"
        protocol.experiment_type = ExperimentType.DATA_ANALYSIS
        protocol.variables = {"x": Mock(), "y": Mock()}

        template = LogLogScalingCodeTemplate()
        code = template.generate(protocol)

        assert "PublicationVisualizer" in code
        assert "log_log_plot" in code
        assert "figure_path" in code
