# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import threading
import time

import requests
import uvicorn
from fastapi import FastAPI
from transcript_to_contract.upload import router as upload_router

app = FastAPI()
app.include_router(upload_router)


def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8181, log_level="error")


def test_api():
    # Wait for uvicorn
    time.sleep(2)
    print("\n[+] Executing Sovereign Payload Drop against Zero-Trust Port (8181)...")

    files = {
        "file": ("contract_matrix.pdf", b"%PDF-1.4 mock binary matrix data", "application/pdf"),
    }
    try:
        response = requests.post("http://127.0.0.1:8181/upload/document", files=files)
        print(f" -> Response Status: {response.status_code}")
        print(f" -> Response Data: {response.json()}")
    except Exception as e:
        print(f" -> Network Request Failed: {e}")


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    test_api()
