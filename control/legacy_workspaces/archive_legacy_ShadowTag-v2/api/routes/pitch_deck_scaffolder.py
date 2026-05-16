# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import subprocess
import logging

logger = logging.getLogger("Kosmos.PitchDeck.CLI")


class OrchestratedScaffolder:
  """
  ⏺ ///▙▖▙▖▞ PHASE 2: HEADLESS CLI ORCHESTRATION
  Executes the @google/gemini-cli binary in headless mode to gather
  ground-truth data before passing context to Veo 3 or Nano Banana for generation.
  """

  def __init__(self):
    # Assumes the user installed via `npm install -g @google/gemini-cli` globally
    # or it's accessible via `npx @google/gemini-cli`
    self.cli_command = ["npx", "-y", "@google/gemini-cli"]

  def gather_pitchdeck_context(
    self, company_name: str, target_market: str
  ) -> str | None:
    """
    Runs a headless terminal prompt using gemini-1.5-pro to research the company
    and market before generating the Pitch Deck asset.
    """
    prompt = (
      f"You are a master pitch deck analyst. Conduct a deep web search on {company_name} "
      f"and its target market ({target_market}). Return exactly 3 bullet points outlining "
      f"the core pain point they solve, their competitive advantage, and their primary audience. "
      f"Output JSON only."
    )

    try:
      logger.info(f"Executing headless gemini CLI for {company_name}")

      # Non-interactive mode, JSON structured output requested
      cmd = self.cli_command + [
        "-m",
        "gemini-2.5-pro",
        "-p",
        prompt,
        "--output-format",
        "json",
      ]

      result = subprocess.run(cmd, capture_output=True, text=True, check=True)

      return result.stdout.strip()

    except subprocess.CalledProcessError as e:
      logger.error(f"Failed to execute gemini-cli: {e.stderr}")
      return None
    except Exception as e:
      logger.error(f"Execution boundary error: {str(e)}")
      return None
