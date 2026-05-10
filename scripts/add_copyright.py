import os

header = "# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.\n"
exclude_dirs = {
  "external_repos",
  "scratch",
  ".venv",
  "site-packages",
  "build",
  "node_modules",
  ".git",
}

count = 0
for root, dirs, files in os.walk("."):
  dirs[:] = [d for d in dirs if d not in exclude_dirs]

  for file in files:
    if not file.endswith(".py"):
      continue
    filepath = os.path.join(root, file)

    with open(filepath) as f:
      content = f.read()

    if header.strip() not in content:
      if content.startswith("#!"):
        parts = content.split("\n", 1)
        if len(parts) > 1:
          new_content = parts[0] + "\n" + header + "\n" + parts[1]
        else:
          new_content = parts[0] + "\n" + header
      else:
        new_content = header + "\n" + content

      with open(filepath, "w") as f:
        f.write(new_content)
      count += 1

print(f"Added copyright header to {count} files.")
