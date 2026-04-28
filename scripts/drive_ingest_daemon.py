#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import asyncio
import logging
import os
import shutil
import subprocess

logging.basicConfig(level=logging.INFO)


class DriveIngestionDaemon:
    def __init__(self, folder_id) -> None:
        self.folder_id = folder_id
        self.workspace_cli = os.environ.get(
            "GOOGLEWORKSPACE_CLI",
            shutil.which("googleworkspace-cli") or "/usr/local/bin/googleworkspace-cli",
        )

    async def start(self) -> None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        extractor = os.path.join(script_dir, "ingest_drive_docs.py")

        while True:
            run_res = subprocess.run(["python3", extractor], check=False)
            if run_res.returncode == 0:
                pass
            else:
                pass

            await asyncio.sleep(300)


if __name__ == "__main__":
    asyncio.run(DriveIngestionDaemon(os.environ.get("DRIVE_FOLDER_ID", "root")).start())
