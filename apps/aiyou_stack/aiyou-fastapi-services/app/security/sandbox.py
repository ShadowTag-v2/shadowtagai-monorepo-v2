# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Code sandboxing implementation for secure code execution."""

import asyncio
import multiprocessing
import resource
import sys
import time
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from io import StringIO
from typing import Any

import psutil
from RestrictedPython import compile_restricted
from RestrictedPython.Guards import guarded_iter_unpack_sequence, safer_getattr

from app.config import SandboxSettings


@dataclass
class ExecutionResult:
    """Result of code execution."""

    success: bool
    output: str
    error: str | None = None
    execution_time: float = 0.0
    memory_used_mb: float = 0.0
    cpu_percent: float = 0.0


class ResourceLimiter:
    """Manage resource limits for code execution."""

    def __init__(self, settings: SandboxSettings):
        self.settings = settings

    @contextmanager
    def limit_resources(self) -> Any:
        """Context manager to limit CPU and memory resources."""
        # Set soft and hard limits for CPU time
        cpu_time_limit = self.settings.max_execution_time

        try:
            # Set memory limit (virtual memory)
            memory_limit = self.settings.max_memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

            # Set CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_time_limit, cpu_time_limit))

            yield
        finally:
            # Reset limits
            try:
                resource.setrlimit(resource.RLIMIT_AS, (-1, -1))
                resource.setrlimit(resource.RLIMIT_CPU, (-1, -1))
            except Exception:
                pass


class CodeSandbox:
    """Sandbox for executing Python code safely."""

    def __init__(self, settings: SandboxSettings):
        self.settings = settings
        self.resource_limiter = ResourceLimiter(settings)

    def _create_safe_globals(self) -> dict[str, Any]:
        """Create a safe global namespace for code execution."""
        safe_builtins = {
            name: getattr(__builtins__, name)
            for name in dir(__builtins__)
            if name not in self.settings.blocked_builtins
        }

        globals_dict = {
            "__builtins__": safe_builtins,
            "_getattr_": safer_getattr,
            "_iter_unpack_sequence_": guarded_iter_unpack_sequence,
            "_print_": lambda *args, **kwargs: print(*args, **kwargs),
        }

        # Add allowed modules
        for module_name in self.settings.allowed_modules:
            with suppress(ImportError):
                globals_dict[module_name] = __import__(module_name)

        return globals_dict

    def _execute_with_timeout(self, code: str, timeout: int) -> ExecutionResult:
        """Execute code with timeout in a separate process."""

        def target(queue: multiprocessing.Queue, code_str: str) -> None:
            """Target function for multiprocessing."""
            try:
                # Capture stdout
                old_stdout = sys.stdout
                sys.stdout = StringIO()

                start_time = time.time()
                process = psutil.Process()

                # Compile restricted code
                byte_code = compile_restricted(code_str, filename="<sandboxed>", mode="exec")

                if byte_code.errors:
                    queue.put(
                        ExecutionResult(
                            success=False,
                            output="",
                            error="\n".join(byte_code.errors),
                        ),
                    )
                    return

                # Execute in safe environment
                safe_globals_dict = self._create_safe_globals()
                exec(byte_code.code, safe_globals_dict)

                # Capture metrics
                execution_time = time.time() - start_time
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)
                cpu_percent = process.cpu_percent()

                output = sys.stdout.getvalue()
                sys.stdout = old_stdout

                queue.put(
                    ExecutionResult(
                        success=True,
                        output=output,
                        execution_time=execution_time,
                        memory_used_mb=memory_mb,
                        cpu_percent=cpu_percent,
                    ),
                )

            except Exception as e:
                queue.put(
                    ExecutionResult(
                        success=False,
                        output="",
                        error=f"{type(e).__name__}: {e!s}",
                    ),
                )
            finally:
                sys.stdout = old_stdout

        queue: multiprocessing.Queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=target, args=(queue, code))

        process.start()
        process.join(timeout=timeout)

        if process.is_alive():
            process.terminate()
            process.join()
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution timed out after {timeout} seconds",
            )

        if not queue.empty():
            return queue.get()

        return ExecutionResult(
            success=False,
            output="",
            error="Execution failed without error message",
        )

    def execute(
        self,
        code: str,
        timeout: int | None = None,
    ) -> ExecutionResult:
        """Execute Python code in a sandboxed environment.

        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds (uses config default if None)

        Returns:
            ExecutionResult containing output and execution metrics

        """
        if not self.settings.enabled:
            return ExecutionResult(
                success=False,
                output="",
                error="Sandbox is disabled",
            )

        timeout = timeout or self.settings.max_execution_time

        try:
            result = self._execute_with_timeout(code, timeout)

            # Validate resource usage
            if result.memory_used_mb > self.settings.max_memory_mb:
                return ExecutionResult(
                    success=False,
                    output=result.output,
                    error=f"Memory limit exceeded: {result.memory_used_mb:.2f}MB > {self.settings.max_memory_mb}MB",
                    execution_time=result.execution_time,
                    memory_used_mb=result.memory_used_mb,
                )

            if result.cpu_percent > self.settings.max_cpu_percent:
                return ExecutionResult(
                    success=False,
                    output=result.output,
                    error=f"CPU limit exceeded: {result.cpu_percent:.2f}% > {self.settings.max_cpu_percent}%",
                    execution_time=result.execution_time,
                    cpu_percent=result.cpu_percent,
                )

            return result

        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Sandbox error: {type(e).__name__}: {e!s}",
            )


class SandboxExecutor:
    """High-level executor for managing sandboxed code execution."""

    def __init__(self, settings: SandboxSettings):
        self.sandbox = CodeSandbox(settings)
        self.execution_history: list[ExecutionResult] = []

    async def execute_async(
        self,
        code: str,
        timeout: int | None = None,
    ) -> ExecutionResult:
        """Execute code asynchronously in sandbox.

        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds

        Returns:
            ExecutionResult

        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self.sandbox.execute,
            code,
            timeout,
        )

        self.execution_history.append(result)
        return result

    def get_execution_stats(self) -> dict[str, Any]:
        """Get statistics about execution history."""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "average_execution_time": 0.0,
                "average_memory_usage": 0.0,
            }

        successful = [r for r in self.execution_history if r.success]

        return {
            "total_executions": len(self.execution_history),
            "successful_executions": len(successful),
            "failed_executions": len(self.execution_history) - len(successful),
            "average_execution_time": (
                sum(r.execution_time for r in successful) / len(successful) if successful else 0.0
            ),
            "average_memory_usage": (
                sum(r.memory_used_mb for r in successful) / len(successful) if successful else 0.0
            ),
        }

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()
