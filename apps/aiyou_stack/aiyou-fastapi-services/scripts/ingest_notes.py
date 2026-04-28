# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import glob
import os

NOTES_DIR = "/Users/pikeymickey/Downloads/iCloud Notes/Notes"
OUTPUT_FILE = "notes_digest.txt"

KEYWORDS = [
    "Cor.",
    "Architecture",
    "Deployment",
    "Valuation",
    "Key",
    "Mission",
    "Protocol",
    "Antigravity",
    "Judge",
]


def ingest_notes():
    print(f"🕵️‍♀️ SCANNING NOTES in {NOTES_DIR}...")

    with open(OUTPUT_FILE, "w") as out:
        folders = [f.path for f in os.scandir(NOTES_DIR) if f.is_dir()]

        for folder in folders:
            # Find the .txt file matching the folder name (usually)
            txt_files = glob.glob(os.path.join(folder, "*.txt"))

            for txt_path in txt_files:
                try:
                    with open(txt_path, encoding="utf-8") as f:
                        content = f.read()

                    # Filtering Logic
                    if any(k in content for k in KEYWORDS) or any(k in txt_path for k in KEYWORDS):
                        title = os.path.basename(txt_path).replace(".txt", "")
                        print(f"✅ Found Intelligence: {title}")

                        out.write(f"--- NOTE: {title} ---\n")
                        out.write(content)
                        out.write("\n\n" + "=" * 50 + "\n\n")

                except Exception as e:
                    print(f"❌ Error reading {txt_path}: {e}")


if __name__ == "__main__":
    ingest_notes()
    print(f"\n📄 Notes Digest saved to {OUTPUT_FILE}")
