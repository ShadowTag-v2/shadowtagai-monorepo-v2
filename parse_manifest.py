import yaml
with open('monorepo_manifest.yaml') as f:
    manifest = yaml.safe_load(f)

valid_roots = set()

# Parse repo_roots
if 'repo_roots' in manifest:
    for item in manifest['repo_roots']:
        if 'path' in item:
            top_level = item['path'].split('/')[0]
            valid_roots.add(top_level)

print("Valid Top-Level Directories defined in Manifest:")
print(sorted(list(valid_roots)))
