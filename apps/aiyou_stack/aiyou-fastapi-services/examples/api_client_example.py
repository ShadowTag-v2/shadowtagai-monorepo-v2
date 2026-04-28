# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Example API client for checkpointing service."""

import asyncio
import tempfile
from pathlib import Path

import httpx

BASE_URL = "http://localhost:8000/api/v1"


async def main():
    """Demonstrate API usage."""
    print("=== Checkpointing API Client Demo ===\n")

    async with httpx.AsyncClient() as client:
        # Health check
        print("1. Checking API health...")
        response = await client.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        print(f"   Status: {response.json()['status']}\n")

        # Create temporary test file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".py") as f:
            f.write("print('Hello from checkpoint')")
            test_file = f.name

        try:
            # Create checkpoint
            print("2. Creating checkpoint...")
            checkpoint_data = {
                "session_id": "api_demo_session",
                "user_message": "Demo checkpoint via API",
                "checkpoint_type": "manual",
                "file_paths": [test_file],
            }

            response = await client.post(f"{BASE_URL}/checkpoints", json=checkpoint_data)

            if response.status_code == 201:
                checkpoint = response.json()
                checkpoint_id = checkpoint["id"]
                print(f"   ✓ Checkpoint created: {checkpoint_id}")
                print(f"   Files: {checkpoint['file_count']}")
                print(f"   Size: {checkpoint['total_size_bytes']} bytes\n")
            else:
                print(f"   ✗ Failed: {response.status_code}\n")
                return

            # Get checkpoint details
            print("3. Retrieving checkpoint details...")
            response = await client.get(f"{BASE_URL}/checkpoints/{checkpoint_id}")

            if response.status_code == 200:
                checkpoint = response.json()
                print(f"   Status: {checkpoint['status']}")
                print(f"   Created: {checkpoint['created_at']}\n")
            else:
                print(f"   ✗ Failed: {response.status_code}\n")

            # List checkpoints
            print("4. Listing session checkpoints...")
            response = await client.get(f"{BASE_URL}/checkpoints/sessions/api_demo_session")

            if response.status_code == 200:
                data = response.json()
                print(f"   Total: {data['total']} checkpoints")
                for cp in data["checkpoints"]:
                    print(f"   - {cp['id'][:8]}... | {cp['user_message']}")
                print()
            else:
                print(f"   ✗ Failed: {response.status_code}\n")

            # Get file snapshots
            print("5. Getting file snapshots...")
            response = await client.get(f"{BASE_URL}/checkpoints/{checkpoint_id}/files")

            if response.status_code == 200:
                snapshots = response.json()
                print(f"   Found {len(snapshots)} file snapshot(s)")
                for snapshot in snapshots:
                    print(f"   - {snapshot['file_path']}")
                    print(f"     Hash: {snapshot['content_hash'][:16]}...")
                    print(f"     Size: {snapshot['size_bytes']} bytes")
                print()
            else:
                print(f"   ✗ Failed: {response.status_code}\n")

            # Get session stats
            print("6. Getting session statistics...")
            response = await client.get(f"{BASE_URL}/checkpoints/sessions/api_demo_session/stats")

            if response.status_code == 200:
                stats = response.json()
                print(f"   Checkpoints: {stats['checkpoint_count']}")
                print(f"   Total files: {stats['total_files']}")
                print(f"   Total size: {stats['total_size_bytes']} bytes")
                print(f"   Active: {stats['active_checkpoints']}")
                print()
            else:
                print(f"   ✗ Failed: {response.status_code}\n")

            # Restore checkpoint
            print("7. Restoring checkpoint...")
            restore_data = {"restore_code": True, "restore_conversation": False}

            response = await client.post(
                f"{BASE_URL}/checkpoints/{checkpoint_id}/restore",
                json=restore_data,
            )

            if response.status_code == 200:
                checkpoint = response.json()
                print("   ✓ Checkpoint restored")
                print(f"   Status: {checkpoint['status']}")
                print(f"   Restored at: {checkpoint['restored_at']}\n")
            else:
                print(f"   ✗ Failed: {response.status_code}\n")

            # Delete checkpoint
            print("8. Deleting checkpoint...")
            response = await client.delete(f"{BASE_URL}/checkpoints/{checkpoint_id}")

            if response.status_code == 204:
                print("   ✓ Checkpoint deleted\n")
            else:
                print(f"   ✗ Failed: {response.status_code}\n")

        finally:
            # Cleanup
            Path(test_file).unlink(missing_ok=True)

    print("=== Demo Complete ===")


if __name__ == "__main__":
    print("Make sure the API server is running: python main.py\n")
    asyncio.run(main())
