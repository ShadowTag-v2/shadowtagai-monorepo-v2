"""Verdict Systems - Core Enumerations
Executive function replacement platform enums
"""

from enum import Enum, StrEnum


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
    BLOCKED = "blocked"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class LockoutMode(StrEnum):
    """Device lockout enforcement levels"""

    NONE = "none"  # No restrictions
    SOFT = "soft"  # Warnings and reminders
    MODERATE = "moderate"  # Block non-essential apps
    STRICT = "strict"  # Full lockout until task completion
    EMERGENCY_ONLY = "emergency_only"  # Only emergency functions available


class VerticalType(StrEnum):
    """Verdict Systems verticals"""

    FAMILY = "family"
    SCHOOL = "school"
    WORKPLACE = "workplace"
    MEDICAL = "medical"
    SENIOR = "senior"
    TRANSPORTATION = "transportation"
    SMART_HOME = "smart_home"


class DeviceType(StrEnum):
    """Supported device types"""

    PHONE = "phone"
    TABLET = "tablet"
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    VEHICLE = "vehicle"
    SMART_SPEAKER = "smart_speaker"
    SMART_DISPLAY = "smart_display"
    WEARABLE = "wearable"


class UserRole(StrEnum):
    """User roles in the system"""

    ADMIN = "admin"  # Full control and oversight
    PARENT = "parent"  # Family oversight
    TEACHER = "teacher"  # School oversight
    MANAGER = "manager"  # Workplace oversight
    CAREGIVER = "caregiver"  # Medical/senior oversight
    USER = "user"  # Standard user
    CHILD = "child"  # Restricted user
    STUDENT = "student"  # Student user
    EMPLOYEE = "employee"  # Employee user
    SENIOR = "senior"  # Senior citizen user


class NotificationType(StrEnum):
    """Notification types"""

    REMINDER = "reminder"
    DEADLINE_WARNING = "deadline_warning"
    LOCKOUT_IMMINENT = "lockout_imminent"
    LOCKOUT_ACTIVE = "lockout_active"
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    EMERGENCY_ALERT = "emergency_alert"
    FAMILY_CHECKIN = "family_checkin"
    MOTIVATIONAL = "motivational"


class PriorityLevel(int, Enum):
    """Task priority levels"""

    LOWEST = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    HIGHEST = 5
    CRITICAL = 6


class CompletionMethod(StrEnum):
    """How a task was marked complete"""

    MANUAL = "manual"  # User marked complete
    AUTO_VERIFIED = "auto_verified"  # System verified completion
    TEACHER_APPROVED = "teacher_approved"
    PARENT_APPROVED = "parent_approved"
    SUBMISSION_BASED = "submission_based"  # File/assignment submitted
    OVERRIDE = "override"  # Admin override
