import json
import fnmatch
from tree_sitter import Language, Parser
import tree_sitter_bash as tsbash


class ASTSecurityPipeline:
  """Ported from utils/bash/: Deterministic AST parsing for shell safety."""

  def __init__(self, settings_path="Settings.json"):
    self.parser = Parser()
    self.parser.set_language(Language(tsbash.language(), "bash"))
    self.block_reason = None

    try:
      with open(settings_path, "r") as f:
        self.rules = json.load(f).get("permissions", {"allow": [], "deny": []})
    except FileNotFoundError:
      self.rules = {"allow": ["*"], "deny": []}

  def can_use_tool(self, tool_name: str, args: dict) -> dict:
    self.block_reason = None
    command = args.get("command", "")
    formatted_call = f"{tool_name}({command})" if command else tool_name

    if command:
      tree = self.parser.parse(bytes(command, "utf8"))
      self._traverse_ast(tree.root_node)
      if self.block_reason:
        return {"blocked": True, "reason": self.block_reason}

    for deny_glob in self.rules.get("deny", []):
      if fnmatch.fnmatch(formatted_call, deny_glob):
        return {"blocked": True, "reason": f"🛑 BLOCKED by deny rule: {deny_glob}"}

    for allow_glob in self.rules.get("allow", []):
      if fnmatch.fnmatch(formatted_call, allow_glob):
        return {"blocked": False, "reason": "ALLOWED"}

    return {"blocked": True, "reason": "Fail-closed (no allow rule matched)."}

  def _traverse_ast(self, node):
    if self.block_reason:
      return
    node_text = node.text.decode("utf8").lower() if node.text else ""

    if node.type == "pipeline":
      has_network = any(cmd in node_text for cmd in ["curl", "wget"])
      has_exec = any(cmd in node_text for cmd in ["bash", "sh", "eval"])
      if has_network and has_exec:
        self.block_reason = "CRITICAL: Network-to-Shell Pipeline Detected (curl | bash)"
        return

    if node.type == "command_name" and node_text in [
      "history",
      "rm ~/.bash_history",
      "sudo",
      "su",
      "chsh",
    ]:
      self.block_reason = (
        f"CRITICAL: Unauthorized escalation/manipulation ({node_text})"
      )
      return

    if node.type == "function_definition":
      name_node = node.child_by_field_name("name")
      if name_node and name_node.text and name_node.text.decode("utf8") == ":":
        self.block_reason = "CRITICAL: Fork Bomb Geometry Detected"
        return

    for child in node.children:
      self._traverse_ast(child)
