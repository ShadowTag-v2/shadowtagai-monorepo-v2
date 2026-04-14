import logging
import os
import sys

from shadowtag_v2.tracking_controller import TrackingController

from src.pnkln.utils.pqc_crypto import get_pqc_metadata

# Setup logging
logging.basicConfig(level=logging.INFO)


def test_pqc_hybrid_provenance():
    print("\n///▞ PQC HARDENING :: Starting Hybrid Operational Test")

    # 1. Check PQC Metadata
    pqc_meta = get_pqc_metadata()
    print(f"///▞ DOCTRINE :: {pqc_meta['status']} (Target: {pqc_meta['pqc_target']})")

    # 2. Initialize TrackingController (loads HybridSigner)
    controller = TrackingController()
    print("///▞ CONTROLLER :: Initialized with Hybrid Falcon-Dilithium Signer")

    # 3. Running a provenance cycle
    test_media = "pqc_hybrid_test.mp4"
    owner = "ErikHancock_Sovereign"

    print(f"///▞ TRACKING :: Registering media '{test_media}' with Hybrid Signature")
    reg_result = controller.watermark_and_register(test_media, "video", owner)

    if reg_result.get("status") == "registered successfully":
        print(f"✅ REGISTRATION :: Success (Block {reg_result['receipt_block']})")
        print(f"///▞ SIGNATURE :: {reg_result['signature'][:32]}... [Hybrid Classical + PQC]")
    else:
        print(f"❌ REGISTRATION :: Failed: {reg_result.get('reason')}")
        return False

    # 4. Verify provenance
    print("///▞ VERIFICATION :: Testing Dual-Algorithm integrity check")
    verify_result = controller.verify_provenance_full_cycle(test_media)

    if verify_result.get("status") == "AUTHENTIC":
        print("✅ VERIFICATION :: Success. Both Ed25519 and PQC-Shim validated.")
        print(f"///▞ AUDITOR :: Consensus - {verify_result['auditor_consensus']}")
        return True
    print(f"❌ VERIFICATION :: Failed: {verify_result.get('status')}")
    return False


if __name__ == "__main__":
    # Ensure PYTHONPATH is set correctly
    os.environ["PYTHONPATH"] = f"{os.getcwd()}:{os.getcwd()}/src"

    success = test_pqc_hybrid_provenance()
    if success:
        print("\n///▞ PQC HARDENING :: Operational Verification Complete 🚀🛡️\n")
        sys.exit(0)
    else:
        print("\n///▞ PQC HARDENING :: Verification FAILED ❌\n")
        sys.exit(1)
