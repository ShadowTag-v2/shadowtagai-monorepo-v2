from fastapi import APIRouter
from ..models.contracts import ContextRequest, ContextResponse
from ..config import load_settings
from ..retrieval.context_builder import collect_context

router = APIRouter(prefix="/api")

@router.post("/context", response_model=ContextResponse)
def api_context(req: ContextRequest):
    s = load_settings()
    _, _, _, _, prompt_context, selected_ids = collect_context(
        s.sqlite_db, s.lancedb_root, s.postgres_dsn, req.repo_id, req.query, s.authority_state_path
    )
    return ContextResponse(query=req.query, repo_id=req.repo_id, prompt_context=prompt_context, selected_ids=selected_ids)
