# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import time
import json
import traceback
from google.colab import drive

# Mount the shared VFS memory bus (Google Drive)
drive.mount("/content/drive")
IPC_DIR = "/content/drive/MyDrive/Antigravity_IPC"
os.makedirs(f"{IPC_DIR}/inbox", exist_ok=True)
os.makedirs(f"{IPC_DIR}/outbox", exist_ok=True)

print("☁️ Sovereign Cloud T4 Worker Online. Polling VFS with Atomic Locks...")

while True:
  try:
    tasks = [f for f in os.listdir(f"{IPC_DIR}/inbox") if f.endswith(".py")]
    for task in tasks:
      inbox_path = f"{IPC_DIR}/inbox/{task}"
      outbox_path = f"{IPC_DIR}/outbox/{task.replace('.py', '.json')}"
      tmp_outbox = outbox_path + ".tmp"

      try:
        namespace = {}
        exec(open(inbox_path).read(), namespace)
        output = {
          "status": "success",
          "data": str(namespace.get("RESULT", "Done")),
        }
      except Exception:
        output = {"status": "error", "traceback": traceback.format_exc()}

      # ATOMIC WRITE: Write to .tmp first, then rename.
      # Prevents the M1 Max from reading a half-synced JSON file.
      with open(tmp_outbox, "w") as f:
        json.dump(output, f)
      os.rename(tmp_outbox, outbox_path)
      os.remove(inbox_path)

  except Exception as e:
    print(f"Polling error: {e}")

  time.sleep(0.5)
