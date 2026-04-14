from google.cloud import discoveryengine_v1beta as discoveryengine

# Configuration
PROJECT_NUMBER = "215390634092"  # Acquired Jet Project Number
LOCATION = "us-central1"


def generate_grounded_content(prompt="How much is Google stock?"):
    """Generates content grounded in Google Search.
    """
    print(f"--- Generating content for: '{prompt}' ---")

    client = discoveryengine.GroundedGenerationServiceClient()

    # The full resource name of the location.
    # Format: projects/{project_number}/locations/{location}
    location_path = client.common_location_path(project=PROJECT_NUMBER, location=LOCATION)
    print(f"Location Path: {location_path}")

    request = discoveryengine.GenerateGroundedContentRequest(
        location=location_path,
        generation_spec=discoveryengine.GenerateGroundedContentRequest.GenerationSpec(
            model_id="gemini-1.5-flash",
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
                    text="Be comprehensive and cite your sources.",
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

    try:
        response = client.generate_grounded_content(request)
        print("\nResponse:")
        print(response.candidates[0].content.parts[0].text)

        if response.candidates[0].grounding_metadata.search_entry_point:
            print("\nSearch Entry Point:")
            print(response.candidates[0].grounding_metadata.search_entry_point.rendered_content)

        print("\nGrounding Support:")
        for support in response.candidates[0].grounding_metadata.grounding_support:
            print(f"- {support}")

    except Exception as e:
        print(f"Error: {e}")
        print(
            "\nNote: If this failed with a 403 or 404, it might be because we need the Project Number instead of Project ID, or the API is not enabled.",
        )


if __name__ == "__main__":
    generate_grounded_content()
    # generate_grounded_content("What are the latest updates on the James Webb Space Telescope?")
