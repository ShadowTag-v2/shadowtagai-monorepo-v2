"""Blast-Radius Declarations — Per-module scope boundaries.

Every module declares its maximum authorized scope.
Judge 6 enforces these boundaries at runtime.
Modules cannot exceed their declared blast radius.

This is the principle of least privilege applied to
internal AI pipeline stages, not just API endpoints.
"""

from enum import Flag, auto


class BlastRadius(Flag):
    """Authorized scope for a module."""
    READ = auto()       # Can read data
    WRITE = auto()      # Can write data
    BLOCK = auto()      # Can block execution
    REWRITE = auto()    # Can modify other modules' output
    ESCALATE = auto()   # Can invoke higher-privilege operations
    DESTROY = auto()    # Can delete data or terminate processes


# Canonical blast-radius declarations for all API modules.
# Adding a module here is a security-critical operation.
MODULE_BLAST_RADIUS: dict[str, BlastRadius] = {
    # Governance
    "judge6":               BlastRadius.READ | BlastRadius.BLOCK,
    "silent_detector":      BlastRadius.READ,
    "auth":                 BlastRadius.READ | BlastRadius.BLOCK,

    # AI Pipeline
    "oracle_studio":        BlastRadius.READ | BlastRadius.WRITE,
    "vent_mode":            BlastRadius.READ | BlastRadius.WRITE,
    "model_router":         BlastRadius.READ,
    "gemini_rag":           BlastRadius.READ,
    "intake_summarizer":    BlastRadius.READ | BlastRadius.WRITE,

    # Privilege
    "kovel_attestation":    BlastRadius.READ | BlastRadius.WRITE,

    # Billing
    "stripe_handler":       BlastRadius.READ | BlastRadius.WRITE | BlastRadius.ESCALATE,
    "stripe_connect":       BlastRadius.READ | BlastRadius.WRITE | BlastRadius.ESCALATE,
    "stripe_connect_webhook": BlastRadius.READ | BlastRadius.WRITE,
    "stripe_multi_attorney": BlastRadius.READ | BlastRadius.WRITE,
    "subscription_notifications": BlastRadius.READ | BlastRadius.ESCALATE,

    # Data
    "firestore_client":     BlastRadius.READ | BlastRadius.WRITE,
    "gdpr":                 BlastRadius.READ | BlastRadius.WRITE | BlastRadius.DESTROY,
    "cloud_tasks_gdpr":     BlastRadius.DESTROY,
    "secret_client":        BlastRadius.READ,

    # Comms
    "workspace_alerts":     BlastRadius.READ | BlastRadius.ESCALATE,
    "email_service":        BlastRadius.READ | BlastRadius.ESCALATE,
    "magic_link":           BlastRadius.READ | BlastRadius.WRITE,

    # Observability
    "telemetry":            BlastRadius.READ | BlastRadius.WRITE,
}


def check_blast_radius(module_name: str, requested: BlastRadius) -> bool:
    """Check if a module is authorized for the requested scope.

    Returns True if authorized, False if the request exceeds
    the module's declared blast radius.
    """
    declared = MODULE_BLAST_RADIUS.get(module_name)
    if declared is None:
        return False  # Unknown modules get NO access
    return (requested & declared) == requested
