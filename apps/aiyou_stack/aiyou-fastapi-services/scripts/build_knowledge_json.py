import json
import os


def build_knowledge_base(flattened_dir, output_file):
    """Builds a JSON index of the flattened codebase."""
    index = []
    for root, _, files in os.walk(flattened_dir):
        for file in files:
            path = os.path.join(root, file)
            with open(path, errors="ignore") as f:
                content = f.read()
            index.append({"path": path, "content": content})

    with open(output_file, "w") as f:
        json.dump(index, f)


if __name__ == "__main__":
    build_knowledge_base(os.path.expanduser("~/antigravity-flattened"), "knowledge_base.json")
