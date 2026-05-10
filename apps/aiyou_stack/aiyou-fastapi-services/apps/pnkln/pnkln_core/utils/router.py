def route_task(task_description: str) -> str:
    """Routes a task description to the appropriate agent or category.

    Args:
        task_description: The input string describing the task.

    Returns:
        A string representing the target category ('dev', 'ops', 'legal', 'general').

    """
    normalized_task = task_description.strip().lower()
    if "code" in normalized_task or "develop" in normalized_task:
        return "dev"
    if "ops" in normalized_task or "deploy" in normalized_task:
        return "ops"
    if "filing" in normalized_task or "legal" in normalized_task:
        return "legal"
    return "general"
