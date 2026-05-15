import os

import uvicorn
from fastapi import FastAPI, File, UploadFile

app = FastAPI(title="ShadowTag Vision Refinery")

# Initialize vLLM engine (This loads the model into GPU memory on startup)
# WARNING: This requires GPU availability. On CPU Cloud Run this will likely fail or be slow.
# model_id = os.getenv("MODEL_ID", "nanaonets/nanonets-ocr-s")
# llm = LLM(model=model_id)


@app.get("/health")
def health():
    return {"status": "ready"}


@app.post("/parse")
async def parse_document(file: UploadFile = File(...)):  # noqa: B008
    """Endpoint to parse a document image/PDF using the Vision Model."""
    # 1. Save temp file
    # 2. Preprocess image
    # 3. Generate text using vLLM
    # prompts = ["Describe this invoice:"]
    # outputs = llm.generate(prompts, SamplingParams(temperature=0.2))

    return {"filename": file.filename, "parsed_text": "Simulation: Invoice #12345 parsed."}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
