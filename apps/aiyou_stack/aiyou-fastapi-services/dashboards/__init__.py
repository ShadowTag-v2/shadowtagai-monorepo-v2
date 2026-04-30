"""Dashboards Module
=================
Rich terminal dashboards for monitoring and management.

Available Dashboards:
- TrainingDashboard: GPU cluster job management
"""

from .training_dashboard import (
    GPUCluster,
    GPUType,
    JobStatus,
    TrainingDashboard,
    TrainingJob,
    TrainingMetrics,
)

__all__ = [
    "GPUCluster",
    "GPUType",
    "JobStatus",
    "TrainingDashboard",
    "TrainingJob",
    "TrainingMetrics",
]
