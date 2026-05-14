# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import sys
from pathlib import Path

# Add src to path to import memory storage
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

try:
    from aiyou.memory.storage import MemoryStorage
except ImportError:
    # Mock if src not found
    class MemoryStorage:
        def load_from_gcs(self):
            return {"status": "mock_gcs"}

        def load_from_firestore(self):
            return {"status": "mock_firestore"}


app = FastAPI(title="Antigravity API", version="0.1.0")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "Antigravity API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": ["/memory/gcs", "/memory/firestore", "/health"],
    }


class MemoryResponse(BaseModel):
    data: dict[str, Any]
    source: str


@app.get("/memory/gcs", response_model=MemoryResponse)
async def get_gcs_memory():
    storage = MemoryStorage()
    data = storage.load_from_gcs()
    return MemoryResponse(data=data, source="gcs")


@app.get("/memory/firestore", response_model=MemoryResponse)
async def get_firestore_memory():
    storage = MemoryStorage()
    data = storage.load_from_firestore()
    return MemoryResponse(data=data, source="firestore")


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
