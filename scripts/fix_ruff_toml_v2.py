# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os


def fix_toml(filepath):
  try:
    with open(filepath, encoding="utf-8") as f:
      lines = f.readlines()
  except Exception:
    return

  changed = False
  in_tool_ruff = False
  out_lines = []

  for line in lines:
    stripped = line.strip()

    if stripped == "[tool.ruff]":
      in_tool_ruff = True
    elif stripped.startswith("[") and stripped.endswith("]"):
      if stripped == "[tool.ruff.lint]":
        in_tool_ruff = False
      elif stripped != "[tool.ruff]":
        in_tool_ruff = False

    if (
      in_tool_ruff
      and "=" in stripped
      and not stripped.startswith("#")
      and not stripped.startswith("[")
    ):
      key = stripped.split("=")[0].strip()
      if key in [
        "select",
        "ignore",
        "per-file-ignores",
        "fixable",
        "unfixable",
        "dummy-variable-rgx",
        "typing-modules",
      ]:
        line = line.replace(key, f"lint.{key}", 1)
        changed = True

    out_lines.append(line)

  if changed:
    with open(filepath, "w", encoding="utf-8") as f:
      f.writelines(out_lines)
    print(f"Fixed {filepath}")


count = 0
for root, dirs, files in os.walk("."):
  if ".venv" in root or "node_modules" in root or "archive" in root:
    continue
  for file in files:
    if file.endswith(".toml"):
      file_path = os.path.join(root, file)
      try:
        with open(file_path, encoding="utf-8") as f:
          content = f.read()
          if "[tool.ruff]" in content:
            fix_toml(file_path)
            count += 1
      except Exception:
        pass
print(f"Ruff settings check complete. Processed {count} toml files with ruff configs.")
