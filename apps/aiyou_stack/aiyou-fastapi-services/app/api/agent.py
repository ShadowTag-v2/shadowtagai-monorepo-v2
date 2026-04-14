"""Agent API endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.claude_client import claude_client
from app.database import get_db
from app.models.message import MessageRole
from app.schemas.agent import AgentQueryRequest, AgentQueryResponse
from app.schemas.conversation import ConversationCreate
from app.schemas.message import MessageCreate
from app.services.conversation_service import ConversationService
from app.services.memory_service import MemoryService
from app.services.search_service import SearchService

router = APIRouter()


@router.post("/query", response_model=AgentQueryResponse)
async def query_with_memory(
    request: AgentQueryRequest,
    db: AsyncSession = Depends(get_db),
):
    """Query Claude with memory context."""
    conversation_service = ConversationService(db)
    memory_service = MemoryService(db)
    search_service = SearchService(db)

    # Get or create conversation
    if request.conversation_id:
        conversation = await conversation_service.get_conversation(request.conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        # Create new conversation
        conversation = await conversation_service.create_conversation(
            ConversationCreate(
                title=request.prompt[:100],  # Use first 100 chars as title
                project_id=request.project_id,
            ),
        )

    # Add user message
    await conversation_service.add_message(
        conversation_id=conversation.id,
        message_data=MessageCreate(
            role=MessageRole.USER,
            content=request.prompt,
        ),
    )

    # Get memory context
    memory_context = None
    memory_used = []
    if request.include_memory:
        memory_context = await memory_service.format_memory_context(project_id=request.project_id)
        # Get memory IDs for response
        memories = await memory_service.list_memory_entries(
            project_id=request.project_id,
            active_only=True,
        )
        memory_used = [str(m.id) for m in memories[:10]]  # Return first 10

    # Get conversation context from search
    conversation_context = None
    conversations_referenced = []
    if request.include_search and request.prompt:
        search_results = await search_service.search_conversations(
            query=request.prompt,
            project_id=request.project_id,
            top_k=3,
        )
        if search_results:
            conversation_context = []
            for result in search_results:
                conversations_referenced.append(result["conversation"].id)
                for msg in result["matched_messages"][:2]:  # Top 2 messages per conversation
                    conversation_context.append(
                        {
                            "role": msg["role"],
                            "content": msg["content"],
                        },
                    )

    # Query Claude
    response_text = ""
    async for chunk in claude_client.query_with_context(
        prompt=request.prompt,
        memory_context=memory_context,
        conversation_context=conversation_context,
        max_tokens=request.max_tokens or 4096,
        temperature=request.temperature or 1.0,
    ):
        response_text += chunk

    # Add assistant message
    await conversation_service.add_message(
        conversation_id=conversation.id,
        message_data=MessageCreate(
            role=MessageRole.ASSISTANT,
            content=response_text,
        ),
    )

    # Index the new messages for search
    if request.include_search:
        await search_service.index_conversation(conversation)

    return AgentQueryResponse(
        response=response_text,
        conversation_id=conversation.id,
        memory_used=memory_used if request.include_memory else None,
        conversations_referenced=conversations_referenced if request.include_search else None,
    )


@router.post("/stream")
async def stream_with_memory(
    request: AgentQueryRequest,
    db: AsyncSession = Depends(get_db),
):
    """Streaming query with memory context."""
    conversation_service = ConversationService(db)
    memory_service = MemoryService(db)
    search_service = SearchService(db)

    # Get or create conversation
    if request.conversation_id:
        conversation = await conversation_service.get_conversation(request.conversation_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )
    else:
        conversation = await conversation_service.create_conversation(
            ConversationCreate(
                title=request.prompt[:100],
                project_id=request.project_id,
            ),
        )

    # Add user message
    await conversation_service.add_message(
        conversation_id=conversation.id,
        message_data=MessageCreate(
            role=MessageRole.USER,
            content=request.prompt,
        ),
    )

    # Get memory context
    memory_context = None
    if request.include_memory:
        memory_context = await memory_service.format_memory_context(project_id=request.project_id)

    # Get conversation context
    conversation_context = None
    if request.include_search and request.prompt:
        search_results = await search_service.search_conversations(
            query=request.prompt,
            project_id=request.project_id,
            top_k=3,
        )
        if search_results:
            conversation_context = []
            for result in search_results:
                for msg in result["matched_messages"][:2]:
                    conversation_context.append(
                        {
                            "role": msg["role"],
                            "content": msg["content"],
                        },
                    )

    async def generate_stream():
        """Generate streaming response."""
        response_text = ""

        # Send metadata first
        yield f"data: {json.dumps({'type': 'metadata', 'data': {'conversation_id': str(conversation.id)}})}\n\n"

        # Stream content
        async for chunk in claude_client.query_with_context(
            prompt=request.prompt,
            memory_context=memory_context,
            conversation_context=conversation_context,
            max_tokens=request.max_tokens or 4096,
            temperature=request.temperature or 1.0,
        ):
            response_text += chunk
            yield f"data: {json.dumps({'type': 'content', 'data': chunk})}\n\n"

        # Add assistant message to conversation
        await conversation_service.add_message(
            conversation_id=conversation.id,
            message_data=MessageCreate(
                role=MessageRole.ASSISTANT,
                content=response_text,
            ),
        )

        # Index for search
        if request.include_search:
            await search_service.index_conversation(conversation)

        # Send done signal
        yield f"data: {json.dumps({'type': 'done', 'data': {}})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
    )
