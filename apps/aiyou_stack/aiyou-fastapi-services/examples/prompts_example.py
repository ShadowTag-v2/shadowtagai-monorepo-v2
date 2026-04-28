# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Example usage of the prompt management API."""

import asyncio

import httpx

BASE_URL = "http://localhost:8000/api/v1"


async def list_default_templates():
    """List all default prompt templates."""
    print("\n=== Default Templates ===")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/prompts/templates")
        templates = response.json()

        print(f"Available templates: {len(templates)}")
        for template_name in templates:
            print(f"  - {template_name}")

        return templates


async def get_template_details(template_name: str):
    """Get details of a specific template."""
    print(f"\n=== Template Details: {template_name} ===")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/prompts/templates/{template_name}")
        template = response.json()

        print(f"Name: {template['name']}")
        print(f"Description: {template['description']}")
        print(f"Variables: {template['variables']}")
        print(f"Template:\n{template['template']}")


async def render_code_assistant_template():
    """Render the code assistant template."""
    print("\n=== Render Code Assistant Template ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/prompts/render",
            json={
                "template_name": "code_assistant",
                "variables": {
                    "language": "Python",
                    "task": "Create a REST API endpoint for user authentication",
                },
            },
        )

        result = response.json()
        print(f"Rendered prompt:\n{result['rendered_prompt']}")


async def render_summarization_template():
    """Render the summarization template."""
    print("\n=== Render Summarization Template ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/prompts/render",
            json={
                "template_name": "summarization",
                "variables": {
                    "style": "technical",
                    "max_length": "100",
                    "text": "FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. It's designed to be easy to use and learn, while also being production-ready with automatic interactive API documentation.",
                },
            },
        )

        result = response.json()
        print(f"Rendered prompt:\n{result['rendered_prompt']}")


async def create_custom_template():
    """Create a custom prompt template."""
    print("\n=== Create Custom Template ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/prompts/templates",
            json={
                "name": "bug_report_analyzer",
                "template": (
                    "Analyze the following bug report and provide:\n"
                    "1. Severity assessment\n"
                    "2. Potential root cause\n"
                    "3. Recommended fix\n\n"
                    "Bug Report:\n{bug_description}\n\n"
                    "Steps to reproduce:\n{steps}\n\n"
                    "Expected behavior: {expected}\n"
                    "Actual behavior: {actual}"
                ),
                "description": "Analyzes bug reports and provides recommendations",
                "variables": ["bug_description", "steps", "expected", "actual"],
                "metadata": {"category": "development", "type": "analysis"},
            },
        )

        result = response.json()
        print(f"Created template: {result['template_name']}")


async def use_custom_template():
    """Use the custom template we created."""
    print("\n=== Use Custom Template ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/prompts/render",
            json={
                "template_name": "bug_report_analyzer",
                "variables": {
                    "bug_description": "Application crashes when uploading large files",
                    "steps": "1. Login to app\n2. Go to upload page\n3. Select file > 10MB\n4. Click upload",
                    "expected": "File should upload successfully",
                    "actual": "Application crashes with memory error",
                },
            },
        )

        result = response.json()
        print(f"Rendered custom prompt:\n{result['rendered_prompt']}")


async def template_with_chat():
    """Use a rendered template with the chat API."""
    print("\n=== Template + Chat Integration ===")

    async with httpx.AsyncClient() as client:
        # First, render a template
        render_response = await client.post(
            f"{BASE_URL}/prompts/render",
            json={
                "template_name": "question_answering",
                "variables": {
                    "context": "FastAPI supports automatic API documentation using Swagger UI and ReDoc. It also includes data validation using Pydantic models.",
                    "question": "What tools does FastAPI use for documentation?",
                },
            },
        )

        rendered_prompt = render_response.json()["rendered_prompt"]

        # Use the rendered prompt in a chat
        chat_response = await client.post(
            f"{BASE_URL}/chat/completions",
            json={
                "message": rendered_prompt,
                "temperature": 0.3,  # Lower temperature for factual answers
            },
            timeout=30.0,
        )

        result = chat_response.json()
        print("Question: What tools does FastAPI use for documentation?")
        print(f"Answer: {result['message']}")


async def creative_writing_template():
    """Use the creative writing template."""
    print("\n=== Creative Writing Template ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/prompts/render",
            json={
                "template_name": "creative_writing",
                "variables": {
                    "content_type": "short story",
                    "genre": "science fiction",
                    "tone": "mysterious",
                    "theme": "artificial intelligence awakening",
                    "length": "300",
                },
            },
        )

        result = response.json()
        print(f"Rendered creative prompt:\n{result['rendered_prompt']}")


async def main():
    """Run all examples."""
    try:
        # List and explore default templates
        templates = await list_default_templates()

        # Get details of specific templates
        if "code_assistant" in templates:
            await get_template_details("code_assistant")

        # Render various templates
        await render_code_assistant_template()
        await render_summarization_template()

        # Create and use custom template
        await create_custom_template()
        await use_custom_template()

        # Integration with chat
        await template_with_chat()

        # Creative writing
        await creative_writing_template()

        print("\n✅ All prompt examples completed successfully!")

    except httpx.ConnectError:
        print("❌ Error: Could not connect to the API server.")
        print("   Make sure the server is running: python -m app.main")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
