"""
MCP (Model Context Protocol) Server
Orchestrates multi-agent workflows for ShadowTag + ShadowTag-v4

Provides:
- Tool endpoints for agent capabilities
- Workflow orchestration
- Message routing between agents
- State management

Integration with Claude Code and other MCP clients
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.agents.ShadowTag-v2_neural_rank import ShadowTag-v2NeuralRankAgent
from src.agents.neural_hash import NeuralHashAgent
from src.protocols.agent_protocol import (
    AgentWorkflow,
    MediaAsset,
    create_ShadowTag-v2_content_workflow,
    create_shadowtag_upload_workflow,
)
from src.services.gemini_batch import GeminiBatchProcessor
from src.services.shadowtag_watermark import ShadowTagWatermarkService

logger = logging.getLogger(__name__)


# ============================================================================
# Request/Response Models
# ============================================================================


class ShadowTagUploadRequest(BaseModel):
    """Request to upload and authenticate media via ShadowTag"""

    asset_url: str = Field(..., description="URL to media asset")
    asset_type: str = Field(..., description="image, video, audio, document")
    title: str | None = None
    description: str | None = None
    creator_id: str = Field(..., description="Content creator ID")
    extracted_text: str | None = None


class ShadowTagUploadResponse(BaseModel):
    """Response from ShadowTag upload workflow"""

    asset_id: str
    neural_fingerprint_id: str
    watermark_id: str
    blockchain_receipt: str | None = None
    processing_time_ms: int
    cost_usd: float
    status: str


class ShadowTag-v2ContentRequest(BaseModel):
    """Request to ingest and rank content for ShadowTag-v4"""

    content_id: str | None = None
    title: str = Field(..., description="Content title")
    description: str | None = None
    text: str | None = None
    url: str | None = None
    source_type: str = Field(..., description="youtube, news, twitter, etc.")


class ShadowTag-v2ContentResponse(BaseModel):
    """Response from ShadowTag-v4 content workflow"""

    content_id: str
    ai_cognition_score: float
    ranking_tier: str
    category: str
    feed_position: int | None = None
    processing_time_ms: int
    cost_usd: float
    status: str


# ============================================================================
# MCP Server
# ============================================================================


class MCPServer:
    """
    MCP Server for ShadowTag + ShadowTag-v4 ecosystem

    Orchestrates multi-agent workflows:
    1. ShadowTag: OCR → Neural Hash → Watermark → Blockchain
    2. ShadowTag-v4: Ingest → Embed → Rank → Feed

    Provides MCP-compatible tool endpoints for external integration
    """

    def __init__(self, gemini_api_key: str, app: FastAPI | None = None):
        """
        Initialize MCP Server

        Args:
            gemini_api_key: Google AI API key for Gemini
            app: Optional existing FastAPI app to attach to
        """
        self.app = app or FastAPI(
            title="ShadowTag-v4 MCP Server",
            description="Model Context Protocol server for ShadowTag + ShadowTag-v4 agents",
            version="1.0.0",
        )

        # Initialize shared batch processor
        self.batch_processor = GeminiBatchProcessor(api_key=gemini_api_key, batch_size=100)

        # Initialize agents and services
        self.neural_hash_agent = NeuralHashAgent(
            gemini_api_key=gemini_api_key, batch_processor=self.batch_processor
        )
        self.watermark_service = ShadowTagWatermarkService()
        self.neural_rank_agent = ShadowTag-v2NeuralRankAgent(
            gemini_api_key=gemini_api_key, batch_processor=self.batch_processor
        )

        # Workflow state storage (in-memory, would use Redis/DB in production)
        self.workflows: dict[str, AgentWorkflow] = {}
        self.assets: dict[str, MediaAsset] = {}

        # Register routes
        self._register_routes()

        logger.info("MCPServer initialized with all agents")

    def _register_routes(self):
        """Register FastAPI routes for MCP tools"""

        @self.app.post(
            "/mcp/tools/shadowtag/upload",
            response_model=ShadowTagUploadResponse,
            tags=["ShadowTag"],
        )
        async def shadowtag_upload(request: ShadowTagUploadRequest):
            """
            ShadowTag upload workflow

            Process: OCR → Neural Hash → Watermark → Blockchain

            Returns authenticated media asset with neural fingerprint
            """
            return await self.execute_shadowtag_upload(request)

        @self.app.post("/mcp/tools/shadowtag/verify", tags=["ShadowTag"])
        async def shadowtag_verify(asset_id: str):
            """
            Verify ShadowTag watermark and neural fingerprint

            Returns verification result with confidence score
            """
            return await self.verify_shadowtag(asset_id)

        @self.app.post(
            "/mcp/tools/shadowtag_v4/ingest",
            response_model=ShadowTag-v2ContentResponse,
            tags=["ShadowTag-v4"],
        )
        async def ShadowTag-v2_ingest(request: ShadowTag-v2ContentRequest):
            """
            ShadowTag-v4 content ingestion workflow

            Process: Ingest → Embed → Rank → Feed

            Returns AI-cognition score and ranking tier
            """
            return await self.execute_ShadowTag-v2_ingestion(request)

        @self.app.get("/mcp/tools/shadowtag_v4/feed", tags=["ShadowTag-v4"])
        async def ShadowTag-v2_feed(tier: str | None = None, limit: int = 50):
            """
            Get ShadowTag-v4 feed ranked by AI-cognition

            Returns top-ranked content (not engagement-based)
            """
            return await self.get_ShadowTag-v2_feed(tier, limit)

        @self.app.get("/mcp/workflows/{workflow_id}", tags=["Workflows"])
        async def get_workflow_status(workflow_id: str):
            """Get workflow execution status"""
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")
            return workflow.dict()

        @self.app.get("/mcp/health", tags=["Health"])
        async def health_check():
            """MCP server health check"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "agents": {
                    "neural_hash": "operational",
                    "watermark": "operational",
                    "neural_rank": "operational",
                },
                "workflows_active": len(self.workflows),
                "assets_stored": len(self.assets),
            }

    async def execute_shadowtag_upload(
        self, request: ShadowTagUploadRequest
    ) -> ShadowTagUploadResponse:
        """
        Execute ShadowTag upload workflow

        Steps:
        1. Create MediaAsset
        2. Generate neural fingerprint
        3. Embed watermark
        4. Record blockchain receipt (simulated)
        """
        start_time = datetime.utcnow()

        # Create asset
        asset = MediaAsset(
            asset_type=request.asset_type,
            url=request.asset_url,
            title=request.title,
            description=request.description,
            extracted_text=request.extracted_text,
            creator_id=request.creator_id,
        )

        # Store asset
        self.assets[asset.asset_id] = asset

        # Create workflow
        workflow = create_shadowtag_upload_workflow(asset)
        self.workflows[workflow.workflow_id] = workflow
        workflow.status = "running"
        workflow.started_at = datetime.utcnow()

        logger.info(f"Starting ShadowTag upload workflow: {workflow.workflow_id}")

        try:
            # Step 1: Neural fingerprint generation
            fingerprint = await self.neural_hash_agent.generate_fingerprint(asset)
            asset.neural_fingerprint = fingerprint.dict()
            workflow.mark_step_completed({"fingerprint_id": fingerprint.fingerprint_id})
            workflow.advance_step()

            # Step 2: Watermark embedding
            watermarked_asset, watermark_data = await self.watermark_service.embed_watermark(
                asset, request.creator_id, neural_fingerprint_id=fingerprint.fingerprint_id
            )
            workflow.mark_step_completed({"watermark_id": watermark_data.watermark_id})
            workflow.advance_step()

            # Step 3: Blockchain receipt (simulated)
            blockchain_hash = await self._record_blockchain_receipt(
                asset, fingerprint, watermark_data
            )
            asset.blockchain_receipt = blockchain_hash
            workflow.mark_step_completed({"blockchain_hash": blockchain_hash})
            workflow.advance_step()

            # Workflow complete
            workflow.status = "completed"
            workflow.completed_at = datetime.utcnow()

            # Update asset
            self.assets[asset.asset_id] = watermarked_asset

            # Calculate metrics
            end_time = datetime.utcnow()
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            cost_usd = 0.002 + 0.001  # Neural hash + watermark

            logger.info(
                f"✓ ShadowTag upload completed: {asset.asset_id} "
                f"({processing_time_ms}ms, ${cost_usd:.3f})"
            )

            return ShadowTagUploadResponse(
                asset_id=asset.asset_id,
                neural_fingerprint_id=fingerprint.fingerprint_id,
                watermark_id=watermark_data.watermark_id,
                blockchain_receipt=blockchain_hash,
                processing_time_ms=processing_time_ms,
                cost_usd=cost_usd,
                status="completed",
            )

        except Exception as e:
            workflow.status = "failed"
            workflow.completed_at = datetime.utcnow()
            logger.error(f"ShadowTag upload failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def verify_shadowtag(self, asset_id: str) -> dict[str, Any]:
        """Verify ShadowTag authentication"""

        asset = self.assets.get(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        # Verify watermark
        watermark_result = await self.watermark_service.verify_watermark(asset)

        # Verify neural fingerprint (would compare against stored fingerprint)
        fingerprint_verified = asset.neural_fingerprint is not None

        return {
            "asset_id": asset_id,
            "watermark_verified": watermark_result["is_watermarked"],
            "fingerprint_verified": fingerprint_verified,
            "blockchain_verified": asset.blockchain_receipt is not None,
            "overall_confidence": watermark_result.get("confidence", 0.0),
            "creator_id": asset.creator_id,
            "created_at": asset.created_at.isoformat(),
        }

    async def execute_ShadowTag-v2_ingestion(self, request: ShadowTag-v2ContentRequest) -> ShadowTag-v2ContentResponse:
        """
        Execute ShadowTag-v4 content ingestion workflow

        Steps:
        1. Create content record
        2. Generate embeddings
        3. Compute AI-cognition score
        4. Add to ranked feed
        """
        start_time = datetime.utcnow()

        # Create content dict
        content = {
            "id": request.content_id or f"content_{datetime.utcnow().timestamp()}",
            "title": request.title,
            "description": request.description,
            "text": request.text,
            "url": request.url,
            "source_type": request.source_type,
        }

        # Create workflow
        workflow = create_ShadowTag-v2_content_workflow(content)
        self.workflows[workflow.workflow_id] = workflow
        workflow.status = "running"
        workflow.started_at = datetime.utcnow()

        logger.info(f"Starting ShadowTag-v4 ingestion workflow: {workflow.workflow_id}")

        try:
            # Step 1: Generate embeddings (via batch processor)
            text = f"{request.title} {request.description or ''} {request.text or ''}"
            embeddings = await self.batch_processor.embed_documents_batch([text])
            workflow.mark_step_completed({"embeddings_generated": 1})
            workflow.advance_step()

            # Step 2: Compute AI-cognition score
            score = await self.neural_rank_agent.rank_content(content)
            workflow.mark_step_completed({"score": score.overall_score})
            workflow.advance_step()

            # Step 3: Add to feed (simulated)
            feed_position = await self._add_to_feed(content, score)
            workflow.mark_step_completed({"feed_position": feed_position})
            workflow.advance_step()

            # Workflow complete
            workflow.status = "completed"
            workflow.completed_at = datetime.utcnow()

            # Calculate metrics
            end_time = datetime.utcnow()
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            cost_usd = 0.002 + 0.003  # Embedding + ranking

            logger.info(
                f"✓ ShadowTag-v4 ingestion completed: {content['id']} "
                f"(score={score.overall_score}, tier={score.tier}, "
                f"${cost_usd:.3f})"
            )

            return ShadowTag-v2ContentResponse(
                content_id=content["id"],
                ai_cognition_score=score.overall_score,
                ranking_tier=score.tier.value,
                category=score.category.value,
                feed_position=feed_position,
                processing_time_ms=processing_time_ms,
                cost_usd=cost_usd,
                status="completed",
            )

        except Exception as e:
            workflow.status = "failed"
            workflow.completed_at = datetime.utcnow()
            logger.error(f"ShadowTag-v4 ingestion failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_ShadowTag-v2_feed(self, tier: str | None = None, limit: int = 50) -> dict[str, Any]:
        """Get ShadowTag-v4 ranked feed"""

        # TODO: Implement actual feed retrieval from database
        # For now, return mock feed

        return {
            "feed": [],
            "tier_filter": tier,
            "total_items": 0,
            "limit": limit,
            "ranking_method": "ai_cognition",
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def _record_blockchain_receipt(
        self, asset: MediaAsset, fingerprint: Any, watermark: Any
    ) -> str:
        """
        Record blockchain receipt (simulated)

        In production, would:
        1. Create hash of (asset_id + fingerprint + watermark)
        2. Submit to blockchain (e.g., Ethereum, Polygon)
        3. Return transaction hash
        """
        import hashlib

        receipt_data = f"{asset.asset_id}:{fingerprint.fingerprint_id}:{watermark.watermark_id}"
        receipt_hash = hashlib.sha256(receipt_data.encode()).hexdigest()

        # Simulate blockchain submission
        await asyncio.sleep(0.1)

        blockchain_hash = f"0x{receipt_hash}"

        logger.info(f"Blockchain receipt recorded: {blockchain_hash}")

        return blockchain_hash

    async def _add_to_feed(self, content: dict[str, Any], score: Any) -> int:
        """
        Add content to ShadowTag-v4 feed

        In production, would:
        1. Insert into feed database
        2. Update rankings
        3. Trigger feed refresh for subscribers
        """

        # Simulate feed insertion
        await asyncio.sleep(0.05)

        # Mock feed position based on score
        if score.overall_score >= 85:
            position = 1
        elif score.overall_score >= 75:
            position = 10
        elif score.overall_score >= 60:
            position = 50
        else:
            position = 100

        return position


# ============================================================================
# Factory Function
# ============================================================================


def create_mcp_server(gemini_api_key: str) -> FastAPI:
    """
    Factory function to create MCP server

    Usage:
        app = create_mcp_server(gemini_api_key="...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    """
    mcp = MCPServer(gemini_api_key=gemini_api_key)
    return mcp.app
