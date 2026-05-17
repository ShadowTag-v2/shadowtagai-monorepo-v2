# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import arbiter

app = FastAPI(
  title="HeadFade API",
  version="1.0.0",
  description="Backend for the HeadFade Global Turing Test. Ethically sourced Human Deception Index generation.",
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

app.include_router(arbiter.router)


@app.get("/health")
@app.get("/healthz")
def health_check():
  return {"status": "operational", "service": "headfade-api"}


if __name__ == "__main__":
  import uvicorn

  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
