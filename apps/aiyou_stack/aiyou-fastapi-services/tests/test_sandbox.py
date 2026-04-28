# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for sandbox functionality."""

import pytest

from app.config import SandboxSettings
from app.security.sandbox import CodeSandbox, SandboxExecutor


@pytest.fixture
def sandbox_settings() -> SandboxSettings:
    """Create test sandbox settings."""
    return SandboxSettings(
        enabled=True,
        max_execution_time=5,
        max_memory_mb=256,
        max_cpu_percent=80.0,
        allowed_modules=["math", "json", "datetime"],
        blocked_builtins=["eval", "exec", "compile", "__import__", "open"],
    )


@pytest.fixture
def sandbox(sandbox_settings: SandboxSettings) -> CodeSandbox:
    """Create sandbox instance."""
    return CodeSandbox(sandbox_settings)


@pytest.fixture
def executor(sandbox_settings: SandboxSettings) -> SandboxExecutor:
    """Create executor instance."""
    return SandboxExecutor(sandbox_settings)


def test_sandbox_simple_execution(sandbox: CodeSandbox) -> None:
    """Test simple code execution."""
    code = "print('Hello, World!')"
    result = sandbox.execute(code)

    assert result.success is True
    assert "Hello, World!" in result.output
    assert result.error is None


def test_sandbox_math_operations(sandbox: CodeSandbox) -> None:
    """Test math operations in sandbox."""
    code = """
import math
result = math.sqrt(16) + math.pi
print(f"Result: {result}")
"""
    result = sandbox.execute(code)

    assert result.success is True
    assert "Result:" in result.output
    assert result.error is None


def test_sandbox_blocked_import(sandbox: CodeSandbox) -> None:
    """Test that blocked imports fail."""
    code = "import os"
    result = sandbox.execute(code)

    # Should fail because 'os' is not in allowed_modules
    assert result.success is False


def test_sandbox_timeout(sandbox: CodeSandbox) -> None:
    """Test execution timeout."""
    code = """
while True:
    pass
"""
    result = sandbox.execute(code, timeout=1)

    assert result.success is False
    assert "timeout" in result.error.lower()


def test_sandbox_syntax_error(sandbox: CodeSandbox) -> None:
    """Test handling of syntax errors."""
    code = "print('missing closing quote"
    result = sandbox.execute(code)

    assert result.success is False
    assert result.error is not None


def test_sandbox_runtime_error(sandbox: CodeSandbox) -> None:
    """Test handling of runtime errors."""
    code = """
x = 1 / 0
"""
    result = sandbox.execute(code)

    assert result.success is False
    assert "ZeroDivisionError" in result.error


def test_sandbox_metrics(sandbox: CodeSandbox) -> None:
    """Test that execution metrics are captured."""
    code = """
import math
for i in range(100):
    result = math.sqrt(i)
print("Done")
"""
    result = sandbox.execute(code)

    assert result.success is True
    assert result.execution_time > 0
    assert result.memory_used_mb >= 0


@pytest.mark.asyncio
async def test_executor_async(executor: SandboxExecutor) -> None:
    """Test async execution."""
    code = "print('Async execution test')"
    result = await executor.execute_async(code)

    assert result.success is True
    assert "Async execution test" in result.output


@pytest.mark.asyncio
async def test_executor_stats(executor: SandboxExecutor) -> None:
    """Test executor statistics tracking."""
    # Execute multiple times
    await executor.execute_async("print('test 1')")
    await executor.execute_async("print('test 2')")
    await executor.execute_async("x = 1 / 0")  # This will fail

    stats = executor.get_execution_stats()

    assert stats["total_executions"] == 3
    assert stats["successful_executions"] == 2
    assert stats["failed_executions"] == 1
    assert stats["average_execution_time"] > 0


@pytest.mark.asyncio
async def test_executor_clear_history(executor: SandboxExecutor) -> None:
    """Test clearing execution history."""
    await executor.execute_async("print('test')")

    stats_before = executor.get_execution_stats()
    assert stats_before["total_executions"] > 0

    executor.clear_history()

    stats_after = executor.get_execution_stats()
    assert stats_after["total_executions"] == 0


def test_sandbox_disabled(sandbox_settings: SandboxSettings) -> None:
    """Test sandbox behavior when disabled."""
    sandbox_settings.enabled = False
    sandbox = CodeSandbox(sandbox_settings)

    code = "print('test')"
    result = sandbox.execute(code)

    assert result.success is False
    assert "disabled" in result.error.lower()
