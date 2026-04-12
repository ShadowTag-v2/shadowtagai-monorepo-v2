"""
Pnkln Context Engine
====================

Implements the "Sessions & Memory" pattern from the Context Engineering whitepaper.
Separates Short-Term (Session) from Long-Term (Memory) with an ETL pipeline.

Integrates:
-   Session Manager (RAM / Hot Path)
-   Memory Layer (Disk / Cold Path) with Judge #6 Validation
-   Gemini v2.0 for Inference (via src.pnkln.gemini_integration)
"""

import asyncio
import datetime
import json
import logging

from pnkln.core.judge_six_pipeline import get_judge

from src.pnkln.gemini_integration import GeminiService

logger = logging.getLogger(__name__)


# --- 1. Session Layer (Short-Term Working Memory) ---
class Session:
    """
    The 'RAM'. Manages the sliding window of the immediate conversation.
    """

    def __init__(self, user_id: str, max_turns: int = 5):
        self.user_id = user_id
        self.history: list[dict[str, str]] = []
        self.max_turns = max_turns

    def add_message(self, role: str, content: str):
        self.history.append(
            {"role": role, "content": content, "timestamp": datetime.datetime.now().isoformat()}
        )
        self._prune()

    def _prune(self):
        """
        Implements 'Compaction'. Keeps the session within context limits.
        """
        if len(self.history) > self.max_turns * 2:
            # Keep the last N turns (*2 because user+ai = 1 turn)
            self.history = self.history[-self.max_turns * 2 :]

    def get_history_text(self) -> str:
        return "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in self.history])


# --- 2. Memory Layer (Long-Term Storage) ---
class MemoryLayer:
    """
    The 'Hard Drive'. Implements the ETL pattern.
    Stores facts that survive beyond the immediate session.
    Protected by Judge #6 validation.
    """

    def __init__(self):
        self.facts: list[str] = []
        # In a real system, we might use a Vector DB client here.
        # For now, in-memory list serves as the "Cold Path" storage for this instance.

        self.llm = GeminiService()
        self.judge = get_judge()

    async def retrieve(self, query: str) -> list[str]:
        """
        Retrieves relevant memories.
        In production, this is a Vector DB (Pinecone/Chroma) search.
        """
        # Simple keyword matching for demo
        keywords = query.lower().split()
        relevant_facts = [fact for fact in self.facts if any(k in fact.lower() for k in keywords)]
        return relevant_facts

    async def extract_and_save(self, user_input: str):
        """
        The ETL Pipeline: 'Reads' input and extracts permanent facts.
        This runs asynchronously to avoid latency on the main chat path.
        """
        extraction_prompt = f"""
        Analyze the following user input. Extract permanent facts,
        preferences, or biographical info. Return a JSON list of strings.
        If no facts are present, return [].

        Input: "{user_input}"
        """

        try:
            response = await self.llm.generate_content(extraction_prompt)
            # Basic cleanup if the model gives markdown code blocks
            clean_response = response.replace("```json", "").replace("```", "").strip()

            # If the mock returns something not JSON-like (e.g. strict text), handle it
            if clean_response.startswith("[") and clean_response.endswith("]"):
                new_facts = json.loads(clean_response)
            else:
                # Fallback/Mock handling if GeminiService returns plain text
                # or if the prompt wasn't followed perfectly.
                # For the purpose of this implementation, we log and skip.
                logger.debug(f"[Memory ETL] Non-JSON response: {clean_response}")
                return

            if new_facts:
                valid_facts = []
                for fact in new_facts:
                    # Judge #6 Validation Logic
                    if self.judge.validate_fact(fact):
                        valid_facts.append(fact)
                    else:
                        logger.info(f"[Memory ETL] Judge #6 REJECTED fact: {fact}")

                if valid_facts:
                    logger.info(f"[Memory ETL] Storing new facts: {valid_facts}")
                    self.facts.extend(valid_facts)

        except Exception as e:
            logger.error(f"[Memory ETL] Error during extraction: {e}")


# --- 3. The Context Engine (Orchestrator) ---
class ContextEngine:
    def __init__(self):
        self.memory_layer = MemoryLayer()
        self.sessions: dict[str, Session] = {}
        self.llm = GeminiService()
        self.system_prompt = "You are a helpful AI assistant for Pnkln Corp."

    def get_session(self, user_id: str) -> Session:
        if user_id not in self.sessions:
            self.sessions[user_id] = Session(user_id)
        return self.sessions[user_id]

    async def chat(self, user_id: str, user_input: str) -> str:
        session = self.get_session(user_id)

        # A. ETL Step (Write Path) - Fire and Forget (using ensure_future or just await if we accept slight latency)
        # The user requested: "runs asynchronously in a real system to avoid latency".
        # In Python async, we can spawn a task.
        asyncio.create_task(self.memory_layer.extract_and_save(user_input))

        # B. Context Assembly (Read Path)
        # 1. Retrieve Long-Term Memories (Facts)
        relevant_memories = await self.memory_layer.retrieve(user_input)

        # 2. Format Memory Block
        memory_block = ""
        if relevant_memories:
            memory_block = "LONG-TERM MEMORY:\n" + "\n".join(f"- {m}" for m in relevant_memories)

        # 3. Get Short-Term Session History
        history_block = session.get_history_text()

        # 4. Construct Final Prompt (The "Context Engineering" Core)
        full_prompt = f"""
        {self.system_prompt}

        {memory_block}

        CURRENT SESSION:
        {history_block}
        USER: {user_input}
        AI:
        """

        # C. Generation
        # logger.info(f"--- PROMPT SENT TO LLM ---\n{full_prompt}\n--------------------------")
        response = await self.llm.generate_content(full_prompt)

        # D. Update Session
        session.add_message("user", user_input)
        session.add_message("ai", response)

        return response
