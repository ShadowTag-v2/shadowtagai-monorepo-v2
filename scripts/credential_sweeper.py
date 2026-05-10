import os
import re

TARGET_DIRS = ["apps", "core", "libs", "rag_engine", "scripts", "tools"]

# Patterns to match high-entropy secrets and keys
CREDENTIAL_PATTERNS = [
  # AWS Access Key
  (
    re.compile(
      r'(?i)(aws_access_key_id|aws_secret_access_key)\s*[:=]\s*["\'][A-Za-z0-9/+=]{16,40}["\']'
    ),
    r'\1 = "REDACTED_AWS_CREDENTIAL"',
  ),
  # Generic Bearer Tokens / API Keys
  (
    re.compile(
      r'(?i)(api[_-]?key|bearer|token|secret)\s*[:=]\s*["\'][A-Za-z0-9\-_]{20,}["\']'
    ),
    r'\1 = "REDACTED_API_KEY"',
  ),
  # GCP Service Account generic JSON matching (simplified)
  (
    re.compile(
      r'"private_key":\s*"-----BEGIN PRIVATE KEY-----\\n[a-zA-Z0-9/+=_\\n]+-----END PRIVATE KEY-----\\n"'
    ),
    r'"private_key": "REDACTED_GCP_PRIVATE_KEY"',
  ),
  # MongoDB/Postgres URIs
  (
    re.compile(r"(mongodb(?:\+srv)?|postgresql|postgres)://[^:]+:[^@]+@"),
    r"\1://REDACTED_USER:REDACTED_PASS@",
  ),
]


def sweep_file(filepath) -> None:
  try:
    with open(filepath, encoding="utf-8") as f:
      content = f.read()
  except Exception:
    return  # Skip binary or unreadable files

  original = content
  for pattern, replacement in CREDENTIAL_PATTERNS:
    content = pattern.sub(replacement, content)

  if content != original:
    with open(filepath, "w", encoding="utf-8") as f:
      f.write(content)


def main() -> None:
  scanned = 0
  for d in TARGET_DIRS:
    if not os.path.exists(d):
      continue
    for root, dirs, files in os.walk(d):
      # Skip hidden dirs
      dirs[:] = [d for d in dirs if not d.startswith(".")]
      for file in files:
        if file.endswith(
          (
            ".py",
            ".json",
            ".yaml",
            ".yml",
            ".ts",
            ".js",
            ".md",
            ".sh",
            ".env.example",
          ),
        ):
          sweep_file(os.path.join(root, file))
          scanned += 1


if __name__ == "__main__":
  main()
