# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True}
