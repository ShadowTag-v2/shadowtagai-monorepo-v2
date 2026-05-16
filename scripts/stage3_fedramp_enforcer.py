# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import re
from pathlib import Path


def sanitize_fedramp_llms(root_path: Path):
    """
    Sips the scales: forcibly replaces all occurrences of non-FedRAMP LLMs
    (Ollama, Qwen, DeepSeek, Llama, Mistral, Anthropic, OpenAI)
    with `gemini-3.1-family`.
    """
    targets = [
        "apps/aiyou_stack/Qwen3-Coder",
        "apps/aiyou_stack/slash-commands",
        "apps/aiyou_stack/aiyou-fastapi-services/vendor/langgraph",
        "apps/aiyou_stack/aiyou-fastapi-services/vendor/langchain",
        "apps/aiyou_stack/claudesync",
        "apps/aiyou_stack/claude-quickstarts",
        "external_sdks/GitNexus",
        "external_sdks/ollama",
        "external_sdks/nanochat",
    ]

    # Regex to catch various model literal names
    pattern = re.compile(
        r"(qwen(?:2\.5|3)?(?:-coder)?|llama(?:-?[23](?:\.\db|b)?)?-?(?:instruct|chat)?|deepseek(?:-coder|-v2|-r1)?|mistral(?:-large|-nemo|-small)?|claude-[23](?:\.[57])?-(?:sonnet|opus|haiku)(?:-\d{8})?|gpt-[34]o?(?:-turbo|-mini)?(?:-\d{4}-\d{2}-\d{2})?|text-embedding(?:-3)?-(?:small|large|ada-\d{3}))",
        re.IGNORECASE,
    )

    replace_count = 0
    file_count = 0

    for target in targets:
        target_dir = root_path / target
        if not target_dir.exists():
            continue

        for filepath in target_dir.rglob("*"):
            if not filepath.is_file() or filepath.is_symlink() or ".git" in filepath.parts:
                continue

            try:
                content = filepath.read_text(encoding="utf-8")
                if pattern.search(content):
                    new_content = pattern.sub("gemini-3.1-family", content)
                    filepath.write_text(new_content, encoding="utf-8")
                    replace_count += 1
                    file_count += 1
                    print(f"  [FEDRAMP ENFORCED] Slipped scale in: {filepath.relative_to(root_path)}")
            except (UnicodeDecodeError, IsADirectoryError, PermissionError):
                pass

    print("\n==============================")
    print("FEDRAMP SWEEP COMPLETE")
    print("==============================")
    print(f"Files Modified: {file_count}")
    print(f"Total Replacements: {replace_count}")


if __name__ == "__main__":
    monorepo_root = Path("/Users/pikeymickey/.gemini/antigravity/Monorepo-Uphillsnowball")
    sanitize_fedramp_llms(monorepo_root)
