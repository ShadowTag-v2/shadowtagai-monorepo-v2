# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Verdict Systems - Medical & Senior Care Vertical
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

from pydantic import BaseModel

from ..enums import VerticalType
from ..models.task import TaskCreate


class MedicationMetadata(BaseModel):
    medication_name: str
    dosage: str
    instructions: str | None = None
    refill_needed: bool = False
    pharmacy_id: str | None = None
    safety_alert_enabled: bool = True  # Notify caregiver if missed


class MedicalAppointmentMetadata(BaseModel):
    doctor_name: str
    location: str
    preparation_instructions: str | None = None
    transport_arranged: bool = False


class MedicalTaskCreate(TaskCreate):
    vertical: VerticalType = VerticalType.MEDICAL
    med_metadata: MedicationMetadata | None = None
    appt_metadata: MedicalAppointmentMetadata | None = None

    def to_task_create(self) -> TaskCreate:
        data = self.model_dump(exclude={"med_metadata", "appt_metadata"})
        meta = {}
        if self.med_metadata:
            meta.update(self.med_metadata.model_dump())
        if self.appt_metadata:
            meta.update(self.appt_metadata.model_dump())
        data["metadata"] = meta
        return TaskCreate(**data)
