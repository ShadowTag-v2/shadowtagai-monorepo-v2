import os
import re

ignored_dirs = {'.git', '.gemini', 'node_modules', '.next', 'dist', 'build', '.tmp.drivedownload', '.tmp.driveupload'}
ignored_exts = {'.png', '.jpg', '.webp', '.mp4', '.pack', '.idx', '.woff', '.woff2', '.pyc'}

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'ShadowTagAI' in content:
            new_content = content.replace('ShadowTagAI', 'ShadowTagAI')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filepath}")
    except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
        pass

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ignored_dirs]
    for file in files:
        if not any(file.endswith(ext) for ext in ignored_exts):
            replace_in_file(os.path.join(root, file))
