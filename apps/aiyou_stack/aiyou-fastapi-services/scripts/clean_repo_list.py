import re


def clean_repos(input_file, output_file):
    with open(input_file) as f:
        lines = f.readlines()

    repos = set()
    # Regex to capture owner/repo, ignoring trailing junk
    # Matches github.com/owner/repo where owner and repo are valid chars
    # Stops at whitespace, quotes, parens, etc.
    pattern = re.compile(r"github\.com/([a-zA-Z0-9._-]+)/([a-zA-Z0-9._-]+)")

    for line in lines:
        match = pattern.search(line)
        if match:
            owner, repo = match.groups()
            # Filter out obvious variables or placeholders
            if "$" in owner or "$" in repo:
                continue
            if owner in ["...", "user", "<user>"]:
                continue

            # Clean up repo name (remove .git suffix if present)
            repo = repo.removesuffix(".git")

            full_name = f"{owner}/{repo}"
            repos.add(full_name)

    # Sort and write
    sorted_repos = sorted(list(repos))
    with open(output_file, "w") as f:
        for repo in sorted_repos:
            f.write(f"github.com/{repo}\n")

    print(f"Cleaned {len(lines)} lines down to {len(sorted_repos)} unique repos.")


if __name__ == "__main__":
    clean_repos("config/antigravity_repos.json", "config/antigravity_repos_clean.json")
