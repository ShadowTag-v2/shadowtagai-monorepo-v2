"""
CodeMender Agent - Neuro-symbolic Repair Agent
Inspired by DeepMind's CodeMender (2025)

Capabilities:
1. Root Cause Analysis (Gemini 2.0 Flash Thinking)
2. Patch Generation (Gemini 1.5 Pro)
3. Verification (Local Test Execution)
"""

import logging
import os
import subprocess
from dataclasses import dataclass
from typing import Any

import google.generativeai as genai  # type: ignore
import vertexai  # type: ignore
from vertexai.generative_models import GenerativeModel  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class RepairResult:
    success: bool
    patch: str | None
    root_cause: str
    verification_log: str


class CodeMenderAgent:
    """
    Autonomous agent for fixing code vulnerabilities/bugs.
    Uses a 'Think -> Patch -> Verify' loop.
    """

    def __init__(self, project_id: str | None = None):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("CLOUD_ML_REGION", "us-central1")

        # Initialize Models
        # 1. Thinking Model for Root Cause Analysis
        self.think_model_name = "gemini-2.0-flash-thinking-exp-1219"
        # 2. Coding Model for Patch Generation
        self.code_model_name = "gemini-1.5-pro-002"

        if self.project_id:
            vertexai.init(project=self.project_id, location=self.location)
            self.think_model = GenerativeModel(self.think_model_name)
            self.code_model = GenerativeModel(self.code_model_name)
            self.mode = "vertex"
        elif os.getenv("GEMINI_API_KEY"):
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.think_model = genai.GenerativeModel(self.think_model_name)
            self.code_model = genai.GenerativeModel(self.code_model_name)
            self.mode = "studio"
        else:
            logger.warning("No credentials found for CodeMender.")
            self.think_model = None
            self.code_model = None

    async def resolve_issue(
        self, file_path: str, issue_description: str, test_command: str | None = None
    ) -> dict[str, Any]:
        """
        Main entry point to fix an issue in a file.
        """
        if not self.think_model:
            return {"status": "error", "reason": "CodeMender not initialized"}

        logger.info(f"CodeMender: Analyzing {file_path} for '{issue_description}'")

        try:
            with open(file_path) as f:
                code_content = f.read()
        except FileNotFoundError:
            return {"status": "error", "reason": f"File {file_path} not found"}

        # Step 1: Root Cause Analysis (Thinking)
        root_cause = await self._analyze_root_cause(code_content, issue_description)

        # Step 2: Generate Patch (Coding)
        patch = await self._generate_patch(code_content, root_cause)

        # Step 3: Verification (Optional)
        verification_log = "Skipped"
        success = False

        if test_command:
            success, verification_log = await self._verify_fix(file_path, patch, test_command)
            # If failed, we could have a retry loop here (future enhancement)
        else:
            # If no test command, we perform a tailored 'syntax check' or just return the patch
            success = True  # Tentative
            verification_log = "No test command provided. Manual review required."

        return {
            "status": "success" if success else "failed",
            "root_cause": root_cause,
            "patch": patch,
            "verification_log": verification_log,
            "file": file_path,
        }

    async def _analyze_root_cause(self, code: str, issue: str) -> str:
        if not self.think_model:
            return "Analysis failed: Thinking model not initialized (check credentials)"

        prompt = f"""
        Analyze the following code to find the root cause of this issue: "{issue}".

        CODE:
        ```
        {code}
        ```

        Think step-by-step. Identify the specific lines and logic causing the failure.
        Return ONLY the Root Cause Analysis explanation.
        """
        try:
            resp = await self.think_model.generate_content_async(prompt)
            return str(resp.text)
        except Exception as e:
            return f"Analysis failed: {str(e)}"

    async def _generate_patch(self, code: str, root_cause: str) -> str:
        if not self.code_model:
            return code  # Return original code if model missing

        prompt = f"""
        You are a Security Patcher. Fix the bug identified below.

        ROOT CAUSE:
        {root_cause}

        CODE:
        ```
        {code}
        ```

        Return the FIXED code block for the file.
        Wrap the code in ```python (or language) blocks.
        Do NOT change unrelated code.
        """
        try:
            resp = await self.code_model.generate_content_async(prompt)
            # Extract code block logic (simplified)
            text = str(resp.text)
            if "```" in text:
                # Naive extraction of first block
                return text.split("```")[1].split("\n", 1)[1].rsplit("\n", 1)[0]
            return text
        except Exception as e:
            return f"Patch gen failed: {str(e)}"

    async def _verify_fix(self, file_path: str, patch: str, test_cmd: str) -> tuple[bool, str]:
        """
        Applies patch temporarily, runs test, reverts if fails.
        """
        # Read original
        try:
            with open(file_path) as f:
                original_content = f.read()

            # Apply Patch (Overwrite for test)
            with open(file_path, "w") as f:
                f.write(patch)

            # Run Test
            logger.info(f"Running verification: {test_cmd}")
            proc = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=30)

            log = f"STDOUT: {proc.stdout}\nSTDERR: {proc.stderr}"

            if proc.returncode == 0:
                # Success! Keep the file or revert?
                # Usually we want to keep it if success, but for safety let's revert and return the patch content
                # allow user to apply it via 'git apply' or similar?
                # For this agent, let's leave it applied if success, revert if fail.
                return True, log
            else:
                # Revert
                with open(file_path, "w") as f:
                    f.write(original_content)
                return False, log

        except Exception as e:
            # Emergency Revert
            if "original_content" in locals():
                with open(file_path, "w") as f:
                    f.write(original_content)
            return False, f"Verification Exception: {str(e)}"
