import os

from google import genai

# Target Files for Multimodal Ingestion
TARGETS = [
    "/Users/pikeymickey/Library/CloudStorage/redacted@shadowtag-v4.local/My Drive/ShadowTag-v2_Phase_Docs/Tech Stack Plan.pdf",
    "/Users/pikeymickey/Library/CloudStorage/redacted@shadowtag-v4.local/My Drive/ShadowTag-v2_Phase_Docs/CTO Persona Finalized.docx",  # Gemini can read DOCX often or we treat as text/blob
    "/Users/pikeymickey/Library/CloudStorage/redacted@shadowtag-v4.local/My Drive/ShadowTag-v2_Phase_Docs/250904 Omega Changes.pdf",
]


def ingest_drive_files():
    print("🚀 INITIATING MULTIMODAL DRIVE INGESTION (Gemini 2.0 Flash)...")

    client = genai.Client(vertexai=True, project="shadowtag-omega-v2", location="us-central1")

    model = "gemini-3.1-flash-lite-preview-001"

    for file_path in TARGETS:
        if not os.path.exists(file_path):
            print(f"⚠️ File not found (Skipping): {file_path}")
            continue

        print(f"📄 Processing: {os.path.basename(file_path)}...")

        try:
            # Read file binary
            with open(file_path, "rb") as f:
                file_data = f.read()

            # Construct Prompt
            prompt = """
            ANALYZE this technical document.
            EXTRACT:
            1. Core Architectural Constraints (Tech Stack, Infrastructure).
            2. Key Personas (Roles, Responsibilities).
            3. Operational Directives (Governance, Security).

            Output as bullet points.
            """

            # Send to Gemini
            # Note: For PDF/DOCX, we pass as inline data payload if small enough, or upload.
            # 2.0 Flash supports PDF input directly.

            mime_type = "application/pdf"
            if file_path.endswith(".docx"):
                mime_type = (
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            response = client.models.generate_content(
                model=model,
                contents=[prompt, genai.types.Part.from_bytes(data=file_data, mime_type=mime_type)],
            )

            print(f"\n✅ ANALYSIS ({os.path.basename(file_path)}):")
            print(response.text)
            print("-" * 50)

        except Exception as e:
            print(f"❌ Failed to process {os.path.basename(file_path)}: {e}")


if __name__ == "__main__":
    ingest_drive_files()
