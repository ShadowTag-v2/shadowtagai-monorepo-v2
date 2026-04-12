class MemoryBank:
    """
    Sovereign OS Memory Layer.
    Suppresses/Overrides specific codebase heuristics using learned context.
    """

    def __init__(self):
        self.learned_rules = [
            {"pattern": "from * import", "action": "suppress", "context": "tests"}
        ]

    def consult(self, code_snippet: str, context: str) -> str:
        for rule in self.learned_rules:
            if rule["pattern"] in code_snippet and rule["context"] in context:
                return "ALLOW"
        return "NEUTRAL"
