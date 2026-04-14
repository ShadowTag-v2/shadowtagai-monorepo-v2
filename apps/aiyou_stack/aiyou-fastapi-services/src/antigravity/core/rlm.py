"""Recursive Language Model (RLM) - Core Logic
Ported from legacy minion v8.

Purpose: Handle unbounded context by treating it as a variable in a REPL environment.
Storage: Uses disk-based storage to avoid VS Code extension state warnings.
"""

import json
from pathlib import Path
from typing import Any


class RecursiveLanguageModel:
    """RLM implementation for unbounded context handling.
    """

    def __init__(
        self,
        context_variable: str = "context",
        storage_path: str = ".gemini/antigravity/rlm_storage",
    ):
        self.context_var = context_variable
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.repl_state: dict[str, Any] = {}
        self.recursion_depth = 0
        self.max_depth = 5

    def _save_context(self, context_id: str, context: Any):
        """Save large context to disk"""
        file_path = self.storage_path / f"{context_id}.json"
        try:
            with open(file_path, "w") as f:
                # Handle non-serializable objects by stringifying if needed
                if isinstance(context, (str, int, float, bool, list, dict)):
                    json.dump(context, f)
                else:
                    f.write(str(context))
        except Exception as e:
            print(f"Warning: RLM context save failed: {e}")

    async def query(
        self, prompt: str, context: Any, llm_call_fn: callable, context_id: str | None = None,
    ) -> str:
        """RLM query with REPL environment.
        """
        # Save context to disk if ID provided, to avoid memory pressure
        if context_id:
            self._save_context(context_id, context)

        # Load context into REPL environment (in-memory for execution)
        self.repl_state[self.context_var] = context

        # Root LM gets query + access to REPL environment
        root_prompt = f"""
        You are a recursive language model with access to a Python REPL environment.

        Context is stored in variable: {self.context_var}

        You can:
        1. Inspect context subsets: context[:100], context[key], etc.
        2. Use regex to search: re.search(pattern, context)
        3. Spawn sub-queries: await rlm_query(sub_prompt, sub_context)
        4. Build final answer and return: FINAL(answer) or FINAL_VAR(var_name)

        Query: {prompt}
        """

        # Execute recursive reasoning
        result = await llm_call_fn(root_prompt, repl_env=self.repl_state)

        return result
