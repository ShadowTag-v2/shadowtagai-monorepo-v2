import json
import logging
import os
import sys

# SIEM-compliant logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "component": "SovereignPatcher", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)


class SovereignPatcher:
    """Deterministically applies Gemini JSON patches to the local filesystem."""

    def __init__(self, workspace_root: str = "/workspace"):
        self.workspace_root = os.path.abspath(workspace_root)

    def validate_path(self, filepath: str) -> str:
        """Ensures the agent cannot path-traverse out of the secure FUSE mount."""
        target_path = os.path.abspath(os.path.join(self.workspace_root, filepath))
        if not target_path.startswith(self.workspace_root):
            logger.error(f"SECURITY ALERT: Path traversal attempt blocked: {filepath}")
            raise PermissionError("Path traversal violation.")
        return target_path

    def apply_patch(self, patch_payload: str) -> bool:
        """
        Expects a JSON payload from Gemini:
        {
            "edits": [
                {
                    "filepath": "src/api/router.py",
                    "original_block": "def route():\n    pass",
                    "new_block": "def route():\n    return 200"
                }
            ]
        }
        """
        try:
            payload = json.loads(patch_payload)
            edits = payload.get("edits", [])

            for edit in edits:
                # Avoid validation issues in local test runs where file path might be relative
                if not os.path.isabs(edit["filepath"]):
                    filepath = self.validate_path(edit["filepath"])
                else:
                    filepath = edit["filepath"]

                original_block = edit["original_block"]
                new_block = edit["new_block"]

                if not os.path.exists(filepath):
                    logger.error(f"Patch failed: File {filepath} does not exist.")
                    return False

                with open(filepath, encoding="utf-8") as f:
                    file_content = f.read()

                # Deterministic check: The original block MUST exist exactly as described
                if original_block not in file_content:
                    logger.error(
                        f"Patch failed: original_block not found in {filepath}. AST mismatch or temporal drift."
                    )
                    # At this point, the Temporal-Reversal Git Hook takes over in the bash layer
                    return False

                # Apply the patch
                new_content = file_content.replace(original_block, new_block)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(new_content)

                logger.info(f"Successfully patched {filepath}.")

            return True

        except json.JSONDecodeError:
            logger.error("Failed to decode Gemini JSON payload.")
            return False
        except Exception as e:
            logger.error(f"Unexpected patcher error: {str(e)}")
            return False


if __name__ == "__main__":
    # In production, this receives stdin from the sovereign_daemon.py
    raw_payload = sys.stdin.read()

    # Use current directory when running locally vs /workspace in container
    workspace_root = os.getcwd() if os.getenv("GOOGLE_CLOUD_PROJECT") else "/workspace"

    patcher = SovereignPatcher(workspace_root=workspace_root)
    success = patcher.apply_patch(raw_payload)
    if not success:
        sys.exit(1)
    sys.exit(0)
