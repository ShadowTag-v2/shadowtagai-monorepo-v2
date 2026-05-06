import os

exclude_dirs = {'.git', 'node_modules', '.next', 'out', '.agent', '.beads', 'public-v1-archive', '__pycache__', '.venv', 'venv'}
exclude_exts = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.mp4', '.webm', '.zip', '.tar', '.gz', '.pdf'}

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False
        
    if 'ShadowTagAI' in content:
        new_content = content.replace('ShadowTagAI', 'ShadowTagAI')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")
        return True
    return False

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
    
    for file in files:
        if file.startswith('.') or any(file.endswith(ext) for ext in exclude_exts):
            continue
        if 'public/dev' in root or 'public-v1-archive' in root:
            continue
        filepath = os.path.join(root, file)
        replace_in_file(filepath)
