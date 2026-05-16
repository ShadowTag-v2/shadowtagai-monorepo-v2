# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Tests for SkillsBridge — dynamic capability discovery."""

from __future__ import annotations

import pytest
from packages.shadowtag_os.skills_bridge.bridge import SkillManifest, SkillsBridge

# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def skills_dir(tmp_path):
    """Create a temporary skills directory with sample SKILL.md files."""
    # Skill 1: with frontmatter
    skill1 = tmp_path / "alpha-skill"
    skill1.mkdir()
    (skill1 / "SKILL.md").write_text("---\nname: Alpha Skill\ndescription: Does alpha things\n---\n# Alpha Skill\n\nInstructions for alpha.\n")

    # Skill 2: minimal frontmatter
    skill2 = tmp_path / "beta-skill"
    skill2.mkdir()
    (skill2 / "SKILL.md").write_text("---\nname: Beta Skill\n---\n# Beta Skill\n")

    # Skill 3: no frontmatter (name from directory)
    skill3 = tmp_path / "gamma-skill"
    skill3.mkdir()
    (skill3 / "SKILL.md").write_text("# Gamma\n\nJust a readme-style skill.\n")

    # Skill 4: nested
    nested = tmp_path / "nested" / "delta-skill"
    nested.mkdir(parents=True)
    (nested / "SKILL.md").write_text("---\nname: Delta Skill\ndescription: Deep nested skill\n---\nDeep instructions.\n")

    return tmp_path


@pytest.fixture
def bridge(skills_dir):
    return SkillsBridge(skills_root=skills_dir)


# ─── Tests: SkillManifest ────────────────────────────────────────────────────


class TestSkillManifest:
    """Test SkillManifest dataclass."""

    def test_basic_creation(self, tmp_path):
        m = SkillManifest(
            name="test",
            description="A test skill",
            path=tmp_path,
        )
        assert m.name == "test"
        assert m.description == "A test skill"
        assert m.instructions == ""
        assert m.metadata == {}

    def test_with_metadata(self, tmp_path):
        m = SkillManifest(
            name="meta-skill",
            description="desc",
            path=tmp_path,
            metadata={"version": "1.0"},
        )
        assert m.metadata["version"] == "1.0"


# ─── Tests: SkillsBridge Discovery ───────────────────────────────────────────


class TestSkillsBridgeDiscovery:
    """Test SkillsBridge.discover() scanning."""

    def test_discovers_all_skills(self, bridge):
        count = bridge.discover()
        assert count == 4  # alpha, beta, gamma, delta

    def test_skill_count_property(self, bridge):
        assert bridge.skill_count == 0
        bridge.discover()
        assert bridge.skill_count == 4

    def test_list_skills_sorted(self, bridge):
        bridge.discover()
        names = bridge.list_skills()
        assert names == sorted(names)
        assert "Alpha Skill" in names
        assert "Beta Skill" in names
        assert "Delta Skill" in names

    def test_gamma_uses_directory_name(self, bridge):
        bridge.discover()
        names = bridge.list_skills()
        assert "gamma-skill" in names

    def test_missing_root_returns_zero(self, tmp_path):
        bridge = SkillsBridge(skills_root=tmp_path / "nonexistent")
        assert bridge.discover() == 0

    def test_auto_discover_on_list(self, bridge):
        """list_skills triggers auto-discover if not loaded."""
        names = bridge.list_skills()
        assert len(names) == 4

    def test_parse_extracts_description(self, bridge):
        bridge.discover()
        # Alpha has explicit description
        alpha = bridge._registry.get("Alpha Skill")
        assert alpha is not None
        assert alpha.description == "Does alpha things"

    def test_instructions_capped(self, tmp_path):
        """Verify instructions are capped at 2000 chars."""
        big_skill = tmp_path / "big"
        big_skill.mkdir()
        (big_skill / "SKILL.md").write_text("---\nname: Big\n---\n" + ("x" * 5000))
        bridge = SkillsBridge(skills_root=tmp_path)
        bridge.discover()
        manifest = bridge._registry["Big"]
        assert len(manifest.instructions) <= 2000


# ─── Tests: SkillsBridge Invoke ──────────────────────────────────────────────


class TestSkillsBridgeInvoke:
    """Test SkillsBridge.invoke() async method."""

    @pytest.mark.asyncio
    async def test_invoke_existing_skill(self, bridge):
        bridge.discover()
        result = await bridge.invoke({"skill_name": "Alpha Skill"})
        assert result["skill"] == "Alpha Skill"
        assert result["status"] == "ready"
        assert "path" in result

    @pytest.mark.asyncio
    async def test_invoke_missing_skill(self, bridge):
        bridge.discover()
        result = await bridge.invoke({"skill_name": "NonexistentSkill"})
        assert "error" in result
        assert "available" in result

    @pytest.mark.asyncio
    async def test_invoke_auto_discovers(self, bridge):
        """Invoke triggers discover if not loaded."""
        result = await bridge.invoke({"skill_name": "Alpha Skill"})
        assert result["skill"] == "Alpha Skill"

    @pytest.mark.asyncio
    async def test_invoke_returns_description(self, bridge):
        bridge.discover()
        result = await bridge.invoke({"skill_name": "Delta Skill"})
        assert result["description"] == "Deep nested skill"


# ─── Tests: Parse Manifest ───────────────────────────────────────────────────


class TestParseManifest:
    """Test static _parse_manifest method."""

    def test_parse_with_full_frontmatter(self, tmp_path):
        f = tmp_path / "skill" / "SKILL.md"
        f.parent.mkdir()
        f.write_text("---\nname: Custom Name\ndescription: Custom desc\n---\n# Instructions\nDo the thing.\n")
        manifest = SkillsBridge._parse_manifest(f)
        assert manifest.name == "Custom Name"
        assert manifest.description == "Custom desc"
        assert "Do the thing." in manifest.instructions

    def test_parse_without_frontmatter(self, tmp_path):
        f = tmp_path / "raw-skill" / "SKILL.md"
        f.parent.mkdir()
        f.write_text("# Just a title\n\nSome content.\n")
        manifest = SkillsBridge._parse_manifest(f)
        assert manifest.name == "raw-skill"
        assert "raw-skill" in manifest.description
