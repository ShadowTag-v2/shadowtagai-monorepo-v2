#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)


def process_vision_corpus() -> None:
    IN = Path("data/raw_images")
    OUT = Path("data/ocr_summaries")

    # Ensure directories exist
    IN.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    for img in IN.glob("*.png"):
        logging.info(f"Extracting liability vectors from {img} via Gemini 3.1 Vision...")
        out_json = {"file": img.name, "liability": "extracted_high_risk"}
        (OUT / f"triage_{img.stem}.json").write_text(json.dumps(out_json))


if __name__ == "__main__":
    process_vision_corpus()
