from google.cloud import discoveryengine_v1 as discoveryengine

# Configuration
PROJECT_NUMBER = "215390634092"  # Replace with your project number
LOCATION = "us-central1"  # Preferred location for Grounded Generation


def generate_grounded_content(prompt="How much is Google stock?"):
    """Generate content grounded in Google Search using Vertex AI Discovery Engine."""
    print(f"--- Generating content for: '{prompt}' ---")

    client = discoveryengine.GroundedGenerationServiceClient()
    # Build the location resource name
    location_path = client.common_location_path(project=PROJECT_NUMBER, location=LOCATION)

    request = discoveryengine.GenerateGroundedContentRequest(
        location=location_path,
        generation_spec=discoveryengine.GenerateGroundedContentRequest.GenerationSpec(
            model_id="gemini-3.1-flash-lite-preview",  # Cost‑effective model (approx $0.08 per 1M tokens)
        ),
        contents=[
            discoveryengine.GroundedGenerationContent(
                role="user",
                parts=[discoveryengine.GroundedGenerationContent.Part(text=prompt)],
            ),
        ],
        system_instruction=discoveryengine.GroundedGenerationContent(
            parts=[
                discoveryengine.GroundedGenerationContent.Part(
                    text="Be comprehensive and cite sources.",
                ),
            ],
        ),
        grounding_spec=discoveryengine.GenerateGroundedContentRequest.GroundingSpec(
            grounding_sources=[
                discoveryengine.GenerateGroundedContentRequest.GroundingSource(
                    google_search_source=discoveryengine.GenerateGroundedContentRequest.GroundingSource.GoogleSearchSource(
                        dynamic_retrieval_config=discoveryengine.GenerateGroundedContentRequest.DynamicRetrievalConfiguration(
                            predictor=discoveryengine.GenerateGroundedContentRequest.DynamicRetrievalConfiguration.DynamicRetrievalPredictor(
                                threshold=0.7,
                            ),
                        ),
                    ),
                ),
            ],
        ),
    )

    response = client.generate_grounded_content(request)
    print("--- Response ---")
    for candidate in response.candidates:
        for part in candidate.content.parts:
            print(part.text)


if __name__ == "__main__":
    generate_grounded_content()
