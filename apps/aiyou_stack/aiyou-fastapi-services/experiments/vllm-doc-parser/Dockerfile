# Use official vLLM image as base (contains CUDA/Python/Pytorch optimized)
FROM vllm/vllm-openai:latest

# Environment variables for Cloud Run
ENV PORT=8000
ENV HUGGING_FACE_HUB_TOKEN=""

# Install any additional dependencies if needed (e.g. for custom document parser logic)
# RUN pip install nanonets-ocr google-cloud-storage

# Override entrypoint if wrapping logic is needed.
# For pure vLLM serving, the default entrypoint works.
# But we might want a lightweight API wrapper to handle Document -> Text logic before LLM.

# Copy our custom wrapper code
WORKDIR /app
COPY main.py .

# Install FastAPI wrapper deps
RUN pip install fastapi uvicorn python-multipart

# Command to run our custom wrapper that calls vLLM engine internally or proxies to it
CMD ["python3", "main.py"]
