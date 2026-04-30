# FILE: genesis_setup.py
# CLASSIFICATION: PROPRIETARY // FOUNDER EYES ONLY
# "It just works."

import os
import subprocess

from google.cloud import firestore

# Default to current project, fallback to specific ID
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v2")
REGION = "us-central1"


def run_cmd(cmd):
    print(f"   > {cmd}")
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError:
        print("     ! Command failed or resource exists. Continuing...")


def main():
    print(f" INITIATING ANTIGRAVITY GENESIS [PROJECT: {PROJECT_ID}]")

    # 1. WAKE THE MIND (Enable APIs)
    print("\n[1/4] Waking the Mind...")
    apis = [
        "run.googleapis.com",
        "firestore.googleapis.com",
        "aiplatform.googleapis.com",
        "secretmanager.googleapis.com",
        "cloudbuild.googleapis.com",
    ]
    run_cmd(f"gcloud services enable {' '.join(apis)} --project {PROJECT_ID}")

    # 2. FORM THE SINGULARITY (Firestore Native)
    print("\n[2/4] Forming the Singularity (Vector Indices)...")
    # Creates the KNN Vector Index for "The Index" (17GB Codebase)
    # Note: Requires gcloud beta or alpha in some environments, checking availability
    try:
        run_cmd(
            f"gcloud firestore indexes composite create "
            f"--project {PROJECT_ID} "
            f"--collection-group=knowledge_base "
            f'--field-config field-path=embedding,vector-config=\'{{"dimension":768, "flat": "{{}}"}}\'',
        )
    except Exception as e:
        print(f"     ! Index creation skipped or failed (might already exist): {e}")

    # 3. SEED THE PACIFIC EDGE (Asset Map)
    print("\n[3/4] Seeding Pacific Edge Protocol...")
    try:
        db = firestore.Client(project=PROJECT_ID)
    except Exception as e:
        print(f"     ! Firestore Client Init Failed (Auth?): {e}")
        return

    # These are not just database entries. They are TARGETS.
    assets = {
        "NODE_0": {
            "name": "Sulphur Bank Mine",
            "role": "THE PRIME (Root of Trust)",
            "type": "GEOTHERMAL",
            "capacity": "100MW",
            "status": "SECURED",
            "action_item": "Deploy Cloud Run",
        },
        "NODE_1": {
            "name": "Diablo Canyon",
            "role": "THE CROWN (West Inference)",
            "type": "NUCLEAR",
            "capacity": "2.2GW",
            "status": "TARGETING",
            "action_item": "File Standstill Agreement (Q4 2025)",
        },
        "NODE_2": {
            "name": "Indian Point",
            "role": "THE BANK (East HFT)",
            "type": "NUCLEAR",
            "capacity": "2.0GW",
            "status": "SURVEYING",
            "action_item": "Subsurface Tunnel Survey",
        },
        "NODE_3": {
            "name": "Gulf Swarm",
            "role": "THE MESH (Sovereignty)",
            "type": "OFFSHORE",
            "capacity": "3.1GW",
            "status": "PLANNING",
            "action_item": "CAISO Pilot Proposal",
        },
        "NODE_4": {
            "name": "Zion Station",
            "role": "THE GIANT (Training)",
            "type": "NUCLEAR",
            "capacity": "2.1GW",
            "status": "WILDCARD",
            "action_item": "NRC FOIA Request",
        },
    }

    for node_id, data in assets.items():
        db.collection("infrastructure_ring").document(node_id).set(data)
        print(f"   + Locked Target: {data['name']}")

    # 4. ENFORCE GULFSTREAM (Financial Law)
    print("\n[4/4] Codifying Gulfstream Rent Logic...")
    # These rules are immutable. Judge 6 reads these to kill bad deals.
    financial_laws = {
        "FIN_01": {"rule": "LTV_CAC_RATIO", "min_threshold": 4.0, "action": "BLOCK"},
        "FIN_02": {"rule": "GROSS_MARGIN", "min_threshold": 0.85, "action": "BLOCK"},
        "FIN_03": {"rule": "PAYBACK_PERIOD", "max_months": 3, "action": "FLAG"},
        "SURV_01": {"rule": "SURVIVAL_RATE", "min_threshold": 0.75, "action": "KILL"},
    }
    db.collection("governance_doctrine").document("gulfstream_laws").set(financial_laws)

    print("\n GENESIS COMPLETE. THE SYSTEM IS ALIVE.")


if __name__ == "__main__":
    main()
