import subprocess
import logging

logger = logging.getLogger("Omni-Triad")


class OmniSearchTriad:
    """The God Mode Search & Replace Engine for Serverless execution."""

    def __init__(self, workspace: str = "/tmp/workspace"):
        self.workspace = workspace

    def execute_strike(
        self, target_pattern: str, ast_pattern: str, ast_rewrite: str, lang: str = "python"
    ):
        """
        Executes the 3-Stage Ballistic Search.
        1. Nowgrep -> 2. Ripgrep -> 3. AST-Grep
        """
        logger.info(f"🚀 STAGE 1: NOWGREP (Macro-Sweep) for '{target_pattern}'")

        # 1. NOWGREP: Find files 30x faster
        nowgrep_out = subprocess.run(
            ["nowgrep", target_pattern, self.workspace], capture_output=True, text=True
        )

        # Extract unique file paths
        files_to_fix = list(
            set([line.split(":")[0] for line in nowgrep_out.stdout.splitlines() if ":" in line])
        )

        if not files_to_fix:
            return "No vulnerabilities detected by Nowgrep."

        logger.info(
            f"🎯 NOWGREP acquired {len(files_to_fix)} targets. STAGE 2: RIPGREP context extraction."
        )

        # 2. RIPGREP: Extract Context for the AI's memory buffer (Logging purposes)
        context_memory = {}
        for file in files_to_fix:
            rg_out = subprocess.run(
                ["rg", target_pattern, file, "-C", "3"], capture_output=True, text=True
            )
            context_memory[file] = rg_out.stdout[:1000]  # Truncate to save tokens

        logger.info("🔪 STAGE 3: AST-GREP (Structural Mutagenesis).")

        # 3. AST-GREP: Mathematically rewrite the syntax tree
        for file in files_to_fix:
            sg_cmd = [
                "sg",
                "run",
                "--pattern",
                ast_pattern,
                "--rewrite",
                ast_rewrite,
                "--lang",
                lang,
                "--update-all",
                file,
            ]
            subprocess.run(sg_cmd, capture_output=True)

        return (
            f"Triad Strike Complete. {len(files_to_fix)} files structurally rewritten via AST-Grep."
        )
