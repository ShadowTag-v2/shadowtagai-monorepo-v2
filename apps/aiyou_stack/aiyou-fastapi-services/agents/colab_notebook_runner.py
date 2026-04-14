#!/usr/bin/env python3
"""Colab Notebook Runner: Execute notebooks in Google Colab environment.
Handles actual Colab integration via API or browser automation.

Part of Cloud Code API + Colab Coop automation stack.
"""

import asyncio
import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class RuntimeType(Enum):
    """Colab runtime types."""

    CPU = "cpu"
    GPU_T4 = "gpu_t4"
    GPU_A100 = "gpu_a100"
    TPU = "tpu"


class ExecutionMode(Enum):
    """How to execute the notebook."""

    LOCAL = "local"  # Local Python execution
    COLAB_API = "colab_api"  # Google Colab API
    BROWSER = "browser"  # Browser automation (Playwright/Selenium)
    CLOUD_CODE = "cloud_code"  # Via Cloud Code API


@dataclass
class NotebookCell:
    """Individual notebook cell."""

    cell_type: str  # "code" or "markdown"
    source: str
    outputs: list[Any] = field(default_factory=list)
    execution_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NotebookResult:
    """Result from notebook execution."""

    success: bool
    cells: list[NotebookCell]
    runtime_type: RuntimeType
    execution_mode: ExecutionMode
    duration_seconds: float
    outputs: list[Any]
    errors: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


class ColabNotebookRunner:
    """Execute notebooks in Colab or locally.

    Supports:
    - Local Python execution (for testing)
    - Cloud Code API integration
    - Browser automation for full Colab access
    """

    def __init__(
        self, mode: ExecutionMode = ExecutionMode.LOCAL, runtime: RuntimeType = RuntimeType.CPU,
    ):
        """Initialize notebook runner.

        Args:
            mode: How to execute notebooks
            runtime: Colab runtime type (for COLAB_API/BROWSER modes)

        """
        self.mode = mode
        self.runtime = runtime
        self.stats = {"notebooks_run": 0, "cells_executed": 0, "errors": 0, "total_duration": 0.0}

        print(f"///▞ NOTEBOOK RUNNER :: Mode={mode.value}, Runtime={runtime.value}")

    def _parse_notebook(self, notebook_path: str) -> list[NotebookCell]:
        """Parse .ipynb file into cells."""
        with open(notebook_path) as f:
            nb = json.load(f)

        cells = []
        for cell in nb.get("cells", []):
            source = cell.get("source", [])
            if isinstance(source, list):
                source = "".join(source)

            cells.append(
                NotebookCell(
                    cell_type=cell.get("cell_type", "code"),
                    source=source,
                    outputs=cell.get("outputs", []),
                    execution_count=cell.get("execution_count"),
                    metadata=cell.get("metadata", {}),
                ),
            )

        return cells

    def _create_notebook(self, cells: list[NotebookCell]) -> dict[str, Any]:
        """Create notebook structure from cells."""
        nb_cells = []
        for cell in cells:
            nb_cell = {
                "cell_type": cell.cell_type,
                "source": cell.source.split("\n") if "\n" in cell.source else [cell.source],
                "metadata": cell.metadata,
            }
            if cell.cell_type == "code":
                nb_cell["outputs"] = cell.outputs
                nb_cell["execution_count"] = cell.execution_count
            nb_cells.append(nb_cell)

        return {
            "nbformat": 4,
            "nbformat_minor": 0,
            "metadata": {
                "colab": {"name": "Generated Notebook"},
                "kernelspec": {"name": "python3", "display_name": "Python 3"},
            },
            "cells": nb_cells,
        }

    async def execute_local(self, cells: list[NotebookCell]) -> NotebookResult:
        """Execute notebook cells locally."""
        import subprocess
        import sys

        outputs = []
        errors = []
        start_time = datetime.now()
        executed_cells = []

        # Create execution namespace
        namespace = {}

        for i, cell in enumerate(cells):
            if cell.cell_type != "code":
                executed_cells.append(cell)
                continue

            try:
                # Execute in subprocess for isolation
                with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                    f.write(cell.source)
                    temp_file = f.name

                result = subprocess.run(
                    [sys.executable, temp_file], capture_output=True, text=True, timeout=60,
                )

                output = result.stdout or result.stderr
                outputs.append(
                    {"cell_index": i, "output": output, "return_code": result.returncode},
                )

                executed_cell = NotebookCell(
                    cell_type="code",
                    source=cell.source,
                    outputs=[{"output_type": "stream", "text": output}],
                    execution_count=i + 1,
                )
                executed_cells.append(executed_cell)

                if result.returncode != 0:
                    errors.append(f"Cell {i}: {result.stderr}")

                os.unlink(temp_file)
                self.stats["cells_executed"] += 1

            except subprocess.TimeoutExpired:
                errors.append(f"Cell {i}: Execution timeout")
                executed_cells.append(cell)
            except Exception as e:
                errors.append(f"Cell {i}: {e!s}")
                executed_cells.append(cell)
                self.stats["errors"] += 1

        duration = (datetime.now() - start_time).total_seconds()
        self.stats["notebooks_run"] += 1
        self.stats["total_duration"] += duration

        return NotebookResult(
            success=len(errors) == 0,
            cells=executed_cells,
            runtime_type=RuntimeType.CPU,
            execution_mode=ExecutionMode.LOCAL,
            duration_seconds=duration,
            outputs=outputs,
            errors=errors,
        )

    async def execute_cloud_code(
        self, cells: list[NotebookCell], client: Any | None = None,
    ) -> NotebookResult:
        """Execute via Cloud Code API."""
        from agents.cloudcode_client import CloudCodeClient

        if client is None:
            client = CloudCodeClient(account_id=1)

        outputs = []
        errors = []
        start_time = datetime.now()
        executed_cells = []
        context = ""

        for i, cell in enumerate(cells):
            if cell.cell_type != "code":
                executed_cells.append(cell)
                continue

            result = await client.execute_notebook_cell(cell.source, context)

            if result.get("error"):
                errors.append(f"Cell {i}: {result['error']}")

            outputs.append(
                {
                    "cell_index": i,
                    "safe_to_execute": result.get("safe_to_execute", True),
                    "dependencies": result.get("dependencies", []),
                    "modified_code": result.get("modified_code", cell.source),
                },
            )

            executed_cell = NotebookCell(
                cell_type="code",
                source=result.get("modified_code", cell.source),
                outputs=[{"output_type": "execute_result", "data": result}],
                execution_count=i + 1,
            )
            executed_cells.append(executed_cell)

            # Build context
            context += f"\n# Cell {i}:\n{cell.source}\n"
            self.stats["cells_executed"] += 1

        duration = (datetime.now() - start_time).total_seconds()
        self.stats["notebooks_run"] += 1
        self.stats["total_duration"] += duration

        return NotebookResult(
            success=len(errors) == 0,
            cells=executed_cells,
            runtime_type=self.runtime,
            execution_mode=ExecutionMode.CLOUD_CODE,
            duration_seconds=duration,
            outputs=outputs,
            errors=errors,
            metadata={"client_account": client.account_id},
        )

    async def execute_browser(self, cells: list[NotebookCell]) -> NotebookResult:
        """Execute via browser automation (Playwright)."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return NotebookResult(
                success=False,
                cells=cells,
                runtime_type=self.runtime,
                execution_mode=ExecutionMode.BROWSER,
                duration_seconds=0,
                outputs=[],
                errors=[
                    "playwright not installed. Run: pip install playwright && playwright install",
                ],
            )

        outputs = []
        errors = []
        start_time = datetime.now()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # Navigate to Colab
                await page.goto("https://colab.research.google.com/")

                # Wait for load
                await page.wait_for_load_state("networkidle")

                # Check if logged in
                # Note: Actual implementation would need OAuth flow

                # Create new notebook
                await page.click('text="New notebook"', timeout=5000)
                await page.wait_for_timeout(2000)

                # Execute cells
                for i, cell in enumerate(cells):
                    if cell.cell_type != "code":
                        continue

                    # Find code cell and input
                    # Note: Actual selectors depend on Colab DOM structure
                    cell_input = await page.query_selector(".cell-input")
                    if cell_input:
                        await cell_input.fill(cell.source)

                        # Run cell
                        await page.keyboard.press("Shift+Enter")
                        await page.wait_for_timeout(3000)

                        # Capture output
                        output_elem = await page.query_selector(".cell-output")
                        if output_elem:
                            output_text = await output_elem.inner_text()
                            outputs.append({"cell_index": i, "output": output_text})

                    self.stats["cells_executed"] += 1

            except Exception as e:
                errors.append(f"Browser automation error: {e!s}")
                self.stats["errors"] += 1
            finally:
                await browser.close()

        duration = (datetime.now() - start_time).total_seconds()
        self.stats["notebooks_run"] += 1
        self.stats["total_duration"] += duration

        return NotebookResult(
            success=len(errors) == 0,
            cells=cells,
            runtime_type=self.runtime,
            execution_mode=ExecutionMode.BROWSER,
            duration_seconds=duration,
            outputs=outputs,
            errors=errors,
        )

    async def run(
        self, notebook: str | list[NotebookCell] | dict[str, Any], **kwargs,
    ) -> NotebookResult:
        """Execute a notebook.

        Args:
            notebook: Path to .ipynb, list of cells, or notebook dict
            **kwargs: Additional execution options

        Returns:
            NotebookResult with execution details

        """
        # Parse input
        if isinstance(notebook, str):
            if notebook.endswith(".ipynb"):
                cells = self._parse_notebook(notebook)
            else:
                # Assume it's code
                cells = [NotebookCell(cell_type="code", source=notebook)]
        elif isinstance(notebook, list):
            cells = notebook
        elif isinstance(notebook, dict):
            cells = self._parse_notebook_dict(notebook)
        else:
            raise ValueError(f"Invalid notebook type: {type(notebook)}")

        # Execute based on mode
        if self.mode == ExecutionMode.LOCAL:
            return await self.execute_local(cells)
        if self.mode == ExecutionMode.CLOUD_CODE:
            return await self.execute_cloud_code(cells, kwargs.get("client"))
        if self.mode == ExecutionMode.BROWSER:
            return await self.execute_browser(cells)
        return await self.execute_local(cells)

    def _parse_notebook_dict(self, nb_dict: dict[str, Any]) -> list[NotebookCell]:
        """Parse notebook dictionary into cells."""
        cells = []
        for cell in nb_dict.get("cells", []):
            source = cell.get("source", "")
            if isinstance(source, list):
                source = "".join(source)

            cells.append(
                NotebookCell(
                    cell_type=cell.get("cell_type", "code"),
                    source=source,
                    outputs=cell.get("outputs", []),
                ),
            )
        return cells

    async def run_from_template(
        self, template_name: str, variables: dict[str, Any],
    ) -> NotebookResult:
        """Run notebook from template with variable substitution.

        Args:
            template_name: Name of template (looks in templates/ directory)
            variables: Variables to substitute in template

        Returns:
            NotebookResult

        """
        template_path = Path(__file__).parent.parent / "templates" / f"{template_name}.ipynb"

        if not template_path.exists():
            return NotebookResult(
                success=False,
                cells=[],
                runtime_type=self.runtime,
                execution_mode=self.mode,
                duration_seconds=0,
                outputs=[],
                errors=[f"Template not found: {template_path}"],
            )

        cells = self._parse_notebook(str(template_path))

        # Substitute variables
        for cell in cells:
            for key, value in variables.items():
                cell.source = cell.source.replace(f"{{{{{key}}}}}", str(value))

        return await self.run(cells)

    def save_notebook(self, cells: list[NotebookCell], output_path: str) -> None:
        """Save cells to .ipynb file."""
        nb = self._create_notebook(cells)
        with open(output_path, "w") as f:
            json.dump(nb, f, indent=2)
        print(f"///▞ NOTEBOOK RUNNER :: Saved to {output_path}")

    def get_stats(self) -> dict[str, Any]:
        """Get runner statistics."""
        return {
            "mode": self.mode.value,
            "runtime": self.runtime.value,
            "notebooks_run": self.stats["notebooks_run"],
            "cells_executed": self.stats["cells_executed"],
            "errors": self.stats["errors"],
            "total_duration_seconds": self.stats["total_duration"],
            "avg_duration": (self.stats["total_duration"] / max(self.stats["notebooks_run"], 1)),
        }


# Convenience function
def create_runner(mode: str = "local", runtime: str = "cpu") -> ColabNotebookRunner:
    """Create a notebook runner with specified configuration."""
    return ColabNotebookRunner(mode=ExecutionMode(mode), runtime=RuntimeType(runtime))


# Standalone test
if __name__ == "__main__":

    async def main():
        # Test local execution
        runner = ColabNotebookRunner(mode=ExecutionMode.LOCAL)

        # Simple code execution
        cells = [
            NotebookCell(cell_type="markdown", source="# Test Notebook"),
            NotebookCell(cell_type="code", source="print('Hello from Colab Coop!')"),
            NotebookCell(cell_type="code", source="import sys; print(f'Python {sys.version}')"),
            NotebookCell(
                cell_type="code", source="result = sum(range(100)); print(f'Sum: {result}')",
            ),
        ]

        result = await runner.run(cells)

        print(f"Success: {result.success}")
        print(f"Duration: {result.duration_seconds:.2f}s")
        print(f"Errors: {result.errors}")
        print(f"Outputs: {result.outputs}")

        # Save executed notebook
        runner.save_notebook(result.cells, "/tmp/test_notebook_result.ipynb")

        print("\nStats:", json.dumps(runner.get_stats(), indent=2))

    asyncio.run(main())
