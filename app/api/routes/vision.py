# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Computer vision API routes - Tegu integration."""

import time
import tempfile
import base64
from pathlib import Path
from fastapi import APIRouter, HTTPException
import structlog

from app.models.vision import (
  ImageClassificationRequest,
  ImageClassificationResponse,
  ClassificationResult,
  ObjectDetectionRequest,
  ObjectDetectionResponse,
  DetectedObject,
  BoundingBox,
  FaceRecognitionRequest,
  FaceRecognitionResponse,
  RecognizedFace,
  VideoClassificationRequest,
  VideoClassificationResponse,
  VideoClass,
  BuildFeatureLibraryRequest,
  BuildFeatureLibraryResponse,
)
from app.services.vision.tegu_client import TeguClient

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/cv", tags=["Computer Vision"])


@router.post("/classify-image", response_model=ImageClassificationResponse)
async def classify_image(request: ImageClassificationRequest):
  """
  Classify image using pre-trained models.

  Supports:
  - ResNet-50, VGG-16, Inception-v3
  - ImageNet 1000-class classification
  - GPU acceleration (if available)
  """
  start_time = time.perf_counter()

  try:
    # Download or decode image
    image_path = await _prepare_image(request.image_url, request.image_base64)

    # Initialize Tegu client
    tegu = TeguClient(model=request.model, gpu=True)

    # Run classification
    predictions = await tegu.classify_image(image_path, top_k=request.top_k)

    latency_ms = (time.perf_counter() - start_time) * 1000

    # Map to response model
    results = [
      ClassificationResult(
        class_id=pred["class_id"],
        class_name=pred["class"],
        confidence=pred["confidence"],
      )
      for pred in predictions
    ]

    logger.info(
      "image_classified",
      model=request.model,
      top_class=results[0].class_name,
      confidence=results[0].confidence,
      latency_ms=latency_ms,
    )

    return ImageClassificationResponse(
      predictions=results,
      model=request.model,
      latency_ms=latency_ms,
    )

  except Exception as e:
    logger.error("image_classification_failed", error=str(e), model=request.model)
    raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

  finally:
    # Cleanup temporary image
    if image_path and Path(image_path).exists():
      Path(image_path).unlink()


@router.post("/detect-objects", response_model=ObjectDetectionResponse)
async def detect_objects(request: ObjectDetectionRequest):
  """
  Detect objects in image using YOLO or SSD.

  Returns:
  - Bounding boxes for detected objects
  - Class labels and confidence scores
  - Supports 80 COCO classes (person, car, dog, etc.)
  """
  start_time = time.perf_counter()

  try:
    # Download or decode image
    image_path = await _prepare_image(request.image_url, request.image_base64)

    # Get image dimensions
    from PIL import Image

    img = Image.open(image_path)
    image_dimensions = {"width": img.width, "height": img.height}

    # Initialize Tegu client
    tegu = TeguClient(model=request.model, gpu=True)

    # Run object detection
    detections = await tegu.detect_objects(
      image_path,
      confidence_threshold=request.confidence_threshold,
    )

    latency_ms = (time.perf_counter() - start_time) * 1000

    # Map to response model
    objects = [
      DetectedObject(
        class_id=det["class_id"],
        class_name=det["class"],
        confidence=det["confidence"],
        bbox=BoundingBox(
          x=det["bbox"][0],
          y=det["bbox"][1],
          width=det["bbox"][2],
          height=det["bbox"][3],
        ),
      )
      for det in detections
    ]

    logger.info(
      "objects_detected",
      model=request.model,
      object_count=len(objects),
      latency_ms=latency_ms,
    )

    return ObjectDetectionResponse(
      objects=objects,
      model=request.model,
      latency_ms=latency_ms,
      image_dimensions=image_dimensions,
    )

  except Exception as e:
    logger.error("object_detection_failed", error=str(e), model=request.model)
    raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

  finally:
    if image_path and Path(image_path).exists():
      Path(image_path).unlink()


@router.post("/recognize-faces", response_model=FaceRecognitionResponse)
async def recognize_faces(request: FaceRecognitionRequest):
  """
  Recognize faces in image.

  Features:
  - Face detection with Haar cascade
  - Face embeddings with FaceNet/VGGFace
  - Matching against feature library
  - Returns bounding boxes and identities
  """
  start_time = time.perf_counter()

  try:
    # Download or decode image
    image_path = await _prepare_image(request.image_url, request.image_base64)

    # Load feature library (if provided)
    feature_library = None
    if request.feature_library_id:
      feature_library = await _load_feature_library(request.feature_library_id)

    # Initialize Tegu client
    tegu = TeguClient(model=request.model, gpu=True)

    # Run face recognition
    faces = await tegu.recognize_faces(
      image_path,
      feature_library=feature_library,
      threshold=request.threshold,
    )

    latency_ms = (time.perf_counter() - start_time) * 1000

    # Map to response model
    recognized_faces = [
      RecognizedFace(
        name=face["name"],
        confidence=face["confidence"],
        bbox=BoundingBox(
          x=face["bbox"][0],
          y=face["bbox"][1],
          width=face["bbox"][2],
          height=face["bbox"][3],
        ),
        embedding=face.get("embedding"),
      )
      for face in faces
    ]

    logger.info(
      "faces_recognized",
      model=request.model,
      face_count=len(recognized_faces),
      latency_ms=latency_ms,
    )

    return FaceRecognitionResponse(
      faces=recognized_faces,
      model=request.model,
      latency_ms=latency_ms,
    )

  except Exception as e:
    logger.error("face_recognition_failed", error=str(e), model=request.model)
    raise HTTPException(status_code=500, detail=f"Recognition failed: {str(e)}")

  finally:
    if image_path and Path(image_path).exists():
      Path(image_path).unlink()


@router.post("/classify-video", response_model=VideoClassificationResponse)
async def classify_video(request: VideoClassificationRequest):
  """
  Classify video by sampling frames.

  Process:
  1. Sample every N frames
  2. Classify each sampled frame
  3. Aggregate predictions across frames
  4. Return top classes with frame counts
  """
  start_time = time.perf_counter()

  try:
    # Download video
    video_path = await _download_video(request.video_url)

    # Initialize Tegu client
    tegu = TeguClient(model=request.model, gpu=True)

    # Run video classification
    result = await tegu.classify_video(
      video_path,
      sample_rate=request.sample_rate,
      top_k=request.top_k,
    )

    latency_ms = (time.perf_counter() - start_time) * 1000

    # Map to response model
    top_classes = [
      VideoClass(
        class_name=cls["class"],
        confidence=cls["confidence"],
        frame_count=cls["frame_count"],
      )
      for cls in result["top_classes"]
    ]

    logger.info(
      "video_classified",
      model=request.model,
      duration=result["duration_seconds"],
      top_class=top_classes[0].class_name if top_classes else None,
      latency_ms=latency_ms,
    )

    return VideoClassificationResponse(
      duration_seconds=result["duration_seconds"],
      total_frames=result["total_frames"],
      sampled_frames=result["sampled_frames"],
      top_classes=top_classes,
      model=request.model,
      latency_ms=latency_ms,
    )

  except Exception as e:
    logger.error("video_classification_failed", error=str(e), model=request.model)
    raise HTTPException(
      status_code=500, detail=f"Video classification failed: {str(e)}"
    )

  finally:
    if video_path and Path(video_path).exists():
      Path(video_path).unlink()


@router.post("/build-feature-library", response_model=BuildFeatureLibraryResponse)
async def build_feature_library(request: BuildFeatureLibraryRequest):
  """
  Build face feature library for recognition.

  Process:
  1. Download face images
  2. Extract face embeddings with FaceNet/VGGFace
  3. Store embeddings in Hive (GCS)
  4. Return library ID for use in recognize-faces
  """
  time.perf_counter()

  try:
    # Initialize Tegu client
    tegu = TeguClient(model=request.model, gpu=True)

    # Extract embeddings for each face
    feature_library = {}
    for face_data in request.faces:
      name = face_data["name"]
      image_url = face_data["image_url"]

      # Download image
      image_path = await _download_image(image_url)

      # Extract embedding
      faces = await tegu.recognize_faces(
        image_path, feature_library=None, threshold=0.0
      )
      if faces:
        feature_library[name] = faces[0].get("embedding")

      # Cleanup
      if Path(image_path).exists():
        Path(image_path).unlink()

    # Store feature library in Hive
    storage_path = await _store_feature_library(request.library_id, feature_library)

    logger.info(
      "feature_library_built",
      library_id=request.library_id,
      face_count=len(feature_library),
      storage_path=storage_path,
    )

    return BuildFeatureLibraryResponse(
      library_id=request.library_id,
      face_count=len(feature_library),
      model=request.model,
      storage_path=storage_path,
    )

  except Exception as e:
    logger.error(
      "feature_library_build_failed", error=str(e), library_id=request.library_id
    )
    raise HTTPException(
      status_code=500, detail=f"Feature library build failed: {str(e)}"
    )


@router.get("/models")
async def list_models():
  """List available computer vision models."""
  return {
    "models": {
      "image_classification": ["resnet50", "vgg16", "inception_v3"],
      "object_detection": ["yolo_v3", "ssd_mobilenet"],
      "face_recognition": ["facenet", "vggface"],
      "video_classification": ["resnet50", "vgg16", "3d_cnn"],
    }
  }


# Helper functions


async def _prepare_image(image_url: str | None, image_base64: str | None) -> str:
  """Download or decode image to temporary file."""
  if image_url:
    return await _download_image(image_url)
  elif image_base64:
    return await _decode_base64_image(image_base64)
  else:
    raise ValueError("Either image_url or image_base64 must be provided")


async def _download_image(url: str) -> str:
  """Download image from URL to temporary file."""
  import httpx

  async with httpx.AsyncClient() as client:
    response = await client.get(url)
    response.raise_for_status()

  # Save to temporary file
  with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
    f.write(response.content)
    return f.name


async def _decode_base64_image(base64_str: str) -> str:
  """Decode base64 image to temporary file."""
  image_data = base64.b64decode(base64_str)

  with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
    f.write(image_data)
    return f.name


async def _download_video(url: str) -> str:
  """Download video from URL to temporary file."""
  import httpx

  async with httpx.AsyncClient(timeout=60.0) as client:
    response = await client.get(url)
    response.raise_for_status()

  with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
    f.write(response.content)
    return f.name


async def _load_feature_library(library_id: str):
  """Load feature library from Hive storage."""
  # Import Hive service
  from app.services.dataops.hive_storage import HiveStorageService

  hive = HiveStorageService()
  library_data = await hive.retrieve_embeddings(f"feature_library_{library_id}")

  return library_data.get("feature_library", {})


async def _store_feature_library(library_id: str, feature_library: dict) -> str:
  """Store feature library to Hive storage."""
  from app.services.dataops.hive_storage import HiveStorageService

  hive = HiveStorageService()
  result = await hive.store_embeddings(
    embedding_id=f"feature_library_{library_id}",
    embeddings=feature_library,
    metadata={"type": "face_feature_library", "library_id": library_id},
  )

  return result.get("storage_path", "")
