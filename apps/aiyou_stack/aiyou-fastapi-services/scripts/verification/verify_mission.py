import os
import signal
import subprocess
import time


def run_test(name, command, cwd=".", wait_time=5, expect_success=True):
    print(f"\n⚡️ Testing: {name}...")
    print(f"   Command: {command}")

    try:
        if wait_time > 0:
            # Process that should stay running (or needs time)
            p = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,
            )
            try:
                # Wait for a bit
                time.sleep(wait_time)

                # Check if it's still running or exited
                ret = p.poll()
                if ret is None:
                    print(f"   ✅ Started successfully (PID {p.pid})")
                    # Clean up
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                else:
                    stdout, stderr = p.communicate()
                    if ret != 0:
                        print(f"   ❌ Failed (Exit {ret})")
                        print(f"   Stderr: {stderr.decode('utf-8')[:200]}...")
                    else:
                        print("   ✅ Finished successfully (Exit 0)")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        else:
            # Run to completion
            res = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
            if res.returncode == 0 or (not expect_success and res.returncode != 0):
                print(f"   ✅ Completed successfully (Exit {res.returncode})")
            else:
                print(f"   ❌ Failed (Exit {res.returncode})")
                print(f"   Stderr: {res.stderr[:200]}...")

    except Exception as e:
        print(f"   ❌ Error executing test: {e}")


print("🧪 Starting Verification Suite")
run_test("Multi-Model Router", "npm run dev", cwd="router", wait_time=5)
run_test(
    "ACE Workflow",
    "npm run triple:pass",
    cwd="tools/orchestrator",
    wait_time=0,
)  # run to completion
run_test("Vision Ingestion", "python3 -m ingestion.moondream_ingest", cwd=".", wait_time=0)
run_test("Computer Use Agent", "python3 -m computer_use.agent", cwd=".", wait_time=3)
print("\n🏁 Verification Complete")
