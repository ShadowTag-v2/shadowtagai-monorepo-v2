#!/usr/bin/env python3
"""Cloud Code API Client: Wrapper for Antigravity Cloud Code API
Supports single account operation with scaling to 10 accounts.

Part of Colab Coop automation stack.
"""

import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import aiohttp
import google.generativeai as genai


@dataclass
class AccountStats:
    """Track usage per account."""

    account_id: int
    requests: int = 0
    tokens_used: int = 0
    errors: int = 0
    last_used: datetime | None = None
    rate_limited_until: datetime | None = None


class CloudCodeClient:
    """Cloud Code API client for Antigravity integration.

    Endpoints:
    - cloudcode-pa.googleapis.com (Cloud Code)
    - cloudaicompanion.googleapis.com (Gemini Code Assist)
    - generativelanguage.googleapis.com (Gemini API direct)

    Single account start → scale to 10.
    """

    # API endpoints
    CLOUD_CODE_URL = "https://cloudcode-pa.googleapis.com"
    CODE_ASSIST_URL = "https://cloudaicompanion.googleapis.com"
    GEMINI_API_URL = "https://generativelanguage.googleapis.com"

    def __init__(self, account_id: int = 1):
        """Initialize client with specific account.

        Args:
            account_id: Account number 1-10, maps to GEMINI_KEY_{n}

        """
        self.account_id = account_id
        self.api_key = self._load_api_key(account_id)
        self.stats = AccountStats(account_id=account_id)

        # Configure Gemini SDK
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")
        else:
            self.model = None

        print(f"///▞ CLOUDCODE :: Initialized account #{account_id}")

    def _load_api_key(self, account_id: int) -> str | None:
        """Load API key for account."""
        # Try account-specific key first
        key = os.getenv(f"GEMINI_KEY_{account_id}")
        if key:
            return key

        # Fall back to single key
        key = os.getenv("GEMINI_API_KEY")
        if key:
            return key

        # Fall back to Google API key
        return os.getenv("GOOGLE_API_KEY")

    async def code_assist(self, context: str, instruction: str) -> dict[str, Any]:
        """Get code assistance from Cloud Code API.

        Args:
            context: Current code context (file content, cursor position)
            instruction: What to do (complete, explain, refactor, etc.)

        Returns:
            dict with response, tokens, cost

        """
        if not self.model:
            return {"error": "No API key configured", "response": ""}

        prompt = f"""You are a code assistant integrated with Antigravity IDE.

Context:
```
{context}
```

Instruction: {instruction}

Provide your response in a format suitable for IDE integration."""

        try:
            self.stats.requests += 1
            self.stats.last_used = datetime.now()

            response = self.model.generate_content(prompt)

            return {
                "response": response.text,
                "account_id": self.account_id,
                "tokens": getattr(response, "usage_metadata", {}).get("total_token_count", 0),
                "success": True,
            }
        except Exception as e:
            self.stats.errors += 1
            return {
                "error": str(e),
                "response": "",
                "account_id": self.account_id,
                "success": False,
            }

    async def generate_code(self, prompt: str, language: str = "python") -> dict[str, Any]:
        """Generate code from natural language description.

        Args:
            prompt: Description of what to generate
            language: Target programming language

        Returns:
            dict with generated code

        """
        if not self.model:
            return {"error": "No API key configured", "code": ""}

        full_prompt = f"""Generate {language} code for the following:

{prompt}

Requirements:
- Production-ready code
- Include error handling
- Add type hints (if applicable)
- Include docstrings

Return ONLY the code, no explanations."""

        try:
            self.stats.requests += 1
            self.stats.last_used = datetime.now()

            response = self.model.generate_content(full_prompt)

            # Extract code from response
            code = response.text
            if "```" in code:
                # Extract from markdown code block
                lines = code.split("```")
                if len(lines) >= 2:
                    code_block = lines[1]
                    code_block = code_block.removeprefix(language)
                    code = code_block.strip()

            return {
                "code": code,
                "language": language,
                "account_id": self.account_id,
                "success": True,
            }
        except Exception as e:
            self.stats.errors += 1
            return {"error": str(e), "code": "", "success": False}

    async def execute_notebook_cell(
        self,
        code: str,
        notebook_context: str | None = None,
    ) -> dict[str, Any]:
        """Prepare code for Colab notebook execution.

        Args:
            code: Code to execute
            notebook_context: Previous cell outputs/variables

        Returns:
            dict with prepared code and execution hints

        """
        if not self.model:
            return {"error": "No API key configured"}

        prompt = f"""Analyze this code for Colab notebook execution:

```python
{code}
```

{"Previous context: " + notebook_context if notebook_context else ""}

Return JSON with:
{{
  "safe_to_execute": true/false,
  "dependencies": ["list", "of", "pip", "packages"],
  "estimated_runtime": "fast/medium/slow",
  "gpu_required": true/false,
  "modified_code": "code with any necessary fixes"
}}"""

        try:
            self.stats.requests += 1
            response = self.model.generate_content(prompt)

            # Parse JSON from response
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "safe_to_execute": True,
                "dependencies": [],
                "estimated_runtime": "unknown",
                "gpu_required": False,
                "modified_code": code,
            }
        except Exception as e:
            self.stats.errors += 1
            return {"error": str(e)}

    async def route_to_minions(self, prompt: str, tier: str = "task") -> dict[str, Any]:
        """Route request to minions server for distributed execution.

        Args:
            prompt: Task prompt
            tier: "task" (Flash) or "governance" (Pro)

        Returns:
            minions response

        """
        minions_url = os.getenv("minionS_URL", "http://localhost:8600")  # noqa: SIM112

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    f"{minions_url}/{tier}",
                    json={"prompt": prompt},
                    timeout=aiohttp.ClientTimeout(total=120),
                ) as response,
            ):
                result = await response.json()
                return {
                    "response": result.get("response", ""),
                    "source": "minions",
                    "tier": tier,
                    "success": True,
                }
        except Exception as e:
            return {"error": str(e), "source": "minions", "success": False}

    def get_stats(self) -> dict[str, Any]:
        """Return account usage statistics."""
        return {
            "account_id": self.stats.account_id,
            "requests": self.stats.requests,
            "errors": self.stats.errors,
            "error_rate": self.stats.errors / max(self.stats.requests, 1),
            "last_used": self.stats.last_used.isoformat() if self.stats.last_used else None,
            "api_key_set": bool(self.api_key),
        }


class CloudCodePool:
    """Pool of CloudCodeClients for multi-account operations.
    Start with 1, scale to 10.
    """

    def __init__(self, num_accounts: int = 1):
        """Initialize pool with specified number of accounts.

        Args:
            num_accounts: Number of accounts to use (1-10)

        """
        self.num_accounts = min(num_accounts, 10)
        self.clients: list[CloudCodeClient] = []
        self.current_index = 0

        for i in range(1, self.num_accounts + 1):
            client = CloudCodeClient(account_id=i)
            if client.api_key:
                self.clients.append(client)

        print(f"///▞ CLOUDCODE POOL :: Initialized {len(self.clients)} accounts")

    def get_next_client(self) -> CloudCodeClient | None:
        """Get next client in round-robin rotation."""
        if not self.clients:
            return None

        client = self.clients[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.clients)
        return client

    async def distribute_tasks(self, prompts: list[str]) -> list[dict[str, Any]]:
        """Distribute tasks across all accounts in parallel.

        Args:
            prompts: List of prompts to process

        Returns:
            List of results

        """
        tasks = []
        for i, prompt in enumerate(prompts):
            client = self.clients[i % len(self.clients)]
            tasks.append(client.code_assist("", prompt))

        return await asyncio.gather(*tasks)

    def get_pool_stats(self) -> dict[str, Any]:
        """Get aggregate statistics for all accounts."""
        total_requests = sum(c.stats.requests for c in self.clients)
        total_errors = sum(c.stats.errors for c in self.clients)

        return {
            "num_accounts": len(self.clients),
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": total_errors / max(total_requests, 1),
            "per_account": [c.get_stats() for c in self.clients],
        }


# Standalone test
if __name__ == "__main__":

    async def main():
        # Single account test
        client = CloudCodeClient(account_id=1)

        # Test code assist
        result = await client.code_assist(
            context="def hello():\n    pass",
            instruction="Complete this function to print Hello World",
        )
        print("Code Assist:", result)

        # Test code generation
        result = await client.generate_code(
            "Create a function that calculates fibonacci numbers",
            language="python",
        )
        print("Generated Code:", result)

        # Test minions routing
        result = await client.route_to_minions("What is 2+2?")
        print("minions:", result)

        print("\nStats:", client.get_stats())

    asyncio.run(main())
