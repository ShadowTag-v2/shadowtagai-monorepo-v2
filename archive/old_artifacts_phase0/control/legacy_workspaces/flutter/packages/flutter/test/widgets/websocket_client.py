import websocket
import json
import logging

logger = logging.getLogger(__name__)

def on_message(ws, message):
    data = json.loads(message)
    logger.info(f"Received message: {data}")

def on_error(ws, error):
    logger.error(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    logger.info("### closed ###")

def on_open(ws):
    logger.info("Opened connection")

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://echo.websocket.org/",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)

    ws.run_forever()
