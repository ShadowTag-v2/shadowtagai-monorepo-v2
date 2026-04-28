# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Context Management Service

Business logic for managing AI analysis sessions and context indices
"""

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from .models import (
    AnalysisRole,
    AnalysisSession,
    ChatSummary,
    ContextIndex,
    CreateSessionRequest,
    CreateSummaryRequest,
    SessionStatus,
)


class ContextManager:
    """Manages AI analysis sessions and context indices

    Provides CRUD operations and search functionality for tracking
    conversation history across multiple AI analysis sessions.
    """

    def __init__(self, storage_path: str = "./data/context_indices"):
        """Initialize the context manager

        Args:
            storage_path: Directory to store context indices (JSON files)

        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.index_file = self.storage_path / "context_index.json"
        self.summaries_file = self.storage_path / "chat_summaries.json"

        # In-memory cache
        self._index: ContextIndex | None = None
        self._summaries: dict[str, ChatSummary] = {}

        # Load from disk
        self._load_index()
        self._load_summaries()

    def _load_index(self) -> None:
        """Load context index from disk"""
        if self.index_file.exists():
            with open(self.index_file) as f:
                data = json.load(f)
                self._index = ContextIndex(**data)
        else:
            self._index = ContextIndex()
            self._save_index()

    def _save_index(self) -> None:
        """Save context index to disk"""
        with open(self.index_file, "w") as f:
            json.dump(self._index.model_dump(mode="json"), f, indent=2, default=str)

    def _load_summaries(self) -> None:
        """Load chat summaries from disk"""
        if self.summaries_file.exists():
            with open(self.summaries_file) as f:
                data = json.load(f)
                self._summaries = {item["session_id"]: ChatSummary(**item) for item in data}
        else:
            self._summaries = {}
            self._save_summaries()

    def _save_summaries(self) -> None:
        """Save chat summaries to disk"""
        with open(self.summaries_file, "w") as f:
            summaries_list = [s.model_dump(mode="json") for s in self._summaries.values()]
            json.dump(summaries_list, f, indent=2, default=str)

    def create_session(self, request: CreateSessionRequest) -> AnalysisSession:
        """Create a new analysis session

        Args:
            request: Session creation request

        Returns:
            Created AnalysisSession

        """
        session_id = self._generate_session_id(request.issue_title)

        session = AnalysisSession(
            session_id=session_id,
            issue_title=request.issue_title,
            role=request.role,
            goal=request.goal,
            constraints=request.constraints,
            model_name=request.model_name,
            confidence_threshold=request.confidence_threshold,
            parent_session_id=request.parent_session_id,
        )

        # Add to index
        self._index.sessions.append(session)
        self._index.total_sessions += 1
        self._index.active_sessions += 1
        self._index.updated_at = datetime.utcnow()

        self._save_index()

        return session

    def get_session(self, session_id: str) -> AnalysisSession | None:
        """Retrieve a session by ID

        Args:
            session_id: Session identifier

        Returns:
            AnalysisSession if found, None otherwise

        """
        for session in self._index.sessions:
            if session.session_id == session_id:
                return session
        return None

    def update_session(
        self,
        session_id: str,
        status: SessionStatus | None = None,
        total_tokens: int | None = None,
        completed_at: datetime | None = None,
    ) -> AnalysisSession | None:
        """Update an existing session

        Args:
            session_id: Session to update
            status: New status
            total_tokens: Updated token count
            completed_at: Completion timestamp

        Returns:
            Updated AnalysisSession if found, None otherwise

        """
        session = self.get_session(session_id)
        if not session:
            return None

        # Track active session count changes
        was_active = session.status == SessionStatus.ACTIVE

        if status:
            session.status = status
        if total_tokens is not None:
            # Update total tokens consumed in index
            delta = total_tokens - session.total_tokens
            self._index.total_tokens_consumed += delta
            session.total_tokens = total_tokens
        if completed_at:
            session.completed_at = completed_at

        session.updated_at = datetime.utcnow()
        self._index.updated_at = datetime.utcnow()

        # Adjust active session count
        is_active = session.status == SessionStatus.ACTIVE
        if was_active and not is_active:
            self._index.active_sessions -= 1
        elif not was_active and is_active:
            self._index.active_sessions += 1

        self._save_index()

        return session

    def list_sessions(
        self,
        role: AnalysisRole | None = None,
        status: SessionStatus | None = None,
        limit: int = 100,
    ) -> list[AnalysisSession]:
        """List sessions with optional filtering

        Args:
            role: Filter by analysis role
            status: Filter by session status
            limit: Maximum number of results

        Returns:
            List of matching sessions

        """
        sessions = self._index.sessions

        # Apply filters
        if role:
            sessions = [s for s in sessions if s.role == role]
        if status:
            sessions = [s for s in sessions if s.status == status]

        # Sort by created_at descending (most recent first)
        sessions = sorted(sessions, key=lambda s: s.created_at, reverse=True)

        return sessions[:limit]

    def create_summary(self, request: CreateSummaryRequest) -> ChatSummary:
        """Create a summary for a completed session

        Args:
            request: Summary creation request

        Returns:
            Created ChatSummary

        """
        summary = ChatSummary(
            session_id=request.session_id,
            summary=request.summary,
            key_decisions=request.key_decisions,
            findings=request.findings,
            recommendations=request.recommendations,
            risks_identified=request.risks_identified,
            related_threads=request.related_threads,
            tags=request.tags,
        )

        self._summaries[request.session_id] = summary
        self._save_summaries()

        # Mark session as completed if not already
        session = self.get_session(request.session_id)
        if session and session.status == SessionStatus.ACTIVE:
            self.update_session(
                request.session_id,
                status=SessionStatus.COMPLETED,
                completed_at=datetime.utcnow(),
            )

        return summary

    def get_summary(self, session_id: str) -> ChatSummary | None:
        """Retrieve a summary by session ID

        Args:
            session_id: Session identifier

        Returns:
            ChatSummary if found, None otherwise

        """
        return self._summaries.get(session_id)

    def search_sessions(
        self,
        query: str,
        search_in: list[str] = None,
    ) -> list[AnalysisSession]:
        """Search sessions by text query

        Args:
            query: Search term
            search_in: Fields to search in

        Returns:
            List of matching sessions

        """
        if search_in is None:
            search_in = ["issue_title", "goal", "constraints"]
        query_lower = query.lower()
        results = []

        for session in self._index.sessions:
            for field in search_in:
                value = getattr(session, field, None)
                if value and query_lower in str(value).lower():
                    results.append(session)
                    break

        return sorted(results, key=lambda s: s.created_at, reverse=True)

    def get_index(self) -> ContextIndex:
        """Get the full context index

        Returns:
            ContextIndex with all sessions

        """
        return self._index

    def export_session_context(self, session_id: str) -> dict | None:
        """Export a session with its summary for AI context loading

        Args:
            session_id: Session to export

        Returns:
            Dictionary with session and summary data

        """
        session = self.get_session(session_id)
        if not session:
            return None

        summary = self.get_summary(session_id)

        return {
            "session": session.model_dump(mode="json"),
            "summary": summary.model_dump(mode="json") if summary else None,
            "export_timestamp": datetime.utcnow().isoformat(),
        }

    def _generate_session_id(self, issue_title: str) -> str:
        """Generate a unique session ID

        Args:
            issue_title: Issue title for ID generation

        Returns:
            Session ID in format: {slug}-{date}-{uuid}

        """
        # Create slug from title
        slug = issue_title.lower()[:30].replace(" ", "-").replace("_", "-")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")

        # Date component
        date_str = datetime.utcnow().strftime("%Y%m%d")

        # Short UUID
        short_uuid = str(uuid4())[:8]

        return f"{slug}-{date_str}-{short_uuid}"

    def get_active_sessions(self) -> list[AnalysisSession]:
        """Get all currently active sessions

        Returns:
            List of active sessions

        """
        return self.list_sessions(status=SessionStatus.ACTIVE)

    def archive_session(self, session_id: str) -> AnalysisSession | None:
        """Archive a completed session

        Args:
            session_id: Session to archive

        Returns:
            Archived session if found

        """
        return self.update_session(session_id, status=SessionStatus.ARCHIVED)
