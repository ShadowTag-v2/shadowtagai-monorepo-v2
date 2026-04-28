# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import datetime
import json
import os

import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/csp-report")
async def csp_report(req: Request):
    payload = await req.json()
    print(
        json.dumps(
            {"ts": datetime.datetime.utcnow().isoformat(), "type": "csp", "payload": payload},
        ),
    )
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8081")))
