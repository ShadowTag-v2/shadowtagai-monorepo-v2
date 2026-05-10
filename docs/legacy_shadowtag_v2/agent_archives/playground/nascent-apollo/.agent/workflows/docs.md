# Workflow: Auto-Documentation

**Trigger:** "Document this repo", "Write the readme", "Setup contributing guidelines".

**Goal:** Create or update `README.md` and `CONTRIBUTING.md` accurately.

## Step 1: Deep Audit
1.  **Analyze Dependencies:** Read `package.json`, `go.mod`, etc. to identify tech stack.
2.  **Map Structure:** Tree scan `src/` to understand architecture.
3.  **Identify Scripts:** Check `scripts` in package files or `Makefile` for build/test/deploy commands.

## Step 2: Generate README.md
Create/Overwrite `README.md`:
1.  **Title & Badge:** Project name + status.
2.  **One-Liner:** Concise description.
3.  **Tech Stack:** List core technologies.
4.  **Prerequisites:** Global installs (Node, Python, Docker).
5.  **Getting Started:** Commands to Clone, Install, Run.
6.  **Project Structure:** High-level folder explanation.

## Step 3: Generate CONTRIBUTING.md
Create/Overwrite `CONTRIBUTING.md`:
1.  **Branching Strategy:** Recommend "Feature Branch Workflow".
2.  **Pull Request Process:** "Tests must pass", "Update docs".
3.  **Code Style:** Reference `.agent/rules` and linter commands.

## Step 4: Verification
1.  **Link Check:** Ensure relative links work.
2.  **Command Validation:** Verify "Getting Started" commands match identified scripts.

## Step 5: Final Output
-   Present changes as a plan/diff.
-   Offer to commit to `docs/update` branch.

// turbo
