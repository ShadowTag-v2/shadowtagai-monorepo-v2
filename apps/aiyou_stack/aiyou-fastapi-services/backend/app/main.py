"""Main FastAPI application for AI Issue Chat Workflow API."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.workflow import ActionType, WorkflowBlock
from app.routes import gemini, health, ingestion, notes, workflows
from app.services.gemini_service import GeminiService
from app.services.ingestion_service import IngestionService
from app.services.storage_service import StorageService
from app.services.workflow_engine import WorkflowEngine

# Global service instances
storage_service: StorageService = None
workflow_engine: WorkflowEngine = None
ingestion_service: IngestionService = None
gemini_service: GeminiService = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Lifespan context manager for application startup and shutdown."""
    global storage_service, workflow_engine, ingestion_service, gemini_service

    # Startup: Initialize services
    print("Starting up application...")

    # Initialize storage service
    storage_service = StorageService()

    # Initialize workflow engine
    workflow_engine = WorkflowEngine(storage_service)

    # Initialize ingestion service
    ingestion_service = IngestionService()

    # Initialize Gemini service
    gemini_api_key = getattr(settings, "gemini_api_key", None)
    gemini_service = GeminiService(
        api_key=gemini_api_key,
        model_name=getattr(settings, "gemini_model", "gemini-3.1-flash-lite-preview"),
    )

    # Register the predefined workflows
    _register_workflows(workflow_engine)

    # Initialize sample data sources
    _initialize_sample_sources(ingestion_service)

    print("Application startup complete")
    if gemini_service.is_available():
        print("✓ Gemini AI is available")
    else:
        print("⚠ Gemini AI not configured (set GEMINI_API_KEY)")

    yield

    # Shutdown: Clean up resources
    print("Shutting down application...")
    # Add any cleanup logic here if needed
    print("Application shutdown complete")


def _register_workflows(engine: WorkflowEngine):
    """Register the predefined workflow blocks."""
    # New AI Issue Chat workflow
    new_issue_chat_workflow = WorkflowBlock(
        block_name="New AI Issue Chat",
        description="Starts a new atomic context chat for a new issue and sets up a note entry to record the issue summary.",
        actions=[
            {
                "type": ActionType.ASK_FOR_INPUT,
                "title": "Issue Title",
                "prompt": "Enter a short title or description for this issue",
            },
            {
                "type": ActionType.ASK_FOR_INPUT,
                "title": "Micro-Brief",
                "prompt": "Describe what you want to achieve in this chat (role, goal, constraints, output format, etc.)",
            },
            {"type": ActionType.GET_DATE, "format": "YYYY-MM-DD HH:mm"},
            {"type": ActionType.OPEN_APP, "appName": "ChatGPT"},
            {
                "type": ActionType.CREATE_NOTE,
                "folder": "Notes",
                "noteTitle": "Context Index",
                "content": "Issue: {{Issue Title}}\nDate: {{Date}}\nBrief: {{Micro-Brief}}\n\nSummary:\nKey decisions:\nRelated threads:\nTags:\n\n---\n",
            },
        ],
    )

    # Save Chat Summary workflow
    save_chat_summary_workflow = WorkflowBlock(
        block_name="Save Chat Summary",
        description="Appends the summary of a finished atomic chat to the Context Index note.",
        actions=[
            {
                "type": ActionType.ASK_FOR_INPUT,
                "title": "Summary",
                "prompt": "Write a concise summary of the chat (context, progress, results).",
            },
            {
                "type": ActionType.ASK_FOR_INPUT,
                "title": "Key Decisions",
                "prompt": "List the key decisions made (comma separated).",
            },
            {
                "type": ActionType.ASK_FOR_INPUT,
                "title": "Related Threads",
                "prompt": "List related thread IDs or titles (comma separated).",
            },
            {
                "type": ActionType.ASK_FOR_INPUT,
                "title": "Tags",
                "prompt": "List tags or keywords for this chat (comma separated).",
            },
            {"type": ActionType.GET_DATE, "format": "YYYY-MM-DD HH:mm"},
            {
                "type": ActionType.APPEND_TO_NOTE,
                "noteTitle": "Context Index",
                "content": "Summary: {{Summary}}\nDate: {{Date}}\nKey decisions: {{Key Decisions}}\nRelated threads: {{Related Threads}}\nTags: {{Tags}}\n\n---\n",
            },
        ],
    )

    # Multi-Source Collection workflow
    multi_source_collection_workflow = WorkflowBlock(
        block_name="Multi-Source Collection",
        description="Configure and start multi-source intelligence collection with quality gates.",
        actions=[
            {
                "type": ActionType.ASK_FOR_INPUT,
                "title": "Collection Name",
                "prompt": "Enter a name for this collection run",
            },
            {
                "type": ActionType.ASK_FOR_INPUT,
                "title": "Target Sources",
                "prompt": "Enter source types to collect from (e.g., YouTube, Twitter, News)",
            },
            {"type": ActionType.GET_DATE, "format": "YYYY-MM-DD HH:mm"},
            {
                "type": ActionType.CREATE_NOTE,
                "folder": "Collections",
                "noteTitle": "Collection Log",
                "content": "Collection: {{Collection Name}}\nStart Time: {{Date}}\nSources: {{Target Sources}}\n\nStatus: Running\nItems Collected:\nQuality Metrics:\n\n---\n",
            },
        ],
    )

    # Quality Gate Check workflow
    quality_gate_check_workflow = WorkflowBlock(
        block_name="Quality Gate Check",
        description="Run quality gate checks on ingested data and record results.",
        actions=[
            {"type": ActionType.GET_DATE, "format": "YYYY-MM-DD HH:mm"},
            {
                "type": ActionType.ASK_FOR_INPUT,
                "title": "Items Count",
                "prompt": "Number of items ingested today",
            },
            {
                "type": ActionType.ASK_FOR_INPUT,
                "title": "Source Count",
                "prompt": "Number of active sources",
            },
            {
                "type": ActionType.ASK_FOR_INPUT,
                "title": "Quality Scores",
                "prompt": "Enter quality scores (relevance, timeliness, completeness)",
            },
            {
                "type": ActionType.APPEND_TO_NOTE,
                "noteTitle": "Quality Gate Log",
                "content": "Date: {{Date}}\nItems: {{Items Count}}\nSources: {{Source Count}}\nScores: {{Quality Scores}}\n\n---\n",
            },
        ],
    )

    engine.register_workflow(new_issue_chat_workflow)
    engine.register_workflow(save_chat_summary_workflow)
    engine.register_workflow(multi_source_collection_workflow)
    engine.register_workflow(quality_gate_check_workflow)

    print(f"Registered {len(engine.get_workflows())} workflows")


def _initialize_sample_sources(service: IngestionService):
    """Initialize sample data sources."""
    from app.models.ingestion import DataSourceType, DataTier

    # Create sample sources for demonstration
    sample_sources = [
        {"name": "YouTube Tech Channels", "type": DataSourceType.YOUTUBE, "tier": DataTier.TIER_1},
        {"name": "Twitter Intelligence", "type": DataSourceType.TWITTER, "tier": DataTier.TIER_1},
        {"name": "Tech News RSS", "type": DataSourceType.RSS, "tier": DataTier.TIER_2},
        {"name": "General News Feed", "type": DataSourceType.NEWS, "tier": DataTier.TIER_2},
        {"name": "Web Crawl", "type": DataSourceType.WEB, "tier": DataTier.TIER_3},
    ]

    for source_data in sample_sources:
        service.create_source(
            name=source_data["name"],
            source_type=source_data["type"],
            tier=source_data["tier"],
            rate_limit=100,
            cost_per_item=0.001,
        )

    print(f"Initialized {len(sample_sources)} sample data sources")


# Create FastAPI application
app = FastAPI(
    title="AI Issue Chat Workflow API",
    description="FastAPI service for managing AI-powered issue chat workflows with automation",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:8000"
    ).split(","),
    allow_credentials=True,
    allow_methods=os.environ.get("CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS,PATCH").split(","),
    allow_headers=os.environ.get(
        "CORS_HEADERS", "Content-Type,Authorization,X-Requested-With"
    ).split(","),
)


# Dependency overrides for service injection
def get_storage_service() -> StorageService:
    """Get the storage service instance."""
    return storage_service


def get_workflow_engine() -> WorkflowEngine:
    """Get the workflow engine instance."""
    return workflow_engine


def get_ingestion_service() -> IngestionService:
    """Get the ingestion service instance."""
    return ingestion_service


def get_gemini_service() -> GeminiService:
    """Get the Gemini service instance."""
    return gemini_service


# Override dependencies in route modules
workflows.get_workflow_engine = get_workflow_engine
notes.get_storage_service = get_storage_service
ingestion.get_ingestion_service = get_ingestion_service
gemini.get_gemini_service = get_gemini_service


# Include routers
app.include_router(health.router)
app.include_router(workflows.router)
app.include_router(notes.router)
app.include_router(ingestion.router)
app.include_router(gemini.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
