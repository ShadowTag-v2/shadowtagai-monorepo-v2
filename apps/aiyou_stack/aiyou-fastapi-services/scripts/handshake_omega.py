import os
import sys
import time

# Add the apps path to sys.path so we can import from src
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../apps/n-autoresearch/Kosmos/BioAgents-server"),
    ),
)
try:
    from src.atomic_core import initiate_research_omega, monitor_and_capture_omega  # noqa: F401
except ImportError:
    # Fallback for direct execution structure
    sys.path.append(
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../apps/n-autoresearch/Kosmos/BioAgents-server/src",
            ),
        ),
    )
    from atomic_core import initiate_research_omega


def execute_handshake():
    print("🤝 INITIATING OMEGA HANDSHAKE...")

    # 1. Verify Credentials
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ GEMINI_API_KEY not found. Assuming ADC (Application Default Credentials).")

    # 2. Pull the Reams (Deep Research on Self)
    query = """
    Conduct a deep technical analysis of the 'A2UI' protocol and the 'Shadowtag-Omega-v2' architecture.
    Identify the specific 'atomic' components required to achieve a Steve Jobs-esque, high-performance UI/UX.
    Synthesize a strict technical specification for the frontend-backend bridge.
    """

    try:
        print("🧠 Dispatching Deep Research Agent (Preview 12-2025)...")
        interaction_id = initiate_research_omega(query)
        print(f"✅ Handshake Accepted. Interaction ID: {interaction_id}")

        # 3. Monitor (Brief check)
        print("Waiting for initial acknowledgement (5s)...")
        time.sleep(5)

        # We won't block forever here, relying on the backend to pick it up later
        # or the user to query status.
        return True
    except Exception as e:
        print(f"❌ Handshake Failed: {e}")
        return False


if __name__ == "__main__":
    success = execute_handshake()
    if not success:
        sys.exit(1)
