import argparse
import json
import logging
import os
import subprocess
import time

# Google Cloud Pub/Sub
try:
    from google.cloud import pubsub_v1
except ImportError:
    print("⚠️  'google-cloud-pubsub' not found. Installing...")
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-cloud-pubsub"])
    from google.cloud import pubsub_v1

# CONFIG
PROJECT_ID = os.environ.get("PROJECT_ID", "shadowtag-omega-v2")
TOPIC_ID = "trinity-input-stream"  # Short name
TOPIC_PATH = f"projects/{PROJECT_ID}/topics/{TOPIC_ID}"


def get_all_remote_branches() -> list[str]:
    """Lists all remote branches."""
    try:
        result = subprocess.check_output(["git", "branch", "-r"], text=True)
        branches = [b.strip() for b in result.splitlines() if "->" not in b]
        return branches
    except Exception as e:
        logging.exception(f"Failed to list branches: {e}")
        return []


def list_files_in_branch(branch: str, extensions=None) -> list[str]:
    """Lists relevant doc files in a specific branch."""
    if extensions is None:
        extensions = [".md", ".txt", ".rst"]
    files = []
    try:
        # git ls-tree -r --name-only BRANCH
        result = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", branch], text=True)
        all_files = result.splitlines()
        for f in all_files:
            if any(f.endswith(ext) for ext in extensions):
                files.append(f)
    except Exception:
        pass
    return files


def read_file_from_branch(branch: str, filepath: str) -> str:
    """Reads content of a file from a branch without checking it out."""
    try:
        # git show BRANCH:FILEPATH
        return subprocess.check_output(["git", "show", f"{branch}:{filepath}"], text=True)
    except Exception:
        return ""


def setup_logging():
    log_format = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
    logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%dT%H:%M:%S%z")


def main():
    setup_logging()
    logger = logging.getLogger("HarvestDocs")

    parser = argparse.ArgumentParser(
        description="Harvest documentation from Git branches to Pub/Sub.",
    )
    parser.parse_args()

    # Initialize Pub/Sub Publisher
    publisher = pubsub_v1.PublisherClient()
    logger.info(f"🔌 Target Pub/Sub Topic: {TOPIC_PATH}")

    branches = get_all_remote_branches()

    # CLOUD HYDRATION (Trojan Horse v2)
    if not branches and not os.path.exists(".git"):
        logger.info("🌤️  Detected Cloud Environment (Empty Repo). Hydrating...")
        try:
            repo_url = os.environ.get(
                "REPO_URL", "https://github.com/ShadowTag-v2/shadowtag_v4-fastapi-services.git",
            )
            subprocess.check_call(["git", "clone", repo_url, "."])
            subprocess.check_call(["git", "fetch", "--all"])
            branches = get_all_remote_branches()
        except Exception as e:
            logger.error(f"❌ Failed to hydrate repo: {e}")

    logger.info(f"🌍 Found {len(branches)} remote branches.")

    total_docs = 0
    futures = []

    for branch in branches:
        logger.info(f"🔍 Scanning {branch}...")
        files = list_files_in_branch(branch)

        for filepath in files:
            content = read_file_from_branch(branch, filepath)
            if not content:
                continue

            payload = {
                "event_type": "DOCUMENT_INGESTION",
                "source": "git_harvest",
                "branch": branch,
                "filepath": filepath,
                "content_snippet": content[:100],
                "data": {"full_text": content, "format": filepath.split(".")[-1]},
                "timestamp": time.time(),
            }

            # Publish to Pub/Sub
            data_str = json.dumps(payload)
            data_bytes = data_str.encode("utf-8")

            try:
                future = publisher.publish(TOPIC_PATH, data_bytes)
                futures.append(
                    (future, filepath),
                )  # Keep track of which future belongs to which file
                total_docs += 1
            except Exception as e:
                logger.error(f"❌ Failed to publish {filepath}: {e}")

    # Wait for all publishes to complete and log IDs
    if futures:
        logger.info(f"⏳ Waiting for {len(futures)} messages to be acknowledged...")
        for future, fname in futures:
            try:
                message_id = future.result()  # Blocks until published
                logger.info(f"✅ Published {fname} | Message ID: {message_id}")
            except Exception as e:
                logger.error(f"❌ Failed to publish {fname}: {e}")

    logger.info(f"✅ Harvest Complete. Ingested {total_docs} documents into Pub/Sub.")


if __name__ == "__main__":
    main()
