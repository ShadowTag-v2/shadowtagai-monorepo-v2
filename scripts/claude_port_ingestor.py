import os
import shutil

SRC_DIR = "/Users/pikeymickey/Downloads/Claude_Source_Code"
DEST_DIR = "_audit_claude_code"


def ingest():
    print("Starting data extraction...")
    targets = ["services", "utils", "ai-modes", "buddy", "coordinator", "assistant", "voice", "hooks"]

    os.makedirs(DEST_DIR, exist_ok=True)

    count = 0
    for target in targets:
        src = os.path.join(SRC_DIR, target)
        if not os.path.exists(src):
            continue

        for root, _, files in os.walk(src):
            for file in files:
                if file.endswith(".ts") and not file.endswith(".tsx"):  # Skip UI
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(src_path, SRC_DIR)
                    dest_path = os.path.join(DEST_DIR, rel_path)

                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                    count += 1

    print(f"Extraction complete. {count} files saved to {DEST_DIR}/")


if __name__ == "__main__":
    ingest()
