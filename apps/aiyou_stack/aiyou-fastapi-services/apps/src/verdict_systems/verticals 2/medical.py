"""
Verdict Systems - Medical & Senior Care Vertical
Appointment reminders, medication tracking, senior independence support

Features:
- Medication reminders with photo verification
- Doctor appointment preparation
- Test/procedure scheduling
- Senior daily structure
- Caregiver oversight
- Safety alerts
- Social prompts
"""

from datetime import datetime, time

from pydantic import BaseModel, Field

from ..core.enums import VerticalType
from ..models.task import TaskCreate


class MedicalTask(TaskCreate):
    """Medical/health-related task"""

    vertical: VerticalType = Field(default=VerticalType.MEDICAL, const=True)

    # Medical fields
    task_category: str = Field(
        ..., description="medication|appointment|test|exercise|meal|social|safety_check"
    )
    recurring: bool = Field(default=False)
    recurrence_pattern: str | None = Field(None, description="daily|weekly|custom")

    # Verification
    requires_photo_proof: bool = Field(default=True)
    requires_caregiver_confirmation: bool = Field(default=False)
    caregiver_id: str | None = None

    # Safety
    critical_health_task: bool = Field(default=False, description="Life-critical (e.g., insulin)")
    emergency_contact: str | None = None


class MedicationReminder(BaseModel):
    """Medication reminder with tracking"""

    reminder_id: str
    user_id: str
    medication_name: str
    dosage: str
    scheduled_time: time
    taken_at: datetime | None = None
    photo_proof_url: str | None = None
    caregiver_confirmed: bool = Field(default=False)
    missed: bool = Field(default=False)


class SeniorDailyStructure(BaseModel):
    """Daily routine structure for seniors"""

    user_id: str
    daily_tasks: list[dict[str, Any]] = Field(
        default_factory=lambda: [
            {"time": "08:00", "task": "Morning medication", "critical": True},
            {"time": "09:00", "task": "Breakfast"},
            {"time": "10:00", "task": "Morning walk"},
            {"time": "12:00", "task": "Lunch"},
            {"time": "14:00", "task": "Social activity"},
            {"time": "18:00", "task": "Dinner"},
            {"time": "20:00", "task": "Evening medication", "critical": True},
            {"time": "21:00", "task": "Family check-in call", "critical": True},
        ]
    )
    caregiver_id: str
    emergency_contacts: list[dict[str, str]]


class SafetyAlert(BaseModel):
    """Safety alert for seniors/patients"""

    alert_id: str
    user_id: str
    alert_type: str = Field(..., description="fall|missed_medication|no_movement|emergency_button")
    triggered_at: datetime
    location: str | None = None
    emergency_services_notified: bool = Field(default=False)
    resolved_at: datetime | None = None
