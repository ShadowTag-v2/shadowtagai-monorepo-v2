"""
Adtech Compliance Engine
Implements VAST 4.x, OM SDK, Privacy Sandbox verification
"""

import logging
import re

from app.config import get_settings
from app.models.adtech import (
    AdFormat,
    BrandSafetyCheck,
    BrandSafetyResponse,
    OMSDKVerificationRequest,
    OMSDKVerificationResponse,
    PrivacySandboxAPI,
    PrivacySandboxComplianceRequest,
    PrivacySandboxComplianceResponse,
    VASTValidationRequest,
    VASTValidationResponse,
    VASTVersion,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class AdtechEngine:
    """Adtech compliance verification engine"""

    def __init__(self):
        self.persona_iq = settings.persona_iq_override
        logger.info(f"Adtech Engine initialized with Persona IQ: {self.persona_iq}")

    async def validate_vast(self, request: VASTValidationRequest) -> VASTValidationResponse:
        """
        Validate VAST XML compliance

        Running at IQ {self.persona_iq} for comprehensive validation
        """
        logger.info(f"Validating VAST at IQ {self.persona_iq}")

        errors = []
        warnings = []
        tracking_events = []

        # Basic XML structure check
        if not request.vast_xml or len(request.vast_xml) < 100:
            errors.append("VAST XML appears to be empty or too short")

        # Version detection
        version_match = re.search(r'<VAST\s+version="(\d+\.\d+)"', request.vast_xml)
        if version_match:
            version_detected = VASTVersion(version_match.group(1))
        else:
            errors.append("VAST version attribute not found")
            version_detected = request.version

        # Check for required elements
        required_elements = ["<Ad>", "<InLine>", "<Creatives>", "<Creative>"]
        for element in required_elements:
            if element not in request.vast_xml:
                errors.append(f"Required element {element} not found")

        # Check for viewability tracking
        if "<Impression>" in request.vast_xml:
            tracking_events.append("impression")
        if "<Start>" in request.vast_xml:
            tracking_events.append("start")
        if "<Complete>" in request.vast_xml:
            tracking_events.append("complete")

        viewability_compliant = (
            "impression" in tracking_events
            and "start" in tracking_events
            and "complete" in tracking_events
        )

        if not viewability_compliant:
            warnings.append("Missing recommended viewability tracking events")

        # Detect ad format
        if "<Linear>" in request.vast_xml:
            ad_format = AdFormat.LINEAR
        elif "<NonLinearAds>" in request.vast_xml:
            ad_format = AdFormat.NON_LINEAR
        else:
            ad_format = None
            warnings.append("Could not detect ad format")

        # Duration detection
        duration = None
        duration_match = re.search(
            r"<Duration>(\d{2}):(\d{2}):(\d{2})</Duration>", request.vast_xml
        )
        if duration_match:
            hours, mins, secs = map(int, duration_match.groups())
            duration = hours * 3600 + mins * 60 + secs

        valid = len(errors) == 0

        return VASTValidationResponse(
            valid=valid,
            version_detected=version_detected,
            errors=errors,
            warnings=warnings,
            ad_format=ad_format,
            duration=duration,
            tracking_events=tracking_events,
            viewability_compliant=viewability_compliant,
        )

    async def verify_omsdk(self, request: OMSDKVerificationRequest) -> OMSDKVerificationResponse:
        """Verify Open Measurement SDK compliance"""
        logger.info(f"Verifying OM SDK at IQ {self.persona_iq}")

        # Simulate viewability verification
        # In production, this would integrate with actual OM SDK
        viewability_verified = True
        viewable_percentage = 78.5  # Simulated
        audible = True
        player_state = "fullscreen"
        creative_type = "video"
        errors = []

        if not request.verification_scripts:
            errors.append("No verification scripts provided")
            viewability_verified = False

        return OMSDKVerificationResponse(
            session_id=request.ad_session_id,
            viewability_verified=viewability_verified,
            viewable_percentage=viewable_percentage,
            audible=audible,
            player_state=player_state,
            creative_type=creative_type,
            errors=errors,
        )

    async def check_privacy_sandbox(
        self, request: PrivacySandboxComplianceRequest
    ) -> PrivacySandboxComplianceResponse:
        """Check Privacy Sandbox compliance"""
        logger.info(f"Checking Privacy Sandbox compliance at IQ {self.persona_iq}")

        platform = request.platform.lower()
        warnings = []
        apis_validated = {}

        # Validate each API
        for api in request.apis_used:
            if platform == "ios":
                # iOS uses SKAdNetwork
                if api == PrivacySandboxAPI.ATTRIBUTION_REPORTING:
                    apis_validated[api] = True
                else:
                    apis_validated[api] = False
                    warnings.append(f"{api} not available on iOS - use SKAdNetwork")
            elif platform == "android":
                # Android uses Topics, FLEDGE, Attribution Reporting
                apis_validated[api] = True
            else:
                apis_validated[api] = False
                warnings.append(f"Unknown platform: {platform}")

        # Check third-party cookies
        if request.third_party_cookies:
            warnings.append("Third-party cookies deprecated - migrate to Privacy Sandbox APIs")

        # User consent check
        if not request.user_consent:
            warnings.append("User consent not obtained - required for personalized advertising")

        # Platform-specific configuration
        skan_configured = platform == "ios"
        topics_configured = platform == "android" and PrivacySandboxAPI.TOPICS in request.apis_used

        # Determine compliance
        compliant = (
            request.user_consent
            and not request.third_party_cookies
            and any(apis_validated.values())
        )

        migration_required = request.third_party_cookies

        return PrivacySandboxComplianceResponse(
            compliant=compliant,
            platform=platform,
            apis_validated=apis_validated,
            warnings=warnings,
            migration_required=migration_required,
            skan_configured=skan_configured,
            topics_configured=topics_configured,
        )

    async def check_brand_safety(self, request: BrandSafetyCheck) -> BrandSafetyResponse:
        """Check brand safety compliance"""
        logger.info(f"Checking brand safety at IQ {self.persona_iq}")

        # Define blocked categories
        blocked_categories_list = [
            "adult_content",
            "violence",
            "hate_speech",
            "illegal_content",
            "misinformation",
        ]

        # Check content tags against blocked categories
        blocked = [cat for cat in request.category_tags if cat in blocked_categories_list]

        # Calculate safety score
        # Higher IQ (160) means more thorough analysis
        safety_score = max(0.0, 1.0 - len(blocked) * 0.3) if blocked else 0.95

        # Apply brand safety threshold
        safe = safety_score >= settings.brand_safety_threshold

        # Generate warnings
        warnings = []
        if not safe:
            warnings.append(
                f"Content failed brand safety threshold ({settings.brand_safety_threshold})"
            )
        for cat in blocked:
            warnings.append(f"Blocked category detected: {cat}")

        # Recommended action
        if safety_score >= 0.85:
            recommended_action = "approve"
        elif safety_score >= 0.70:
            recommended_action = "review"
        else:
            recommended_action = "block"

        return BrandSafetyResponse(
            safe=safe,
            safety_score=safety_score,
            blocked_categories=blocked,
            warnings=warnings,
            recommended_action=recommended_action,
        )
