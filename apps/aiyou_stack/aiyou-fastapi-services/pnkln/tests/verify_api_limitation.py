"""Test script to verify if Gemini API actually blocks simultaneous use of
custom tools and Google Search grounding.

CRITICAL: This must be run FIRST before implementing any workaround.
If the API doesn't actually block, we can use both features natively.
"""

import os

import vertexai
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Tool, grounding

# ============================================================================
# TEST CONFIGURATION
# ============================================================================
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
MODEL_NAME = "gemini-1.5-flash"


# ============================================================================
# SAMPLE CUSTOM TOOL
# ============================================================================
def create_test_tool() -> Tool:
    """Create a simple custom tool for testing."""
    get_weather = FunctionDeclaration(
        name="get_weather",
        description="Get the current weather for a location",
        parameters={
            "type": "object",
            "properties": {"location": {"type": "string", "description": "City name"}},
            "required": ["location"],
        },
    )
    return Tool(function_declarations=[get_weather])


# ============================================================================
# TEST CASES
# ============================================================================
def test_tools_only():
    """Test 1: Custom tools only (should work)."""
    print("\n" + "=" * 60)
    print("TEST 1: Custom tools ONLY")
    print("=" * 60)

    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel(MODEL_NAME)

        test_tool = create_test_tool()

        response = model.generate_content("What's the weather in San Francisco?", tools=[test_tool])

        print("✅ SUCCESS: Custom tools work alone")
        print(f"Response: {response.text[:200]}...")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e!s}")
        return False


def test_grounding_only():
    """Test 2: Google Search grounding only (should work)."""
    print("\n" + "=" * 60)
    print("TEST 2: Google Search grounding ONLY")
    print("=" * 60)

    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel(MODEL_NAME)

        response = model.generate_content(
            "What are the latest news about artificial intelligence?",
            tools=[grounding.Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())],
        )

        print("✅ SUCCESS: Google Search grounding works alone")
        print(f"Response: {response.text[:200]}...")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e!s}")
        return False


def test_both_combined():
    """Test 3: Custom tools + Google Search grounding (this is what we're testing)."""
    print("\n" + "=" * 60)
    print("TEST 3: Custom tools + Google Search grounding COMBINED")
    print("=" * 60)
    print("🎯 This is the critical test - does Gemini block this combination?")

    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel(MODEL_NAME)

        test_tool = create_test_tool()
        search_grounding = grounding.Tool.from_google_search_retrieval(
            grounding.GoogleSearchRetrieval(),
        )

        response = model.generate_content(
            "What's the weather in San Francisco and what are the latest tech news?",
            tools=[test_tool, search_grounding],
        )

        print("✅ SUCCESS: Both work together! API does NOT block!")
        print("🚨 ACTION: We can use native Gemini features - no workaround needed!")
        print(f"Response: {response.text[:200]}...")
        return True

    except Exception as e:
        error_msg = str(e).lower()

        # Check for specific blocking errors
        if "mutually exclusive" in error_msg or "cannot use both" in error_msg:
            print("❌ CONFIRMED: Gemini API blocks tools + grounding")
            print("🚨 ACTION: Must implement workaround (Option 3 → Option 1)")
            print(f"Error: {e!s}")
            return False
        print(f"❌ FAILED with unexpected error: {e!s}")
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def run_verification():
    """Run all tests and provide actionable conclusion."""
    print("\n" + "=" * 60)
    print("GEMINI API LIMITATION VERIFICATION TEST")
    print("=" * 60)
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Model: {MODEL_NAME}")

    if not PROJECT_ID:
        print("\n❌ ERROR: GCP_PROJECT_ID environment variable not set")
        print("Set it with: export GCP_PROJECT_ID='your-project-id'")
        return None

    results = {
        "tools_only": test_tools_only(),
        "grounding_only": test_grounding_only(),
        "both_combined": test_both_combined(),
    }

    print("\n" + "=" * 60)
    print("FINAL VERDICT")
    print("=" * 60)

    if results["both_combined"]:
        print("✅ API DOES NOT BLOCK - Use native Gemini features")
        print("\nRECOMMENDATION:")
        print("  1. No workaround needed")
        print("  2. Use tools + grounding together directly")
        print("  3. Focus on other revenue features")

    elif results["tools_only"] and results["grounding_only"]:
        print("❌ API BLOCKS COMBINATION - Workaround required")
        print("\nRECOMMENDATION:")
        print("  1. Implement Option 3: Brave Search as MCP tool (ship now)")
        print("  2. Build Option 1: Sequential orchestration (long-term)")
        print("  3. Run quality comparison: Brave vs Google Grounding")
        print("  4. Monitor metrics against SUCCESS_THRESHOLDS")

    else:
        print("⚠️  INCONCLUSIVE - Check GCP permissions and API access")
        print("\nTROUBLESHOOTING:")
        print("  1. Verify Vertex AI API is enabled")
        print("  2. Check service account permissions")
        print("  3. Confirm model availability in region")

    print("\n" + "=" * 60)

    return results


if __name__ == "__main__":
    run_verification()
