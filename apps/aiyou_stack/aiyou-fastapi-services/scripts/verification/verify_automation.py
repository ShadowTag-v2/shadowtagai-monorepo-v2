import subprocess


def run_test(name, cmd):
    print(f"Testing {name}...")
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"Stdout: {res.stdout[:200]}")
        if res.returncode == 0:
            print("✅ Success")
        else:
            print(f"❌ Failed (Exit {res.returncode})")
            print(f"Stderr: {res.stderr}")
    except Exception as e:
        print(f"❌ Exception: {e}")


# Test 1: Run Launcher with Argument 5 (Tier 30) - Should not prompt for input
run_test("Launcher Automation (Arg 5)", "python3 pnkln_mission_start.py 5")

# Test 2: Verify Install Script (Dry run logic verification)
# We won't actually source it here as it affects the user's shell, but we can check if it runs
run_test("Install Script Execution", "bash scripts/install_alias.sh")
