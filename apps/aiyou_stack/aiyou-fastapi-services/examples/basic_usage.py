# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Basic usage example for checkpointing."""

import asyncio
import tempfile
from pathlib import Path

from src.core.checkpointing import checkpoint_manager


async def main():
    """Demonstrate basic checkpointing functionality."""
    print("=== ShadowTag-v2 FastAPI Services - Checkpointing Demo ===\n")

    # Set session
    session_id = "demo_session_001"
    checkpoint_manager.set_session(session_id)
    print(f"✓ Session set: {session_id}\n")

    # Create temporary test files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Create test files
        file1 = tmpdir_path / "example1.py"
        file2 = tmpdir_path / "example2.py"

        file1.write_text("def hello():\n    print('Hello, World!')\n")
        file2.write_text("def goodbye():\n    print('Goodbye!')\n")

        print("✓ Created test files:")
        print(f"  - {file1}")
        print(f"  - {file2}\n")

        # Create first checkpoint
        print("Creating checkpoint before changes...")
        checkpoint_id_1 = await checkpoint_manager.auto_checkpoint(
            file_paths=[str(file1), str(file2)],
            user_message="Initial version",
        )
        print(f"✓ Checkpoint created: {checkpoint_id_1}\n")

        # Modify files
        print("Modifying files...")
        file1.write_text("def hello(name):\n    print(f'Hello, {name}!')\n")
        file2.write_text("def goodbye(name):\n    print(f'Goodbye, {name}!')\n")
        print("✓ Files modified\n")

        # Create second checkpoint
        print("Creating checkpoint after changes...")
        checkpoint_id_2 = await checkpoint_manager.auto_checkpoint(
            file_paths=[str(file1), str(file2)],
            user_message="Added name parameter",
        )
        print(f"✓ Checkpoint created: {checkpoint_id_2}\n")

        # List checkpoints
        print("Listing all checkpoints for session:")
        checkpoints = checkpoint_manager.get_session_checkpoints()
        for i, cp in enumerate(checkpoints, 1):
            print(
                f"  {i}. ID: {cp['id'][:8]}... | Message: {cp['user_message']} | Files: {cp['file_count']}",
            )
        print()

        # Display current file content
        print("Current file content (file1):")
        print(f"  {file1.read_text()}")

        # Restore first checkpoint
        print(f"Restoring to first checkpoint ({checkpoint_id_1[:8]}...)...")
        await checkpoint_manager.rewind(checkpoint_id_1, restore_code=True)
        print("✓ Checkpoint restored\n")

        # Display restored file content
        print("Restored file content (file1):")
        print(f"  {file1.read_text()}")

        print("\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
