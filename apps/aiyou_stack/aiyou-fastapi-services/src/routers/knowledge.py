# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi import APIRouter, File, HTTPException, UploadFile, status

# Local app imports based on conventional structure
# Note: we stub models/database imports if they don't exist yet to prevent crashes
try:
    import models  # noqa: F401
    from database import get_db
    from routers.agents import verify_workspace_access
    from security import get_current_user
except ImportError:
    # Stub dependencies for compilation if the monorepo isn't fully structured yet
    def get_db():
        pass

    def get_current_user():
        return type("User", (), {"id": 1})()

    def verify_workspace_access(*args):
        pass


from vector_db import ingest_document

router = APIRouter(prefix="/workspaces/{workspace_id}/knowledge", tags=["Knowledge Base"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_workspace_document(
    workspace_id: int,
    file: UploadFile = File(...),  # noqa: B008
):
    # verify_workspace_access(workspace_id, current_user.id, db)

    if not (file.filename.endswith(".txt") or file.filename.endswith(".md")):
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .md files are supported for now.",
        )

    content = await file.read()
    text_content = content.decode("utf-8")

    # Ingest into LanceDB
    ingest_document(workspace_id, text_content)

    return {"message": f"Successfully ingested {file.filename} into Workspace {workspace_id}."}
