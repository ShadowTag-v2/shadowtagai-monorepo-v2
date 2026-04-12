import re
import os

files_to_remove_w3 = [
    "external_repos/apps/JamAIBase/services/api/pyproject.toml",
    "external_repos/apps/JamAIBase/clients/python/pyproject.toml",
    "apps/aiyou_stack/aiyou-fastapi-services/external_repos/JamAIBase/services/api/pyproject.toml",
    "apps/aiyou_stack/aiyou-fastapi-services/external_repos/JamAIBase/clients/python/pyproject.toml"
]

for fpath in files_to_remove_w3:
    if os.path.exists(fpath):
        with open(fpath, "r") as f:
            content = f.read()
        # Remove "W3", from select = [...]
        content = re.sub(r'"W3",\s*', '', content)
        with open(fpath, "w") as f:
            f.write(content)

# Fix Agentic-AI-Pipeline merge conflict
fpath = "apps/aiyou_stack/aiyou-fastapi-services/external_repos/Agentic-AI-Pipeline/clients/python/pyproject.toml"
if os.path.exists(fpath):
    fixed_content = """[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "agentic-ai-client"
version = "0.1.0"
description = "Python client SDK for Agentic AI (FastAPI + SSE)."
requires-python = ">=3.10"
dependencies = ["httpx>=0.27.0","anyio>=4.0.0"]

[project.scripts]
agentic-ai-client = "agentic_ai_client.__main__:main"

[tool.setuptools.package-dir]
"" = "."

[tool.setuptools.packages.find]
where = ["."]
"""
    with open(fpath, "w") as f:
        f.write(fixed_content)

# Fix syntax error in other Agentic-AI-Pipeline
fpath = "external_repos/agents/Agentic-AI-Pipeline/clients/python/pyproject.toml"
if os.path.exists(fpath):
    with open(fpath, "r") as f:
        content = f.read()
    content = content.replace('\n= "."\n', '\n"" = "."\n')
    with open(fpath, "w") as f:
        f.write(content)

# Fix Kosmos deprecations
kosmos_files = [
    "external_repos/Kosmos/pyproject.toml",
    "apps/aiyou_stack/aiyou-fastapi-services/external_repos/Kosmos/pyproject.toml"
]
for fpath in kosmos_files:
    if os.path.exists(fpath):
        with open(fpath, "r") as f:
            content = f.read()
        
        # Replace [tool.ruff.per-file-ignores] with [tool.ruff.lint.per-file-ignores]
        content = content.replace("[tool.ruff.per-file-ignores]", "[tool.ruff.lint.per-file-ignores]")
        
        # We need to move select and ignore under [tool.ruff.lint]
        # Find the [tool.ruff] section and extract it
        if "[tool.ruff.lint]" not in content:
            # Simple approach: change select = [ to [tool.ruff.lint]\nselect = [
            # Wait, this will leave [tool.ruff] for line-length and target-version, which is correct.
            content = content.replace("select = [", "[tool.ruff.lint]\nselect = [")

        with open(fpath, "w") as f:
            f.write(content)

