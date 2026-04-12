"""
Notion Import Script for Boy Scout Rule Registry

Imports skills and agents from registry.json to Notion databases.

Usage:
    # Set environment variables
    export NOTION_API_KEY = "REDACTED_API_KEY"
    export NOTION_SKILLS_DB="your_skills_database_id"
    export NOTION_AGENTS_DB="your_agents_database_id"

    # Run import
    python -m pnkln.scout.importers.notion_import

    # Or from code
    from pnkln.scout.importers.notion_import import import_registry
    import_registry()

Databases Created:
    - Skills Database: All skill definitions
    - Agents Database: All agent definitions with metadata templates
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("Please install requests: pip install requests")
    sys.exit(1)


class NotionImporter:
    """Import Boy Scout Rule Registry to Notion"""

    NOTION_VERSION = "2022-06-28"

    def __init__(
        self,
        api_key: str | None = None,
        skills_db_id: str | None = None,
        agents_db_id: str | None = None,
    ):
        self.api_key = api_key or os.environ.get("NOTION_API_KEY")
        self.skills_db_id = skills_db_id or os.environ.get("NOTION_SKILLS_DB")
        self.agents_db_id = agents_db_id or os.environ.get("NOTION_AGENTS_DB")

        if not self.api_key:
            raise ValueError("NOTION_API_KEY environment variable required")
        if not self.skills_db_id:
            raise ValueError("NOTION_SKILLS_DB environment variable required")
        if not self.agents_db_id:
            raise ValueError("NOTION_AGENTS_DB environment variable required")

        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION,
        }

    def _make_request(
        self, method: str, endpoint: str, data: dict | None = None, retries: int = 3
    ) -> dict[str, Any]:
        """Make API request with retry logic"""
        url = f"{self.base_url}/{endpoint}"

        for attempt in range(retries):
            try:
                if method == "GET":
                    response = requests.get(url, headers=self.headers)
                elif method == "POST":
                    response = requests.post(url, headers=self.headers, json=data)
                elif method == "PATCH":
                    response = requests.patch(url, headers=self.headers, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                # Rate limiting - Notion allows 3 requests/second
                if response.status_code == 429:
                    wait_time = 2**attempt
                    print(f"Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()
                return response.json()

            except requests.RequestException as e:
                if attempt == retries - 1:
                    raise
                wait_time = 2**attempt
                print(f"Request failed, retrying in {wait_time}s: {e}")
                time.sleep(wait_time)

        return {}

    def _create_page(self, database_id: str, properties: dict) -> str:
        """Create a page in a Notion database"""
        data = {"parent": {"database_id": database_id}, "properties": properties}
        result = self._make_request("POST", "pages", data)
        return result.get("id", "")

    def _rich_text(self, content: str) -> list[dict]:
        """Create rich text block"""
        return [{"type": "text", "text": {"content": content}}]

    def create_skills_records(self, skills: list[dict]) -> list[str]:
        """Create skill pages in Notion database"""
        created_ids = []

        for skill in skills:
            properties = {
                "Name": {"title": self._rich_text(skill["name"])},
                "Description": {"rich_text": self._rich_text(skill["description"])},
                "Triggers": {"rich_text": self._rich_text(", ".join(skill.get("triggers", [])))},
                "Version": {"rich_text": self._rich_text(skill.get("version", "1.0"))},
            }

            page_id = self._create_page(self.skills_db_id, properties)
            created_ids.append(page_id)
            time.sleep(0.35)  # Rate limiting

        return created_ids

    def create_agents_records(self, agents: list[dict]) -> list[str]:
        """Create agent pages in Notion database"""
        created_ids = []

        for agent in agents:
            metadata_json = json.dumps(agent.get("metadataTemplate", {}), indent=2)

            properties = {
                "Name": {"title": self._rich_text(agent["name"])},
                "Description": {"rich_text": self._rich_text(agent["description"])},
                "Skills": {"rich_text": self._rich_text(", ".join(agent.get("skills", [])))},
                "Metadata Template": {"rich_text": self._rich_text(metadata_json)},
                "Boy Scout Enabled": {"checkbox": True},
            }

            page_id = self._create_page(self.agents_db_id, properties)
            created_ids.append(page_id)
            time.sleep(0.35)

        return created_ids

    def import_from_registry(self, registry_path: Path | None = None) -> dict[str, Any]:
        """Import full registry to Notion"""
        if registry_path is None:
            registry_path = Path(__file__).parent.parent / "registry.json"

        with open(registry_path) as f:
            registry = json.load(f)

        print(f"Importing {len(registry.get('skills', []))} skills...")
        skill_ids = self.create_skills_records(registry.get("skills", []))

        print(f"Importing {len(registry.get('agents', []))} agents...")
        agent_ids = self.create_agents_records(registry.get("agents", []))

        return {
            "skills_imported": len(skill_ids),
            "agents_imported": len(agent_ids),
            "skill_ids": skill_ids,
            "agent_ids": agent_ids,
        }


def import_registry(
    api_key: str | None = None,
    skills_db_id: str | None = None,
    agents_db_id: str | None = None,
    registry_path: Path | None = None,
) -> dict[str, Any]:
    """
    Convenience function to import registry to Notion.

    Args:
        api_key: Notion Integration Token (or set NOTION_API_KEY env var)
        skills_db_id: Skills Database ID (or set NOTION_SKILLS_DB env var)
        agents_db_id: Agents Database ID (or set NOTION_AGENTS_DB env var)
        registry_path: Path to registry.json (defaults to pnkln/scout/registry.json)

    Returns:
        Dict with import results

    Example:
        >>> result = import_registry()
        >>> print(f"Imported {result['skills_imported']} skills")
    """
    importer = NotionImporter(api_key=api_key, skills_db_id=skills_db_id, agents_db_id=agents_db_id)
    return importer.import_from_registry(registry_path)


def create_database_schema() -> str:
    """Return Notion database schema instructions."""
    return """
    Notion Database Schema Required
    ================================

    Create two databases in your Notion workspace:

    1. Skills Database
       Properties:
       - Name (Title) - Primary property
       - Description (Text)
       - Triggers (Text)
       - Version (Text)

    2. Agents Database
       Properties:
       - Name (Title) - Primary property
       - Description (Text)
       - Skills (Text)
       - Metadata Template (Text)
       - Boy Scout Enabled (Checkbox)

    Setup Steps:
    1. Create a Notion Integration at https://www.notion.so/my-integrations
    2. Share both databases with your integration
    3. Copy the database IDs from the URLs

    Database ID is the 32-character string in the URL:
    https://notion.so/workspace/DATABASE_ID?v=...

    Set environment variables:
        export NOTION_API_KEY="secret_XXXXXXXX"
        export NOTION_SKILLS_DB="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        export NOTION_AGENTS_DB="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

    Run import:
        python -m pnkln.scout.importers.notion_import
    """


if __name__ == "__main__":
    try:
        result = import_registry()
        print("\nImport complete!")
        print(f"  Skills imported: {result['skills_imported']}")
        print(f"  Agents imported: {result['agents_imported']}")
    except ValueError as e:
        print(f"Configuration error: {e}")
        print(create_database_schema())
        sys.exit(1)
    except Exception as e:
        print(f"Import failed: {e}")
        sys.exit(1)
