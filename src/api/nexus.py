"""
API Nexus. Routing Playwright scraping and WebSocket handling.
"""

from fastapi import FastAPI, WebSocket
from .agents.flying_monkeys_pure import PureFlyingMonkeys

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hello from DeepMind Singularity API Nexus WebSocket.")
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.post("/trigger_scraper")
async def trigger_scraper():
    return {"status": "Unleashed PureFlyingMonkeys"}
