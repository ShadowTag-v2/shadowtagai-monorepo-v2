import re


class SecretScanner:
    def __init__(self):
        # Assembled at runtime so the scanner doesn't detect its own source code
        self.anthropic = "".join(["s", "k", "-", "a", "n", "t", "-", "a", "p", "i"])
        self.github = "".join(["g", "h", "p", "_"])

    def scan(self, text: str) -> str:
        text = re.sub(f"{self.anthropic}[A-Za-z0-9_-]{{20,}}", "[REDACTED_API_KEY]", text)
        text = re.sub(f"{self.github}[A-Za-z0-9]{{36}}", "[REDACTED_GITHUB_PAT]", text)
        return text
