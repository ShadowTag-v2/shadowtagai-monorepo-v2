# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi import FastAPI
from pydantic import BaseModel

# from services import orchestrate # commented out until implementation

app = FastAPI()


class Query(BaseModel):
    q: str
    user_id: str | None = None
    mode: str = "default"  # or "code", "doc", "image"


@app.post("/search")
async def search(q: Query):
    # result = await orchestrate.run_all(q.q, q.user_id, mode=q.mode)
    # return result
    return {"status": "placeholder", "message": "Orchestrator not yet linked"}
