# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import os
import re


def replace_in_file(filepath):
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        return False

    new_content = re.sub(r"judge6", "Claude_Code_6", content, flags=re.IGNORECASE)
    new_content = re.sub(r"judge_six", "Claude_Code_6", new_content, flags=re.IGNORECASE)

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False


def main():
    root_dir = "."
    for dirpath, _dirnames, filenames in os.walk(root_dir, topdown=False):
        if (
            ".git" in dirpath
            or "node_modules" in dirpath
            or "__pycache__" in dirpath
            or ".junie" in dirpath
            or ".agents" in dirpath
            or ".venv" in dirpath
            or "venv" in dirpath
        ):
            continue

        for filename in filenames:
            if filename == "rename_judge6_to_Claude_Code_6.py" or filename == "rename_Claude_Code_6.py":
                continue
            filepath = os.path.join(dirpath, filename)

            # replace inside file
            if replace_in_file(filepath):
                print(f"Replaced content in {filepath}")

            new_filename = filename
            new_filename = re.sub(r"judge6", "Claude_Code_6", new_filename, flags=re.IGNORECASE)
            new_filename = re.sub(r"judge_six", "Claude_Code_6", new_filename, flags=re.IGNORECASE)

            if new_filename != filename:
                new_filepath = os.path.join(dirpath, new_filename)
                try:
                    os.rename(filepath, new_filepath)
                    print(f"Renamed file {filepath} to {new_filepath}")
                except FileNotFoundError:
                    pass

        # rename directories
        dir_name = os.path.basename(dirpath)
        new_dir_name = re.sub(r"judge6", "Claude_Code_6", dir_name, flags=re.IGNORECASE)
        new_dir_name = re.sub(r"judge_six", "Claude_Code_6", new_dir_name, flags=re.IGNORECASE)

        if new_dir_name != dir_name:
            parent_dir = os.path.dirname(dirpath)
            new_dirpath = os.path.join(parent_dir, new_dir_name)
            try:
                os.rename(dirpath, new_dirpath)
                print(f"Renamed directory {dirpath} to {new_dirpath}")
            except Exception as e:
                print(f"Error renaming directory {dirpath}: {e}")


if __name__ == "__main__":
    main()
