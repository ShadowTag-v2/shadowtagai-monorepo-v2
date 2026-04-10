class EchoProtocol:
    def __init__(self, max_tokens=100000):
        self.max_tokens = max_tokens

    def amplify(self, query: str, context: str = "") -> str:
        """
        Applies the Leviathan 'Prompt Repetition' technique.
        TVR (Trust-Verify-Repeat) Protocol.
        Transforms: [QUERY] -> [QUERY][QUERY]

        Why: Allows token attention mechanism to 'see' the start of the
        instruction again after processing the context.
        """
        # Safety Check: Don't double if we are hitting context limits
        total_len = len(query) + len(context)
        if total_len > self.max_tokens:
            return f"{context}\n{query}"  # Fallback to standard

        # The Paper's winning format: <QUERY><QUERY>
        # We add a newline for readability, which the paper's 'Verbose' variant supports.
        amplified_prompt = f"""
        --- INSTRUCTION STREAM 1 ---
        {query}

        --- CONTEXT ---
        {context}

        --- INSTRUCTION STREAM 2 (ATTENTION REINFORCEMENT) ---
        {query}
        """
        return amplified_prompt
