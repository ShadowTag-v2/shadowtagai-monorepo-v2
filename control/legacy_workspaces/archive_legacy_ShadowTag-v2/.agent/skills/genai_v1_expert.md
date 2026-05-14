# Google GenAI SDK v1.0+ Expert Guide (Antigravity Edition)

name: genai-v1-expert
description: Teaches the Antigravity IDE Agent how to flawlessly utilize the modern `google-genai` SDK and its Native Code Execution tool, bypassing legacy `google.generativeai` limitations.

## Context

The legacy `google.generativeai` module is obsolete. The new standard is `google-genai`. This SDK shifts to a class-based `genai.Client()` instantiation and allows zero-configuration tool use, including native sandboxed Python execution (`code_execution`).

## I. Initialization & Client Setup

**Legacy (BANNED):**

```python
import google.generativeai as genai
genai.configure(api_key="...")
model = genai.GenerativeModel("gemini-1.5-pro")
```

**Modern (REQUIRED):**

```python
from google import genai

# Automatically detects GOOGLE_API_KEY or Vertex AI GOOGLE_CLOUD_PROJECT credentials in the environment
client = genai.Client()

# Or explicitly for Vertex AI:
# client = genai.Client(vertexai=True, location="us-central1")
```

## II. Generating Content

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Explain quantum mechanics.",
    config=types.GenerateContentConfig(
        temperature=0.3,
        system_instruction="You are a physicist."
    )
)
print(response.text)
```

## III. Flawless Code Execution Tool (The Quant Radar)

This is the Zenith capability. You can grant Gemini the ability to spawn a secure Google sandbox, write arbitrary Python code (including data manipulation and matplotlib), execute it, and return the output natively.

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Generate a matplotlib chart of a Sine wave, calculate its integral over the first period, and return the image.",
    config=types.GenerateContentConfig(
        # EXPLICITLY grant code execution natively. No external libraries needed.
        tools=[{"code_execution": {}}],
        temperature=0.1
    )
)

# Extracting the output
for part in response.candidates[0].content.parts:
    if part.text:
        print(f"Model thought: {part.text}")
    elif hasattr(part, "executable_code") and part.executable_code:
        print(f"Code written by Gemini:\n{part.executable_code.code}")
    elif hasattr(part, "executable_code_result") and part.executable_code_result:
        print("Result from secure execution sandbox:")
        print(f"Stdout/Stderr: {part.executable_code_result.output}")
        if part.executable_code_result.output_images:
            for i, img in enumerate(part.executable_code_result.output_images):
                # Save the natively generated images
                with open(f"chart_{i}.png", "wb") as f:
                    f.write(img.image_bytes)
                print(f"Image {i} saved successfully.")
```

## RULES OF ENGAGEMENT

1. ALWAYS import `from google import genai`. Never import `google.generativeai`.
2. Do not attempt to catch missing parts lazily. Always check `hasattr(part, "executable_code_result")`.
3. Use the `types.GenerateContentConfig` class for all parameters. Do not pass `temperature` as a direct kwarg to `generate_content`.
