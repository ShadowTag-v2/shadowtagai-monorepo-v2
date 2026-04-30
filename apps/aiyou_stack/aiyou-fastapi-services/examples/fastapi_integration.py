#!/usr/bin/env python3
"""FastAPI Integration Example

This example demonstrates how to integrate Claude Agent SDK with FastAPI
for building AI-powered APIs.
"""

import os

from claude_agent_sdk import ClaudeAgentOptions, query
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Claude Agent API Example",
    description="Example FastAPI application with Claude Agent SDK",
)


class QueryRequest(BaseModel):
    prompt: str
    temperature: float | None = 0.7
    max_tokens: int | None = 1024


class QueryResponse(BaseModel):
    response: str


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """Query Claude Agent

    - **prompt**: Your question or task
    - **temperature**: Sampling temperature (0-1)
    - **max_tokens**: Maximum response length
    """
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

        options = ClaudeAgentOptions(
            system_prompt="You are a helpful AI assistant.",
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            api_key=api_key,
        )

        response_text = ""
        async for message in query(prompt=request.prompt, options=options):
            response_text += str(message)

        return QueryResponse(response=response_text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
