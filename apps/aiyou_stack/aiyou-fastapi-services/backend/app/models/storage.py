"""Pydantic models for storage (notes, issues, etc.).
"""

from datetime import datetime

from pydantic import BaseModel, Field


class Note(BaseModel):
    """Represents a note in the system."""

    note_id: str = Field(..., description="Unique note identifier")
    folder: str = Field(..., description="Folder containing the note")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CreateNoteRequest(BaseModel):
    """Request to create a new note."""

    folder: str = Field(..., description="Folder for the note")
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")


class CreateNoteResponse(BaseModel):
    """Response after creating a note."""

    note_id: str = Field(..., description="ID of the created note")
    message: str = Field(..., description="Success message")


class AppendToNoteRequest(BaseModel):
    """Request to append content to a note."""

    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Content to append")


class AppendToNoteResponse(BaseModel):
    """Response after appending to a note."""

    note_id: str = Field(..., description="ID of the updated note")
    message: str = Field(..., description="Success message")


class GetNoteRequest(BaseModel):
    """Request to get a note."""

    title: str = Field(..., description="Note title")


class GetNoteResponse(BaseModel):
    """Response when getting a note."""

    note: Note = Field(..., description="The requested note")


class ListNotesResponse(BaseModel):
    """Response when listing notes."""

    notes: list[Note] = Field(..., description="List of notes")
    count: int = Field(..., description="Total count")


class Issue(BaseModel):
    """Represents an issue/topic being tracked."""

    issue_id: str = Field(..., description="Unique issue identifier")
    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Issue description")
    status: str = Field(default="open", description="Issue status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: list[str] = Field(default_factory=list, description="Issue tags")


class CreateIssueRequest(BaseModel):
    """Request to create a new issue."""

    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Issue description")
    tags: list[str] | None = Field(default_factory=list, description="Issue tags")


class CreateIssueResponse(BaseModel):
    """Response after creating an issue."""

    issue_id: str = Field(..., description="ID of the created issue")
    message: str = Field(..., description="Success message")
