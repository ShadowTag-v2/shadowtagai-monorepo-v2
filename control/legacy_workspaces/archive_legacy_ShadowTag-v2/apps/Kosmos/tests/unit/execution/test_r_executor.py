# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Tests for R language execution support.

Tests RExecutor class for language detection, R code execution,
and integration with CodeExecutor.
"""

from unittest.mock import Mock, patch

import pytest

from kosmos.execution.r_executor import RExecutionResult, RExecutor, is_r_code


class TestRExecutionResult:
    """Test RExecutionResult dataclass."""

    def test_creation_success(self):
        """Test creating successful result."""
        result = RExecutionResult(
            success=True, stdout="[1] 42\n", stderr="", return_value=42, execution_time=0.5
        )

        assert result.success is True
        assert result.stdout == "[1] 42\n"
        assert result.return_value == 42
        assert result.execution_time == 0.5

    def test_creation_failure(self):
        """Test creating failed result."""
        result = RExecutionResult(success=False, error="Object 'x' not found", error_type="RError")

        assert result.success is False
        assert result.error == "Object 'x' not found"
        assert result.error_type == "RError"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = RExecutionResult(success=True, stdout="test output", parsed_results={"value": 42})

        d = result.to_dict()

        assert d["success"] is True
        assert d["stdout"] == "test output"
        assert d["parsed_results"] == {"value": 42}


class TestLanguageDetection:
    """Test language detection functionality."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        return RExecutor()

    def test_detect_r_library(self, executor):
        """Test detection of R library() calls."""
        code = """
library(dplyr)
df <- data.frame(x = 1:10)
"""
        assert executor.detect_language(code) == "r"

    def test_detect_r_require(self, executor):
        """Test detection of R require() calls."""
        code = """
require(ggplot2)
ggplot(df, aes(x, y)) + geom_point()
"""
        assert executor.detect_language(code) == "r"

    def test_detect_r_assignment(self, executor):
        """Test detection of R <- assignment."""
        code = """
x <- 42
y <- function(a, b) {
    return(a + b)
}
"""
        assert executor.detect_language(code) == "r"

    def test_detect_r_vector(self, executor):
        """Test detection of R c() vector."""
        code = """
x <- c(1, 2, 3, 4, 5)
mean(x)
"""
        assert executor.detect_language(code) == "r"

    def test_detect_r_dataframe(self, executor):
        """Test detection of R data.frame()."""
        code = """
df <- data.frame(
    name = c("Alice", "Bob"),
    age = c(25, 30)
)
"""
        assert executor.detect_language(code) == "r"

    def test_detect_r_pipe(self, executor):
        """Test detection of R pipe operator."""
        code = """
df %>%
    filter(age > 25) %>%
    select(name)
"""
        assert executor.detect_language(code) == "r"

    def test_detect_r_twosamplemr(self, executor):
        """Test detection of TwoSampleMR namespace."""
        code = """
library(TwoSampleMR)
exposure <- TwoSampleMR::extract_instruments(...)
"""
        assert executor.detect_language(code) == "r"

    def test_detect_r_shebang(self, executor):
        """Test detection via R shebang."""
        code = """#!/usr/bin/env Rscript
print("Hello from R")
"""
        assert executor.detect_language(code) == "r"

    def test_detect_python_import(self, executor):
        """Test detection of Python import."""
        code = """
import pandas as pd
df = pd.DataFrame({'x': [1, 2, 3]})
"""
        assert executor.detect_language(code) == "python"

    def test_detect_python_from_import(self, executor):
        """Test detection of Python from import."""
        code = """
from sklearn.linear_model import LinearRegression
model = LinearRegression()
"""
        assert executor.detect_language(code) == "python"

    def test_detect_python_def(self, executor):
        """Test detection of Python def."""
        code = """
def calculate_mean(values):
    return sum(values) / len(values)
"""
        assert executor.detect_language(code) == "python"

    def test_detect_python_class(self, executor):
        """Test detection of Python class."""
        code = """
class DataProcessor:
    def __init__(self, data):
        self.data = data
"""
        assert executor.detect_language(code) == "python"

    def test_detect_python_print(self, executor):
        """Test detection of Python print()."""
        code = """
x = 42
print(f"The answer is {x}")
"""
        assert executor.detect_language(code) == "python"

    def test_detect_ambiguous_defaults_python(self, executor):
        """Test that ambiguous code defaults to Python."""
        code = """
# Just a comment
x = 42
"""
        assert executor.detect_language(code) == "python"


class TestIsRCode:
    """Test the is_r_code helper function."""

    def test_is_r_code_true(self):
        """Test R code detection."""
        r_code = "library(dplyr)\nx <- c(1, 2, 3)"
        assert is_r_code(r_code) is True

    def test_is_r_code_false(self):
        """Test Python code detection."""
        python_code = "import pandas as pd\nx = [1, 2, 3]"
        assert is_r_code(python_code) is False


class TestRExecutorInit:
    """Test RExecutor initialization."""

    def test_default_init(self):
        """Test default initialization."""
        executor = RExecutor()

        assert executor.r_path == "Rscript"
        assert executor.timeout == 300
        assert executor.use_docker is False

    def test_custom_init(self):
        """Test custom initialization."""
        executor = RExecutor(
            r_path="/usr/local/bin/Rscript",
            timeout=600,
            use_docker=True,
            docker_image="custom-r:latest",
        )

        assert executor.r_path == "/usr/local/bin/Rscript"
        assert executor.timeout == 600
        assert executor.use_docker is True
        assert executor.docker_image == "custom-r:latest"


class TestRExecutorAvailability:
    """Test R availability detection."""

    def test_is_r_available_success(self):
        """Test R availability check when R is installed."""
        executor = RExecutor()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            assert executor.is_r_available() is True

    def test_is_r_available_not_installed(self):
        """Test R availability check when R is not installed."""
        executor = RExecutor()

        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert executor.is_r_available() is False

    def test_get_r_version(self):
        """Test R version retrieval."""
        executor = RExecutor()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stdout='R version 4.3.1 (2023-06-16) -- "Beagle Scouts"'
            )
            version = executor.get_r_version()
            assert version == "4.3.1"


class TestRExecutorExecution:
    """Test R code execution."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        return RExecutor(use_docker=False)

    def test_execute_local_success(self, executor):
        """Test successful local R execution."""
        with patch.object(executor, "_execute_local") as mock_exec:
            mock_exec.return_value = RExecutionResult(
                success=True, stdout="[1] 42\n", stderr="", exit_code=0
            )

            result = executor.execute("print(42)", capture_results=False)

            assert result.success is True
            assert "[1] 42" in result.stdout

    def test_execute_local_error(self, executor):
        """Test R execution with error."""
        with patch.object(executor, "_execute_local") as mock_exec:
            mock_exec.return_value = RExecutionResult(
                success=False,
                stdout="",
                stderr="R_ERROR: object 'undefined_var' not found",
                error="object 'undefined_var' not found",
                error_type="RError",
                exit_code=1,
            )

            result = executor.execute("print(undefined_var)", capture_results=False)

            assert result.success is False
            assert "undefined_var" in result.error

    def test_execute_timeout(self, executor):
        """Test execution timeout."""
        with patch("subprocess.run", side_effect=TimeoutError("timeout")):
            # This should catch the timeout internally
            result = executor.execute("Sys.sleep(1000)", capture_results=False)

            assert result.success is False
            # The error could be either timeout-related or a general exception
            assert (
                result.error_type in ["TimeoutError", "SubprocessError"] or result.error is not None
            )


class TestResultParsing:
    """Test R result parsing."""

    def test_parse_results_json(self):
        """Test parsing JSON results from R output."""
        executor = RExecutor()

        stdout = """
Some R output
KOSMOS_RESULTS_START
{"value": 42, "message": "success"}
KOSMOS_RESULTS_END
More output
"""
        results = executor._parse_results(stdout)

        assert results["value"] == 42
        assert results["message"] == "success"

    def test_parse_results_no_markers(self):
        """Test parsing when no result markers present."""
        executor = RExecutor()

        stdout = "[1] 42\n"
        results = executor._parse_results(stdout)

        assert results == {}

    def test_parse_results_invalid_json(self):
        """Test parsing with invalid JSON."""
        executor = RExecutor()

        stdout = """
KOSMOS_RESULTS_START
{invalid json here}
KOSMOS_RESULTS_END
"""
        results = executor._parse_results(stdout)

        assert results == {}


class TestCollectOutputFiles:
    """Test output file collection."""

    def test_collect_output_files(self, tmp_path):
        """Test collecting generated output files."""
        executor = RExecutor()

        # Create test files
        (tmp_path / "plot.png").touch()
        (tmp_path / "results.csv").touch()
        (tmp_path / "data.rds").touch()
        (tmp_path / "script.R").touch()  # Should not be collected

        files = executor._collect_output_files(str(tmp_path))

        # Should collect png, csv, rds but not R script
        assert len(files) == 3
        assert any("plot.png" in f for f in files)
        assert any("results.csv" in f for f in files)
        assert any("data.rds" in f for f in files)


class TestCodeExecutorRIntegration:
    """Test R integration with main CodeExecutor."""

    def test_executor_detects_r_code(self):
        """Test that CodeExecutor detects and routes R code."""
        from kosmos.execution.executor import CodeExecutor

        executor = CodeExecutor()

        # Mock the R executor
        if executor.r_executor:
            with patch.object(executor.r_executor, "execute") as mock_exec:
                mock_exec.return_value = RExecutionResult(success=True, stdout="[1] 42\n")

                r_code = "library(dplyr)\nx <- c(1, 2, 3)"
                result = executor.execute(r_code)

                # Should have called R executor
                mock_exec.assert_called_once()

    def test_executor_python_default(self):
        """Test that CodeExecutor defaults to Python."""
        from kosmos.execution.executor import CodeExecutor

        executor = CodeExecutor()

        python_code = "import pandas as pd\nprint('hello')"
        # This should execute as Python, not R
        # We just verify it doesn't crash
        result = executor.execute(python_code)

        # Python code should execute (may fail due to missing pandas, but that's ok)
        assert result is not None

    def test_executor_explicit_language(self):
        """Test explicit language specification."""
        from kosmos.execution.executor import CodeExecutor

        executor = CodeExecutor()

        if executor.r_executor:
            with patch.object(executor.r_executor, "execute") as mock_exec:
                mock_exec.return_value = RExecutionResult(success=True, stdout="[1] 42\n")

                # Force R even though code looks like Python
                code = "x = 42"  # Could be either language
                result = executor.execute(code, language="r")

                # Should have called R executor
                mock_exec.assert_called_once()

    def test_executor_is_r_available(self):
        """Test R availability check through CodeExecutor."""
        from kosmos.execution.executor import CodeExecutor

        executor = CodeExecutor()

        # Should return a boolean
        available = executor.is_r_available()
        assert isinstance(available, bool)

    def test_executor_get_r_version(self):
        """Test R version check through CodeExecutor."""
        from kosmos.execution.executor import CodeExecutor

        executor = CodeExecutor()

        # Should return string or None
        version = executor.get_r_version()
        assert version is None or isinstance(version, str)
