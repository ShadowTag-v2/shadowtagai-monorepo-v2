# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Content Provenance Engine
Implements C2PA content credentials and provenance tracking
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from app.config import get_settings
from app.models.content import (
    C2PAAssertion,
    C2PAManifest,
    C2PAVerificationRequest,
    C2PAVerificationResponse,
    ContentProvenanceRequest,
    ContentProvenanceResponse,
    ContentType,
    WatermarkRequest,
    WatermarkResponse,
)

# Import ShadowTag tools
try:
    from src.pnkln.tools.shadowtag_tools import (
        shadowtag_embed_audio,
        shadowtag_embed_video,
        shadowtag_verify,
    )
except ImportError:
    try:
        from pnkln.tools.shadowtag_tools import (
            shadowtag_embed_audio,
            shadowtag_embed_video,
            shadowtag_verify,
        )
    except ImportError:
        # Fallback for when tools are not available
        def shadowtag_embed_video(*args, **kwargs):
            raise NotImplementedError("ShadowTag tools not found")

        def shadowtag_embed_audio(*args, **kwargs):
            raise NotImplementedError("ShadowTag tools not found")

        def shadowtag_verify(*args, **kwargs):
            raise NotImplementedError("ShadowTag tools not found")


# Import ShadowTag tools
try:
    from src.pnkln.tools.shadowtag_tools import (
        shadowtag_embed_audio,
        shadowtag_embed_video,
        shadowtag_verify,
    )
except ImportError:
    try:
        from pnkln.tools.shadowtag_tools import (
            shadowtag_embed_audio,
            shadowtag_embed_video,
            shadowtag_verify,
        )
    except ImportError:
        # Fallback for when tools are not available
        def shadowtag_embed_video(*args, **kwargs):
            raise NotImplementedError("ShadowTag tools not found")

        def shadowtag_embed_audio(*args, **kwargs):
            raise NotImplementedError("ShadowTag tools not found")

        def shadowtag_verify(*args, **kwargs):
            raise NotImplementedError("ShadowTag tools not found")


logger = logging.getLogger(__name__)
settings = get_settings()


class ContentEngine:
    """Content provenance and C2PA verification engine"""

    def __init__(self):
        self.persona_iq = settings.persona_iq_override
        self.provenance_store: dict[str, dict[str, Any]] = {}
        logger.info(f"Content Engine initialized with Persona IQ: {self.persona_iq}")

    async def verify_c2pa(self, request: C2PAVerificationRequest) -> C2PAVerificationResponse:
        """Verify C2PA content credentials

        Running at IQ {self.persona_iq} for thorough provenance analysis
        """
        logger.info(f"Verifying C2PA credentials at IQ {self.persona_iq}")

        # Simulate C2PA verification
        # In production, this would use actual C2PA SDK

        has_credentials = request.content_data is not None or request.content_url is not None

        if has_credentials:
            # Simulate manifest extraction
            manifest = C2PAManifest(
                claim_generator="Omega Content Engine v1.0",
                title="Content Provenance Record",
                format=request.content_type.value,
                instance_id=str(uuid.uuid4()),
                assertions=[
                    C2PAAssertion(
                        label="c2pa.actions",
                        data={"actions": [{"action": "c2pa.created"}]},
                        timestamp=datetime.utcnow(),
                    ),
                    C2PAAssertion(
                        label="c2pa.claim_creation",
                        data={"claim_generator": "Omega"},
                        timestamp=datetime.utcnow(),
                    ),
                ],
                signature="simulated_signature_hash",
            )

            # Check for AI generation
            ai_generated = any(
                "ai_generated" in str(assertion.data).lower() for assertion in manifest.assertions
            )

            # Check training permissions
            ai_training_allowed = True  # Default unless explicitly denied

            # Verify signature
            signature_valid = True  # Simulated

            # Check for tampering
            tampered = False

            # Build chain of custody
            chain_of_custody = [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "actor": "creator_001",
                    "action": "created",
                },
            ]

            verified = signature_valid and not tampered

        else:
            manifest = None
            ai_generated = False
            ai_training_allowed = True
            signature_valid = False
            tampered = False
            chain_of_custody = []
            verified = False

        errors = []
        if not has_credentials:
            errors.append("No C2PA credentials found")
        if not verified:
            errors.append("Verification failed")

        return C2PAVerificationResponse(
            verified=verified,
            has_credentials=has_credentials,
            manifest=manifest,
            chain_of_custody=chain_of_custody,
            ai_generated=ai_generated,
            ai_training_allowed=ai_training_allowed,
            errors=errors,
            tampered=tampered,
            signature_valid=signature_valid,
        )

    async def create_provenance(
        self,
        request: ContentProvenanceRequest,
    ) -> ContentProvenanceResponse:
        """Create content provenance record"""
        logger.info(f"Creating provenance record at IQ {self.persona_iq}")

        provenance_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        # Store provenance record
        provenance_record = {
            "provenance_id": provenance_id,
            "content_id": request.content_id,
            "content_type": request.content_type,
            "creator_id": request.creator_id,
            "action": request.action,
            "metadata": request.metadata,
            "parent_content_id": request.parent_content_id,
            "timestamp": timestamp,
        }

        self.provenance_store[request.content_id] = provenance_record

        # Generate manifest URL (simulated)
        manifest_url = f"https://omega.example/provenance/{provenance_id}/manifest.json"

        # Credential status
        credential_status = "active" if settings.c2pa_verification_enabled else "pending"

        # Blockchain transaction (if enabled)
        blockchain_tx = None
        if settings.blockchain_integration_enabled:
            blockchain_tx = f"0x{uuid.uuid4().hex}"

        return ContentProvenanceResponse(
            provenance_id=provenance_id,
            content_id=request.content_id,
            timestamp=timestamp,
            manifest_url=manifest_url,
            credential_status=credential_status,
            blockchain_tx=blockchain_tx,
        )

    async def get_provenance(self, content_id: str) -> ContentProvenanceResponse | None:
        """Get provenance record for content"""
        record = self.provenance_store.get(content_id)

        if not record:
            return None

        return ContentProvenanceResponse(
            provenance_id=record["provenance_id"],
            content_id=record["content_id"],
            timestamp=record["timestamp"],
            manifest_url=f"https://omega.example/provenance/{record['provenance_id']}/manifest.json",
            credential_status="active",
            blockchain_tx=record.get("blockchain_tx"),
        )

    async def attach_credentials(self, content_id: str, creator_id: str) -> dict[str, Any]:
        """Attach C2PA credentials to content"""
        logger.info(f"Attaching C2PA credentials at IQ {self.persona_iq}")

        manifest_id = str(uuid.uuid4())

        return {
            "content_id": content_id,
            "manifest_id": manifest_id,
            "credentials_attached": True,
            "signature": f"sig_{uuid.uuid4().hex[:16]}",
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_credential_status(self, content_id: str) -> dict[str, Any]:
        """Get C2PA credential status for content"""
        provenance = await self.get_provenance(content_id)

        if provenance:
            return {
                "content_id": content_id,
                "has_credentials": True,
                "status": provenance.credential_status,
                "manifest_url": provenance.manifest_url,
                "verified": True,
            }
        return {
            "content_id": content_id,
            "has_credentials": False,
            "status": "none",
            "manifest_url": None,
            "verified": False,
        }

    async def watermark_content(self, request: WatermarkRequest) -> WatermarkResponse:
        """Watermark content using ShadowTag"""
        logger.info(f"Watermarking content: {request.content_path} at IQ {self.persona_iq}")

        # Determine media type and apply watermark
        if request.content_type == ContentType.VIDEO:
            result_path = shadowtag_embed_video(
                video_path=request.content_path,
                watermark_data=request.metadata.get("payload", "default_payload"),
                output_path=request.output_path,
            )
        elif request.content_type == ContentType.AUDIO:
            result_path = shadowtag_embed_audio(
                audio_path=request.content_path,
                watermark_data=request.metadata.get("payload", "default_payload"),
                output_path=request.output_path,
            )
        else:
            raise ValueError(f"Unsupported content type for watermarking: {request.content_type}")

        # Verify immediately to ensure integrity
        verify_result = shadowtag_verify(
            media_path=result_path,
            media_type=request.content_type.value,
        )

        return WatermarkResponse(
            content_path=result_path,
            watermarked=verify_result["watermark_detected"],
            watermark_payload=verify_result["payload"],
            audit_trail=verify_result["audit_trail"],
            timestamp=datetime.utcnow(),
        )
