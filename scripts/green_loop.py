#!/usr/bin/env python3
import json
import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)


def green_loop() -> None:
    if subprocess.call(["pytest", "."]) == 0:
        logging.info("Green Line intact. Preserving artifact.")
        os.makedirs("data/green_loop", exist_ok=True)
        with open("data/green_loop/latest.json", "w") as f:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
            )
            f.write(json.dumps({"hash": result.stdout.strip()}))


if __name__ == "__main__":
    green_loop()
