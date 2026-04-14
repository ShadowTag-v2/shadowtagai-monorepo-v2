"""Tegu Integration for AiU+ShadowTag-v4 Platform
Machine Learning Toolbox for Computer Vision

Provides:
- Object Detection (YOLOv3) for tower monitoring
- Facial Recognition (FaceNet) for vendor verification
- Video Classification (ActivityNet) for content moderation
- License Plate Recognition for geo-commerce

All operations validated through AiUCRM pre-execution compliance.
"""

from .services.content_moderation import ContentModerationService
from .services.lpr_service import LicensePlateRecognitionService
from .services.tower_monitoring import TowerMonitoringService
from .services.vendor_verification import VendorVerificationService

__version__ = "1.0.0"
__all__ = [
    "ContentModerationService",
    "LicensePlateRecognitionService",
    "TowerMonitoringService",
    "VendorVerificationService",
]
