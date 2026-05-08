"""ANTIGRAVITY :: GOD MODE :: OMEGA DEPLOYMENT
Classification: TIER 30 SOVEREIGN
Context: 1M+
"""

import logging

from google.api_core.client_options import ClientOptions
from google.cloud import notebooks_v2

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# --- CONFIGURATION (UPDATED) ---
PROJECT_ID = "shadowtag-omega-v2"  # <--- TARGET UPDATED
REGION = "us-central1"
ZONE = "us-central1-a"
INSTANCE_NAME = "judge-six-omega-node"


def deploy():
    logger.info(f">>> 🖥️  PROVISIONING OMEGA NODE: {INSTANCE_NAME}...")
    logger.info(f"    Target: {PROJECT_ID} (Zone: {ZONE})")

    client_options = ClientOptions(api_endpoint=f"{REGION}-notebooks.googleapis.com:443")
    client = notebooks_v2.NotebookServiceClient(client_options=client_options)
    parent = f"projects/{PROJECT_ID}/locations/{ZONE}"

    # Define Instance with DRIVE ACCESS Scopes
    instance = notebooks_v2.Instance(
        gce_setup=notebooks_v2.GceSetup(
            machine_type="n1-standard-4",
            vm_image=notebooks_v2.VmImage(
                project="deeplearning-platform-release",
                image_family="common-cpu-notebooks",
            ),
            # CRITICAL: Grant the VM permission to touch Google Drive
            service_accounts=[
                notebooks_v2.ServiceAccount(
                    email="default",
                    scopes=[
                        "https://www.googleapis.com/auth/cloud-platform",
                        "https://www.googleapis.com/auth/drive",  # <--- THE 10TB KEY
                        "https://www.googleapis.com/auth/userinfo.email",
                    ],
                ),
            ],
            network_interfaces=[notebooks_v2.NetworkInterface(network="global/networks/default")],
            boot_disk=notebooks_v2.BootDisk(disk_size_gb=200, disk_type="PD_SSD"),
            disable_public_ip=False,
        ),
    )

    # Check if exists
    instance_path = f"{parent}/instances/{INSTANCE_NAME}"
    try:
        client.get_instance(name=instance_path)
        logger.info(f"    ✅ Instance {INSTANCE_NAME} already exists.")
        return
    except Exception:
        logger.info("    Instance not found. Creating...")

    try:
        op = client.create_instance(
            request=notebooks_v2.CreateInstanceRequest(
                parent=parent,
                instance_id=INSTANCE_NAME,
                instance=instance,
            ),
        )
        logger.info("    ⏳ Creation initiated... (approx 5-10 mins)")
        op.result(timeout=600)
        logger.info(f"    ✅ SUCCESS: https://{ZONE}-{PROJECT_ID}.notebooks.googleusercontent.com")
        logger.info("    NOTE: Open JupyterLab -> Terminal to access the 10TB Drive.")
    except Exception as e:
        logger.error(f"    ❌ FAILED: {e}")


if __name__ == "__main__":
    deploy()
