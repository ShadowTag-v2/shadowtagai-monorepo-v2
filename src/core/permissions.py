import fnmatch

class PermissionLearner:
    def __init__(self):
        self.rules = {"allow": ["git status", "npm run *"], "deny": ["rm -rf /"]}
        
    def is_allowed(self, command: str):
        for rule in self.rules['deny']:
            if fnmatch.fnmatch(command, rule): return False
        for rule in self.rules['allow']:
            if fnmatch.fnmatch(command, rule): return True
        return None # Require manual operator approval
        
    def suggest_rule(self, command: str):
        parts = command.split()
        return f"{parts[0]} {parts[1]} *" if len(parts) >= 2 else f"{command} *"
