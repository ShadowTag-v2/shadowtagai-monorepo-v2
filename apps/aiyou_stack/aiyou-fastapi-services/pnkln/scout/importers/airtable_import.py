"""
Airtable Import Script for Boy Scout Rule Registry

Imports skills and agents from registry.json to Airtable.

Usage:
    # Set environment variables
    export AIRTABLE_API_KEY = "REDACTED_API_KEY"
    export AIRTABLE_BASE_ID="your_base_id"

    # Run import
    python -m pnkln.scout.importers.airtable_import

    # Or from code
    from pnkln.scout.importers.airtable_import import import_registry
    import_registry()

Tables Created:
    - Skills: All skill definitions
    - Agents: All agent definitions with metadata templates
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


class AirtableImporter:
    """Import Boy Scout Rule Registry to Airtable"""

    def __init__(self, api_key: str | None = None, base_id: str | None = None):
        self.api_key = api_key or os.environ.get("AIRTABLE_API_KEY")
        self.base_id = base_id or os.environ.get("AIRTABLE_BASE_ID")

        if not self.api_key:
            raise ValueError("AIRTABLE_API_KEY environment variable required")
        if not self.base_id:
            raise ValueError("AIRTABLE_BASE_ID environment variable required")

        self.base_url = f"https://api.airtable.com/v0/{self.base_id}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
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

                # Rate limiting - Airtable allows 5 requests/second
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

    def create_skills_records(self, skills: list[dict]) -> list[str]:
        """Create skill records in Airtable"""
        records = []
        for skill in skills:
            records.append(
                {
                    "fields": {
                        "Name": skill["name"],
                        "Description": skill["description"],
                        "Triggers": ", ".join(skill.get("triggers", [])),
                        "Version": skill.get("version", "1.0"),
                    }
                }
            )

        # Airtable batch limit is 10 records
        created_ids = []
        for i in range(0, len(records), 10):
            batch = records[i : i + 10]
            result = self._make_request("POST", "Skills", {"records": batch})
            created_ids.extend([r["id"] for r in result.get("records", [])])
            time.sleep(0.25)  # Rate limiting

        return created_ids

    def create_agents_records(self, agents: list[dict]) -> list[str]:
        """Create agent records in Airtable"""
        records = []
        for agent in agents:
            # Serialize metadata template to JSON string
            metadata_json = json.dumps(agent.get("metadataTemplate", {}), indent=2)

            records.append(
                {
                    "fields": {
                        "Name": agent["name"],
                        "Description": agent["description"],
                        "Skills": ", ".join(agent.get("skills", [])),
                        "Metadata Template": metadata_json,
                        "Boy Scout Enabled": True,
                    }
                }
            )

        created_ids = []
        for i in range(0, len(records), 10):
            batch = records[i : i + 10]
            result = self._make_request("POST", "Agents", {"records": batch})
            created_ids.extend([r["id"] for r in result.get("records", [])])
            time.sleep(0.25)

        return created_ids

    def import_from_registry(self, registry_path: Path | None = None) -> dict[str, Any]:
        """Import full registry to Airtable"""
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
    api_key: str | None = None, base_id: str | None = None, registry_path: Path | None = None
) -> dict[str, Any]:
    """
    Convenience function to import registry to Airtable.

    Args:
        api_key: Airtable Personal Access Token (or set AIRTABLE_API_KEY env var)
        base_id: Airtable Base ID (or set AIRTABLE_BASE_ID env var)
        registry_path: Path to registry.json (defaults to pnkln/scout/registry.json)

    Returns:
        Dict with import results

    Example:
        >>> result = import_registry()
        >>> print(f"Imported {result['skills_imported']} skills")
    """
    importer = AirtableImporter(api_key=api_key, base_id=base_id)
    return importer.import_from_registry(registry_path)


def create_base_schema() -> str:
    """
    Return Airtable base schema instructions.

    Before running import, create these tables in your Airtable base:

    Skills Table:
        - Name (Single line text, Primary)
        - Description (Long text)
        - Triggers (Long text)
        - Version (Single line text)

    Agents Table:
        - Name (Single line text, Primary)
        - Description (Long text)
        - Skills (Long text)
        - Metadata Template (Long text)
        - Boy Scout Enabled (Checkbox)
    """
    return """
    Airtable Base Schema Required
    =============================

    Create two tables in your Airtable base:

    1. Skills Table
       - Name (Single line text) - Primary field
       - Description (Long text)
       - Triggers (Long text)
       - Version (Single line text)

    2. Agents Table
       - Name (Single line text) - Primary field
       - Description (Long text)
       - Skills (Long text)
       - Metadata Template (Long text)
       - Boy Scout Enabled (Checkbox)

    Then set environment variables:
        export AIRTABLE_API_KEY = "REDACTED_API_KEY"
        export AIRTABLE_BASE_ID="appXXXXXXXXXXXXXX"

    Run import:
        python -m pnkln.scout.importers.airtable_import
    """


if __name__ == "__main__":
    try:
        result = import_registry()
        print("\nImport complete!")
        print(f"  Skills imported: {result['skills_imported']}")
        print(f"  Agents imported: {result['agents_imported']}")
    except ValueError as e:
        print(f"Configuration error: {e}")
        print(create_base_schema())
        sys.exit(1)
    except Exception as e:
        print(f"Import failed: {e}")
        sys.exit(1)
