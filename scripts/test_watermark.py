import json
import time

import requests


def test_watermark():
    url = "http://localhost:8000/api/v1/content/watermark"
    payload = {
        "content_path": "/mock/video.mp4",
        "content_type": "video",
        "metadata": {"payload": "test_payload"},
        "output_path": "/mock/video_watermarked.mp4",
    }

    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response text: {response.text}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Wait for server to start
    time.sleep(2)
    test_watermark()
