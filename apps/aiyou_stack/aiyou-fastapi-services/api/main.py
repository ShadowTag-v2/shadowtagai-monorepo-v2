"""Main FastAPI application for ShadowTag v2."""

import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from shadowtag_v2 import __version__
from shadowtag_v2.audio_stego import (
    AudioWatermarkConfig,
    embed_audio_watermark,
    extract_audio_watermark,
)
from shadowtag_v2.receipt_chain import BlockchainConfig, ChainType, create_blockchain_receipt
from shadowtag_v2.video_stego import (
    VideoWatermarkConfig,
    embed_video_watermark,
    extract_video_watermark,
)

from api.config import settings
from api.models import (
    EmbedRequest,
    EmbedResponse,
    ErrorResponse,
    HealthResponse,
    MediaType,
    VerifyRequest,
    VerifyResponse,
)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Dual-layer steganographic watermarking API for content authenticity",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Ensure directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.output_dir, exist_ok=True)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=__version__,
        blockchain_enabled=settings.blockchain_enabled,
        vertex_enabled=settings.vertex_enabled,
    )


@app.post(
    f"{settings.api_prefix}/embed",
    response_model=EmbedResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["Watermarking"],
)
async def embed_watermark(
    file: UploadFile = File(..., description="Video or audio file to watermark"),
    request: EmbedRequest = None,
) -> EmbedResponse:
    """Embed watermark into video or audio file.

    - **file**: Video or audio file (MP4, WAV, etc.)
    - **prompt**: Prompt text to embed as watermark
    - **media_type**: Type of media (video or audio)
    - **create_receipt**: Whether to create blockchain receipt
    - **chain**: Blockchain network (if create_receipt=true)
    """
    # Validate file size
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {settings.max_upload_size_mb} MB limit",
        )

    # Save uploaded file
    input_path = Path(settings.upload_dir) / file.filename
    with open(input_path, "wb") as f:
        f.write(content)

    try:
        # Determine output filename
        output_filename = f"watermarked_{file.filename}"
        output_path = Path(settings.output_dir) / output_filename

        # Embed watermark based on media type
        if request.media_type == MediaType.VIDEO:
            config = VideoWatermarkConfig()
            result = embed_video_watermark(input_path, output_path, request.prompt, config)
        elif request.media_type == MediaType.AUDIO:
            config = AudioWatermarkConfig()
            result = embed_audio_watermark(input_path, output_path, request.prompt, config)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported media type: {request.media_type}",
            )

        # Create blockchain receipt if requested
        receipt = None
        if request.create_receipt and settings.blockchain_enabled:
            if not request.chain:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Chain must be specified when create_receipt=true",
                )

            blockchain_config = BlockchainConfig(
                chain=ChainType(request.chain.value),
                gcp_secret_name=settings.gcp_secret_name,
                gcp_project_id=settings.gcp_project_id,
            )

            receipt = create_blockchain_receipt(
                request.prompt,
                blockchain_config,
                metadata={"media_type": request.media_type.value, "filename": file.filename},
            )

        return EmbedResponse(
            ok=True,
            message="Watermark embedded successfully",
            output_filename=output_filename,
            watermark_result=result,
            blockchain_receipt=receipt,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding failed: {e!s}",
        )
    finally:
        # Cleanup input file
        if input_path.exists():
            input_path.unlink()


@app.post(
    f"{settings.api_prefix}/verify",
    response_model=VerifyResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["Watermarking"],
)
async def verify_watermark(
    file: UploadFile = File(..., description="Watermarked video or audio file"),
    request: VerifyRequest = None,
) -> VerifyResponse:
    """Verify watermark in video or audio file.

    - **file**: Watermarked video or audio file
    - **expected_prompt**: Expected prompt text
    - **media_type**: Type of media (video or audio)
    - **verify_receipt**: Whether to verify blockchain receipt
    - **chain**: Blockchain network (if verify_receipt=true)
    - **tx_hash**: Transaction hash to verify (if verify_receipt=true)
    """
    # Validate file size
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {settings.max_upload_size_mb} MB limit",
        )

    # Save uploaded file
    input_path = Path(settings.upload_dir) / file.filename
    with open(input_path, "wb") as f:
        f.write(content)

    try:
        # Extract and verify watermark
        if request.media_type == MediaType.VIDEO:
            config = VideoWatermarkConfig()
            result = extract_video_watermark(input_path, request.expected_prompt, config)
        elif request.media_type == MediaType.AUDIO:
            config = AudioWatermarkConfig()
            result = extract_audio_watermark(input_path, request.expected_prompt, config)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported media type: {request.media_type}",
            )

        verified = result.get("verified", False)
        message = "Watermark verified successfully" if verified else "Watermark verification failed"

        # Verify blockchain receipt if requested
        receipt_result = None
        if request.verify_receipt and request.tx_hash:
            from shadowtag_v2.receipt_chain import verify_blockchain_receipt

            blockchain_config = BlockchainConfig(chain=ChainType(request.chain.value))
            receipt_result = verify_blockchain_receipt(
                request.tx_hash,
                request.expected_prompt,
                blockchain_config,
            )

        return VerifyResponse(
            ok=True,
            verified=verified,
            message=message,
            extracted_hash=result["extracted_hash"],
            expected_hash=result.get("expected_hash"),
            bit_error_rate=result.get("bit_error_rate"),
            blockchain_receipt=receipt_result,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {e!s}",
        )
    finally:
        # Cleanup input file
        if input_path.exists():
            input_path.unlink()


@app.get(
    f"{settings.api_prefix}/download/{{filename}}",
    response_class=FileResponse,
    tags=["Files"],
)
async def download_file(filename: str) -> FileResponse:
    """Download watermarked file."""
    file_path = Path(settings.output_dir) / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {filename}",
        )

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail).model_dump(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
