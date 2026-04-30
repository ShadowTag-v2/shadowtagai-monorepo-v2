"""
Integration tests for R language execution.

These tests require R to be installed on the system. They test actual R code
execution, result capture, and statistical analysis functionality.

Run with: pytest tests/integration/test_r_execution.py -v
"""

import subprocess

import pytest

from kosmos.execution.r_executor import RExecutor


def r_available():
    """Check if R is available on the system."""
    try:
        result = subprocess.run(["Rscript", "--version"], capture_output=True, timeout=10)
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


# Skip all tests if R is not available
pytestmark = pytest.mark.skipif(not r_available(), reason="R is not installed")


class TestRExecutorRealExecution:
    """Test real R code execution."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        return RExecutor(use_docker=False, timeout=60)

    def test_simple_print(self, executor):
        """Test simple print statement execution."""
        code = 'print("Hello from R")'
        result = executor.execute(code, capture_results=False)

        assert result.success is True
        assert "Hello from R" in result.stdout
        assert result.exit_code == 0

    def test_arithmetic(self, executor):
        """Test basic arithmetic."""
        code = """
x <- 10
y <- 20
print(x + y)
"""
        result = executor.execute(code, capture_results=False)

        assert result.success is True
        assert "30" in result.stdout

    def test_vector_operations(self, executor):
        """Test vector operations."""
        code = """
x <- c(1, 2, 3, 4, 5)
print(mean(x))
print(sum(x))
print(length(x))
"""
        result = executor.execute(code, capture_results=False)

        assert result.success is True
        assert "3" in result.stdout  # mean
        assert "15" in result.stdout  # sum
        assert "5" in result.stdout  # length

    def test_dataframe_creation(self, executor):
        """Test data.frame creation and manipulation."""
        code = """
df <- data.frame(
    name = c("Alice", "Bob", "Charlie"),
    age = c(25, 30, 35),
    score = c(85.5, 90.0, 78.5)
)
print(df)
print(nrow(df))
print(mean(df$score))
"""
        result = executor.execute(code, capture_results=False)

        assert result.success is True
        assert "Alice" in result.stdout
        assert "3" in result.stdout  # nrow

    def test_statistical_analysis(self, executor):
        """Test basic statistical analysis."""
        code = """
# Generate sample data
set.seed(42)
group_a <- rnorm(30, mean=10, sd=2)
group_b <- rnorm(30, mean=12, sd=2)

# Perform t-test
result <- t.test(group_a, group_b)
print(result)
print(paste("p-value:", result$p.value))
"""
        result = executor.execute(code, capture_results=False)

        assert result.success is True
        assert "t.test" in result.stdout or "t =" in result.stdout
        assert "p-value" in result.stdout

    def test_correlation_analysis(self, executor):
        """Test correlation analysis."""
        code = """
set.seed(42)
x <- 1:100
y <- 2*x + rnorm(100, 0, 10)

# Pearson correlation
cor_result <- cor.test(x, y)
print(cor_result)
"""
        result = executor.execute(code, capture_results=False)

        assert result.success is True
        # Should find significant positive correlation
        assert "cor" in result.stdout.lower()

    def test_linear_regression(self, executor):
        """Test linear regression."""
        code = """
set.seed(42)
x <- 1:50
y <- 3*x + 5 + rnorm(50, 0, 5)

model <- lm(y ~ x)
summary(model)
"""
        result = executor.execute(code, capture_results=False)

        assert result.success is True
        assert "Coefficients" in result.stdout
        assert "R-squared" in result.stdout

    def test_error_handling(self, executor):
        """Test that R errors are captured properly."""
        code = "print(undefined_variable)"
        result = executor.execute(code, capture_results=False)

        assert result.success is False
        # Error should be captured
        assert result.error is not None or "not found" in result.stderr.lower()


class TestRResultCapture:
    """Test R result capture with JSON."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        return RExecutor(use_docker=False, timeout=60)

    def test_capture_scalar_result(self, executor):
        """Test capturing a scalar result."""
        code = """
result <- 42
kosmos_capture("answer", result)
"""
        result = executor.execute(code, capture_results=True)

        assert result.success is True
        assert "answer" in result.parsed_results
        assert result.parsed_results["answer"] == 42

    def test_capture_vector_result(self, executor):
        """Test capturing a vector result."""
        code = """
values <- c(1, 2, 3, 4, 5)
kosmos_capture("values", values)
kosmos_capture("mean", mean(values))
"""
        result = executor.execute(code, capture_results=True)

        assert result.success is True
        assert "values" in result.parsed_results
        assert result.parsed_results["mean"] == 3

    def test_capture_dataframe_result(self, executor):
        """Test capturing a data.frame result."""
        code = """
df <- data.frame(
    x = c(1, 2, 3),
    y = c(4, 5, 6)
)
kosmos_capture("data", df)
"""
        result = executor.execute(code, capture_results=True)

        assert result.success is True
        assert "data" in result.parsed_results

    def test_capture_statistical_result(self, executor):
        """Test capturing statistical test results."""
        code = """
set.seed(42)
x <- rnorm(30, mean=10, sd=2)
y <- rnorm(30, mean=12, sd=2)

test_result <- t.test(x, y)

kosmos_capture("t_statistic", test_result$statistic)
kosmos_capture("p_value", test_result$p.value)
kosmos_capture("conf_int", test_result$conf.int)
"""
        result = executor.execute(code, capture_results=True)

        assert result.success is True
        assert "t_statistic" in result.parsed_results
        assert "p_value" in result.parsed_results
        # P-value should be small since means are different
        assert result.parsed_results["p_value"] < 0.05


class TestROutputFiles:
    """Test R output file generation."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        return RExecutor(use_docker=False, timeout=60)

    def test_generate_csv(self, executor, tmp_path):
        """Test generating CSV output."""
        code = f'''
df <- data.frame(
    id = 1:5,
    value = c(10, 20, 30, 40, 50)
)
write.csv(df, "{tmp_path}/output.csv", row.names=FALSE)
'''
        result = executor.execute(code, capture_results=False, output_dir=str(tmp_path))

        assert result.success is True
        assert (tmp_path / "output.csv").exists()

        # Verify CSV content
        import pandas as pd

        df = pd.read_csv(tmp_path / "output.csv")
        assert len(df) == 5
        assert list(df.columns) == ["id", "value"]

    def test_generate_plot(self, executor, tmp_path):
        """Test generating plot output."""
        code = f'''
png("{tmp_path}/plot.png", width=800, height=600)
plot(1:10, (1:10)^2, main="Test Plot", xlab="X", ylab="Y")
dev.off()
'''
        result = executor.execute(code, capture_results=False, output_dir=str(tmp_path))

        assert result.success is True
        assert (tmp_path / "plot.png").exists()
        # Verify it's a valid image (non-empty)
        assert (tmp_path / "plot.png").stat().st_size > 0


class TestRPackages:
    """Test R package functionality."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        return RExecutor(use_docker=False, timeout=120)

    def test_base_packages(self, executor):
        """Test that base R packages work."""
        code = """
library(stats)
library(utils)
library(methods)

# Test stats functions
result <- cor(1:10, 1:10)
print(result)
"""
        result = executor.execute(code, capture_results=False)

        assert result.success is True
        assert "1" in result.stdout  # Perfect correlation

    def test_survival_analysis(self, executor):
        """Test survival package if available."""
        code = """
if (require(survival, quietly=TRUE)) {
    # Simple survival example
    fit <- survfit(Surv(time, status) ~ 1, data=lung)
    print(summary(fit))
    cat("survival_available: TRUE\\n")
} else {
    cat("survival_available: FALSE\\n")
}
"""
        result = executor.execute(code, capture_results=False)

        assert result.success is True
        # Test passes whether survival is installed or not

    def test_mass_package(self, executor):
        """Test MASS package if available."""
        code = """
if (require(MASS, quietly=TRUE)) {
    # Test robust regression
    set.seed(42)
    x <- 1:50
    y <- 2*x + rnorm(50)
    fit <- rlm(y ~ x)
    print(coef(fit))
    cat("mass_available: TRUE\\n")
} else {
    cat("mass_available: FALSE\\n")
}
"""
        result = executor.execute(code, capture_results=False)

        assert result.success is True


class TestCodeExecutorRIntegration:
    """Test R integration through main CodeExecutor."""

    def test_auto_detect_r_code(self):
        """Test that CodeExecutor auto-detects R code."""
        from kosmos.execution.executor import CodeExecutor

        executor = CodeExecutor()

        if not executor.is_r_available():
            pytest.skip("R not available")

        r_code = """
library(stats)
x <- c(1, 2, 3, 4, 5)
print(mean(x))
"""
        result = executor.execute(r_code)

        assert result.success is True
        assert "3" in result.stdout

    def test_explicit_r_execution(self):
        """Test explicit R execution method."""
        from kosmos.execution.executor import CodeExecutor

        executor = CodeExecutor()

        if not executor.is_r_available():
            pytest.skip("R not available")

        r_code = "print(42)"
        result = executor.execute_r(r_code)

        assert result.success is True
        assert "42" in result.stdout

    def test_r_version_check(self):
        """Test R version retrieval."""
        from kosmos.execution.executor import CodeExecutor

        executor = CodeExecutor()

        if not executor.is_r_available():
            pytest.skip("R not available")

        version = executor.get_r_version()

        assert version is not None
        # Should be a version string like "4.3.1"
        assert "." in version


class TestStatisticalGeneticsWorkflow:
    """Test statistical genetics workflows (Mendelian Randomization)."""

    @pytest.fixture
    def executor(self):
        """Create executor for testing."""
        return RExecutor(use_docker=False, timeout=180)

    def test_basic_mr_workflow(self, executor):
        """Test basic MR-style analysis without TwoSampleMR package."""
        # This test works even without TwoSampleMR installed
        code = """
# Simulate Mendelian Randomization data
set.seed(42)
n <- 1000

# Genetic instrument (SNP)
g <- rbinom(n, 2, 0.3)

# Exposure affected by genotype
x <- 0.5 * g + rnorm(n)

# Outcome affected by exposure (causal effect = 0.3)
y <- 0.3 * x + rnorm(n)

# Two-stage least squares (simple MR)
# First stage: regress exposure on instrument
first_stage <- lm(x ~ g)
x_predicted <- fitted(first_stage)

# Second stage: regress outcome on predicted exposure
second_stage <- lm(y ~ x_predicted)

# Get causal estimate
causal_estimate <- coef(second_stage)[2]
se <- summary(second_stage)$coefficients[2, 2]

cat("Causal estimate:", causal_estimate, "\\n")
cat("Standard error:", se, "\\n")
cat("95% CI: [", causal_estimate - 1.96*se, ",", causal_estimate + 1.96*se, "]\\n")
"""
        result = executor.execute(code, capture_results=False)

        assert result.success is True
        assert "Causal estimate" in result.stdout

    def test_twosamplemr_if_available(self, executor):
        """Test TwoSampleMR package if installed."""
        code = """
if (require(TwoSampleMR, quietly=TRUE)) {
    cat("TwoSampleMR version:", packageVersion("TwoSampleMR"), "\\n")
    cat("twosamplemr_available: TRUE\\n")
} else {
    cat("twosamplemr_available: FALSE\\n")
    cat("Install with: remotes::install_github('MRCIEU/TwoSampleMR')\\n")
}
"""
        result = executor.execute(code, capture_results=False)

        assert result.success is True
        # Test passes whether package is installed or not
