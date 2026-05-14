# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Pydantic models for computer vision API."""

from pydantic import BaseModel, Field


class ImageClassificationRequest(BaseModel):
    """Request for image classification."""

    image_url: str | None = Field(None, description="URL to image (alternative to base64)")
    image_base64: str | None = Field(None, description="Base64-encoded image")
    model: str = Field("resnet50", description="Model to use (resnet50, vgg16, inception_v3)")
    top_k: int = Field(5, ge=1, le=10, description="Number of top predictions to return")


class ClassificationResult(BaseModel):
    """Single classification result."""

    class_id: str
    class_name: str = Field(..., alias="class")
    confidence: float = Field(..., ge=0.0, le=1.0)


class ImageClassificationResponse(BaseModel):
    """Response for image classification."""

    predictions: list[ClassificationResult]
    model: str
    latency_ms: float


class ObjectDetectionRequest(BaseModel):
    """Request for object detection."""

    image_url: str | None = None
    image_base64: str | None = None
    model: str = Field("yolo_v3", description="Model to use (yolo_v3, ssd_mobilenet)")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0)


class BoundingBox(BaseModel):
    """Bounding box coordinates."""

    x: int
    y: int
    width: int
    height: int


class DetectedObject(BaseModel):
    """Detected object."""

    class_id: int
    class_name: str = Field(..., alias="class")
    confidence: float
    bbox: BoundingBox


class ObjectDetectionResponse(BaseModel):
    """Response for object detection."""

    objects: list[DetectedObject]
    model: str
    latency_ms: float
    image_dimensions: dict[str, int]  # {width, height}


class FaceRecognitionRequest(BaseModel):
    """Request for face recognition."""

    image_url: str | None = None
    image_base64: str | None = None
    model: str = Field("facenet", description="Model to use (facenet, vggface)")
    feature_library_id: str | None = Field(None, description="Feature library for matching")
    threshold: float = Field(0.6, ge=0.0, le=1.0)


class RecognizedFace(BaseModel):
    """Recognized face."""

    name: str
    confidence: float
    bbox: BoundingBox
    embedding: list[float] | None = Field(None, description="128-dim face embedding")


class FaceRecognitionResponse(BaseModel):
    """Response for face recognition."""

    faces: list[RecognizedFace]
    model: str
    latency_ms: float


class VideoClassificationRequest(BaseModel):
    """Request for video classification."""

    video_url: str
    model: str = Field("resnet50", description="Model for frame classification")
    sample_rate: int = Field(30, ge=1, description="Sample every N frames")
    top_k: int = Field(3, ge=1, le=10)


class VideoClass(BaseModel):
    """Aggregated video classification."""

    class_name: str = Field(..., alias="class")
    confidence: float
    frame_count: int


class VideoClassificationResponse(BaseModel):
    """Response for video classification."""

    duration_seconds: float
    total_frames: int
    sampled_frames: int
    top_classes: list[VideoClass]
    model: str
    latency_ms: float


class BuildFeatureLibraryRequest(BaseModel):
    """Request to build face feature library."""

    library_id: str
    faces: list[dict[str, str]]  # [{name: str, image_url: str}]
    model: str = Field("facenet")


class BuildFeatureLibraryResponse(BaseModel):
    """Response for building feature library."""

    library_id: str
    face_count: int
    model: str
    storage_path: str
