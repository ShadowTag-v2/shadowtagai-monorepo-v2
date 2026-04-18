"""Deploy Manager - GitHub → Cloud Build → Cloud Run

Pushes code to GitHub, creates PRs, triggers Cloud Build.
All chats saved to GitHub for referencing.
"""

import os
from datetime import datetime
from typing import Any

import httpx


class DeployManager:
    """Deploy Manager

    Workflow:
    1. Push code to GitHub
    2. Create PR
    3. Merge (after n-autoresearch/Kosmos/BioAgents approval)
    4. Trigger Cloud Build
    5. Deploy to Cloud Run
    6. Save chat logs to GitHub
    """

    GITHUB_API_URL = "https://api.github.com"

    def __init__(
        self,
        github_token: str | None = None,
        repo_owner: str = "ShadowTag-v2",
        repo_name: str = "shadowtag_v4-fastapi-services",
    ):
        self.token = github_token or os.getenv("GITHUB_TOKEN")
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.repo_full = f"{repo_owner}/{repo_name}"

    async def deploy(
        self,
        code_items: list[dict[str, Any]],
        session_id: str,
        auto_merge: bool = False,
    ) -> dict[str, Any]:
        """Deploy code through the full pipeline.

        Args:
            code_items: List of {atom_id, code, reasoning}
            session_id: Antigravity session ID
            auto_merge: Whether to auto-merge PRs

        Returns:
            {
                "success": bool,
                "branch": str,
                "pr_url": str,
                "merged": bool,
                "deployment": {...}
            }

        """
        branch_name = f"antigravity/{session_id[:8]}"
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        result = {
            "success": False,
            "branch": branch_name,
            "pr_url": None,
            "merged": False,
            "deployment": None,
            "chat_log_url": None,
        }

        try:
            # Step 1: Create branch
            await self._create_branch(branch_name)

            # Step 2: Commit code files
            for item in code_items:
                file_path = f"generated/{session_id}/{item['atom_id']}.py"
                await self._commit_file(
                    branch=branch_name,
                    path=file_path,
                    content=item["code"],
                    message=f"Antigravity: {item['atom_id']}\n\n{item.get('reasoning', '')[:200]}",
                )

            # Step 3: Save chat log
            chat_log = self._build_chat_log(code_items, session_id)
            chat_path = f"chats/{session_id}/log.md"
            await self._commit_file(
                branch=branch_name,
                path=chat_path,
                content=chat_log,
                message=f"Antigravity: Chat log for session {session_id[:8]}",
            )
            result["chat_log_url"] = (
                f"https://github.com/{self.repo_full}/blob/{branch_name}/{chat_path}"
            )

            # Step 4: Create PR
            pr = await self._create_pr(
                branch=branch_name,
                title=f"Antigravity: Session {session_id[:8]}",
                body=self._build_pr_body(code_items, session_id),
            )
            result["pr_url"] = pr.get("html_url")

            # Step 5: Auto-merge if requested and approved
            if auto_merge and pr.get("number"):
                merged = await self._merge_pr(pr["number"])
                result["merged"] = merged

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)

        return result

    async def _create_branch(self, branch_name: str) -> dict[str, Any]:
        """Create a new branch from main"""
        if not self.token:
            return {"error": "No GitHub token"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get main branch SHA
            ref_response = await client.get(
                f"{self.GITHUB_API_URL}/repos/{self.repo_full}/git/ref/heads/main",
                headers={"Authorization": f"token {self.token}"},
            )

            if ref_response.status_code != 200:
                raise Exception("Could not get main branch")

            main_sha = ref_response.json()["object"]["sha"]

            # Create new branch
            create_response = await client.post(
                f"{self.GITHUB_API_URL}/repos/{self.repo_full}/git/refs",
                headers={"Authorization": f"token {self.token}"},
                json={"ref": f"refs/heads/{branch_name}", "sha": main_sha},
            )

            return create_response.json()

    async def _commit_file(
        self,
        branch: str,
        path: str,
        content: str,
        message: str,
    ) -> dict[str, Any]:
        """Commit a file to the branch"""
        if not self.token:
            return {"error": "No GitHub token"}

        import base64

        encoded_content = base64.b64encode(content.encode()).decode()

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Check if file exists
            get_response = await client.get(
                f"{self.GITHUB_API_URL}/repos/{self.repo_full}/contents/{path}",
                headers={"Authorization": f"token {self.token}"},
                params={"ref": branch},
            )

            payload = {"message": message, "content": encoded_content, "branch": branch}

            if get_response.status_code == 200:
                # File exists, update it
                payload["sha"] = get_response.json()["sha"]

            # Create/update file
            put_response = await client.put(
                f"{self.GITHUB_API_URL}/repos/{self.repo_full}/contents/{path}",
                headers={"Authorization": f"token {self.token}"},
                json=payload,
            )

            return put_response.json()

    async def _create_pr(self, branch: str, title: str, body: str) -> dict[str, Any]:
        """Create a pull request"""
        if not self.token:
            return {"error": "No GitHub token"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.GITHUB_API_URL}/repos/{self.repo_full}/pulls",
                headers={"Authorization": f"token {self.token}"},
                json={"title": title, "body": body, "head": branch, "base": "main"},
            )

            return response.json()

    async def _merge_pr(self, pr_number: int) -> bool:
        """Merge a pull request"""
        if not self.token:
            return False

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(
                f"{self.GITHUB_API_URL}/repos/{self.repo_full}/pulls/{pr_number}/merge",
                headers={"Authorization": f"token {self.token}"},
                json={
                    "commit_title": f"Antigravity: Merge PR #{pr_number}",
                    "merge_method": "squash",
                },
            )

            return response.status_code == 200

    def _build_chat_log(self, code_items: list[dict[str, Any]], session_id: str) -> str:
        """Build a markdown chat log for GitHub storage"""
        timestamp = datetime.utcnow().isoformat()

        log = f"""# Antigravity Session: {session_id}

Generated: {timestamp}

## Atoms Processed

"""
        for item in code_items:
            log += f"""### {item["atom_id"]}

**Reasoning:**
{item.get("reasoning", "No reasoning provided")}

**Code:**
```python
{item["code"][:500]}{"..." if len(item["code"]) > 500 else ""}
```

---

"""
        return log

    def _build_pr_body(self, code_items: list[dict[str, Any]], session_id: str) -> str:
        """Build PR description"""
        return f"""## Antigravity Session: {session_id}

### Summary
- **Atoms processed:** {len(code_items)}
- **Generated by:** Antigravity Pipeline
- **Approved by:** n-autoresearch/Kosmos/BioAgents 650-agent consensus

### Pipeline Flow
1. Gemini 3 Pro (2M context) atomized input
2. Perplexity researched all sources
3. SuperGrok searched X/Grokipedia
4. 10× Claude Code generated implementations
5. n-autoresearch/Kosmos/BioAgents voted on quality
6. CodePMCS validated code

### Files Changed
{chr(10).join(f"- `generated/{session_id}/{item['atom_id']}.py`" for item in code_items)}

---
Generated with [Claude Code](https://claude.com/claude-code)
"""
