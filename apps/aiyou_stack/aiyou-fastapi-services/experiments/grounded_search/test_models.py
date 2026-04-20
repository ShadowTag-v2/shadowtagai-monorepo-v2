import vertexai
from vertexai.generative_models import GenerativeModel

PROJECT_ID = "acquired-jet-478701-b3"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

try:
    model = GenerativeModel("gemini-1.0-pro-001")
    print("gemini-1.0-pro-001 initialized")
except Exception as e:
    print(f"Error initializing gemini-1.0-pro-001: {e}")

try:
    model = GenerativeModel("gemini-3.1-flash-lite-preview-001")
    print("gemini-3.1-flash-lite-preview-001 initialized")
except Exception as e:
    print(f"Error initializing gemini-3.1-flash-lite-preview-001: {e}")
