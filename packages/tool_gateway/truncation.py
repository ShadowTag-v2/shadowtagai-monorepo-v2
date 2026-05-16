# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Layer 1 stdout truncation limits for tool responses."""

from typing import Any


class StdoutTruncator:
  """Handles Layer 1 truncation to prevent context window overflow from excessive tool output."""

  def __init__(
    self,
    max_length: int = 10000,
    truncation_message: str = "\n...[Output truncated due to length limits]...",
  ):
    """
    Initialize the truncator.

    Args:
        max_length (int): Maximum allowed characters before truncation.
        truncation_message (str): Message appended when output is truncated.
    """
    self.max_length = max_length
    self.truncation_message = truncation_message

  def truncate(self, text: str) -> str:
    """
    Truncate text if it exceeds the maximum length.

    Args:
        text (str): The stdout or stderr text to evaluate.

    Returns:
        str: The potentially truncated text.
    """
    if len(text) > self.max_length:
      return text[: self.max_length] + self.truncation_message
    return text

  def apply_to_tool_result(self, result: dict[str, Any]) -> dict[str, Any]:
    """
    Apply truncation limits to a tool execution result dictionary.

    Args:
        result (Dict[str, Any]): The tool result containing 'stdout' and 'stderr'.

    Returns:
        Dict[str, Any]: The result dictionary with truncated outputs.
    """
    processed_result = result.copy()

    if "stdout" in processed_result and isinstance(processed_result["stdout"], str):
      processed_result["stdout"] = self.truncate(processed_result["stdout"])

    if "stderr" in processed_result and isinstance(processed_result["stderr"], str):
      processed_result["stderr"] = self.truncate(processed_result["stderr"])

    return processed_result
