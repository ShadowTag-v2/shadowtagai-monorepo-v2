from app.schemas import RiskLevel, TaskRequest

# Keywords that trigger higher risk levels
RED_KEYWORDS = [
    "auth",
    "security",
    "password",
    "key",
    "secret",
    "payment",
    "crypto",
    "database_migration",
]
AMBER_KEYWORDS = ["refactor", "api_change", "schema", "config"]

# File patterns
RED_FILES = ["*.env", "secrets.py", "auth.py", "security.py"]
AMBER_FILES = ["models.py", "schemas.py", "config.py"]


def calculate_risk(request: TaskRequest) -> RiskLevel:
    """Determines the risk level of a task based on description/content and file paths."""
    text = request.description.lower()

    # 1. Check Keywords
    if any(k in text for k in RED_KEYWORDS):
        return RiskLevel.RED
    if any(k in text for k in AMBER_KEYWORDS):
        return RiskLevel.AMBER

    # 2. Check Files (Simple extension/name match)
    # real implementation would use fnmatch
    for f in request.file_paths:
        f_lower = f.lower()
        if "auth" in f_lower or "secret" in f_lower or ".env" in f_lower:
            return RiskLevel.RED
        if "model" in f_lower or "schema" in f_lower or "config" in f_lower:
            return RiskLevel.AMBER

    return RiskLevel.GREEN
