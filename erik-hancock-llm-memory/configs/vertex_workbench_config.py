# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Vertex AI Workbench Memory Configuration
Auto-loads Pnkln architecture on notebook startup
Storage: GCS-backed, Gemini Pro context injection
Cost: $0.02/month storage + API calls
"""

import os
from pathlib import Path
from google.cloud import storage
from google.auth import default
import sys

# GCS Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "pnkln-prod")
BUCKET_NAME = f"{PROJECT_ID}-workbench-memory"
MEMORY_BLOB_PATH = "memory/current.json"
LOCAL_MEMORY_PATH = Path.home() / ".workbench" / "memory.json"

# IPython startup directory
IPYTHON_STARTUP = Path.home() / ".ipython" / "profile_default" / "startup"


class VertexMemoryManager:
    """Manage memory loading in Vertex AI Workbench"""

    def __init__(self):
        self.credentials, self.project = default()
        self.storage_client = storage.Client(project=PROJECT_ID, credentials=self.credentials)
        self.bucket = None

    def create_gcs_bucket(self):
        """Create GCS bucket for memory storage"""
        try:
            self.bucket = self.storage_client.get_bucket(BUCKET_NAME)
            print(f"✓ Using existing bucket: {BUCKET_NAME}")
        except Exception:
            # Create bucket if it doesn't exist
            bucket = self.storage_client.create_bucket(BUCKET_NAME, location="us-central1")
            self.bucket = bucket
            print(f"✓ Created bucket: {BUCKET_NAME}")

            # Set lifecycle policy (delete old versions after 90 days)
            bucket.lifecycle_rules = [{"action": {"type": "Delete"}, "condition": {"age": 90, "isLive": False}}]
            bucket.patch()
            print("✓ Set lifecycle policy: 90-day retention")

    def upload_memory(self, memory_file: Path):
        """Upload memory snapshot to GCS"""
        if not memory_file.exists():
            raise FileNotFoundError(f"Memory file not found: {memory_file}")

        blob = self.bucket.blob(MEMORY_BLOB_PATH)
        blob.upload_from_filename(str(memory_file))

        # Enable versioning
        blob.metadata = {"uploaded_at": blob.time_created.isoformat(), "source": "erik-hancock-llm-memory"}
        blob.patch()

        print(f"✓ Uploaded {memory_file.name} to gs://{BUCKET_NAME}/{MEMORY_BLOB_PATH}")

    def download_memory(self) -> Path:
        """Download memory from GCS to local"""
        LOCAL_MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)

        blob = self.bucket.blob(MEMORY_BLOB_PATH)
        blob.download_to_filename(str(LOCAL_MEMORY_PATH))

        print(f"✓ Downloaded memory to {LOCAL_MEMORY_PATH}")
        return LOCAL_MEMORY_PATH

    def create_startup_script(self):
        """Create IPython startup script to load memory"""
        IPYTHON_STARTUP.mkdir(parents=True, exist_ok=True)

        startup_script = f'''"""
Auto-load Pnkln Memory on Vertex Workbench Startup
"""

import json
from pathlib import Path
from IPython import get_ipython

# Memory path
MEMORY_PATH = Path("{LOCAL_MEMORY_PATH}")

def load_pnkln_memory():
    """Load Pnkln architecture into session"""
    if not MEMORY_PATH.exists():
        print("⚠️  Memory not found. Run sync_memory() to download.")
        return None

    with open(MEMORY_PATH) as f:
        memory = json.load(f)

    print("=" * 60)
    print("Pnkln Architecture Memory Loaded")
    print("=" * 60)
    print(f"Version: {{memory.get('version', '1.0.0')}}")
    print(f"Last Updated: {{memory.get('last_updated', 'Unknown')}}")

    if 'statistics' in memory:
        stats = memory['statistics']
        print(f"Conversations: {{stats.get('total_conversations', 0):,}}")

    print("\\nArchitectures:")
    print("  • Judge #6 (98% coverage, p99 ≤90ms)")
    print("  • ShadowTag 2.0 (DCT watermarking)")
    print("  • Cor/NS (Execution brain + service mesh)")

    print("\\nFrameworks:")
    print("  • JR Framework (Purpose • Reasons • Brakes)")
    print("  • Bootstrap Gates (ROI 3x/18mo, LTV:CAC 4:1/12mo)")

    print("\\nLLM Allocation:")
    for llm, alloc in memory.get('llm_allocation', {{}}).items():
        print(f"  • {{llm.upper()}}: {{alloc * 100}}%")

    print("=" * 60)

    return memory

def sync_memory():
    """Sync memory from GCS"""
    from google.cloud import storage
    import os

    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', '{PROJECT_ID}')
    bucket_name = f"{{project_id}}-workbench-memory"

    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob("{MEMORY_BLOB_PATH}")

    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    blob.download_to_filename(str(MEMORY_PATH))

    print(f"✓ Memory synced from GCS")
    return load_pnkln_memory()

# Auto-load on startup
try:
    pnkln_memory = load_pnkln_memory()
except Exception as e:
    print(f"⚠️  Could not auto-load memory: {{e}}")
    print("Run sync_memory() to download from GCS")
    pnkln_memory = None

# Make available in global namespace
get_ipython().user_ns['pnkln_memory'] = pnkln_memory
get_ipython().user_ns['sync_memory'] = sync_memory
'''

        startup_file = IPYTHON_STARTUP / "00-load-pnkln-memory.py"
        with open(startup_file, "w") as f:
            f.write(startup_script)

        print(f"✓ Created startup script: {startup_file}")


def setup_vertex_workbench(memory_source: Path = None):
    """
    Setup Vertex AI Workbench memory integration

    Args:
        memory_source: Path to memory/current.json from erik-hancock-llm-memory repo
    """
    print("=" * 60)
    print("Vertex AI Workbench Memory Setup")
    print("=" * 60)

    manager = VertexMemoryManager()

    # Create GCS bucket
    print("\n1. Setting up GCS storage...")
    manager.create_gcs_bucket()

    # Upload memory if provided
    if memory_source and memory_source.exists():
        print("\n2. Uploading memory to GCS...")
        manager.upload_memory(memory_source)
    else:
        print("\n2. Skipping upload (no source file provided)")
        print(f"   Upload manually: gsutil cp memory/current.json gs://{BUCKET_NAME}/{MEMORY_BLOB_PATH}")

    # Download to local
    print("\n3. Downloading memory to local...")
    try:
        manager.download_memory()
    except Exception as e:
        print(f"   ⚠️  Could not download: {e}")
        print("   Memory will be synced on first notebook startup")

    # Create startup script
    print("\n4. Creating IPython startup script...")
    manager.create_startup_script()

    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart Jupyter kernel")
    print("2. Memory auto-loads on notebook startup")
    print("3. Access via: pnkln_memory variable")
    print("4. Manual sync: sync_memory()")
    print("\nCost:")
    print("  - Storage: $0.02/month (~100MB)")
    print("  - Egress: $0.12/GB (minimal for sync)")
    print("  - Total: ~$0.02-0.05/month")


if __name__ == "__main__":
    # Check for memory source argument
    if len(sys.argv) > 1:
        memory_source = Path(sys.argv[1])
    else:
        # Default to repo location
        memory_source = Path(__file__).parent.parent / "memory" / "current.json"

    setup_vertex_workbench(memory_source)
