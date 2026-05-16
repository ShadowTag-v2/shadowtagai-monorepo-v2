# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import init_db
from app.api.routes import conversations, memories, search, projects
from app.services import embedding_service

# Configure logging
logging.basicConfig(level=settings.log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting up Claude Memory & Search Service...")

    # Initialize database
    logger.info("Initializing database...")
    await init_db()

    # Initialize embedding service
    logger.info("Initializing embedding service...")
    await embedding_service.initialize()

    logger.info("Startup complete!")

    yield

    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    A comprehensive implementation of Claude's chat search and memory features.

    ## Features

    * **Semantic Search**: Search through conversations and memories using natural language
    * **Memory Management**: Store and retrieve key insights from conversations
    * **Project-based Isolation**: Separate memory contexts for different projects
    * **Automatic Summarization**: Auto-generate conversation summaries and extract memories
    * **Incognito Mode**: Private conversations that aren't saved to memory
    * **Memory Synthesis**: Automatic synthesis of memories updated every 24 hours

    ## Core Endpoints

    * **Conversations**: Create and manage chat conversations
    * **Messages**: Add messages to conversations with automatic embedding generation
    * **Memories**: Store, retrieve, and search through memories
    * **Search**: Semantic search across conversations and memories
    * **Projects**: Organize conversations and memories by project
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(conversations.router, prefix=settings.api_prefix)
app.include_router(memories.router, prefix=settings.api_prefix)
app.include_router(search.router, prefix=settings.api_prefix)
app.include_router(projects.router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "features": [
            "Semantic conversation search",
            "Memory management",
            "Project-based isolation",
            "Automatic summarization",
            "Incognito mode",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.reload, log_level=settings.log_level.lower())
