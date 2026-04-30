import contextlib
import time

import requests


def test_watermark() -> None:
    url = "http://localhost:8000/api/v1/content/watermark"
    payload = {
        "content_path": "/mock/video.mp4",
        "content_type": "video",
        "metadata": {"payload": "test_payload"},
        "output_path": "/mock/video_watermarked.mp4",
    }

    try:
        requests.post(url, json=payload, timeout=30)
        with contextlib.suppress(BaseException):
            pass
    except Exception:
        pass


if __name__ == "__main__":
    # Wait for server to start
    time.sleep(2)
    test_watermark()
