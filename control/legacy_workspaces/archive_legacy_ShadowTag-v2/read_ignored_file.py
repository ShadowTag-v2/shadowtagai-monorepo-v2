# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import json
import os

BEADS_FILE = ".beads/issues.jsonl"


def recall():
  if not os.path.exists(BEADS_FILE):
    return "Memory Empty."
  with open(BEADS_FILE) as f:
    lines = f.readlines()
  return "\n".join([json.loads(line).get("content", "") for line in lines[-5:]])


if __name__ == "__main__":
  print(recall())
