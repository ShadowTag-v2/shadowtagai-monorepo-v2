import time

from google.cloud import notebooks_v2

# CONFIGURATION
PROJECT_ID = "shadowtag-omega-v2"
REGION = "us-central1"
ZONE = "us-central1-a"
INSTANCE_NAME = "pnkln-god-mode-v3"


def deploy():
    print(f">>> 🖥️  PROVISIONING JUDGE 6 INFRASTRUCTURE (V2): {INSTANCE_NAME}...")

    time.time()
    # Client Setup (Use default global endpoint to avoid 404/Protocol/501 errors)
    client = notebooks_v2.NotebookServiceClient()

    # Location Parent
    parent = f"projects/{PROJECT_ID}/locations/{ZONE}"

    # Instance Config (Hardened)
    instance = notebooks_v2.Instance(
        gce_setup=notebooks_v2.GceSetup(
            machine_type="n1-standard-4",
            vm_image=notebooks_v2.VmImage(
                project="deeplearning-platform-release",
                family="common-cpu-notebooks",
            ),
            network_interfaces=[notebooks_v2.NetworkInterface(network="global/networks/default")],
            boot_disk=notebooks_v2.BootDisk(
                disk_size_gb=200,  # 200GB required
                disk_type="PD_SSD",
            ),
            disable_public_ip=False,
        ),
    )

    # Check Existence
    try:
        client.get_instance(name=f"{parent}/instances/{INSTANCE_NAME}")
        print(f"    ✅ Instance {INSTANCE_NAME} already active.")
        return
    except Exception:
        print("    Instance not found. Initiating creation sequence...")

    # Create
    try:
        op = client.create_instance(
            request=notebooks_v2.CreateInstanceRequest(
                parent=parent,
                instance_id=INSTANCE_NAME,
                instance=instance,
            ),
        )
        print("    ⏳ Deploying... (Wait 5-10 mins)")
        op.result(timeout=900)
        print("    ✅ SUCCESS. Judge 6 Node Online.")
        print(f"    👉 Access: https://{ZONE}-{PROJECT_ID}.notebooks.googleusercontent.com")
    except Exception as e:
        print(f"    ❌ DEPLOYMENT FAILED: {e}")


if __name__ == "__main__":
    deploy()
