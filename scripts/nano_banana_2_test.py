#!/usr/bin/env python3
"""
Nano Banana 2 — Gemini 3.1 Flash Image Generation Test
Model: gemini-3.1-flash-image-preview
SDK: google-genai
"""
import os
from io import BytesIO

import PIL.Image
from google import genai

# Load API key from environment
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY not set. Source your .env file first.")

client = genai.Client(api_key=api_key)

prompt = """
    Show me a picture of a nano banana dish in a fancy restaurant with a Gemini theme
"""

print("🍌 Generating image with gemini-3.1-flash-image-preview...")
response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents=[prompt],
)

output_dir = os.path.dirname(os.path.abspath(__file__))
image_count = 0

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(f"📝 Model text: {part.text}")
    elif part.inline_data is not None:
        image_count += 1
        out_path = os.path.join(output_dir, f"nano_banana_2_test_{image_count}.png")
        image = PIL.Image.open(BytesIO(part.inline_data.data))
        image.save(out_path)
        print(f"✅ Image saved: {out_path}")

if image_count == 0:
    print("⚠️  No images generated. Check model availability and response.")
else:
    print(f"🎉 Generated {image_count} image(s) successfully.")
