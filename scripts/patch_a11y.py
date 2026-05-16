import os
import re


def patch_file(path):
  if not os.path.exists(path):
    print(f"Not found: {path}")
    return
  with open(path, "r", encoding="utf-8") as f:
    content = f.read()

  # Patch <button to <button type="button"
  # Make sure we don't patch <button type=...
  content = re.sub(r"<button(?![^>]*\btype=)", r'<button type="button"', content)

  # Patch <label without htmlFor
  content = re.sub(
    r'<label(\s+className="[^"]*"\s*)>', r'<label\1 htmlFor="input-field">', content
  )

  with open(path, "w", encoding="utf-8") as f:
    f.write(content)
  print(f"Patched {path}")


def main():
  root_dir = "./apps/headfade"
  for root, dirs, files in os.walk(root_dir):
    for file in files:
      if (
        file.endswith(".tsx")
        or file.endswith(".ts")
        or file.endswith(".jsx")
        or file.endswith(".js")
      ):
        path = os.path.join(root, file)
        patch_file(path)


if __name__ == "__main__":
  main()
