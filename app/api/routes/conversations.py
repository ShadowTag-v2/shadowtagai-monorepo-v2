# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Conversation API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationWithMessages,
    MessageCreate,
    MessageResponse,
)
from app.schemas.search import RecentChatsQuery, RecentChatsResponse
from app.services import conversation_service

router = APIRouter(prefix="/conversations", tags=["conversations"])


# Mock user dependency (replace with real auth)
async def get_current_user_id() -> int:
    """Get current user ID from auth token."""
    return 1  # TODO: Implement real authentication


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(conversation_data: ConversationCreate, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Create a new conversation."""
    conversation = await conversation_service.create_conversation(db, user_id, conversation_data)
    return conversation


@router.get("/recent", response_model=RecentChatsResponse)
async def get_recent_conversations(
    limit: int = 20,
    project_id: int = None,
    include_incognito: bool = False,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """Get recent conversations."""
    query = RecentChatsQuery(limit=limit, project_id=project_id, include_incognito=include_incognito)

    conversations = await conversation_service.get_recent_conversations(db, user_id, query)

    return RecentChatsResponse(conversations=conversations, total=len(conversations))


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(conversation_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Get a conversation by ID with messages."""
    conversation = await conversation_service.get_conversation(db, conversation_id, user_id, include_messages=True)

    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return conversation


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int, conversation_data: ConversationUpdate, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    """Update a conversation."""
    conversation = await conversation_service.update_conversation(db, conversation_id, user_id, conversation_data)

    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    """Delete a conversation."""
    success = await conversation_service.delete_conversation(db, conversation_id, user_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    conversation_id: int, message_data: MessageCreate, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    """Add a message to a conversation."""
    # Ensure conversation_id in path matches message_data
    if message_data.conversation_id != conversation_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conversation ID mismatch")

    message = await conversation_service.add_message(db, user_id, message_data)

    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return message


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    conversation_id: int, limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db), user_id: int = Depends(get_current_user_id)
):
    """Get messages from a conversation."""
    messages = await conversation_service.get_messages(db, conversation_id, user_id, limit, offset)

    return messages
