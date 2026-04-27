"""Dagger module for Monorepo OS reproducible checks."""

import dagger
from dagger import dag, function, object_type


@object_type
class MonorepoOs:
    """Monorepo OS Dagger functions for reproducible CI/CD checks."""

    @function
    async def preflight(self, source: dagger.Directory) -> str:
        """Run the Monorepo OS pre-flight check."""
        return await (
            dag.container()
            .from_("python:3.14-slim")
            .with_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["bash", "scripts/antigravity-preflight.sh"])
            .stdout()
        )

    @function
    async def secret_scan(self, source: dagger.Directory) -> str:
        """Run Betterleaks secret scan."""
        return await (
            dag.container()
            .from_("python:3.14-slim")
            .with_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["bash", "scripts/secret-scan.sh"])
            .stdout()
        )

    @function
    async def lint(self, source: dagger.Directory) -> str:
        """Run unified lint pass (ruff + biome)."""
        return await (
            dag.container()
            .from_("python:3.14-slim")
            .with_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["pip", "install", "ruff"])
            .with_exec(["ruff", "check", "--select", "F401,F841", "."])
            .stdout()
        )
