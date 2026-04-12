import logging
import shlex
import subprocess

logger = logging.getLogger("Jetski")


class Jetski:
    """
    Real-world Shell Executor for Self-Prompting n-autoresearch/Kosmos/BioAgents.
    """

    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir
        self.timeout = 300  # 5 minutes max per command

    def run_check(self, cmd: str) -> tuple[bool, str, str]:
        """
        Executes a shell command with strict timeout and capture.
        Returns: (success, stdout, stderr)
        """
        logger.info(f"🚤 JETSKI: Running '{cmd}' in {self.working_dir}...")

        # Security: Prevent basic injection if possible, but relies on Monkey/Judge checks
        args = shlex.split(cmd)

        try:
            result = subprocess.run(
                args, cwd=self.working_dir, capture_output=True, text=True, timeout=self.timeout
            )

            stdout = result.stdout.strip()
            stderr = result.stderr.strip()

            if result.returncode == 0:
                logger.debug(f"✅ Success: {stdout[:100]}...")
                return True, stdout, stderr
            else:
                logger.error(f"❌ Failed (RC={result.returncode}): {stderr[:100]}...")
                return False, stdout, stderr

        except subprocess.TimeoutExpired:
            msg = f"⏱️ TIMEOUT ({self.timeout}s) exceeded."
            logger.error(msg)
            return False, "", msg
        except Exception as e:
            logger.error(f"💥 EXECUTION ERROR: {e}")
            return False, "", str(e)
