import os
import subprocess
import sys
import time


def run_build():
    env = os.environ.copy()
    env["CARGO_HOME"] = (
        "/Users/pikeymickey/.gemini/extensions/pickle-rick/sessions/2026-03-06-d83e665a/cargo_home"
    )
    env["RUSTUP_HOME"] = (
        "/Users/pikeymickey/.gemini/extensions/pickle-rick/sessions/2026-03-06-d83e665a/rustup_home"
    )

    biome_dir = "/Users/pikeymickey/.gemini/extensions/pickle-rick/sessions/2026-03-06-d83e665a/7a3f12e1/build/biome"
    target_bin = os.path.join(biome_dir, "target/release/biome")

    print(f"Starting build in {biome_dir}...")

    # Run in background
    process = subprocess.Popen(
        ["cargo", "build", "--release", "-p", "biome_cli"],
        cwd=biome_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    start_time = time.time()
    while True:
        if process.poll() is not None:
            print(f"Process exited with code {process.returncode}")
            output = process.stdout.read()
            print(output)
            break

        if os.path.exists(target_bin):
            print(f"Binary found at {target_bin}!")
            # Still wait for process to finish clean
            process.wait()
            break

        elapsed = time.time() - start_time
        print(f"Still building... ({int(elapsed)}s elapsed)")
        sys.stdout.flush()
        time.sleep(30)  # Heartbeat every 30 seconds


if __name__ == "__main__":
    run_build()
