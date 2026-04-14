#!/usr/bin/env python3
"""Quick API test script for Omega Governance Service
"""

import asyncio
import sys

from app.main import app
from app.models.adtech import VASTValidationRequest
from app.models.governance import ComplianceFramework, GovernanceAssessmentRequest
from app.services.adtech_engine import AdtechEngine
from app.services.governance_engine import GovernanceEngine


async def test_governance():
    """Test governance engine"""
    print("\n🏛️  Testing Governance Engine (IQ 160)...")

    engine = GovernanceEngine()

    request = GovernanceAssessmentRequest(
        content_type="video",
        is_ai_generated=True,
        frameworks=[ComplianceFramework.EU_AI_ACT, ComplianceFramework.NIST_RMF],
    )

    result = await engine.assess(request)

    print(f"  ✅ Risk Level: {result['risk_level']}")
    print(f"  ✅ Compliance Score: {result['compliance_score']:.2%}")
    print(f"  ✅ Controls Assessed: {len(result['controls'])}")
    print(f"  ✅ Recommendations: {len(result['recommendations'])}")

    return True


async def test_adtech():
    """Test adtech engine"""
    print("\n📺 Testing Adtech Engine (IQ 160)...")

    engine = AdtechEngine()

    vast_xml = """<?xml version="1.0" encoding="UTF-8"?>
<VAST version="4.3">
  <Ad>
    <InLine>
      <AdSystem>Omega</AdSystem>
      <AdTitle>Test Ad</AdTitle>
      <Impression><![CDATA[https://example.com/impression]]></Impression>
      <Creatives>
        <Creative>
          <Linear>
            <Duration>00:00:30</Duration>
            <TrackingEvents>
              <Tracking event="start"><![CDATA[https://example.com/start]]></Tracking>
              <Tracking event="complete"><![CDATA[https://example.com/complete]]></Tracking>
            </TrackingEvents>
            <MediaFiles>
              <MediaFile><![CDATA[https://example.com/video.mp4]]></MediaFile>
            </MediaFiles>
          </Linear>
        </Creative>
      </Creatives>
    </InLine>
  </Ad>
</VAST>"""

    request = VASTValidationRequest(vast_xml=vast_xml)
    result = await engine.validate_vast(request)

    print(f"  ✅ VAST Valid: {result.valid}")
    print(f"  ✅ Version: {result.version_detected}")
    print(f"  ✅ Viewability Compliant: {result.viewability_compliant}")
    print(f"  ✅ Tracking Events: {', '.join(result.tracking_events)}")

    return result.valid


async def test_endpoints():
    """Test that endpoints are configured correctly"""
    print("\n🔗 Testing API Endpoints...")

    # Check that routes are registered
    routes = [route.path for route in app.routes]

    expected_routes = [
        "/health",
        "/api/v1/governance/assess",
        "/api/v1/adtech/vast/validate",
        "/api/v1/content/c2pa/verify",
        "/api/v1/accessibility/wcag/audit",
        "/api/v1/recommender/explain",
        "/api/v1/kpi/dashboard",
    ]

    all_found = True
    for route in expected_routes:
        if route in routes:
            print(f"  ✅ {route}")
        else:
            print(f"  ❌ {route} NOT FOUND")
            all_found = False

    return all_found


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Omega Governance Service - API Tests")
    print("=" * 60)
    print("\nPersona IQ: 160 (Maximum Intelligence)")
    print("Testing all governance engines at peak performance...")

    try:
        # Test governance
        gov_passed = await test_governance()

        # Test adtech
        adtech_passed = await test_adtech()

        # Test endpoints
        endpoints_passed = await test_endpoints()

        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)

        all_passed = gov_passed and adtech_passed and endpoints_passed

        if all_passed:
            print("✅ All tests passed!")
            print("\n🚀 Service is ready for deployment")
            return 0
        print("❌ Some tests failed")
        return 1

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
