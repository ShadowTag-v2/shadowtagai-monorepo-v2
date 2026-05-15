import os
import sys

TEMPLATE = """
from google.adk.tools import BaseTool

class {tool_name}Tool(BaseTool):
    \"\"\"
    TODO: Add tool description.
    \"\"\"

    def execute(self, arg1: str) -> dict:
        \"\"\"
        TODO: Implement logic.
        \"\"\"
        return {{"status": "not implemented", "arg1": arg1}}

    def get_schema(self) -> dict:
        return {{
            "type": "object",
            "properties": {{
                "arg1": {{
                    "type": "string",
                    "description": "TODO: Description of argument"
                }}
            }},
            "required": ["arg1"]
        }}
"""


def scaffold(tool_name):
  filename = f"{tool_name}Tool.py"
  if os.path.exists(filename):
    print(f"Error: {filename} already exists.")
    sys.exit(1)

  content = TEMPLATE.format(tool_name=tool_name)
  with open(filename, "w") as f:
    f.write(content.strip())

  print(f"Created {filename}")


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: python scaffold_tool.py <ToolName>")
    sys.exit(1)

  scaffold(sys.argv[1])
