import json
import os
import subprocess
import time
from pathlib import Path

# Configuration
TARGET_DIR = Path(os.path.expanduser("~/antigravity-flattened"))
INDEX_FILE = TARGET_DIR / "index.json"
DELAY_SECONDS = 15

# List of repos found in codebase
REPOS_TO_FORK = [
    # --- Strategy Checkpoint: Ironwood & Genkit (Added 2025-12-13) ---
    "https://github.com/google/flax",  # JAX Neural Networks (Linen API)
    "https://github.com/google-deepmind/gemma",  # TPU Reference Implementation
    "https://github.com/google/jax",  # Core JAX/XLA
    "https://github.com/firebase/genkit",  # Genkit Core Source
    "https://github.com/google/generative-ai-python",  # Official Gemini SDK
    "https://github.com/lucidrains/titans-pytorch",  # Titans Memory Blueprint
    "https://github.com/model-context-protocol/python-sdk",  # MCP Reference Python SDK
    "https://github.com/google/osv-scanner",  # Governance/Security Scanner
    # --- End Strategy Checkpoint ---
    "https://github.com/deepseek-ai/LPLB",
    "https://github.com/opentimestamps/opentimestamps-client",
    "https://github.com/donnemartin/system-design-primer",
    "https://github.com/anthropics/anthropic-sdk-typescript",
    "https://github.com/openai/openai-node",
    "https://github.com/shadowtagai/mock-universal-copilot",
    "https://github.com/diet103/claude-code-infrastructure-showcase",
    "https://github.com/generalized-intelligence/GAAS",
    # --- Strategy Checkpoint: Synthesis (Added 2025-12-13) ---
    "https://github.com/isaacphi/mcp-gdrive",  # Primary Drive Implementation
    "https://github.com/felores/gdrive-mcp-server",  # Fallback Drive Implementation
    # --- Strategy Checkpoint: GCP Omni (Added 2025-12-13) ---
    "https://github.com/googleapis/google-cloud-python",  # The "All APIs" Monorepo
    "https://github.com/generalized-intelligence/Tegu",
    "https://github.com/huggingface/hf-mcp-server",
    "https://github.com/jlowin/fastmcp",
    "https://github.com/mondaycom/mcp",
    "https://github.com/Arize-ai/arize-tracing-assistant",
    "https://github.com/TransmitSecurity/transmit-security-journey-builder",
    "https://github.com/chronosphereio/chronosphere-mcp",
    "https://github.com/google-gemini/gemini-cli",
    "https://github.com/ehanc69/erik-hancock-llm-memory",
    "https://github.com/trunk-io/plugins",
    "https://github.com/gemini-cli-extensions/alloydb",
    "https://github.com/gemini-cli-extensions/alloydb-observability",
    "https://github.com/gemini-cli-extensions/bigquery-conversational-analytics",
    "https://github.com/gemini-cli-extensions/bigquery-data-analytics",
    "https://github.com/gemini-cli-extensions/cloud-sql-mysql",
    "https://github.com/gemini-cli-extensions/cloud-sql-mysql-observability",
    "https://github.com/gemini-cli-extensions/cloud-sql-postgresql",
    "https://github.com/gemini-cli-extensions/cloud-sql-postgresql-observability",
    "https://github.com/gemini-cli-extensions/cloud-sql-sqlserver",
    "https://github.com/gemini-cli-extensions/cloud-sql-sqlserver-observability",
    "https://github.com/gemini-cli-extensions/datacommons",
    "https://github.com/gemini-cli-extensions/dataplex",
    "https://github.com/gemini-cli-extensions/firestore-native",
    "https://github.com/gemini-cli-extensions/flutter",
    "https://github.com/gemini-cli-extensions/jules",
    "https://github.com/gemini-cli-extensions/looker",
    "https://github.com/gemini-cli-extensions/mcp-toolbox",
    "https://github.com/gemini-cli-extensions/mysql",
    "https://github.com/gemini-cli-extensions/nanobanana",
    "https://github.com/gemini-cli-extensions/postgres",
    "https://github.com/gemini-cli-extensions/spanner",
    "https://github.com/gemini-cli-extensions/sql-server",
]


def load_index():
    if not INDEX_FILE.exists():
        print(f"Index file not found at {INDEX_FILE}. Assuming empty index.")
        return {}
    try:
        with open(INDEX_FILE) as f:
            data = json.load(f)
            return data.get("repos", {})
    except Exception as e:
        print(f"Error reading index file: {e}")
        return {}


def get_repo_name(url):
    return url.split("/")[-1].replace(".git", "")


def fork_repo(url):
    repo_name = get_repo_name(url)
    target_path = TARGET_DIR / repo_name

    if target_path.exists():
        print(f"Skipping {repo_name}: Directory already exists.")
        return

    print(f"Forking {repo_name} from {url}...")
    try:
        # Try gh repo fork first
        cmd = ["gh", "repo", "fork", url, "--clone", "--remote"]
        subprocess.run(cmd, cwd=TARGET_DIR, check=True)
        print(f"Successfully forked {repo_name}")
    except subprocess.CalledProcessError:
        print(f"gh fork failed for {repo_name}, falling back to git clone...")
        try:
            cmd = ["git", "clone", url]
            subprocess.run(cmd, cwd=TARGET_DIR, check=True)
            print(f"Successfully cloned {repo_name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone {repo_name}: {e}")
            return

    print(f"Waiting {DELAY_SECONDS} seconds to respect rate limits...")
    time.sleep(DELAY_SECONDS)


def main():
    if not TARGET_DIR.exists():
        print(f"Target directory {TARGET_DIR} does not exist. Creating it.")
        TARGET_DIR.mkdir(parents=True, exist_ok=True)

    existing_repos = load_index()
    print(f"Found {len(existing_repos)} repos in index.")

    for url in REPOS_TO_FORK:
        repo_name = get_repo_name(url)

        # Check if in index
        if repo_name in existing_repos:
            print(f"Skipping {repo_name}: Found in index.")
            continue

        # Check if directory exists (double check)
        if (TARGET_DIR / repo_name).exists():
            print(f"Skipping {repo_name}: Directory exists.")
            continue

        fork_repo(url)

    print("Done processing repos.")


if __name__ == "__main__":
    main()
