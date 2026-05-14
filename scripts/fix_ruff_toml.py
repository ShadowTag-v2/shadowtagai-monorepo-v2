# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import glob


def fix_toml(filepath):
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return

    changed = False
    in_tool_ruff = False
    in_tool_ruff_lint = False
    out_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped == "[tool.ruff]":
            in_tool_ruff = True
        elif stripped.startswith("[") and stripped.endswith("]"):
            if stripped == "[tool.ruff.lint]":
                in_tool_ruff_lint = True
                in_tool_ruff = False
            elif stripped != "[tool.ruff]":
                in_tool_ruff = False
                in_tool_ruff_lint = False

        if in_tool_ruff and "=" in stripped and not stripped.startswith("#") and not stripped.startswith("["):
            key = stripped.split("=")[0].strip()
            if key in [
                "select",
                "ignore",
                "per-file-ignores",
                "fixable",
                "unfixable",
                "dummy-variable-rgx",
                "typing-modules",
            ]:
                line = line.replace(key, f"lint.{key}", 1)
                changed = True

        out_lines.append(line)

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(out_lines)
        print(f"Fixed {filepath}")


if __name__ == "__main__":
    # Fix in apps and libs
    count = 0
    for file_path in glob.glob("**/*.toml", recursive=True):
        if "node_modules" in file_path or ".venv" in file_path or "archive" in file_path:
            continue
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                if "[tool.ruff]" in content:
                    fix_toml(file_path)
                    count += 1
        except Exception:
            pass
    print(f"Ruff settings check complete. Processed {count} toml files with ruff configs.")
