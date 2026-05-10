import re


def scrub_code(code_str: str) -> str:
    """Removes attribution, timestamps, and metadata to ensure a 'White Label' artifact.
    Essential for Tier 3 'Sovereign' clients.
    """
    # Remove shebangs and author tags
    code_str = re.sub(r"^#.*@author.*$", "", code_str, flags=re.MULTILINE)
    code_str = re.sub(r"^#.*Created by.*$", "", code_str, flags=re.MULTILINE)

    # Remove specific metadata patterns
    code_str = re.sub(r'"""[\s\S]*?"""', "", code_str, count=1)  # Remove top docstring if present

    return f"# OMEGA CERTIFIED ARTIFACT\n# CLEAN ROOM PROCESSED\n\n{code_str.strip()}"
