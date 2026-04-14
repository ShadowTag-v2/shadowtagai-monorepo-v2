"""Boy Scout Rule Registry Importers

Import scripts for pushing the scout registry to external platforms:
- Airtable: airtable_import.py
- Notion: notion_import.py

Usage:
    from pnkln.scout.importers import airtable_import, notion_import

    # Import to Airtable
    airtable_import.import_registry()

    # Import to Notion
    notion_import.import_registry()

Environment Variables Required:
    AIRTABLE_API_KEY: Your Airtable Personal Access Token
    AIRTABLE_BASE_ID: The base ID to import to
    NOTION_API_KEY: Your Notion integration token
    NOTION_DATABASE_ID: The database ID to import to
"""

from pathlib import Path

REGISTRY_DIR = Path(__file__).parent.parent
JSON_REGISTRY = REGISTRY_DIR / "registry.json"
YAML_REGISTRY = REGISTRY_DIR / "registry.yaml"
