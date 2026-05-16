# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
SkillsBridge — Integration with google/skills repository.

Provides dynamic capability discovery and invocation by scanning
the external_repos/skills directory for SKILL.md manifests and
making them available to the CoreOrchestrator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Default path to the google/skills clone
_DEFAULT_SKILLS_ROOT = Path(__file__).resolve().parents[3] / "external_repos" / "skills"


@dataclass
class SkillManifest:
    """Parsed skill manifest from a SKILL.md file."""

    name: str
    description: str
    path: Path
    instructions: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class SkillsBridge:
    """
    Bridge to the google/skills repository.

    Scans the skills directory tree for SKILL.md files,
    parses their frontmatter, and indexes them for
    dynamic invocation by the orchestrator.
    """

    def __init__(self, skills_root: Path | None = None):
        self._skills_root = skills_root or _DEFAULT_SKILLS_ROOT
        self._registry: dict[str, SkillManifest] = {}
        self._loaded = False

    def discover(self) -> int:
        """
        Scan the skills directory and register all SKILL.md files.

        Returns:
            Number of skills discovered.
        """
        if not self._skills_root.exists():
            logger.warning("skills_bridge.missing_root", path=str(self._skills_root))
            return 0

        count = 0
        for skill_file in self._skills_root.rglob("SKILL.md"):
            try:
                manifest = self._parse_manifest(skill_file)
                self._registry[manifest.name] = manifest
                count += 1
            except Exception as e:
                logger.warning(
                    "skills_bridge.parse_error",
                    path=str(skill_file),
                    error=str(e),
                )

        self._loaded = True
        logger.info("skills_bridge.discovered", count=count)
        return count

    async def invoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Invoke a skill by name.

        Args:
            payload: Must contain 'skill_name' and optionally 'args'.

        Returns:
            Skill execution result.
        """
        if not self._loaded:
            self.discover()

        skill_name = payload.get("skill_name", "")
        if skill_name not in self._registry:
            available = list(self._registry.keys())[:10]
            return {
                "error": f"Skill '{skill_name}' not found",
                "available": available,
            }

        manifest = self._registry[skill_name]
        logger.info("skills_bridge.invoke", skill=skill_name, path=str(manifest.path))

        return {
            "skill": skill_name,
            "description": manifest.description,
            "path": str(manifest.path),
            "status": "ready",
        }

    @staticmethod
    def _parse_manifest(skill_file: Path) -> SkillManifest:
        """Parse a SKILL.md file into a SkillManifest."""
        content = skill_file.read_text(encoding="utf-8", errors="replace")

        # Extract name from frontmatter or directory
        name = skill_file.parent.name
        description = ""

        # Simple frontmatter parser
        lines = content.split("\n")
        in_frontmatter = False
        instructions_start = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    instructions_start = i + 1
                    break
            if in_frontmatter:
                if stripped.startswith("name:"):
                    name = stripped.split(":", 1)[1].strip().strip("'\"")
                elif stripped.startswith("description:"):
                    description = stripped.split(":", 1)[1].strip().strip("'\"")

        instructions = "\n".join(lines[instructions_start:]).strip()

        return SkillManifest(
            name=name,
            description=description or f"Skill from {skill_file.parent.name}",
            path=skill_file.parent,
            instructions=instructions[:2000],  # Cap for memory
        )

    @property
    def skill_count(self) -> int:
        """Number of registered skills."""
        return len(self._registry)

    def list_skills(self) -> list[str]:
        """List all registered skill names."""
        if not self._loaded:
            self.discover()
        return sorted(self._registry.keys())
