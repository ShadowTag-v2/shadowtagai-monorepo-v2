# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import sys

# Add the directory containing ingest_drive_docs.py to the Python path
sys.path.append("/Users/pikeymickey/aiyou-stack/ShadowTag-v2/shadowtag-omega-v4/scripts")

# Now we can import the process_file function
from ingest_drive_docs import process_file

if __name__ == "__main__":
    # The path to the downloaded PDF
    pdf_path = "/Users/pikeymickey/.gemini/tmp/0da024195fb5064e2f16e3e05dabdc4f48caf098f191ca93e2248337cc5a9d2c/2511.02824.pdf"
    print(f"Processing {pdf_path}")
    process_file(pdf_path)
