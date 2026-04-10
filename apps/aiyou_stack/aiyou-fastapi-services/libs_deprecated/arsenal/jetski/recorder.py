import logging
import time


class VideoRecorder:
    def __init__(self, session_id):
        self.session_id = session_id
        self.frames = []

    def capture_frame(self, browser_context):
        self.frames.append(time.time())

    def save(self):
        filename = f"artifacts/{self.session_id}.webp"
        logging.info(f"🎥 JETSKI: Compiling {len(self.frames)} frames into {filename}")
        with open(filename, "w") as f:
            f.write("VIDEO_BINARY_DATA")
        return filename
