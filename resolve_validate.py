import re

with open("scripts/ai-validate.sh") as f:
  content = f.read()

# Replace block by keeping incoming branch content
pattern = re.compile(
  r"<<<<<<< HEAD.*?=======\n(.*?)\n>>>>>>> fix-invariants-103-105", re.DOTALL
)
resolved_content = pattern.sub(r"\1", content)

with open("scripts/ai-validate.sh", "w") as f:
  f.write(resolved_content)

# print("Conflicts resolved in ai-validate.sh")
