import subprocess
import os
import unicodedata
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.tools.bash_security import BashSecurityValidator


class BashExecutor:
    def __init__(self, initial_cwd=None):
        self.cwd = initial_cwd or os.getcwd()
        self.validator = BashSecurityValidator()

    def run_command(self, command: str):
        # 1. Zero-Trust AST Gate
        try:
            self.validator.validate(command)
        except ValueError as e:
            return "", f"🚨 {str(e)}", 1

        # 2. CWD Persistence Wrapper (macOS Darwin target)
        snapshot_file = f"/tmp/ag-cwd-snapshot-{os.getpid()}"
        escaped_command = command.replace("'", "'\\''")
        wrapped = f"cd '{self.cwd}' && export CI=true CLAUDECODE=1 && eval '{escaped_command}' && pwd -P > {snapshot_file}"

        result = subprocess.run(wrapped, shell=True, capture_output=True, text=True)

        # 3. APFS Unicode Normalization
        if os.path.exists(snapshot_file):
            with open(snapshot_file) as f:
                raw_cwd = f.read().strip()
                if raw_cwd:
                    # Protect against Apple's NFD decomposed Unicode triggering false changes
                    self.cwd = unicodedata.normalize("NFC", raw_cwd)
            os.remove(snapshot_file)

        return result.stdout, result.stderr, result.returncode
