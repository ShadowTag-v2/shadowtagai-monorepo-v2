# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os


def replace_in_file(filepath):
  try:
    with open(filepath, encoding="utf-8") as f:
      content = f.read()
  except (UnicodeDecodeError, FileNotFoundError):
    return False

  new_content = content.replace("Claude_Code_6", "Cor_Claude_Code_6")
  new_content = new_content.replace("CLAUDE_CODE_6", "COR_CLAUDE_CODE_6")
  new_content = new_content.replace("Kairos", "Cor_Kairos")
  new_content = new_content.replace("KAIROS", "COR.KAIROS")

  if new_content != content:
    with open(filepath, "w", encoding="utf-8") as f:
      f.write(new_content)
    return True
  return False


def main():
  root_dir = "."
  for dirpath, _dirnames, filenames in os.walk(root_dir):
    if (
      ".git" in dirpath
      or "node_modules" in dirpath
      or "__pycache__" in dirpath
      or ".junie" in dirpath
      or ".agents" in dirpath
    ):
      continue

    for filename in filenames:
      if filename == "rename_Claude_Code_6.py":
        continue
      filepath = os.path.join(dirpath, filename)
      replace_in_file(filepath)

      new_filename = filename
      if "Claude_Code_6" in new_filename:
        new_filename = new_filename.replace("Claude_Code_6", "Cor_Claude_Code_6")
      if "Kairos" in new_filename:
        new_filename = new_filename.replace("Kairos", "Cor_Kairos")

      if new_filename != filename:
        new_filepath = os.path.join(dirpath, new_filename)
        try:
          os.rename(filepath, new_filepath)
          print(f"Renamed {filepath} to {new_filepath}")
        except FileNotFoundError:
          pass


if __name__ == "__main__":
  main()
