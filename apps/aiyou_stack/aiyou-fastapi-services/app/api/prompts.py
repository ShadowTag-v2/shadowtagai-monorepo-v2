# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Prompt management API endpoints."""

import structlog
from fastapi import APIRouter, HTTPException

from app.schemas.chat import PromptRenderRequest, PromptTemplateCreate
from app.services.prompt_manager import PromptManager, PromptTemplate

logger = structlog.get_logger()
router = APIRouter(prefix="/prompts", tags=["prompts"])

# Global prompt manager instance
prompt_manager = None


def get_prompt_manager() -> PromptManager:
    """Get or create prompt manager instance."""
    global prompt_manager
    if prompt_manager is None:
        prompt_manager = PromptManager()
    return prompt_manager


@router.get("/templates", response_model=list[str])
async def list_templates():
    """List all available prompt templates."""
    try:
        manager = get_prompt_manager()
        templates = manager.list_templates()

        return templates

    except Exception as e:
        logger.error("List templates failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/templates/{template_name}")
async def get_template(template_name: str):
    """Get a specific prompt template by name."""
    try:
        manager = get_prompt_manager()
        template = manager.get_template(template_name)

        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {template_name}")

        return template.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Get template failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/templates")
async def create_template(request: PromptTemplateCreate):
    """Create a new prompt template."""
    try:
        manager = get_prompt_manager()

        template = PromptTemplate(
            name=request.name,
            template=request.template,
            description=request.description,
            variables=request.variables,
            metadata=request.metadata,
        )

        manager.add_template(template)

        return {"message": "Template created successfully", "template_name": request.name}

    except Exception as e:
        logger.error("Create template failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.delete("/templates/{template_name}")
async def delete_template(template_name: str):
    """Delete a prompt template."""
    try:
        manager = get_prompt_manager()
        deleted = manager.remove_template(template_name)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Template not found: {template_name}")

        return {"message": "Template deleted successfully", "template_name": template_name}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Delete template failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/render")
async def render_template(request: PromptRenderRequest):
    """Render a prompt template with provided variables."""
    try:
        manager = get_prompt_manager()

        rendered = manager.render_template(request.template_name, **request.variables)

        return {
            "template_name": request.template_name,
            "rendered_prompt": rendered,
            "variables": request.variables,
        }

    except ValueError as e:
        logger.error("Render template failed - validation error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Render template failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/templates/export")
async def export_templates(filepath: str):
    """Export all templates to a JSON file."""
    try:
        manager = get_prompt_manager()
        manager.export_templates(filepath)

        return {"message": "Templates exported successfully", "filepath": filepath}

    except Exception as e:
        logger.error("Export templates failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/templates/import")
async def import_templates(filepath: str):
    """Import templates from a JSON file."""
    try:
        manager = get_prompt_manager()
        manager.import_templates(filepath)

        return {"message": "Templates imported successfully", "filepath": filepath}

    except Exception as e:
        logger.error("Import templates failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error") from e
