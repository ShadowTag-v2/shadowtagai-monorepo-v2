# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os


def fix_file_content(path):
  try:
    with open(path) as f:
      content = f.read()
    if "Cor_Claude_Code_6" in content:
      content = content.replace("Cor_Claude_Code_6", "Cor_Claude_Code_6")
      with open(path, "w") as f:
        f.write(content)
      print(f"Fixed content in {path}")
  except Exception as e:
    print(f"Error reading {path}: {e}")


for root, _dirs, files in os.walk("."):
  for filename in files:
    if filename.endswith(".py"):
      filepath = os.path.join(root, filename)
      fix_file_content(filepath)
      if "Cor_Claude_Code_6" in filename:
        new_filename = filename.replace("Cor_Claude_Code_6", "Cor_Claude_Code_6")
        new_filepath = os.path.join(root, new_filename)
        os.rename(filepath, new_filepath)
        print(f"Renamed {filepath} to {new_filepath}")
