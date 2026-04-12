import re

with open("monorepo_manifest.yaml", "r") as f:
    content = f.read()

# Replace all conflict blocks by picking the bottom section (after =======)
# and removing the conflict markers.
pattern = re.compile(r'<<<<<<< HEAD.*?=======\n(.*?)\n>>>>>>> fix-invariants-103-105', re.DOTALL)
resolved_content = pattern.sub(r'\1', content)

with open("monorepo_manifest.yaml", "w") as f:
    f.write(resolved_content)

print("Conflicts resolved.")
