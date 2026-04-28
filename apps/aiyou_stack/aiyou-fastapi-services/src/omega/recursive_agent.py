# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Mocking an LLM client for demonstration.
# Replace this with standard OpenAI/Gemini/Anthropic API calls.
class LLMClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_response(self, prompt: str, context: str) -> str:
        """In a real scenario, this sends the prompt + context to GPT-4o or Gemini 1.5.
        Returns a structured command string.
        """
        # REAL IMPLEMENTATION:
        # response = client.chat.completions.create(...)
        # return response.choices[0].message.content

        # DUMMY LOGIC FOR DEMO:
        if "Table of Contents" in context:
            return "JUMP 15000"  # Simulating finding the right chapter
        if "Specific Answer" in context:
            return "ANSWER The solution is 42."
        return "READ_NEXT"


class TextEnvironment:
    """Represents the 'World' the model lives in.
    This allows the model to access a massive file without loading it all into memory.
    """

    def __init__(self, file_path: str, chunk_size: int = 1000):
        with open(file_path, encoding="utf-8") as f:
            self.full_text = f.read()
        self.total_length = len(self.full_text)
        self.chunk_size = chunk_size

    def read(self, start_index: int) -> str:
        """Reads a specific chunk from the environment."""
        end_index = min(start_index + self.chunk_size, self.total_length)
        return self.full_text[start_index:end_index]


class RecursiveAgent:
    def __init__(self, client: LLMClient, env: TextEnvironment):
        self.client = client
        self.env = env
        self.max_depth = 3  # Prevent infinite recursion loops

    def construct_system_prompt(self, query: str, current_pos: int, total_len: int) -> str:
        return f"""
        GOAL: Answer the user's query: "{query}"

        ENVIRONMENT STATUS:
        - Total Document Length: {total_len} characters.
        - Your Current Position: {current_pos}.

        INSTRUCTIONS:
        You are an intelligent reader. You are NOT retrieving vectors. You are navigating a book.
        Based on the text chunk you see below, decide your next move.

        COMMANDS YOU CAN USE:
        1. READ_NEXT: Read the immediate next chunk.
        2. JUMP <integer>: Jump to a specific character index (e.g., if you see a Chapter Index).
        3. RECURSE <query>: Spawn a sub-agent to investigate a specific sub-topic found in the text.
        4. ANSWER <text>: You found the answer. Output it and end.

        OUTPUT FORMAT:
        Just the command. Example: "JUMP 5000"
        """

    def solve(self, query: str, start_index: int = 0, depth: int = 0) -> str:
        """The recursive loop. The agent reads, thinks, and moves."""
        current_pos = start_index
        steps_taken = 0
        max_steps = 10  # Safety limit

        print(
            f"{'  ' * depth}➤ [Depth {depth}] Agent started at index {current_pos} for query: '{query}'",
        )

        while steps_taken < max_steps:
            # 1. Observe the environment (Read)
            chunk = self.env.read(current_pos)

            # 2. Construct the prompt
            prompt = self.construct_system_prompt(query, current_pos, self.env.total_length)

            # 3. Act (Call LLM)
            # In real code, print(chunk) would go into the context
            decision = self.client.get_response(prompt, context=chunk)
            print(f"{'  ' * depth}  Action: {decision}")

            # 4. Parse Decision
            if decision.startswith("ANSWER"):
                return decision.replace("ANSWER ", "")

            if decision.startswith("JUMP"):
                try:
                    target = int(decision.split()[1])
                    current_pos = target
                except Exception:
                    print(f"{'  ' * depth}  ! Error parsing Jump")

            elif decision.startswith("READ_NEXT"):
                current_pos += self.env.chunk_size

            elif decision.startswith("RECURSE"):
                # *** THE RECURSIVE MAGIC ***
                # The agent found a complex topic and spawns a NEW agent to solve just that part.
                sub_query = decision.replace("RECURSE ", "")
                if depth < self.max_depth:
                    sub_answer = self.solve(sub_query, start_index=current_pos, depth=depth + 1)
                    # The sub-agent returns its finding, which becomes context for the parent
                    print(f"{'  ' * depth}  Sub-agent returned: {sub_answer}")
                    # We might assume the sub-agent answered the question, or we continue
                    return sub_answer
                return "Error: Max recursion depth reached."

            steps_taken += 1

        return "I could not find the answer within the step limit."


# --- USAGE ---
if __name__ == "__main__":
    # 1. Create a dummy text file to simulate a large book
    dummy_text = (
        "Index: Chapter 1 (0-1000), Chapter 2 (1000-2000)... "
        + ("." * 15000)
        + " Specific Answer: The solution is 42."
    )
    with open("large_book.txt", "w") as f:
        f.write(dummy_text)

    # 2. Initialize
    llm = LLMClient(api_key="your-key-here")
    environment = TextEnvironment("large_book.txt")
    agent = RecursiveAgent(llm, environment)

    # 3. Run
    final_answer = agent.solve("What is the solution mentioned in Chapter 2?")
    print(f"\nFINAL ANSWER: {final_answer}")
