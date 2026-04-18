import os

from google import genai


class RecursiveAgent:
    def __init__(self):
        self.client = genai.Client(vertexai=True, location="us-central1")
        self.model = "gemini-3.1-flash-lite-preview"

    def solve(self, prompt):
        ctx = ""
        if os.path.exists(".agent/context/DOCTRINE.md"):
            with open(".agent/context/DOCTRINE.md") as f:
                ctx = f"[DOCTRINE]\n{f.read()}\n"
        return self.client.models.generate_content(model=self.model, contents=ctx + prompt).text
