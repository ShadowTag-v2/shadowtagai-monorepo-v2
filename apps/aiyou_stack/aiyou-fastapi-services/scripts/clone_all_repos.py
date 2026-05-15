#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests


def get_repos_for_entity(entity_name: str, entity_type: str, token: str) -> list[dict]:
    """Fetches a list of repositories for a user or organization from the GitHub API.

    :param entity_name: The username or organization name.
    :param entity_type: The type of entity, either 'users' or 'orgs'.
    :param token: The GitHub PAT.
    :return: A list of repository dictionaries.
    """
    if entity_type not in ["users", "orgs"]:
        raise ValueError("entity_type must be 'users' or 'orgs'")

    repos = []
    page = 1
    per_page = 100  # Max allowed by GitHub API

    print(f"Fetching repository list for {entity_type[:-1]} '{entity_name}' from GitHub API...")

    while True:
        api_url = f"https://api.github.com/{entity_type}/{entity_name}/repos?page={page}&per_page={per_page}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        try:
            response = requests.get(api_url, headers=headers)
            # Handle rate limiting
            if response.status_code == 403 and "rate limit" in response.text.lower():
                print(
                    "GitHub API rate limit exceeded. Please try again later or use an authenticated token.",
                    file=sys.stderr,
                )
                break

            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

            data = response.json()
            if not data:
                break  # No more repos

            repos.extend(data)
            page += 1
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repositories for {entity_name}: {e}", file=sys.stderr)
            break

    print(f"Found {len(repos)} repositories for {entity_name}.")
    return repos


def clone_or_update_repo(repo_info: dict, target_base: Path):
    """Clones a repository if it doesn't exist, or pulls updates if it does."""
    repo_name = repo_info["name"]
    clone_url = repo_info["clone_url"]
    owner = repo_info["owner"]["login"]

    # Store in owner subdirectory to avoid name collisions
    repo_path = target_base / owner / repo_name
    repo_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if repo_path.exists():
            print(f"[{owner}/{repo_name}] Repository exists. Fetching updates...")
            subprocess.run(
                ["git", "pull", "--rebase"],
                cwd=repo_path,
                check=True,
                capture_output=True,
                text=True,
            )
            return f"Updated: {owner}/{repo_name}"
        print(f"[{owner}/{repo_name}] Cloning from {clone_url}...")
        subprocess.run(
            ["git", "clone", clone_url, str(repo_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        return f"Cloned: {owner}/{repo_name}"
    except subprocess.CalledProcessError as e:
        error_message = f"[{owner}/{repo_name}] Failed.\n  - Command: {' '.join(e.cmd)}\n  - Stderr: {e.stderr.strip()}"
        print(error_message, file=sys.stderr)
        return f"Failed: {owner}/{repo_name}"


def main():
    """Parses arguments and orchestrates fetching and cloning/updating repositories."""
    parser = argparse.ArgumentParser(
        description="Clone or update all public repositories for specified GitHub users and/or organizations.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--users", nargs="+", metavar="USER", help="One or more GitHub usernames.")
    parser.add_argument(
        "--orgs",
        nargs="+",
        metavar="ORG",
        help="One or more GitHub organization names.",
    )
    parser.add_argument(
        "--dest-dir",
        type=Path,
        default=Path("external_repos"),
        help="The local base directory to clone repositories into.",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("GITHUB_TOKEN"),
        help="GitHub Personal Access Token. Defaults to GITHUB_TOKEN environment variable.",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=10,
        help="Number of parallel workers for cloning/pulling.",
    )

    args = parser.parse_args()

    if not args.token:
        parser.error(
            "GitHub token not found. Please set the GITHUB_TOKEN environment variable or use the --token argument.",
        )

    if not args.users and not args.orgs:
        parser.error("You must specify at least one entity with --users and/or --orgs.")

    dest_dir = args.dest_dir
    print(f"All repositories will be cloned/updated in: {dest_dir.resolve()}\n")

    all_repos = []
    if args.users:
        for user in args.users:
            all_repos.extend(get_repos_for_entity(user, "users", args.token))
    if args.orgs:
        for org in args.orgs:
            all_repos.extend(get_repos_for_entity(org, "orgs", args.token))

    if not all_repos:
        print("No repositories found for the specified users/orgs.")
        return

    print(
        f"\nStarting processing of {len(all_repos)} total repositories with {args.workers} threads...",
    )

    # Use a ThreadPoolExecutor to run tasks in parallel
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        # Create a future for each repository task
        future_to_repo = {
            executor.submit(clone_or_update_repo, repo, dest_dir): repo["name"]
            for repo in all_repos
        }

        success_count = 0
        failure_count = 0

        # Process results as they complete
        for future in as_completed(future_to_repo):
            try:
                result = future.result()
                if result.startswith("Failed"):
                    failure_count += 1
                else:
                    success_count += 1
            except Exception as exc:
                print(f"A worker generated an exception: {exc}", file=sys.stderr)
                failure_count += 1

    print("\n--- Summary ---")
    print(f"Successfully processed: {success_count}")
    print(f"Failed: {failure_count}")
    print("All tasks complete.")


if __name__ == "__main__":
    main()
