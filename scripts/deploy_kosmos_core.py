#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import datetime
import os
import zipfile


def deploy_kosmos_core() -> None:
    """Packages the Kosmos Swarm Core for transfer to other LLM instances.
    Includes:
    - Doctrine (Knowledge Base)
    - Invisible Swarm (Audit Layer)
    - Judge 6 (Governance Logic).
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"kosmos_core_transfer_{timestamp}.zip"

    # Define files to package
    files_to_package = [
        "core/pnkln-evolve.py",
        "src/pnkln/judge_six.py",
        "scripts/deploy_kosmos_core.py",  # Include self for installation logic
    ]

    core_dirs = [
        "doctrine",
        "apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services/external_repos/n-autoresearch",
        "apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services/external_repos/Kosmos",
        "apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services/external_repos/BioAgents",
    ]

    try:
        # Create Zip File
        with zipfile.ZipFile(output_filename, "w") as zipf:
            # Add Core Files
            for file_path in files_to_package:
                if os.path.exists(file_path):
                    zipf.write(file_path)
                else:
                    pass

            # Add directories
            for dir_path in core_dirs:
                if os.path.exists(dir_path):
                    for root, _, files in os.walk(dir_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path)
                else:
                    pass

    except Exception:
        pass


if __name__ == "__main__":
    deploy_kosmos_core()
