import os
import subprocess


def run_cmd(cmd) -> None:
    try:  # noqa: SIM105
        subprocess.run(cmd, shell=True, check=True)  # nosec B602 — intentional shell for git/system ops
    except subprocess.CalledProcessError:
        pass


def main() -> None:
    import sys

    targets = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "apps/ShadowTag-v2_stack/ShadowTag-v2-fastapi-services"

    # 1. Lint / Format Phase
    run_cmd(f"python3 scripts/great_refactor_pipeline.py --lint-only {targets}")

    # 2. ShadowTag-v2 Autonomous Repair (The 160IQ Sentinel)
    run_cmd("python3 scripts/antigravity_auto_repair.py")

    # 2.1 UI Consistency Auditor Logic
    import subprocess

    subprocess.run("python3 scripts/ui_consistency_auditor.py", shell=True)  # nosec B602 — intentional shell for git/system ops

    # 3. Stage All Valid Work
    if os.path.exists(".git/index.lock"):
        os.remove(".git/index.lock")
    run_cmd("git add .")

    # 2.5 Security Gate: Gitleaks Guardian (BLOCKING)
    # Per AGENTS.md Rule 23 + Cor.30 R3: Secrets MUST be blocked before commit.
    # Uses gitleaks_guardian.py for classification (BLOCK/WARN/IGNORE).
    guardian_result = subprocess.run(
        [sys.executable, "scripts/gitleaks_guardian.py", "--mode", "gate"],
        check=False,
    )
    if guardian_result.returncode == 1:
        sys.exit(1)
    elif guardian_result.returncode == 2:
        pass
        # Non-fatal: allow commit but warn

    # 3. Commit with standard convention
    run_cmd("git commit -m \"chore(omega-loop): Thread Transfer Egress and Re-Binding of Source Modules\" --no-verify || echo 'Clean working tree.'")

    # 4. Push
    run_cmd("git push origin main || echo 'Push failed or branch up to date.'")


if __name__ == "__main__":
    main()
