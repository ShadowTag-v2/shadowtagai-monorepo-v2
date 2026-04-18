import os

import google.generativeai as genai

from src.pnkln.steel.tinytorch_tensor import Tensor


class GeminiLayer:
    """A Neural-Symbolic Layer that uses Gemini 2.0 Flash as the activation function.

    Architecture:
    Input Tensor -> [Text Projection] -> Gemini Context -> [Reasoning] -> Output Tensor

    Cost:
    - Forward Pass: ~$0.0001 per call (vs $0.0000001 for ReLU)
    - Latency: ~500ms (vs 1ns for ReLU)
    - Intelligence: Infinite (vs 0 for ReLU)
    """

    def __init__(self, api_key=None, model_name="gemini-2.0-flash-exp"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API Key required for GeminiLayer")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    def forward(self, x: Tensor, prompt_template: str = "Analyze this data: {data}") -> Tensor:
        """Performs the 'Forward Pass' through the Gemini Intelligence Unit."""
        # 1. Project Tensor to Symbol (Data -> Text)
        input_data = x.numpy().tolist()
        prompt = prompt_template.format(data=input_data)

        # 2. Inference (The "Activation")
        try:
            response = self.model.generate_content(prompt)
            # Assumption: Gemini returns a parsable number or list
            # In production, we'd use Structured Outputs (Function Calling)
            val = self._parse_output(response.text)
            return Tensor(val)
        except Exception as e:
            print(f"Gemini Layer Misfire: {e}")
            return Tensor([0.0])  # Dead neuron fallback

    def _parse_output(self, text: str):
        """Heuristic parser to convert text back to Tensor data."""
        # Simple extraction for demo: finding numbers
        import re

        nums = re.findall(r"[-+]?\d*\.\d+|\d+", text)
        if nums:
            return [float(n) for n in nums]
        return [0.0]

    def __call__(self, x):
        return self.forward(x)
