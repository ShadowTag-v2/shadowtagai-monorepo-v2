import subprocess

PROJECT_ID = "shadowtag-omega-v2"
REGION = "us-central1"
SERVICE_NAME = "judge-six-omega"


def deploy():
    print(">>> 🚀 DEPLOYING OMEGA TO CLOUD RUN...")

    # Source-based deploy (no Dockerfile needed if using Buildpacks, but we should ensure structure)
    cmd = [
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
        # "--allow-unauthenticated",  # For MCP server access (Use with caution or behind Gateway)
        # Note: Removing allow-unauthenticated by default for Judge 6, user can enable if needed for pub access
        f"--set-env-vars=PROJECT_ID={PROJECT_ID},REGION={REGION}",
    ]

    try:
        subprocess.run(cmd, check=True)
        print("    ✅ DEPLOYED.")
    except subprocess.CalledProcessError as e:
        print(f"    ❌ DEPLOY FAILED: {e}")


if __name__ == "__main__":
    deploy()
