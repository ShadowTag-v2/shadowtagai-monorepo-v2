import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.governance.judge_six.sentinel import JudgeSixSentinel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(
    title="UphillSnowball Sovereign OS",
    version="1.0.0",
    description="The internal engine powering CounselConduit and ShadowTag AI products",
)

# CORS for CounselConduit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://kovelai.com",
        "https://shadowtagai.com",
        "http://localhost:3000",
    ],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

judge = JudgeSixSentinel()


class MissionRequest(BaseModel):
    query: str
    context: str = "general"


class RAGQueryRequest(BaseModel):
    question: str
    top_k: int = 5
    table_name: str = "shadowtag_docs"


@app.get("/health")
async def health_check():
    """Cloud Run health check endpoint."""
    return {
        "status": "healthy",
        "service": "uphillsnowball-sovereign",
        "version": "1.0.0",
    }


@app.post("/mission")
async def launch_mission(req: MissionRequest):
    """The Single Entrypoint.
    Guarded by Judge #6 and the 650-Unit Army.
    """
    # 1. Governance Gate
    verdict = judge.evaluate(req.query, req.context)

    if verdict["status"] == "BLOCKED":
        raise HTTPException(status_code=403, detail=verdict)

    # 2. Execution (Placeholder for Agent Logic)
    return {
        "status": "MISSION_GO",
        "governance_receipt": verdict,
        "payload": f"Executing: {req.query}",
    }


@app.post("/rag/query")
async def rag_query(req: RAGQueryRequest):
    """RAG endpoint — wires CounselConduit to UphillSnowball's LanceDB pipeline.

    This is the bridge: CounselConduit sends legal queries here,
    UphillSnowball retrieves context from LanceDB and generates answers.
    """
    try:
        # Lazy import to avoid loading ML models at startup
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        from src.rag.lancedb_pipeline import RAGPipeline

        pipeline = RAGPipeline(table_name=req.table_name)
        result = pipeline.query(req.question, top_k=req.top_k)

        return {
            "status": "ok",
            "answer": result["answer"],
            "sources": result["sources"],
            "num_sources": result["num_sources"],
        }
    except ImportError as e:
        logger.error("RAG pipeline not available: %s", e)
        raise HTTPException(
            status_code=503,
            detail=f"RAG pipeline not available: {e}",
        )
    except Exception as e:
        logger.error("RAG query failed: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"RAG query error: {e}",
        )


@app.get("/rag/stats")
async def rag_stats():
    """Return LanceDB pipeline statistics."""
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        from src.rag.lancedb_pipeline import RAGPipeline

        pipeline = RAGPipeline()
        return pipeline.stats()
    except Exception as e:
        return {"error": str(e), "status": "unavailable"}


@app.on_event("startup")
async def startup_event():
    """Log startup info."""
    logger.info("UphillSnowball Sovereign OS v1.0.0 — starting")
    logger.info("GCP Project: %s", os.environ.get("GCP_PROJECT", "shadowtag-omega-v4"))
    logger.info("Port: %s", os.environ.get("PORT", "8080"))


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

