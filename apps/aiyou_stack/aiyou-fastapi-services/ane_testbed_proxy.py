#!/usr/bin/env python3
import os
import sys
import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Add repo root to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.append(root_dir)

try:
    from zero_cpu_router import dispatch_compute
except ImportError:
    dispatch_compute = None

app = FastAPI(title="UphillSnowball ANE Metrics Proxy")


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    payload = await request.json()
    model = payload.get("model", "ane-default")
    messages = payload.get("messages", [])

    if not messages:
        return JSONResponse({"error": "No messages provided"}, status_code=400)

    # Extract the last user message
    prompt = messages[-1].get("content", "")

    if dispatch_compute is None:
        return JSONResponse({"error": "zero_cpu_router missing"}, status_code=500)

    try:
        # Route through the hardware orchestrator
        # file_name="ide_proxy" defines the telemetry source implicitly
        results = dispatch_compute(
            text=prompt,
            prompt_description="proxy_query",
            examples=[],
            file_name="ide_proxy",
        )

        # Format the result back into OpenAI schema
        output_text = "ERROR: No claim extracted"
        if results and len(results) > 0:
            output_text = results[0].get("text", output_text)

        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": output_text},
                    "logprobs": None,
                    "finish_reason": "stop",
                },
            ],
            "usage": {
                "prompt_tokens": len(prompt) // 4,
                "completion_tokens": len(output_text) // 4,
                "total_tokens": (len(prompt) + len(output_text)) // 4,
            },
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    port = int(os.environ.get("ANE_PROXY_PORT", 12347))
    print(f"🚀 UphillSnowball ANE Metrics Proxy listening on port {port}")
    uvicorn.run(app, host="127.0.0.1", port=port)
