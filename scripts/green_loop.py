#!/usr/bin/env python3
import json, subprocess, logging, os
logging.basicConfig(level=logging.INFO)

def green_loop():
    if subprocess.call(["pytest", "."]) == 0:
        logging.info("Green Line intact. Preserving artifact.")
        os.makedirs("data/green_loop", exist_ok=True)
        with open("data/green_loop/latest.json", "w") as f:
            f.write(json.dumps({"hash": subprocess.getoutput("git rev-parse HEAD")}))

if __name__ == "__main__":
    green_loop()
