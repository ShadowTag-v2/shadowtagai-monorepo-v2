"""
AiYou Stack — FastAPI Main Application
Privilege-preserving LLM routing for ShadowTagAI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
  title="AiYou Stack",
  description="AI-powered service layer with privilege-preserving LLM routing",
  version="0.1.0",
  docs_url="/docs",
  redoc_url="/redoc",
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["https://shadowtagai.com", "https://kovelai.com"],
  allow_credentials=True,
  allow_methods=["GET", "POST", "PUT", "DELETE"],
  allow_headers=["*"],
)


@app.get("/health")
async def health():
  """Health check endpoint."""
  return {"status": "ok", "service": "aiyou_stack", "version": "0.1.0"}


@app.get("/")
async def root():
  """Root endpoint."""
  return {"message": "AiYou Stack API", "docs": "/docs"}
