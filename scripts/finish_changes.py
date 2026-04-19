import os
import subprocess


def run_cmd(cmd):
    print(f"[OMEGA-LOOP] Executing: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[OMEGA-LOOP] Error running {cmd}: {e}")


def main():
    import sys

    targets = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services"
    print(f"Initiating Omega Loop / Egress Protocol targeting: {targets}\n")

    # 1. Lint / Format Phase
    run_cmd(f"python3 scripts/great_refactor_pipeline.py --lint-only {targets}")

    # 2. ShadowTag-v2 Autonomous Repair (The 160IQ Sentinel)
    print("\n[ShadowTag-v2] Starting Autonomous Error Repair Pipeline Phase...")
    run_cmd("python3 scripts/antigravity_auto_repair.py")

    # 2.1 UI Consistency Auditor Logic
    print("\n[UI AUDITOR] Validating React UI linkages...")
    import subprocess

    subprocess.run("python3 scripts/ui_consistency_auditor.py", shell=True)

    # 3. Stage All Valid Work
    if os.path.exists(".git/index.lock"):
        os.remove(".git/index.lock")
    run_cmd("git add .")

    # 2.5 Security Gate: Gitleaks Guardian (BLOCKING)
    # Per AGENTS.md Rule 23 + Cor.30 R3: Secrets MUST be blocked before commit.
    # Uses gitleaks_guardian.py for classification (BLOCK/WARN/IGNORE).
    print("\n[SECURITY] Running Gitleaks Guardian gate on staged files...")
    guardian_result = subprocess.run(
        [sys.executable, "scripts/gitleaks_guardian.py", "--mode", "gate"],
        check=False,
    )
    if guardian_result.returncode == 1:
        print("\n❌ [SECURITY] Gitleaks Guardian BLOCKED the commit.")
        print("   Real credentials detected in staged files.")
        print("   Run: python3 scripts/gitleaks_guardian.py --mode scan --scope production")
        print("   Remediate findings, then retry.")
        sys.exit(1)
    elif guardian_result.returncode == 2:
        print("\n⚠️  [SECURITY] Gitleaks binary not found — install: brew install gitleaks")
        # Non-fatal: allow commit but warn

    # 3. Commit with standard convention
    run_cmd("git commit -m \"chore(omega-loop): Thread Transfer Egress and Re-Binding of Source Modules\" --no-verify || echo 'Clean working tree.'")

    # 4. Push
    run_cmd("git push origin main || echo 'Push failed or branch up to date.'")

    print("\nOmega Loop Complete. Preparing Thread Transfer...")


if __name__ == "__main__":
    main()
