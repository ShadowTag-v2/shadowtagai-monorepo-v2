# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import subprocess

PROJECT_ID = "shadowtag-omega-v2"
REGION = "us-central1"
SERVICE_NAME = "judge-six-omega"


def deploy():
    print(">>> 🚀 DEPLOYING OMEGA TO CLOUD RUN...")

    # Source-based deploy (no Docker)
    subprocess.run(
        [
            "gcloud",
            "run",
            "deploy",
            SERVICE_NAME,
            f"--project={PROJECT_ID}",
            f"--region={REGION}",
            "--source=.",  # Deploy from source
            "--platform=managed",
            "--min-instances=1",  # Judge#6 SLA (p99≤90ms)
            "--max-instances=10",
            "--memory=512Mi",
            "--timeout=300s",
            "--allow-unauthenticated",  # For MCP server access
            "--set-env-vars=PROJECT_ID=shadowtag-omega-v2,REGION=us-central1",
        ],
        check=True,
    )

    print("    ✅ DEPLOYED.")


if __name__ == "__main__":
    deploy()
