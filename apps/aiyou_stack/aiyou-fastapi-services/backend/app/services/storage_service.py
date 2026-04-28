# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Storage service for managing notes, issues, and other data."""

import uuid
from datetime import datetime

from app.models.storage import Issue, Note


class StorageService:
    """In-memory storage service for notes and issues.
    In production, this should be replaced with a database backend.
    """

    def __init__(self):
        """Initialize the storage service."""
        self.notes: dict[str, Note] = {}
        self.issues: dict[str, Issue] = {}
        # Index notes by title for quick lookup
        self.notes_by_title: dict[str, str] = {}

    # Note operations

    def create_note(self, folder: str, title: str, content: str) -> str:
        """Create a new note.

        Args:
            folder: Folder for the note
            title: Note title
            content: Note content

        Returns:
            Note ID

        """
        note_id = str(uuid.uuid4())
        now = datetime.utcnow()

        note = Note(
            note_id=note_id,
            folder=folder,
            title=title,
            content=content,
            created_at=now,
            updated_at=now,
        )

        self.notes[note_id] = note
        self.notes_by_title[title] = note_id

        return note_id

    def get_note_by_title(self, title: str) -> Note | None:
        """Get a note by its title.

        Args:
            title: Note title

        Returns:
            Note if found, None otherwise

        """
        note_id = self.notes_by_title.get(title)
        if note_id:
            return self.notes.get(note_id)
        return None

    def get_note_by_id(self, note_id: str) -> Note | None:
        """Get a note by its ID.

        Args:
            note_id: Note ID

        Returns:
            Note if found, None otherwise

        """
        return self.notes.get(note_id)

    def append_to_note(self, title: str, content: str) -> str:
        """Append content to an existing note.

        Args:
            title: Note title
            content: Content to append

        Returns:
            Note ID

        Raises:
            ValueError: If note not found

        """
        note = self.get_note_by_title(title)
        if not note:
            raise ValueError(f"Note with title '{title}' not found")

        # Append content
        note.content += content
        note.updated_at = datetime.utcnow()

        return note.note_id

    def list_notes(self, folder: str | None = None) -> list[Note]:
        """List all notes, optionally filtered by folder.

        Args:
            folder: Optional folder to filter by

        Returns:
            List of notes

        """
        notes = list(self.notes.values())

        if folder:
            notes = [n for n in notes if n.folder == folder]

        # Sort by created_at descending
        notes.sort(key=lambda n: n.created_at, reverse=True)

        return notes

    def delete_note(self, note_id: str) -> bool:
        """Delete a note.

        Args:
            note_id: Note ID

        Returns:
            True if deleted, False if not found

        """
        note = self.notes.get(note_id)
        if not note:
            return False

        # Remove from both indexes
        del self.notes[note_id]
        if note.title in self.notes_by_title:
            del self.notes_by_title[note.title]

        return True

    # Issue operations

    def create_issue(self, title: str, description: str, tags: list[str] | None = None) -> str:
        """Create a new issue.

        Args:
            title: Issue title
            description: Issue description
            tags: Optional list of tags

        Returns:
            Issue ID

        """
        issue_id = str(uuid.uuid4())
        now = datetime.utcnow()

        issue = Issue(
            issue_id=issue_id,
            title=title,
            description=description,
            status="open",
            created_at=now,
            updated_at=now,
            tags=tags or [],
        )

        self.issues[issue_id] = issue

        return issue_id

    def get_issue(self, issue_id: str) -> Issue | None:
        """Get an issue by ID.

        Args:
            issue_id: Issue ID

        Returns:
            Issue if found, None otherwise

        """
        return self.issues.get(issue_id)

    def list_issues(self, status: str | None = None) -> list[Issue]:
        """List all issues, optionally filtered by status.

        Args:
            status: Optional status to filter by

        Returns:
            List of issues

        """
        issues = list(self.issues.values())

        if status:
            issues = [i for i in issues if i.status == status]

        # Sort by created_at descending
        issues.sort(key=lambda i: i.created_at, reverse=True)

        return issues

    def update_issue_status(self, issue_id: str, status: str) -> bool:
        """Update issue status.

        Args:
            issue_id: Issue ID
            status: New status

        Returns:
            True if updated, False if not found

        """
        issue = self.issues.get(issue_id)
        if not issue:
            return False

        issue.status = status
        issue.updated_at = datetime.utcnow()

        return True

    def delete_issue(self, issue_id: str) -> bool:
        """Delete an issue.

        Args:
            issue_id: Issue ID

        Returns:
            True if deleted, False if not found

        """
        if issue_id in self.issues:
            del self.issues[issue_id]
            return True
        return False
