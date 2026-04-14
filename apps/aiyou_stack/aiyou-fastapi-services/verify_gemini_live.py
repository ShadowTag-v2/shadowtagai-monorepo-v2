import asyncio
import json

import websockets


async def test_live():
    # Use 127.0.0.1 to avoid possible localhost ipv6 issues
    uri = "ws://127.0.0.1:8001/api/v1/gemini/ws/live"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Successfully connected to Gemini Live WebSocket")

            # Send a simple text message
            # The google-genai SDK live session send() can take a string or dict
            msg = {
                "client_content": {
                    "turns": [
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "text": "Hello Gemini, this is a test from Antigravity. Please respond with 'OK' and your name if you hear me.",
                                },
                            ],
                        },
                    ],
                    "turn_complete": True,
                },
            }

            await websocket.send(json.dumps(msg))
            print("Sent test message.")

            # Listen for responses (Gemini Live usually sends multiple chunks)
            print("Waiting for response (listening for 5 seconds)...")
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < 5:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(response)

                    # Check for server_content or other fields
                    if "server_content" in data:
                        parts = data["server_content"].get("model_turn", {}).get("parts", [])
                        for part in parts:
                            if "text" in part:
                                print(f"Gemini Text: {part['text']}")
                            if "inline_data" in part:
                                print(
                                    f"Gemini Audio Chunk received ({len(part['inline_data']['data'])} bytes)",
                                )
                    else:
                        print(f"Received other data: {list(data.keys())}")

                except TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed by server")
                    break

    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_live())
