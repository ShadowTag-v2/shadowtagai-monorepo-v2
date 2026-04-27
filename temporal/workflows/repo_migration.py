"""Temporal workflow for long-running repository migrations."""

# TODO: Implement with temporalio/sdk-python
# This is a stub for Phase 3 ToolGateway integration.

from dataclasses import dataclass


@dataclass
class MigrationState:
    """State for a repository migration workflow."""

    source_repo: str
    target_path: str
    phase: str = "pending"
    files_processed: int = 0
    total_files: int = 0
