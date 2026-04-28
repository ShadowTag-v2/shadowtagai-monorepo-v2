# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Verdict Systems - Core Enumerations
Executive function replacement platform enums
"""

from enum import StrEnum


class UrgencyLevel(StrEnum):
    """Task urgency tile colors"""

    GREEN = "green"  # Low urgency, ample time
    YELLOW = "yellow"  # Medium urgency, attention needed
    RED = "red"  # High urgency, immediate action required
    CRITICAL = "critical"  # Past deadline, lockout active


class TaskStatus(StrEnum):
    """Task lifecycle status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    ARCHIVED = "archived"


class LockoutMode(StrEnum):
    """Focus enforcement levels"""

    NONE = "none"
    SOFT = "soft"  # Warnings only
    MODERATE = "moderate"  # Block social apps
    STRICT = "strict"  # Block everything except task apps
    EMERGENCY_ONLY = "emergency_only"  # Similar to strict but allows calls


class VerticalType(StrEnum):
    """Supported verticals"""

    SCHOOL = "school"
    FAMILY = "family"
    WORKPLACE = "workplace"
    MEDICAL = "medical"
    SENIOR = "senior"
    TRANSPORTATION = "transportation"
    SMART_HOME = "smart_home"


class PriorityLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class CompletionMethod(StrEnum):
    CHECKBOX = "checkbox"
    PHOTO_PROOF = "photo_proof"
    SUBMISSION = "submission"
    QR_SCAN = "qr_scan"
    GPS_VERIFICATION = "gps_verification"


class NotificationType(StrEnum):
    REMINDER = "reminder"
    URGENCY_CHANGE = "urgency_change"
    LOCKOUT_ALERT = "lockout_alert"
    ENCOURAGEMENT = "encouragement"
    ADMIN_ALERT = "admin_alert"


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"  # Parent, Teacher, Manager
    SUPER_ADMIN = "super_admin"


class DeviceType(StrEnum):
    MOBILE = "mobile"
    DESKTOP = "desktop"
    VEHICLE = "vehicle"
    IOT = "iot"
