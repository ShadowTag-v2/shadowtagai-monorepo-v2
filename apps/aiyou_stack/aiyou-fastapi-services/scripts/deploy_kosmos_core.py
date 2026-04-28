#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import datetime
import os
import zipfile


def deploy_kosmos_core():
    """Packages the Kosmos Swarm Core for transfer to other LLM instances.
    Includes:
    - Doctrine (Knowledge Base)
    - Invisible Swarm (Audit Layer)
    - Judge 6 (Governance Logic)
    """
    print("///▞ KOSMOS CORE :: Initiating Transfer Protocol...")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"kosmos_core_transfer_{timestamp}.zip"

    # Define files to package
    files_to_package = [
        "agents/autoresearch.py",
        "src/pnkln/judge_six.py",
        "scripts/deploy_kosmos_core.py",  # Include self for installation logic
    ]

    core_dirs = ["doctrine"]

    try:
        # Create Zip File
        with zipfile.ZipFile(output_filename, "w") as zipf:
            # Add Core Files
            for file_path in files_to_package:
                if os.path.exists(file_path):
                    print(f"Packing: {file_path}")
                    zipf.write(file_path)
                else:
                    print(f"Warning: {file_path} not found!")

            # Add directories
            for dir_path in core_dirs:
                if os.path.exists(dir_path):
                    print(f"Packing Directory: {dir_path}")
                    for root, _, files in os.walk(dir_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            print(f"  - {file_path}")
                            zipf.write(file_path)
                else:
                    print(f"Warning: Core directory missing: {dir_path}")

        print(f"\n✅ Kosmos Core Package Created: {output_filename}")
        print("\nINSTRUCTIONS FOR TRANSFER:")
        print("1. Upload this zip file to the target LLM instance.")
        print("2. Unzip the contents.")
        print("3. Ensure 'agents/' and 'doctrine/' directories are placed correctly.")
        print(
            "4. Run 'python3 run_operation_glow_up.py' (or integrate InvisibleSwarm into your main loop).",
        )
        print("5. Verify 'Make Cash' governance via Judge 6.")

    except Exception as e:
        print(f"❌ Transfer Failed: {e}")


if __name__ == "__main__":
    deploy_kosmos_core()
