import json
import os


class MemoryBank:
    """
    Stores learned rules to suppress repetitive false positives.
    Loads from 'learned_rules.json' (Ingested from Teleport Sessions).
    """

    def __init__(self):
        self.rules_path = "src/governance/memory/learned_rules.json"
        self.learned_rules = []
        if os.path.exists(self.rules_path):
            with open(self.rules_path) as f:
                self.learned_rules = json.load(f)
        else:
            # Default static rules
            self.learned_rules = [
                {
                    "context": "python",
                    "file_match": "test",
                    "rule": "allow_wildcard_imports",
                    "action": "suppress",
                }
            ]

    def consult(self, file_path: str, finding_type: str) -> str:
        for rule in self.learned_rules:
            if rule.get("file_match", "") in file_path and rule.get("rule") == finding_type:
                return "ALLOW" if rule["action"] == "suppress" else "NEUTRAL"
        return "NEUTRAL"
