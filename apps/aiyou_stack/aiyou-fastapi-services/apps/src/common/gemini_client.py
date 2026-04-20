import logging
import os

import google.generativeai as genai


class GeminiClient:
    def __init__(self, model_name="gemini-3.1-flash-lite-preview"):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.model_name = model_name

    def generate(self, prompt: str) -> dict:
        if not self.api_key:
            logging.warning("⚠️ Google API Key missing. Using simulation.")
            return {"simulated": True, "content": f"Simulated generation for: {prompt}"}

        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return {"content": response.text}
        except Exception as e:
            logging.exception(f"❌ Gemini API Error: {e}")
            return {"error": str(e)}
