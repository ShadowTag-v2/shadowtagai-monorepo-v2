"""Persona Engine — Manages and injects Antigravity personas from .antigravity/prompts/
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("PersonaEngine")

PROMPTS_DIR = Path(".antigravity/prompts")


class PersonaEngine:
    def __init__(self, prompts_dir: Path = PROMPTS_DIR):
        self.prompts_dir = prompts_dir
        self.personas = {}
        self.load_personas()

    def load_personas(self):
        """Loads all .md files from the prompts directory as personas."""
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory {self.prompts_dir} not found.")
            return

        for prompt_file in self.prompts_dir.glob("*.md"):
            persona_name = prompt_file.stem
            try:
                content = prompt_file.read_text()
                self.personas[persona_name] = content
                logger.info(f"Loaded persona: {persona_name}")
            except Exception as e:
                logger.error(f"Failed to load persona {persona_name}: {e}")

    def get_persona(self, name: str) -> str:
        """Retrieves a persona by name."""
        return self.personas.get(name, "Persona not found.")

    def list_personas(self) -> list:
        """Lists available personas."""
        return list(self.personas.keys())

    def update_judge_6_1(self, doctrinal_updates: str):
        """Specifically updates the Judge 6.1 persona with new doctrinal logic."""
        judge_path = self.prompts_dir / "judge_6_1.md"
        try:
            current_content = judge_path.read_text() if judge_path.exists() else ""
            new_content = f"{current_content}\n\n## Refined Logic (v6.1)\n{doctrinal_updates}"
            judge_path.write_text(new_content)
            self.personas["judge_6_1"] = new_content
            logger.info("Judge 6.1 persona updated with refined logic.")
        except Exception as e:
            logger.error(f"Failed to update Judge 6.1: {e}")


if __name__ == "__main__":
    engine = PersonaEngine()
    print(f"Available Personas: {engine.list_personas()}")
    print("-" * 20)
    print(f"Master Persona Snippet:\n{engine.get_persona('master')[:100]}...")
