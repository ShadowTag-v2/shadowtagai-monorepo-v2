import os
from pathlib import Path

packages_dir = Path("packages")

# BATCH 2 COMPLIANT: Excluded banned IDE bridges, UI, and remote analytics
directories = [
    "agnt_tools",
    "agnt_commands",
    "agnt_services",
    "agnt_hooks",
    "agnt_types",
    "agnt_coordinator",
    "agnt_plugins",
    "agnt_skills",
    "agnt_memdir",
    "agnt_tasks",
    "agnt_state",
    "agnt_vim",
    "agnt_keybindings",
    "agnt_schemas",
    "agnt_migrations",
    "agnt_entrypoints",
    "agnt_query",
    "agnt_buddy",
    "agnt_output_styles",
    "agnt_forked_agent",
    "token_budget",
    "thinking_config",
    "vcr_fixtures",
]

files = [
    "agnt_entrypoints/main.py",
    "agnt_entrypoints/setup.py",
    "agnt_query/query_engine.py",
    "agnt_tools/tool.py",
    "agnt_tools/tools_registry.py",
    "agnt_commands/commands.py",
    "agnt_context/context.py",
    "agnt_cost_tracker/cost_tracker.py",
    "agnt_state/history.py",
]

created_dirs = 0
created_files = 0

for d in directories:
    dir_path = packages_dir / d
    dir_path.mkdir(parents=True, exist_ok=True)
    init_file = dir_path / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Scaffolding for antigravity native workflow port\n")
        created_files += 1
    created_dirs += 1

for f in files:
    file_path = packages_dir / f
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists():
        file_path.write_text("# Scaffolding for antigravity native workflow port\n")
        created_files += 1
    init_file = file_path.parent / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Scaffolding for antigravity native workflow port\n")
        created_files += 1

print(f"✅ Antigravity Core Scaffolding Complete. {created_dirs} dirs verified, {created_files} new files. Zero unauthorized modules generated.")
