"""Vertex Workbench / GKE Native Deployment
Memory-enabled consensus system for Google Cloud Platform

Architecture:
1. Memory stored in GCS bucket (gs://consensus-memory/)
2. Init container syncs memory to pods
3. ConfigMap holds current memory state
4. Gemini Pro loads context from GCS
5. Cross-device sync via GCS
"""

import os
from datetime import datetime
from pathlib import Path


class VertexMemoryManager:
    """Manages memory persistence for Vertex Workbench and GKE deployments.

    Uses Google Cloud Storage for centralized memory storage,
    accessible from any Vertex notebook or GKE pod.
    """

    def __init__(
        self,
        project_id: str = None,
        bucket_name: str = "consensus-memory",
        memory_prefix: str = "memories/",
    ):
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.bucket_name = bucket_name
        self.memory_prefix = memory_prefix

        # Initialize GCS client
        self.storage_client = None
        self.bucket = None

        try:
            from google.cloud import storage

            self.storage_client = storage.Client(project=self.project_id)
            self.bucket = self.storage_client.bucket(self.bucket_name)
        except ImportError:
            print("[WARNING] google-cloud-storage not installed")
        except Exception as e:
            print(f"[WARNING] Failed to initialize GCS client: {e}")

    def upload_memory(self, memory_content: str, filename: str = "current_memory.md") -> bool:
        """Upload memory content to GCS.

        Args:
            memory_content: Markdown formatted memory
            filename: Name of memory file

        Returns:
            True if successful

        """
        if not self.bucket:
            print("[ERROR] GCS bucket not initialized")
            return False

        try:
            blob_path = f"{self.memory_prefix}{filename}"
            blob = self.bucket.blob(blob_path)

            # Add metadata
            blob.metadata = {
                "updated_at": datetime.utcnow().isoformat(),
                "source": "consensus_archive",
                "version": "ultrathink_v1",
            }

            # Upload
            blob.upload_from_string(memory_content, content_type="text/markdown")
            print(f"[GCS] Uploaded: gs://{self.bucket_name}/{blob_path}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to upload memory: {e}")
            return False

    def download_memory(self, filename: str = "current_memory.md") -> str | None:
        """Download memory content from GCS.

        Args:
            filename: Name of memory file

        Returns:
            Memory content or None

        """
        if not self.bucket:
            print("[ERROR] GCS bucket not initialized")
            return None

        try:
            blob_path = f"{self.memory_prefix}{filename}"
            blob = self.bucket.blob(blob_path)

            if not blob.exists():
                print(f"[WARNING] Memory file not found: gs://{self.bucket_name}/{blob_path}")
                return None

            content = blob.download_as_text()
            print(f"[GCS] Downloaded: gs://{self.bucket_name}/{blob_path}")
            return content

        except Exception as e:
            print(f"[ERROR] Failed to download memory: {e}")
            return None

    def sync_local_to_gcs(self, local_path: str = "~/.claude-code/memory.md"):
        """Sync local memory file to GCS.

        Args:
            local_path: Path to local memory file

        """
        local_file = Path(local_path).expanduser()

        if not local_file.exists():
            print(f"[ERROR] Local memory file not found: {local_file}")
            return False

        content = local_file.read_text()
        return self.upload_memory(content)

    def sync_gcs_to_local(self, local_path: str = "~/.claude-code/memory.md"):
        """Sync GCS memory to local file.

        Args:
            local_path: Path to local memory file

        """
        content = self.download_memory()

        if not content:
            return False

        local_file = Path(local_path).expanduser()
        local_file.parent.mkdir(parents=True, exist_ok=True)
        local_file.write_text(content)
        print(f"[Local] Synced to: {local_file}")
        return True

    def create_configmap_yaml(self, output_path: str = "k8s/memory-configmap.yaml") -> bool:
        """Generate Kubernetes ConfigMap YAML for memory.

        Args:
            output_path: Where to save ConfigMap YAML

        Returns:
            True if successful

        """
        memory_content = self.download_memory()

        if not memory_content:
            print("[ERROR] No memory content to create ConfigMap")
            return False

        # Escape for YAML
        import yaml

        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "consensus-memory",
                "namespace": "default",
                "labels": {"app": "consensus-orchestrator", "component": "memory"},
            },
            "data": {"memory.md": memory_content, "updated_at": datetime.utcnow().isoformat()},
        }

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            yaml.dump(configmap, f, default_flow_style=False)

        print(f"[K8s] ConfigMap generated: {output_file}")
        return True


def generate_gke_deployment_yaml(output_path: str = "k8s/consensus-deployment.yaml"):
    """Generate complete GKE deployment YAML with memory init container.
    """
    deployment_yaml = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: consensus-orchestrator
  namespace: default
  labels:
    app: consensus-orchestrator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: consensus-orchestrator
  template:
    metadata:
      labels:
        app: consensus-orchestrator
    spec:
      # Service account with GCS access
      serviceAccountName: consensus-sa

      # Init container: Sync memory from GCS
      initContainers:
      - name: memory-sync
        image: google/cloud-sdk:alpine
        command:
        - sh
        - -c
        - |
          echo "Syncing memory from GCS..."
          gsutil cp gs://consensus-memory/memories/current_memory.md /memory/memory.md || echo "No memory found"
          echo "Memory sync complete"
        volumeMounts:
        - name: memory-volume
          mountPath: /memory
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "your-project-id"

      # Main container: Consensus orchestrator
      containers:
      - name: orchestrator
        image: gcr.io/your-project/consensus-orchestrator:latest
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: google-api-key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic-api-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-api-key
        - name: XAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: xai-api-key
        - name: PERPLEXITY_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: perplexity-api-key
        - name: MEMORY_PATH
          value: "/memory/memory.md"
        volumeMounts:
        - name: memory-volume
          mountPath: /memory
          readOnly: true
        - name: archive-volume
          mountPath: /data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"

      # Volumes
      volumes:
      - name: memory-volume
        emptyDir: {}
      - name: archive-volume
        persistentVolumeClaim:
          claimName: consensus-archive-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: consensus-orchestrator
  namespace: default
spec:
  selector:
    app: consensus-orchestrator
  ports:
  - port: 80
    targetPort: 8000
    name: http
  type: LoadBalancer

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: consensus-archive-pvc
  namespace: default
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard-rwo
"""

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(deployment_yaml)

    print(f"[K8s] Deployment YAML generated: {output_file}")
    return output_file


def generate_vertex_notebook_startup():
    """Generate Vertex Workbench startup script for memory sync.
    """
    startup_script = """#!/bin/bash
# Vertex Workbench Startup Script
# Auto-syncs consensus memory from GCS

set -e

echo "=== Consensus Memory Sync ==="

# Sync memory from GCS
MEMORY_DIR=/home/jupyter/.claude-code
mkdir -p $MEMORY_DIR

if gsutil -q stat gs://consensus-memory/memories/current_memory.md; then
    echo "Downloading memory from GCS..."
    gsutil cp gs://consensus-memory/memories/current_memory.md $MEMORY_DIR/memory.md
    echo "✓ Memory synced"
else
    echo "⚠ No memory found in GCS"
fi

# Clone consensus repo
REPO_DIR=/home/jupyter/shadowtag_v4-fastapi-services
if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning consensus repository..."
    cd /home/jupyter
    git clone https://github.com/ShadowTag-v2/shadowtag_v4-fastapi-services.git
    cd shadowtag_v4-fastapi-services/voice_consensus
    pip install -r requirements.txt
    echo "✓ Repository cloned"
fi

echo "=== Startup Complete ==="
"""

    output_file = Path("vertex/startup-script.sh")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(startup_script)
    output_file.chmod(0o755)

    print(f"[Vertex] Startup script generated: {output_file}")
    return output_file


# === CLI ===


def main():
    """CLI for Vertex/GKE deployment management"""
    import sys

    if len(sys.argv) < 2:
        print("Vertex Workbench / GKE Deployment Manager")
        print("\nCommands:")
        print("  sync-to-gcs         - Upload local memory to GCS")
        print("  sync-from-gcs       - Download memory from GCS to local")
        print("  create-configmap    - Generate K8s ConfigMap YAML")
        print("  create-deployment   - Generate K8s Deployment YAML")
        print("  create-vertex-startup - Generate Vertex startup script")
        print("  help                - Show this help")
        return

    command = sys.argv[1].lower()
    manager = VertexMemoryManager()

    if command == "sync-to-gcs":
        print("\nSyncing local memory to GCS...")
        success = manager.sync_local_to_gcs()
        if success:
            print("✓ Memory uploaded to GCS\n")
        else:
            print("✗ Failed to upload memory\n")

    elif command == "sync-from-gcs":
        print("\nSyncing memory from GCS to local...")
        success = manager.sync_gcs_to_local()
        if success:
            print("✓ Memory downloaded from GCS\n")
        else:
            print("✗ Failed to download memory\n")

    elif command == "create-configmap":
        print("\nGenerating Kubernetes ConfigMap...")
        success = manager.create_configmap_yaml()
        if success:
            print("✓ ConfigMap YAML created\n")
            print("Apply with:")
            print("  kubectl apply -f k8s/memory-configmap.yaml\n")
        else:
            print("✗ Failed to create ConfigMap\n")

    elif command == "create-deployment":
        print("\nGenerating Kubernetes Deployment...")
        generate_gke_deployment_yaml()
        print("\n✓ Deployment YAML created")
        print("\nCustomize k8s/consensus-deployment.yaml, then apply:")
        print("  kubectl apply -f k8s/consensus-deployment.yaml\n")

    elif command == "create-vertex-startup":
        print("\nGenerating Vertex Workbench startup script...")
        generate_vertex_notebook_startup()
        print("\n✓ Startup script created")
        print("\nUpload to GCS:")
        print("  gsutil cp vertex/startup-script.sh gs://your-bucket/")
        print("\nConfigure in Vertex Workbench notebook settings.\n")

    elif command == "help":
        print("\nVertex Workbench / GKE Native Deployment")
        print("=" * 60)
        print("\nThis tool manages consensus memory for Google Cloud deployments.")
        print("\nSetup:")
        print("  1. Create GCS bucket: gsutil mb gs://consensus-memory")
        print("  2. Sync local memory: python vertex_gke_deployment.py sync-to-gcs")
        print("  3. Generate K8s manifests: python vertex_gke_deployment.py create-deployment")
        print("  4. Deploy to GKE: kubectl apply -f k8s/")
        print("\nFor Vertex Workbench:")
        print("  1. Generate startup script: python vertex_gke_deployment.py create-vertex-startup")
        print("  2. Upload to GCS")
        print("  3. Configure in notebook settings\n")

    else:
        print(f"Unknown command: {command}")
        print("Run 'python vertex_gke_deployment.py help' for usage.")


if __name__ == "__main__":
    main()
