import argparse
import os
import subprocess
import sys

# Add apps path to reach zero_cpu_router
sys.path.insert(0, os.path.abspath("apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services"))

try:
    from zero_cpu_router import dispatch_compute
except ImportError:
    print("WARNING: zero_cpu_router not found. Formatting will proceed locally without Cloud dispatch.")


def run_local_linting(target_dir):
    """
    Tier 1: High-speed, local operations on the Apple M1 Max.
    Runs ruff and biome across the integrated monorepo.
    """
    print(f"[+] Launching Tier 1 Local ANE/Silicon Compute: Linting {target_dir}")
    # Using biome for JS/TS and ruff for Python
    cmds = [
        ["npx", "--yes", "@biomejs/biome", "format", "--write", target_dir],
        ["npx", "--yes", "@biomejs/biome", "lint", "--write", target_dir],
        ["python3", "-m", "ruff", "check", "--fix", target_dir],
        ["python3", "-m", "ruff", "format", target_dir],
    ]

    for cmd in cmds:
        try:
            print(f" -> Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=False)
        except Exception as e:
            print(f"    [!] Failed to run {cmd[0]}: {e}")


def dispatch_heavy_refactor(file_path):
    """
    Tier 3: Asynchronous structural refactoring.
    Sends the file to the Colab inbox via Google Drive IPC.
    """
    print(f"[+] Dispatching Tier 3 Colab Refactor: {file_path}")

    with open(file_path) as f:
        code_content = f.read()

    # Create the payload for the Colab worker to process
    payload = f"""
# SYSTEM: Refactor this file to comply with the ShadowTag-v2 Monorepo Standards.
# Strip out legacy YOLO code, ensure typing, and optimize.
FILE_PATH = '{file_path}'
CODE = '''
{code_content}
'''

def perform_refactoring(code):
    # This represents the LLM inference logic that Colab will execute
    # Return the refactored code string
    return code

RESULT = perform_refactoring(CODE)
"""

    # Send payload to zero_cpu_router which will drop it in the IPC Drive Inbox
    # We estimate the bytes to force tier 3 (Cloud) if needed, or explicitly setting requires_cloud
    dispatch_compute(payload, estimated_bytes=len(payload), requires_cloud=True)


def main():
    parser = argparse.ArgumentParser(description="The Great Monorepo Refactor Pipeline")
    parser.add_argument(
        "--refactor",
        action="store_true",
        help="Execute the Great Refactor across all apps/ and libs/",
    )
    parser.add_argument("--lint-only", action="store_true", help="Only run the local M1 Max linters")
    parser.add_argument("targets", nargs="*", default=["apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services"], help="Target directories")
    args = parser.parse_args()

    target_dirs = args.targets

    if args.lint_only or args.refactor:
        for d in target_dirs:
            if os.path.exists(d):
                run_local_linting(d)

    if args.refactor:
        print("\n[+] Initiating The Great Refactor (Colab T4 Swarm)...")
        # In a real scenario, we would selectively target complex monolithic files
        # For demonstration, we simulate targeting a few Python files
        for root, _, files in os.walk("apps"):
            for file in files:
                if file.endswith(".py") and os.path.getsize(os.path.join(root, file)) > 10000:  # Files > 10KB
                    file_path = os.path.join(root, file)
                    dispatch_heavy_refactor(file_path)
        print("[+] All refactoring payloads dispatched to Google Drive IPC Inbox. Awaiting Colab workers...")


if __name__ == "__main__":
    main()
