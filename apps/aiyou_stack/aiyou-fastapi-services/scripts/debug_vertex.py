import os

from google import genai

client = genai.Client(
    vertexai=True,
    project=os.environ.get("PROJECT_ID", "shadowtag-omega-v2"),
    location="us-central1",
)

print("🔍 Listing Available Vertex AI Models...")
try:
    # Attempt to list models to see what's valid
    # The SDK 'models.list' might return Gemini models or PaLM ones depending on filter
    for m in client.models.list():
        print(f" - {m.name}")
except Exception as e:
    print(f"❌ Failed to list models: {e}")

print("\n🔍 Testing 'gemini-3.1-flash-lite-preview-001' connectivity...")
try:
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview-001", contents="Ping"
    )
    print(f"✅ gemini-3.1-flash-lite-preview-001 is ACTIVE. Response: {response.text}")
except Exception as e:
    print(f"❌ gemini-3.1-flash-lite-preview-001 Failed: {e}")
