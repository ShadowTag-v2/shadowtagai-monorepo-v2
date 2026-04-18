import os

from google import genai

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v2")
LOCATION = "us-central1"


def list_models():
    print(f"Listing models for {PROJECT_ID} in {LOCATION}...")
    try:
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        # The SDK might have a different way to list, but let's try standard methods or just try to generate and catch specific errors
        # Actually, let's try to just print help or use a known list method if available.
        # Newer genai SDK (0.X) has client.models.list() maybe?

        # fallback if list isn't obvious, we try creating a model object and seeing if it errors differently
        # But let's try the iterate/list if it exists.

        # Based on typical SDKs:
        # Pager object
        for model in client.models.list():
            print(f"Model: {model.name} - {model.display_name}")

    except Exception as e:
        print(f"Error listing models: {e}")
        # Fallback: try using 'gemini-1.0-pro' as a test content generation
        print("Attempting fallbacks...")
        fallbacks = ["gemini-1.0-pro", "gemini-pro", "gemini-3.1-flash-lite-preview-preview-0409"]
        for m in fallbacks:
            print(f"Testing {m}...")
            try:
                client.models.generate_content(model=m, contents="Hello")
                print(f"SUCCESS: {m} is valid!")
                break
            except Exception as ex:
                print(f"Failed {m}: {ex}")


if __name__ == "__main__":
    list_models()
