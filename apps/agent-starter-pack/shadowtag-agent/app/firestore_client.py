# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Firestore CRUD client for the ShadowTag Engine database.

This module provides a typed interface to the `shadowtag-engine` Firestore
database within the `shadowtag-omega-v4` GCP project. All collections follow
the UphillSnowball namespace convention.

Collections:
    uphillsnowball_intakes — Case intake records
    uphillsnowball_screenings — Sanctions screening results
    uphillsnowball_analyses — Document analysis results
    uphillsnowball_billing — Billable activity entries
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# Firestore client singleton — lazy-initialized
_db = None


def _get_db():
    """Returns a Firestore client, initializing on first call.

    Uses the `shadowtag-engine` database in the `shadowtag-omega-v4` project.
    Falls back gracefully when GCP credentials are unavailable (e.g. in tests).
    """
    global _db
    if _db is not None:
        return _db

    try:
        from google.cloud import firestore

        project = os.environ.get("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
        _db = firestore.Client(project=project, database="shadowtag-engine")
        logger.info("Firestore client initialized: project=%s, db=shadowtag-engine", project)
    except Exception as e:
        logger.warning("Firestore unavailable (test env?): %s", e)
        _db = None

    return _db


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------


def create_intake(intake_data: dict[str, Any]) -> str | None:
    """Writes a case intake record to Firestore.

    Args:
        intake_data: Dict from uphillsnowball_case_intake tool output.

    Returns:
        The Firestore document ID, or None if write failed.
    """
    db = _get_db()
    if db is None:
        logger.warning("Firestore unavailable — intake not persisted")
        return None

    doc_ref = db.collection("uphillsnowball_intakes").document(intake_data.get("intake_id"))
    doc_ref.set(intake_data)
    logger.info("Intake persisted: %s", doc_ref.id)
    return doc_ref.id


def create_screening(screening_data: dict[str, Any]) -> str | None:
    """Writes a sanctions screening result to Firestore.

    Args:
        screening_data: Dict from uphillsnowball_sanctions_check tool output.

    Returns:
        The Firestore document ID, or None if write failed.
    """
    db = _get_db()
    if db is None:
        logger.warning("Firestore unavailable — screening not persisted")
        return None

    doc_ref = db.collection("uphillsnowball_screenings").document(screening_data.get("screening_id"))
    doc_ref.set(screening_data)
    logger.info("Screening persisted: %s", doc_ref.id)
    return doc_ref.id


def create_analysis(analysis_data: dict[str, Any]) -> str | None:
    """Writes a document analysis result to Firestore.

    Args:
        analysis_data: Dict from uphillsnowball_document_analysis tool output.

    Returns:
        The Firestore document ID, or None if write failed.
    """
    db = _get_db()
    if db is None:
        logger.warning("Firestore unavailable — analysis not persisted")
        return None

    doc_ref = db.collection("uphillsnowball_analyses").document(analysis_data.get("analysis_id"))
    doc_ref.set(analysis_data)
    logger.info("Analysis persisted: %s", doc_ref.id)
    return doc_ref.id


def create_billing_entry(billing_data: dict[str, Any]) -> str | None:
    """Writes a billing entry to Firestore.

    Args:
        billing_data: Dict from uphillsnowball_billing_tracker tool output.

    Returns:
        The Firestore document ID, or None if write failed.
    """
    db = _get_db()
    if db is None:
        logger.warning("Firestore unavailable — billing not persisted")
        return None

    doc_ref = db.collection("uphillsnowball_billing").document(billing_data.get("entry_id"))
    doc_ref.set(billing_data)
    logger.info("Billing persisted: %s", doc_ref.id)
    return doc_ref.id


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------


def get_intake(intake_id: str) -> dict[str, Any] | None:
    """Retrieves a case intake by ID.

    Args:
        intake_id: The intake document ID (e.g. 'USI-20260413143500').

    Returns:
        The intake document as a dict, or None if not found.
    """
    db = _get_db()
    if db is None:
        return None

    doc = db.collection("uphillsnowball_intakes").document(intake_id).get()
    return doc.to_dict() if doc.exists else None


def get_screening(screening_id: str) -> dict[str, Any] | None:
    """Retrieves a sanctions screening by ID."""
    db = _get_db()
    if db is None:
        return None

    doc = db.collection("uphillsnowball_screenings").document(screening_id).get()
    return doc.to_dict() if doc.exists else None


def get_analysis(analysis_id: str) -> dict[str, Any] | None:
    """Retrieves a document analysis by ID."""
    db = _get_db()
    if db is None:
        return None

    doc = db.collection("uphillsnowball_analyses").document(analysis_id).get()
    return doc.to_dict() if doc.exists else None


def get_billing_entry(entry_id: str) -> dict[str, Any] | None:
    """Retrieves a billing entry by ID."""
    db = _get_db()
    if db is None:
        return None

    doc = db.collection("uphillsnowball_billing").document(entry_id).get()
    return doc.to_dict() if doc.exists else None


def list_intakes(matter_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    """Lists case intakes, optionally filtered by matter.

    Args:
        matter_id: Optional matter ID filter.
        limit: Maximum number of records to return (default 50).

    Returns:
        List of intake documents.
    """
    db = _get_db()
    if db is None:
        return []

    query = db.collection("uphillsnowball_intakes").order_by(
        "timestamp", direction="DESCENDING"
    ).limit(limit)

    if matter_id:
        query = query.where("matter_id", "==", matter_id)

    return [doc.to_dict() for doc in query.stream()]


def list_billing_by_matter(matter_id: str, limit: int = 100) -> list[dict[str, Any]]:
    """Lists billing entries for a specific matter.

    Args:
        matter_id: The matter ID to filter by.
        limit: Maximum number of records (default 100).

    Returns:
        List of billing entries for the matter.
    """
    db = _get_db()
    if db is None:
        return []

    query = (
        db.collection("uphillsnowball_billing")
        .where("matter_id", "==", matter_id)
        .order_by("timestamp", direction="DESCENDING")
        .limit(limit)
    )

    return [doc.to_dict() for doc in query.stream()]


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------


def update_intake_status(intake_id: str, new_status: str) -> bool:
    """Updates the status of an existing intake.

    Args:
        intake_id: The intake document ID.
        new_status: New status value (e.g. 'ASSIGNED', 'IN_REVIEW', 'CLOSED').

    Returns:
        True if update succeeded, False otherwise.
    """
    db = _get_db()
    if db is None:
        return False

    doc_ref = db.collection("uphillsnowball_intakes").document(intake_id)
    doc_ref.update({"status": new_status})
    logger.info("Intake %s status updated to %s", intake_id, new_status)
    return True


def update_billing_status(entry_id: str, new_status: str) -> bool:
    """Updates billing entry status (e.g. PENDING_REVIEW → APPROVED).

    Args:
        entry_id: The billing entry ID.
        new_status: New status value.

    Returns:
        True if update succeeded, False otherwise.
    """
    db = _get_db()
    if db is None:
        return False

    doc_ref = db.collection("uphillsnowball_billing").document(entry_id)
    doc_ref.update({"status": new_status})
    logger.info("Billing %s status updated to %s", entry_id, new_status)
    return True


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------


def delete_intake(intake_id: str) -> bool:
    """Deletes a case intake record.

    Args:
        intake_id: The intake document ID to delete.

    Returns:
        True if deletion succeeded, False otherwise.
    """
    db = _get_db()
    if db is None:
        return False

    db.collection("uphillsnowball_intakes").document(intake_id).delete()
    logger.info("Intake deleted: %s", intake_id)
    return True


def delete_billing_entry(entry_id: str) -> bool:
    """Deletes a billing entry.

    Args:
        entry_id: The billing entry ID to delete.

    Returns:
        True if deletion succeeded, False otherwise.
    """
    db = _get_db()
    if db is None:
        return False

    db.collection("uphillsnowball_billing").document(entry_id).delete()
    logger.info("Billing entry deleted: %s", entry_id)
    return True
