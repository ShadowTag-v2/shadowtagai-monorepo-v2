# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Vision services - Tegu CV integration."""

from app.services.vision.tegu_client import TeguClient
from app.services.vision.video_classifier import VideoClassifierService
from app.services.vision.face_recognition import FaceRecognitionService
from app.services.vision.object_detection import ObjectDetectionService
from app.services.vision.license_plate import LicensePlateService

__all__ = [
  "TeguClient",
  "VideoClassifierService",
  "FaceRecognitionService",
  "ObjectDetectionService",
  "LicensePlateService",
]
