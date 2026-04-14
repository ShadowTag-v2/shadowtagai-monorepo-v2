from typing import Any
from uuid import UUID

from .schemas import ContractDraft


class InMemoryDB:
    """Simulates a persistent database/storage layer for development/testing.
    Replace with SQLAlchemy/PostgreSQL + GCS in production.
    """

    jobs: dict[UUID, dict[str, Any]] = {}
    transcripts: dict[UUID, Any] = {}
    contracts: dict[UUID, ContractDraft] = {}
    attorney_queue: dict[UUID, ContractDraft] = {}
    signatures: dict[UUID, dict[str, str]] = {}
