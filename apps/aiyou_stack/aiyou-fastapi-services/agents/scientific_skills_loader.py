"""
Scientific Skills Loader for n-autoresearch/Kosmos/BioAgents Cavalry Squadron.
Loads and injects 119 scientific skills from claude-scientific-skills repo.

Maps skills to Troop specializations:
- HHT (Headquarters): orchestration, meta-analysis, coordination skills
- AIR_CAV (Aerial Recon): research, literature, databases, discovery
- ALPHA (Abrams): heavy computation, ML, deep learning, GNNs
- BRAVO (Bradley): integration, pipelines, workflows, ETL
- CHARLIE (Cavalry): domain-specific expertise, specialized analysis
"""

import os
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class SkillDomain(StrEnum):
    """Scientific skill domains mapped to cavalry operations."""

    # Discovery & Research
    LITERATURE = "literature"  # Literature review, paper analysis
    DATABASES = "databases"  # Scientific databases, data sources
    DISCOVERY = "discovery"  # Hypothesis generation, exploration

    # Computation & Analysis
    ML_DEEP = "ml_deep"  # Deep learning, GNNs, transformers
    ML_CLASSIC = "ml_classic"  # Classical ML, statistics
    COMPUTATION = "computation"  # Heavy compute, simulations

    # Domain Expertise
    BIOINFORMATICS = "bioinformatics"  # Genomics, proteomics
    CHEMISTRY = "chemistry"  # Drug discovery, molecular
    PHYSICS = "physics"  # Astronomy, materials
    MEDICINE = "medicine"  # Clinical, health data

    # Integration & Workflow
    VISUALIZATION = "visualization"  # Plotting, charts, figures
    DATA_HANDLING = "data_handling"  # ETL, data processing
    INTEGRATION = "integration"  # Lab systems, APIs

    # Meta-Analysis
    EVALUATION = "evaluation"  # Peer review, validation
    WRITING = "writing"  # Scientific writing, reports


@dataclass
class ScientificSkill:
    """Represents a single scientific skill."""

    name: str
    description: str
    domain: SkillDomain
    skill_path: Path
    content: str = ""

    @property
    def summary(self) -> str:
        """Get compact skill summary for prompt injection."""
        return f"[{self.name}] {self.description[:200]}..."


# Skill to Domain mapping (119 skills categorized)
SKILL_DOMAIN_MAP: dict[str, SkillDomain] = {
    # Literature & Research (AIR_CAV - Aerial Reconnaissance)
    "literature-review": SkillDomain.LITERATURE,
    "perplexity-search": SkillDomain.LITERATURE,
    "openalex-database": SkillDomain.LITERATURE,
    "pubmed-database": SkillDomain.LITERATURE,
    "biorxiv-database": SkillDomain.LITERATURE,
    "paper-2-web": SkillDomain.LITERATURE,
    "scholar-evaluation": SkillDomain.EVALUATION,
    "peer-review": SkillDomain.EVALUATION,
    # Database Skills (AIR_CAV)
    "gene-database": SkillDomain.DATABASES,
    "uniprot-database": SkillDomain.DATABASES,
    "pdb-database": SkillDomain.DATABASES,
    "chembl-database": SkillDomain.DATABASES,
    "drugbank-database": SkillDomain.DATABASES,
    "pubchem-database": SkillDomain.DATABASES,
    "kegg-database": SkillDomain.DATABASES,
    "ensembl-database": SkillDomain.DATABASES,
    "clinvar-database": SkillDomain.DATABASES,
    "cosmic-database": SkillDomain.DATABASES,
    "gwas-database": SkillDomain.DATABASES,
    "string-database": SkillDomain.DATABASES,
    "reactome-database": SkillDomain.DATABASES,
    "opentargets-database": SkillDomain.DATABASES,
    "clinicaltrials-database": SkillDomain.DATABASES,
    "alphafold-database": SkillDomain.DATABASES,
    "fda-database": SkillDomain.DATABASES,
    "ena-database": SkillDomain.DATABASES,
    "geo-database": SkillDomain.DATABASES,
    "hmdb-database": SkillDomain.DATABASES,
    "metabolomics-workbench-database": SkillDomain.DATABASES,
    "clinpgx-database": SkillDomain.DATABASES,
    "zinc-database": SkillDomain.DATABASES,
    "uspto-database": SkillDomain.DATABASES,
    # Deep Learning & GNNs (ALPHA - Heavy Armor)
    "deepchem": SkillDomain.ML_DEEP,
    "torch_geometric": SkillDomain.ML_DEEP,
    "torchdrug": SkillDomain.ML_DEEP,
    "transformers": SkillDomain.ML_DEEP,
    "pytorch-lightning": SkillDomain.ML_DEEP,
    "esm": SkillDomain.ML_DEEP,
    "stable-baselines3": SkillDomain.ML_DEEP,
    "pufferlib": SkillDomain.ML_DEEP,
    "diffdock": SkillDomain.ML_DEEP,
    "scvi-tools": SkillDomain.ML_DEEP,
    # Classical ML & Statistics (ALPHA)
    "scikit-learn": SkillDomain.ML_CLASSIC,
    "scikit-survival": SkillDomain.ML_CLASSIC,
    "scikit-bio": SkillDomain.ML_CLASSIC,
    "statsmodels": SkillDomain.ML_CLASSIC,
    "pymc": SkillDomain.ML_CLASSIC,
    "statistical-analysis": SkillDomain.ML_CLASSIC,
    "shap": SkillDomain.ML_CLASSIC,
    "umap-learn": SkillDomain.ML_CLASSIC,
    "pymoo": SkillDomain.ML_CLASSIC,
    # Computation & Simulation (ALPHA)
    "simpy": SkillDomain.COMPUTATION,
    "fluidsim": SkillDomain.COMPUTATION,
    "sympy": SkillDomain.COMPUTATION,
    "dask": SkillDomain.COMPUTATION,
    "modal": SkillDomain.COMPUTATION,
    "networkx": SkillDomain.COMPUTATION,
    # Bioinformatics (CHARLIE - Domain Expertise)
    "biopython": SkillDomain.BIOINFORMATICS,
    "scanpy": SkillDomain.BIOINFORMATICS,
    "anndata": SkillDomain.BIOINFORMATICS,
    "pysam": SkillDomain.BIOINFORMATICS,
    "pydeseq2": SkillDomain.BIOINFORMATICS,
    "deeptools": SkillDomain.BIOINFORMATICS,
    "gget": SkillDomain.BIOINFORMATICS,
    "cellxgene-census": SkillDomain.BIOINFORMATICS,
    "arboreto": SkillDomain.BIOINFORMATICS,
    "etetoolkit": SkillDomain.BIOINFORMATICS,
    "cobrapy": SkillDomain.BIOINFORMATICS,
    "bioservices": SkillDomain.BIOINFORMATICS,
    "lamindb": SkillDomain.BIOINFORMATICS,
    "geniml": SkillDomain.BIOINFORMATICS,
    "gtars": SkillDomain.BIOINFORMATICS,
    # Chemistry & Drug Discovery (CHARLIE)
    "rdkit": SkillDomain.CHEMISTRY,
    "datamol": SkillDomain.CHEMISTRY,
    "molfeat": SkillDomain.CHEMISTRY,
    "matchms": SkillDomain.CHEMISTRY,
    "medchem": SkillDomain.CHEMISTRY,
    "pyopenms": SkillDomain.CHEMISTRY,
    "pytdc": SkillDomain.CHEMISTRY,
    "tooluniverse": SkillDomain.CHEMISTRY,
    "biomni": SkillDomain.CHEMISTRY,
    "adaptyv": SkillDomain.CHEMISTRY,
    "denario": SkillDomain.CHEMISTRY,
    # Physics & Materials (CHARLIE)
    "astropy": SkillDomain.PHYSICS,
    "pymatgen": SkillDomain.PHYSICS,
    "geopandas": SkillDomain.PHYSICS,
    "aeon": SkillDomain.PHYSICS,
    # Medical & Clinical (CHARLIE)
    "pyhealth": SkillDomain.MEDICINE,
    "neurokit2": SkillDomain.MEDICINE,
    "pydicom": SkillDomain.MEDICINE,
    "pathml": SkillDomain.MEDICINE,
    "histolab": SkillDomain.MEDICINE,
    "flowio": SkillDomain.MEDICINE,
    # Visualization (BRAVO - Integration)
    "matplotlib": SkillDomain.VISUALIZATION,
    "plotly": SkillDomain.VISUALIZATION,
    "seaborn": SkillDomain.VISUALIZATION,
    "scientific-visualization": SkillDomain.VISUALIZATION,
    # Data Handling (BRAVO)
    "polars": SkillDomain.DATA_HANDLING,
    "vaex": SkillDomain.DATA_HANDLING,
    "zarr-python": SkillDomain.DATA_HANDLING,
    "exploratory-data-analysis": SkillDomain.DATA_HANDLING,
    "reportlab": SkillDomain.DATA_HANDLING,
    "markitdown": SkillDomain.DATA_HANDLING,
    "document-skills": SkillDomain.DATA_HANDLING,
    # Lab Integration (BRAVO)
    "benchling-integration": SkillDomain.INTEGRATION,
    "dnanexus-integration": SkillDomain.INTEGRATION,
    "latchbio-integration": SkillDomain.INTEGRATION,
    "omero-integration": SkillDomain.INTEGRATION,
    "opentrons-integration": SkillDomain.INTEGRATION,
    "protocolsio-integration": SkillDomain.INTEGRATION,
    "labarchive-integration": SkillDomain.INTEGRATION,
    "pylabrobot": SkillDomain.INTEGRATION,
    "datacommons-client": SkillDomain.INTEGRATION,
    "get-available-resources": SkillDomain.INTEGRATION,
    # Meta & Discovery (HHT - Headquarters)
    "hypothesis-generation": SkillDomain.DISCOVERY,
    "scientific-brainstorming": SkillDomain.DISCOVERY,
    "scientific-critical-thinking": SkillDomain.EVALUATION,
    "scientific-writing": SkillDomain.WRITING,
    "hypogenic": SkillDomain.DISCOVERY,
}

# Troop to Domain mapping
TROOP_DOMAINS: dict[str, list[SkillDomain]] = {
    "HHT": [SkillDomain.DISCOVERY, SkillDomain.EVALUATION, SkillDomain.WRITING],
    "AIR_CAV": [SkillDomain.LITERATURE, SkillDomain.DATABASES],
    "ALPHA": [SkillDomain.ML_DEEP, SkillDomain.ML_CLASSIC, SkillDomain.COMPUTATION],
    "BRAVO": [SkillDomain.VISUALIZATION, SkillDomain.DATA_HANDLING, SkillDomain.INTEGRATION],
    "CHARLIE": [
        SkillDomain.BIOINFORMATICS,
        SkillDomain.CHEMISTRY,
        SkillDomain.PHYSICS,
        SkillDomain.MEDICINE,
    ],
}


class ScientificSkillsLoader:
    """
    Load and inject 119 scientific skills into n-autoresearch/Kosmos/BioAgents squadron.

    Skills are loaded from claude-scientific-skills/scientific-skills/ and
    mapped to cavalry troops based on domain specialization.

    Usage:
        loader = ScientificSkillsLoader()
        loader.load_all_skills()

        # Get skills for a specific troop
        alpha_skills = loader.get_skills_for_troop("ALPHA")

        # Inject into Antigravity prompt
        enhanced_prompt = loader.inject_skills_to_prompt(
            "ALPHA",
            base_prompt="You are a computational analyst..."
        )
    """

    def __init__(self, skills_base_path: str | None = None):
        """Initialize loader with path to skills directory."""
        if skills_base_path:
            self.skills_path = Path(skills_base_path)
        else:
            # Default relative to this file
            self.skills_path = (
                Path(__file__).parent.parent / "claude-scientific-skills" / "scientific-skills"
            )

        self.skills: dict[str, ScientificSkill] = {}
        self.skills_by_domain: dict[SkillDomain, list[ScientificSkill]] = {
            domain: [] for domain in SkillDomain
        }
        self.loaded = False

    def _parse_frontmatter(self, content: str) -> tuple[str, str, str]:
        """Parse YAML frontmatter from SKILL.md file."""
        name = ""
        description = ""
        body = content

        # Match YAML frontmatter
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
        if match:
            frontmatter = match.group(1)
            body = match.group(2)

            # Extract name
            name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip().strip("\"'")

            # Extract description
            desc_match = re.search(
                r'^description:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.MULTILINE | re.DOTALL
            )
            if desc_match:
                description = desc_match.group(1).strip().strip("\"'")

        return name, description, body

    def load_skill(self, skill_dir: str) -> ScientificSkill | None:
        """Load a single skill from its directory."""
        skill_path = self.skills_path / skill_dir / "SKILL.md"

        if not skill_path.exists():
            return None

        try:
            content = skill_path.read_text(encoding="utf-8")
            name, description, body = self._parse_frontmatter(content)

            # Get domain from mapping, default to DATA_HANDLING
            domain = SKILL_DOMAIN_MAP.get(skill_dir, SkillDomain.DATA_HANDLING)

            skill = ScientificSkill(
                name=name or skill_dir,
                description=description,
                domain=domain,
                skill_path=skill_path,
                content=body[:5000],  # Limit content for memory
            )

            return skill

        except Exception as e:
            print(f"Error loading skill {skill_dir}: {e}")
            return None

    def load_all_skills(self) -> int:
        """
        Load all 119 skills from the scientific-skills directory.

        Returns:
            Number of skills loaded successfully.
        """
        if not self.skills_path.exists():
            raise FileNotFoundError(f"Skills directory not found: {self.skills_path}")

        loaded_count = 0

        for skill_dir in sorted(os.listdir(self.skills_path)):
            skill_dir_path = self.skills_path / skill_dir

            if skill_dir_path.is_dir() and not skill_dir.startswith("."):
                skill = self.load_skill(skill_dir)

                if skill:
                    self.skills[skill.name] = skill
                    self.skills_by_domain[skill.domain].append(skill)
                    loaded_count += 1

        self.loaded = True
        return loaded_count

    def get_skills_for_domain(self, domain: SkillDomain) -> list[ScientificSkill]:
        """Get all skills for a specific domain."""
        return self.skills_by_domain.get(domain, [])

    def get_skills_for_troop(self, troop_name: str) -> list[ScientificSkill]:
        """
        Get relevant skills for a cavalry troop.

        Args:
            troop_name: One of HHT, AIR_CAV, ALPHA, BRAVO, CHARLIE

        Returns:
            List of ScientificSkill objects relevant to the troop.
        """
        domains = TROOP_DOMAINS.get(troop_name, [])
        skills = []

        for domain in domains:
            skills.extend(self.skills_by_domain.get(domain, []))

        return skills

    def get_skill_summary_block(self, troop_name: str, max_skills: int = 20) -> str:
        """
        Generate a compact skill summary block for prompt injection.

        Args:
            troop_name: Troop to generate summary for
            max_skills: Maximum skills to include

        Returns:
            Formatted string block for Antigravity prompt injection.
        """
        skills = self.get_skills_for_troop(troop_name)[:max_skills]

        if not skills:
            return ""

        lines = [
            f"\n## SCIENTIFIC SKILLS ACTIVE ({len(skills)} skills)",
            "Domain expertise available for this mission:\n",
        ]

        for skill in skills:
            lines.append(f"- **{skill.name}**: {skill.description[:100]}...")

        return "\n".join(lines)

    def inject_skills_to_prompt(
        self,
        troop_name: str,
        base_prompt: str,
        max_skills: int = 15,
        injection_marker: str = "{{SCIENTIFIC_SKILLS}}",
    ) -> str:
        """
        Inject relevant scientific skills into an Antigravity prompt.

        Args:
            troop_name: Troop receiving the prompt
            base_prompt: Base Antigravity prompt with optional injection marker
            max_skills: Maximum skills to inject
            injection_marker: Marker to replace with skills (or append if not found)

        Returns:
            Enhanced prompt with scientific skills injected.
        """
        skill_block = self.get_skill_summary_block(troop_name, max_skills)

        if injection_marker in base_prompt:
            return base_prompt.replace(injection_marker, skill_block)
        else:
            # Append skills before the final instruction block
            return f"{base_prompt}\n{skill_block}"

    def get_full_skill_content(self, skill_name: str) -> str:
        """
        Get the full SKILL.md content for a specific skill.

        Used when an agent needs deep expertise in a particular area.
        """
        skill = self.skills.get(skill_name)
        if not skill:
            return ""

        try:
            return skill.skill_path.read_text(encoding="utf-8")
        except Exception:
            return skill.content

    def get_stats(self) -> dict:
        """Get loader statistics."""
        return {
            "total_skills": len(self.skills),
            "loaded": self.loaded,
            "skills_by_domain": {
                domain.value: len(skills) for domain, skills in self.skills_by_domain.items()
            },
            "skills_by_troop": {
                troop: len(self.get_skills_for_troop(troop)) for troop in TROOP_DOMAINS
            },
        }


# Global singleton instance
_loader_instance: ScientificSkillsLoader | None = None


def get_skills_loader() -> ScientificSkillsLoader:
    """Get or create the global skills loader instance."""
    global _loader_instance

    if _loader_instance is None:
        _loader_instance = ScientificSkillsLoader()
        _loader_instance.load_all_skills()

    return _loader_instance


def inject_skills_for_mission(troop_name: str, base_prompt: str) -> str:
    """
    Convenience function to inject skills for a mission.

    Args:
        troop_name: Troop executing the mission
        base_prompt: Base prompt to enhance

    Returns:
        Enhanced prompt with scientific skills.
    """
    loader = get_skills_loader()
    return loader.inject_skills_to_prompt(troop_name, base_prompt)


# Quick test when run directly
if __name__ == "__main__":
    loader = ScientificSkillsLoader()
    count = loader.load_all_skills()

    print(f"\n{'=' * 60}")
    print("SCIENTIFIC SKILLS LOADER - n-autoresearch/Kosmos/BioAgents Phase 3")
    print(f"{'=' * 60}")
    print(f"\nLoaded {count} scientific skills")

    stats = loader.get_stats()

    print("\nSkills by Domain:")
    for domain, count in stats["skills_by_domain"].items():
        if count > 0:
            print(f"  {domain}: {count}")

    print("\nSkills by Troop:")
    for troop, count in stats["skills_by_troop"].items():
        print(f"  {troop}: {count} skills")

    print(f"\n{'=' * 60}")
    print("Sample injection for ALPHA Troop:")
    print(f"{'=' * 60}")
    print(loader.get_skill_summary_block("ALPHA", max_skills=5))
