# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""AGNT Bash Classifier — 35-check bash security pipeline with telemetry."""

from packages.agnt_bash_classifier.classifier import (
    BashSecurityClassifier,
    CheckResult,
    CheckVerdict,
    PipelineResult,
)
from packages.agnt_bash_classifier.security_checks import (
    COMMAND_SUBSTITUTION_PATTERNS,
    HEREDOC_IN_SUBSTITUTION,
    BashSecurityCheckId,
    ZSH_DANGEROUS_COMMANDS,
)
from packages.agnt_bash_classifier.telemetry import BashTelemetryTracker

__all__ = [
    "BashSecurityCheckId",
    "BashSecurityClassifier",
    "BashTelemetryTracker",
    "CheckResult",
    "CheckVerdict",
    "COMMAND_SUBSTITUTION_PATTERNS",
    "HEREDOC_IN_SUBSTITUTION",
    "PipelineResult",
    "ZSH_DANGEROUS_COMMANDS",
]
