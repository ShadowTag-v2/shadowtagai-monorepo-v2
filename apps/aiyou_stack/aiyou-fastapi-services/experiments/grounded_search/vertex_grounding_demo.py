# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import vertexai
from vertexai.generative_models import GenerativeModel, Tool, grounding

# Configuration
PROJECT_ID = "acquired-jet-478701-b3"
LOCATION = "us-central1"


def generate_grounded_content(prompt="How much is Google stock?"):
    print(f"--- Generating content for: '{prompt}' ---")

    vertexai.init(project=PROJECT_ID, location=LOCATION)

    model = GenerativeModel("gemini-1.0-pro")

    # Define the Google Search Retrieval tool
    tool = Tool.from_google_search_retrieval(
        google_search_retrieval=grounding.GoogleSearchRetrieval(),
    )

    try:
        response = model.generate_content(
            prompt,
            tools=[tool],
            generation_config={"temperature": 0.0},
        )

        print("\nResponse:")
        print(response.text)

        print("\nGrounding Metadata:")
        # Accessing grounding metadata can vary slightly by version, printing the object helps.
        if response.candidates[0].grounding_metadata:
            print(response.candidates[0].grounding_metadata)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    generate_grounded_content()
